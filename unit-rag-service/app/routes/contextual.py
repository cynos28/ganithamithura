"""
Contextual questions generation based on AR measurements
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.services.question_generator import question_generator
from app.services.embeddings_service import embeddings_service
from app.models.database import QuestionModel, StudentAnswerModel
from app.services.adaptive_engine import adaptive_engine

router = APIRouter(prefix="/api/v1/contextual", tags=["Contextual Questions"])


class ARMeasurementContext(BaseModel):
    """Context from AR measurement"""
    measurement_type: str
    value: float
    unit: str
    object_name: str
    context_description: str
    topic: str
    personalized_prompt: str
    difficulty_hints: List[str] = Field(default_factory=list)


class ContextualQuestionRequest(BaseModel):
    """Request for AR-based contextual questions"""
    student_id: str
    measurement_context: ARMeasurementContext
    grade: int = Field(ge=1, le=5)
    num_questions: int = Field(default=5, ge=1, le=10)


class ContextualQuestion(BaseModel):
    """Generated contextual question"""
    question_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    difficulty_level: int
    hints: List[str] = Field(default_factory=list)


@router.post("/generate-questions")
async def generate_contextual_questions(request: ContextualQuestionRequest):
    """
    Generate personalized questions based on AR measurement
    
    Flow:
    1. Receive AR measurement context
    2. Use RAG to retrieve relevant curriculum content
    3. Generate personalized questions using the ACTUAL measurement
    4. Return questions with student's measured object
    """
    
    try:
        context = request.measurement_context
        
        # Build RAG query using the measurement context
        rag_query = f"{context.topic} measurement {context.value}{context.unit} {context.object_name}"
        
        print(f"🔍 RAG Query: {rag_query}")
        
        # Retrieve relevant chunks from RAG
        filter_meta = {"topic": context.topic} if hasattr(embeddings_service, 'collection') and embeddings_service.collection else {}
        relevant_chunks = await embeddings_service.search_similar_chunks(
            query=rag_query,
            n_results=5,
            filter_metadata=filter_meta
        )
        
        # Build context for question generation
        if relevant_chunks:
            curriculum_context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
            print(f"✅ Retrieved {len(curriculum_context)} characters from RAG")
        else:
            # Fallback to basic context
            curriculum_context = f"Teaching {context.topic} measurement concepts for grade {request.grade}"
            print(f"⚠️  No RAG chunks found, using fallback context")
        
        # Generate personalized questions
        questions = await _generate_ar_questions(
            measurement_context=context,
            curriculum_context=curriculum_context,
            grade=request.grade,
            num_questions=request.num_questions
        )
        
        # Save questions to database (with timeout protection)
        saved_questions = []
        for q_data in questions:
            try:
                question = QuestionModel(
                    unit_id=f"ar_{context.topic.lower()}_{request.student_id}",
                    topic=context.topic,
                    question_text=q_data['question_text'],
                    question_type=q_data.get('question_type', 'mcq'),
                    correct_answer=q_data['correct_answer'],
                    options=q_data.get('options'),
                    grade_level=request.grade,
                    difficulty_level=q_data.get('difficulty_level', 3),
                    explanation=q_data.get('explanation', ''),
                    hints=q_data.get('hints', []),
                    concepts=[context.topic, f"AR_{context.measurement_type}"],
                )
                
                await question.save()  # Beanie uses save() not insert()
                saved_questions.append(question)
            except Exception as db_error:
                # If DB save fails, still return the question
                print(f"⚠️  Failed to save question to DB: {str(db_error)}")
                # Create a dict version for response
                saved_questions.append(q_data)
        
        print(f"✅ Generated and saved {len(saved_questions)} contextual questions")
        
        return {
            "success": True,
            "measurement_context": {
                "object": context.object_name,
                "measurement": f"{context.value}{context.unit}",
                "topic": context.topic,
            },
            "questions": [
                ContextualQuestion(
                    question_id=str(q.id),
                    question_text=q.question_text,
                    question_type=q.question_type,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    explanation=q.explanation,
                    difficulty_level=q.difficulty_level,
                    hints=q.hints,
                )
                for q in saved_questions
            ],
            "total_questions": len(saved_questions),
        }
        
    except Exception as e:
        print(f"❌ Error generating contextual questions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating contextual questions: {str(e)}"
        )


async def _generate_ar_questions(
    measurement_context: ARMeasurementContext,
    curriculum_context: str,
    grade: int,
    num_questions: int,
    target_difficulty: Optional[int] = None,
    exclude_questions: List[str] = None
) -> List[dict]:
    """Generate questions using LLM with AR measurement context"""
    
    from app.utils.llm_client import llm_client
    import json
    import random
    
    exclude_questions = exclude_questions or []
    
    # Add variety prompts to ensure different question types
    variety_prompts = [
        "Focus on unit conversion questions",
        "Create comparison questions (bigger/smaller)",
        "Generate measurement calculation questions", 
        "Ask about practical applications",
        "Create estimation and rounding questions"
    ]
    
    selected_variety = random.choice(variety_prompts)
    exclusion_note = f"\n\nAVOID THESE RECENT QUESTIONS:\n{chr(10).join([f'- {q}' for q in exclude_questions])}" if exclude_questions else ""
    
    # Build personalized prompt
    difficulty_instruction = f"at difficulty level {target_difficulty} (1=easiest, 5=hardest)" if target_difficulty else "progressing from easy to hard"
    
    prompt = f"""Generate {num_questions} educational question(s) {difficulty_instruction} based on this REAL measurement by a student:

STUDENT'S MEASUREMENT:
{measurement_context.personalized_prompt}
Object: {measurement_context.object_name}
Exact measurement: {measurement_context.value}{measurement_context.unit}
Topic: {measurement_context.topic}
Grade Level: {grade}

CURRICULUM CONTEXT:
{curriculum_context[:2000]}

VARIETY FOCUS: {selected_variety}

CRITICAL RULES FOR AR-BASED QUESTIONS:
1. Use "YOUR {measurement_context.object_name}" to make it personal
2. Reference the EXACT measurement ({measurement_context.value}{measurement_context.unit})
3. Make questions conversational, like talking about THEIR object
4. Create DIFFERENT types of questions each time for variety
5. Include these difficulty hints: {', '.join(measurement_context.difficulty_hints[:3])}

EXAMPLE GOOD QUESTIONS:
✅ "Your {measurement_context.object_name} is {measurement_context.value}{measurement_context.unit}. How many millimeters is that?"
✅ "If you have 3 {measurement_context.object_name}s like yours, what is the total length?"
✅ "Your {measurement_context.object_name} is {measurement_context.value}{measurement_context.unit}. Is it longer or shorter than 20cm?"
✅ "Round your {measurement_context.object_name}'s measurement to the nearest 10cm."

AVOID GENERIC QUESTIONS:
❌ "A pencil is X cm. Convert to mm." (too generic)
❌ "What is the length?" (doesn't use their measurement){exclusion_note}

Generate ONLY valid JSON in this format:
{{
  "questions": [
    {{
      "question_text": "Your question here using THEIR measurement",
      "question_type": "mcq",
      "correct_answer": "Answer text",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "difficulty_level": 1-5,
      "explanation": "Why this is correct",
      "hints": ["Hint 1", "Hint 2"]
    }}
  ]
}}
"""
    
    try:
        # Generate using existing LLM client
        response = await llm_client.generate_completion(
            prompt=prompt,
            system_message=f"You are an expert math teacher creating personalized questions about a student's REAL measurement. Grade {grade}.",
            temperature=0.8,
            max_tokens=2000
        )
        
        # Parse JSON response
        response_text = response.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        questions_data = json.loads(response_text.strip())
        
        return questions_data.get('questions', [])
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        # Return fallback questions
        return _generate_fallback_questions(measurement_context, grade, num_questions)
    
    except Exception as e:
        print(f"❌ LLM generation error: {str(e)}")
        return _generate_fallback_questions(measurement_context, grade, num_questions)


def _generate_fallback_questions(
    context: ARMeasurementContext,
    grade: int,
    num_questions: int
) -> List[dict]:
    """Generate simple fallback questions if LLM fails"""
    
    questions = []
    
    # Basic conversion question
    if context.measurement_type == "length" and context.unit == "cm":
        questions.append({
            "question_text": f"Your {context.object_name} is {context.value}cm long. How many millimeters is that?",
            "question_type": "mcq",
            "correct_answer": f"{context.value * 10}mm",
            "options": [f"{context.value * 10}mm", f"{context.value * 100}mm", f"{context.value}mm", f"{context.value / 10}mm"],
            "difficulty_level": 2,
            "explanation": f"1 cm = 10 mm, so {context.value}cm = {context.value * 10}mm",
            "hints": ["Remember: 1 centimeter = 10 millimeters"]
        })
    
    # Multiplication question
    questions.append({
        "question_text": f"If you have 2 {context.object_name}s like yours, what is the total {context.measurement_type}?",
        "question_type": "mcq",
        "correct_answer": f"{context.value * 2}{context.unit}",
        "options": [f"{context.value * 2}{context.unit}", f"{context.value * 3}{context.unit}", f"{context.value}{context.unit}", f"{context.value / 2}{context.unit}"],
        "difficulty_level": 1,
        "explanation": f"{context.value} + {context.value} = {context.value * 2}",
        "hints": ["Add the two measurements together"]
    })
    
    return questions[:num_questions]


@router.post("/adaptive-measurement-question")
async def get_adaptive_measurement_question(request: ContextualQuestionRequest):
    """
    Get next adaptive question based on measurement context
    Uses IRT to select optimal difficulty for student
    """
    
    try:
        context = request.measurement_context
        
        # Get or create student ability state for this measurement type (grade-aware)
        unit_id = f"measurement_{context.measurement_type}_{request.student_id}"
        student_ability = await adaptive_engine.get_student_state(
            student_id=request.student_id,
            unit_id=unit_id,
            grade_level=request.grade
        )
        
        # Calculate optimal difficulty based on current ability and grade
        target_difficulty = adaptive_engine.select_optimal_difficulty(
            student_ability.ability_score,
            grade_level=request.grade
        )
        
        print(f"🎯 Student ability: {student_ability.ability_score:.2f}, Target difficulty: {target_difficulty}")
        
        # Get recent questions to avoid repetition
        recent_questions = await QuestionModel.find(
            QuestionModel.unit_id == unit_id,
            QuestionModel.grade_level == request.grade
        ).sort(-QuestionModel.id).limit(5).to_list()
        
        recent_question_texts = [q.question_text for q in recent_questions] if recent_questions else []
        
        # Build RAG query
        rag_query = f"{context.topic} measurement {context.value}{context.unit} {context.object_name}"
        
        # Retrieve relevant curriculum chunks
        filter_meta = {"topic": context.topic} if hasattr(embeddings_service, 'collection') and embeddings_service.collection else {}
        relevant_chunks = await embeddings_service.search_similar_chunks(
            query=rag_query,
            n_results=5,
            filter_metadata=filter_meta
        )
        
        # Build context
        if relevant_chunks:
            curriculum_context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
        else:
            curriculum_context = f"Teaching {context.topic} measurement concepts for grade {request.grade}"
        
        # Generate ONE question at target difficulty (with uniqueness check)
        questions = await _generate_ar_questions(
            measurement_context=context,
            curriculum_context=curriculum_context,
            grade=request.grade,
            num_questions=1,
            target_difficulty=target_difficulty,
            exclude_questions=recent_question_texts  # Pass recent questions to avoid
        )
        
        if not questions:
            raise HTTPException(status_code=500, detail="Failed to generate question")
        
        q_data = questions[0]
        
        # Save question to database
        question = QuestionModel(
            unit_id=unit_id,
            topic=context.topic,
            question_text=q_data['question_text'],
            question_type=q_data.get('question_type', 'mcq'),
            correct_answer=q_data['correct_answer'],
            options=q_data.get('options'),
            grade_level=request.grade,
            difficulty_level=target_difficulty,
            explanation=q_data.get('explanation', ''),
            hints=q_data.get('hints', []),
            concepts=[context.topic, f"measurement_{context.measurement_type}"],
        )
        
        await question.save()
        
        print(f"✅ Generated adaptive question at difficulty {target_difficulty}")
        
        return {
            "success": True,
            "question": ContextualQuestion(
                question_id=str(question.id),
                question_text=question.question_text,
                question_type=question.question_type,
                options=question.options,
                correct_answer=question.correct_answer,
                explanation=question.explanation,
                difficulty_level=question.difficulty_level,
                hints=question.hints,
            ),
            "student_ability": student_ability.ability_score,
            "target_difficulty": target_difficulty,
        }
        
    except Exception as e:
        print(f"❌ Error generating adaptive measurement question: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating adaptive question: {str(e)}"
        )


@router.post("/submit-measurement-answer")
async def submit_measurement_answer(
    student_id: str,
    question_id: str,
    answer: str,
    measurement_type: str,
    time_taken: Optional[int] = None
):
    """
    Submit answer for measurement question and update student ability
    """
    
    try:
        # Get the question
        question = await QuestionModel.get(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Check if answer is correct
        is_correct = answer.strip().lower() == question.correct_answer.strip().lower()
        
        # Get student ability state (grade-aware - use grade 1 as default for now)
        # TODO: Store and retrieve actual student grade from profile
        grade = 1  # Default grade level
        unit_id = f"measurement_{measurement_type}_{student_id}"
        student_ability = await adaptive_engine.get_student_state(
            student_id=student_id,
            unit_id=unit_id,
            grade_level=grade
        )
        
        # Update ability using IRT
        old_ability = student_ability.ability_score
        new_ability = adaptive_engine.update_ability(
            current_ability=old_ability,
            is_correct=is_correct,
            question_difficulty=question.difficulty_level
        )
        
        # Calculate new target difficulty (grade-aware)
        new_target = adaptive_engine.select_optimal_difficulty(new_ability, grade_level=grade)
        
        # Update student record
        student_ability.ability_score = new_ability
        student_ability.current_difficulty = new_target
        await student_ability.save()
        
        # Save answer record
        answer_record = StudentAnswerModel(
            student_id=student_id,
            question_id=str(question.id),
            unit_id=unit_id,
            answer_given=answer,
            is_correct=is_correct,
            time_taken=time_taken or 0,
            difficulty_at_attempt=question.difficulty_level,
        )
        await answer_record.insert()
        
        print(f"📊 Ability: {old_ability:.2f} → {new_ability:.2f}, Next difficulty: {new_target}")
        
        return {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation,
            "old_ability": round(old_ability, 2),
            "new_ability": round(new_ability, 2),
            "next_difficulty": new_target,
            "ability_change": round(new_ability - old_ability, 2),
        }
        
    except Exception as e:
        print(f"❌ Error submitting measurement answer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting answer: {str(e)}"
        )
