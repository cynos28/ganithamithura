from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from app.models.database import DocumentModel, QuestionModel
from app.models.schemas import (
    QuestionGenerationRequest,
    QuestionResponse,
    QuestionCreate,
    QuestionUpdate
)
from app.services.question_generator import question_generator
from app.utils.llm_client import llm_client
from app.config import settings

router = APIRouter(prefix="/api/v1/questions", tags=["questions"])


@router.post("/generate")
async def generate_questions(
    request: QuestionGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate questions from a document (background task)
    
    - Retrieves document content
    - Generates questions for specified grade levels
    - Runs as background task
    """
    # Check for common placeholder mistakes
    if request.document_id.lower() in ['string', 'str', 'example', 'objectid']:
        raise HTTPException(
            status_code=400,
            detail="Please replace the example 'string' with an actual document ID from the uploaded documents list"
        )
    
    # Validate ObjectId format (24 hex characters)
    if len(request.document_id) != 24 or not all(c in '0123456789abcdef' for c in request.document_id.lower()):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document_id format. Must be a 24-character hexadecimal MongoDB ObjectId. Got: '{request.document_id}'"
        )
    
    # Verify document exists
    try:
        from bson import ObjectId
        document = await DocumentModel.find_one(DocumentModel.id == ObjectId(request.document_id))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid document_id format: {str(e)}"
        )
    
    if not document:
        raise HTTPException(
            status_code=404, 
            detail=f"Document with ID '{request.document_id}' not found. Please check the document ID from the upload list."
        )
    
    if document.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Document is not ready for question generation"
        )
    
    # Add background task
    background_tasks.add_task(
        generate_questions_task,
        document_id=request.document_id,
        grade_levels=request.grade_levels,
        questions_per_grade=request.questions_per_grade,
        question_types=['mcq', 'true_false'],  # Only MCQ and true/false for Flutter UI
        use_rag=request.use_rag,
        use_images=request.use_images
    )
    
    print(f"🚀 Starting question generation for document {request.document_id} (RAG: {request.use_rag}, Images: {request.use_images})")
    
    return {
        "message": "Question generation started in background",
        "document_id": request.document_id,
        "estimated_questions": len(request.grade_levels) * request.questions_per_grade,
        "status": "processing",
        "use_rag": request.use_rag,
        "use_images": request.use_images,
        "note": "Check GET /api/v1/questions/document/{document_id} to see generated questions"
    }


async def generate_questions_task(
    document_id: str,
    grade_levels: List[int],
    questions_per_grade: int,
    question_types: List[str],
    use_rag: bool = True,
    use_images: bool = True
):
    """Background task to generate questions using RAG, images, or full document"""
    mode = "RAG" if use_rag else "Full Document"
    mode += " + Vision" if use_images else ""
    print(f"📝 Question generation task started for document {document_id} (Mode: {mode})")
    try:
        from bson import ObjectId
        from app.services.image_question_generator import image_question_generator
        
        document = await DocumentModel.find_one(DocumentModel.id == ObjectId(document_id))
        
        if not document:
            print(f"❌ Document {document_id} not found in background task")
            return
        
        print(f"📄 Found document: {document.title}")
        print(f"📂 Topic: {document.topic}")
        print(f"🎯 Generating {questions_per_grade} questions per grade for grades {grade_levels}")
        
        all_questions = []
        
        # Check if topic is a measurement topic that has images
        measurement_topics = ["length", "area", "weight", "volume", "capacity"]
        has_images = document.topic and document.topic.lower() in measurement_topics
        
        for grade in grade_levels:
            grade_questions = []
            
            # Strategy 1: Generate image-based questions if enabled and images available
            if use_images and has_images:
                try:
                    print(f"\n📸 Generating ALL {questions_per_grade} image-based questions for Grade {grade}...")
                    print(f"   GPT-4 Vision will analyze real measurement photos")
                    
                    # Retrieve document context for vision prompts
                    context = await question_generator.retrieve_relevant_chunks(
                        document_id=document_id,
                        topic=document.topic,
                        grade_level=grade,
                        num_chunks=3
                    )
                    
                    # Generate ALL questions from images (100% image-based)
                    image_questions = await image_question_generator.generate_image_based_questions(
                        topic=document.topic.lower(),
                        grade_level=grade,
                        total_questions=questions_per_grade,
                        document_context=context
                    )
                    
                    grade_questions.extend(image_questions)
                    print(f"✅ Generated {len(image_questions)} image-based questions for Grade {grade}")
                    
                except Exception as img_err:
                    print(f"⚠️ Image generation failed: {img_err}")
                    import traceback
                    print(traceback.format_exc())
                    print("   Falling back to text-only generation")
            
            # Strategy 2: Generate text-based questions ONLY if image generation failed or disabled
            remaining_needed = questions_per_grade - len(grade_questions)
            
            if remaining_needed > 0:
                print(f"\n📝 Generating {remaining_needed} text-based questions for Grade {grade}...")
                
                text_questions = await question_generator.generate_questions_for_document(
                    document_id=document_id,
                    document_content=document.content,
                    grade_levels=[grade],
                    topic=document.topic or "measurement",
                    questions_per_grade=remaining_needed,
                    question_types=question_types,
                    use_rag=use_rag
                )
                
                grade_questions.extend(text_questions)
                print(f"✅ Generated {len(text_questions)} text-based questions for Grade {grade}")
            
            all_questions.extend(grade_questions)
            print(f"📊 Total Grade {grade} questions: {len(grade_questions)}")
        
        print(f"\n💡 Total questions generated: {len(all_questions)}")
        
        # Save to MongoDB
        question_count = 0
        for q_data in all_questions:
            # Generate unit_id based on document topic and grade
            unit_id = f"unit_{document.topic.lower()}_{q_data['grade_level']}" if document.topic else None
            
            question = QuestionModel(
                document_id=document_id,
                unit_id=unit_id,
                topic=document.topic,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                correct_answer=q_data["correct_answer"],
                options=q_data.get("options"),
                grade_level=q_data["grade_level"],
                difficulty_level=q_data["difficulty_level"],
                bloom_level=q_data.get("bloom_level"),
                concepts=q_data.get("concepts", []),
                explanation=q_data.get("explanation"),
                hints=q_data.get("hints", []),
                image_url=q_data.get("image_url"),
                object_images=q_data.get("object_images")
            )
            await question.insert()
            question_count += 1
            
            has_image = "Image" if q_data.get("image_url") else "Icons" if q_data.get("object_images") else "Text"
            print(f"💾 Saved question {question_count}/{len(all_questions)} [{has_image}] - Grade {q_data['grade_level']}")
        
        # Update document question count
        document.questions_count = document.questions_count + question_count
        await document.save()
        
        print(f"\n✅ Generated {question_count} new questions for document {document_id}")
        print(f"📈 Total document questions: {document.questions_count}")
        
    except Exception as e:
        import traceback
        print(f"❌ Error generating questions: {str(e)}")
        print(traceback.format_exc())


@router.get("/document/{document_id}", response_model=List[QuestionResponse])
async def get_questions_by_document(
    document_id: str,
    grade_level: Optional[int] = None,
    difficulty_level: Optional[int] = None,
    question_type: Optional[str] = None
):
    """Get all questions for a document with optional filters"""
    print(f"🔍 Looking for questions with document_id: {document_id}")
    query = {"document_id": document_id}
    
    if grade_level:
        query["grade_level"] = grade_level
    if difficulty_level:
        query["difficulty_level"] = difficulty_level
    if question_type:
        query["question_type"] = question_type
    
    print(f"🔍 Query: {query}")
    questions = await QuestionModel.find(query).to_list()
    print(f"📊 Found {len(questions)} questions")
    
    # Return empty list instead of 404 if no questions found
    if not questions:
        print(f"⚠️ No questions found for document {document_id}")
        return []
    
    return [
        QuestionResponse(
            id=str(q.id),
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            grade_level=q.grade_level,
            difficulty_level=q.difficulty_level,
            bloom_level=q.bloom_level,
            concepts=q.concepts,
            explanation=q.explanation,
            hints=q.hints,
            image_url=q.image_url
        )
        for q in questions
    ]


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: str):
    """Get a specific question by ID"""
    # Check for placeholder values
    if question_id.lower() in ['string', 'str', 'example', 'objectid']:
        raise HTTPException(
            status_code=400,
            detail="Please replace 'string' with an actual question ID"
        )
    
    # Validate ObjectId format
    if len(question_id) != 24 or not all(c in '0123456789abcdef' for c in question_id.lower()):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid question_id format. Must be a 24-character hexadecimal MongoDB ObjectId"
        )
    
    try:
        from bson import ObjectId
        question = await QuestionModel.find_one(QuestionModel.id == ObjectId(question_id))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid question_id: {str(e)}"
        )
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return QuestionResponse(
        id=str(question.id),
        question_text=question.question_text,
        question_type=question.question_type,
        options=question.options,
        grade_level=question.grade_level,
        difficulty_level=question.difficulty_level,
        bloom_level=question.bloom_level,
        concepts=question.concepts,
        explanation=question.explanation,
        hints=question.hints,
        image_url=question.image_url
    )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: str, update: QuestionUpdate):
    """Update a question"""
    try:
        from bson import ObjectId
        question = await QuestionModel.find_one(QuestionModel.id == ObjectId(question_id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid question_id: {str(e)}")
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Update fields
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
    
    await question.save()
    
    return QuestionResponse(
        id=str(question.id),
        question_text=question.question_text,
        question_type=question.question_type,
        options=question.options,
        grade_level=question.grade_level,
        difficulty_level=question.difficulty_level,
        bloom_level=question.bloom_level,
        concepts=question.concepts,
        explanation=question.explanation,
        hints=question.hints,
        image_url=question.image_url
    )


@router.delete("/document/{document_id}/all")
async def delete_all_questions_for_document(document_id: str):
    """Delete all questions for a document"""
    try:
        from bson import ObjectId
        
        # Verify document exists
        document = await DocumentModel.find_one(DocumentModel.id == ObjectId(document_id))
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete all questions for this document
        questions = await QuestionModel.find({"document_id": document_id}).to_list()
        deleted_count = 0
        
        for question in questions:
            await question.delete()
            deleted_count += 1
        
        # Reset document question count
        document.questions_count = 0
        await document.save()
        
        print(f"🗑️ Deleted {deleted_count} questions for document {document_id}")
        
        return {
            "message": f"Deleted all questions for document",
            "document_id": document_id,
            "questions_deleted": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting questions: {str(e)}")


@router.delete("/{question_id}")
async def delete_question(question_id: str):
    """Delete a question"""
    try:
        from bson import ObjectId
        question = await QuestionModel.find_one(QuestionModel.id == ObjectId(question_id))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid question_id: {str(e)}")
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    await question.delete()
    
    return {"message": "Question deleted successfully"}
