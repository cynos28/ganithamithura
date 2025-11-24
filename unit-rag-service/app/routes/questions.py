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
    # Verify document exists
    document = await DocumentModel.get(request.document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
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
        question_types=request.question_types
    )
    
    return {
        "message": "Question generation started",
        "document_id": request.document_id,
        "estimated_questions": len(request.grade_levels) * request.questions_per_grade
    }


async def generate_questions_task(
    document_id: str,
    grade_levels: List[int],
    questions_per_grade: int,
    question_types: List[str]
):
    """Background task to generate questions"""
    try:
        document = await DocumentModel.get(document_id)
        
        if not document:
            print(f"Document {document_id} not found")
            return
        
        # Generate questions using the service
        questions = await question_generator.generate_questions_for_document(
            document_id=document_id,
            document_content=document.content,
            grade_levels=grade_levels,
            questions_per_grade=questions_per_grade,
            question_types=question_types
        )
        
        # Save to MongoDB
        question_count = 0
        for q_data in questions:
            question = QuestionModel(
                document_id=document_id,
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                correct_answer=q_data["correct_answer"],
                options=q_data.get("options"),
                grade_level=q_data["grade_level"],
                difficulty_level=q_data["difficulty_level"],
                bloom_level=q_data.get("bloom_level"),
                concepts=q_data.get("concepts", []),
                explanation=q_data.get("explanation"),
                hints=q_data.get("hints", [])
            )
            await question.insert()
            question_count += 1
        
        # Update document question count
        document.questions_count = question_count
        await document.save()
        
        print(f"✅ Generated {question_count} questions for document {document_id}")
        
    except Exception as e:
        print(f"❌ Error generating questions: {str(e)}")


@router.get("/document/{document_id}", response_model=List[QuestionResponse])
async def get_questions_by_document(
    document_id: str,
    grade_level: Optional[int] = None,
    difficulty_level: Optional[int] = None,
    question_type: Optional[str] = None
):
    """Get all questions for a document with optional filters"""
    query = {"document_id": document_id}
    
    if grade_level:
        query["grade_level"] = grade_level
    if difficulty_level:
        query["difficulty_level"] = difficulty_level
    if question_type:
        query["question_type"] = question_type
    
    questions = await QuestionModel.find(query).to_list()
    
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
            hints=q.hints
        )
        for q in questions
    ]


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: str):
    """Get a specific question by ID"""
    question = await QuestionModel.get(question_id)
    
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
        hints=question.hints
    )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: str, update: QuestionUpdate):
    """Update a question"""
    question = await QuestionModel.get(question_id)
    
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
        hints=question.hints
    )


@router.delete("/{question_id}")
async def delete_question(question_id: str):
    """Delete a question"""
    question = await QuestionModel.get(question_id)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    await question.delete()
    
    return {"message": "Question deleted successfully"}
