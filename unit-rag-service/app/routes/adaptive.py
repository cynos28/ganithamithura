"""
Adaptive learning routes — question-level IRT endpoints.

These complement the game-level IRT in routes/games.py.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.database import StudentAbilityModel, QuestionModel
from app.services.adaptive_engine import adaptive_engine

router = APIRouter(prefix="/api/v1/adaptive", tags=["Adaptive Learning"])


@router.get("/next-question")
async def get_next_question(
    student_id: str,
    unit_id: str,
    grade_level: int = Query(1, ge=1, le=5),
):
    """
    Select the next question at optimal difficulty for a student.
    Uses IRT to match question difficulty to student ability.
    """
    # Get / create student state
    ability = await adaptive_engine.get_student_state(
        student_id=student_id,
        unit_id=unit_id,
        grade_level=grade_level,
    )

    target = adaptive_engine.select_optimal_difficulty(
        ability.ability_score, grade_level=grade_level,
    )

    # Find a question at the target difficulty
    question = await QuestionModel.find_one(
        QuestionModel.unit_id == unit_id,
        QuestionModel.difficulty_level == target,
        QuestionModel.grade_level == grade_level,
    )

    # Fall back to any difficulty for this unit if exact match not found
    if question is None:
        question = await QuestionModel.find_one(
            QuestionModel.unit_id == unit_id,
            QuestionModel.grade_level == grade_level,
        )

    if question is None:
        raise HTTPException(404, "No questions available for this unit and grade")

    return {
        "question_id": str(question.id),
        "question_text": question.question_text,
        "question_type": question.question_type,
        "options": question.options,
        "difficulty": question.difficulty_level,
        "hints": question.hints,
        "current_ability": round(ability.ability_score, 3),
        "estimated_probability": round(
            adaptive_engine.update_ability.__func__  # just for display
            and 0.7,  # placeholder
            3,
        ),
    }


@router.post("/submit-answer")
async def submit_answer(
    student_id: str,
    question_id: str,
    unit_id: str,
    answer: str,
    grade_level: int = Query(1, ge=1, le=5),
    time_taken: Optional[int] = None,
):
    """Submit an answer and update student ability via IRT."""
    from bson import ObjectId
    from app.models.database import StudentAnswerModel

    try:
        question = await QuestionModel.find_one(
            QuestionModel.id == ObjectId(question_id)
        )
    except Exception:
        raise HTTPException(400, "Invalid question ID")

    if not question:
        raise HTTPException(404, "Question not found")

    is_correct = answer.strip().lower() == question.correct_answer.strip().lower()

    # Update ability
    ability = await adaptive_engine.get_student_state(
        student_id=student_id,
        unit_id=unit_id,
        grade_level=grade_level,
    )
    old_score = ability.ability_score
    new_score = adaptive_engine.update_ability(
        current_ability=old_score,
        is_correct=is_correct,
        question_difficulty=question.difficulty_level,
    )
    new_target = adaptive_engine.select_optimal_difficulty(
        new_score, grade_level=grade_level,
    )

    ability.ability_score = new_score
    ability.current_difficulty = new_target
    ability.total_questions += 1
    if is_correct:
        ability.correct_answers += 1
    await ability.save()

    # Persist answer
    record = StudentAnswerModel(
        student_id=student_id,
        question_id=question_id,
        unit_id=unit_id,
        answer_given=answer,
        is_correct=is_correct,
        time_taken=time_taken or 0,
        difficulty_at_attempt=question.difficulty_level,
    )
    await record.insert()

    return {
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "new_ability_score": round(new_score, 3),
        "recommended_difficulty": new_target,
        "progress_percentage": round(
            (ability.correct_answers / max(1, ability.total_questions)) * 100, 1
        ),
    }


@router.get("/student-state/{student_id}")
async def get_student_state(
    student_id: str,
    unit_id: Optional[str] = None,
):
    """Return a student's ability state(s)."""
    if unit_id:
        ability = await StudentAbilityModel.find_one(
            StudentAbilityModel.student_id == student_id,
            StudentAbilityModel.unit_id == unit_id,
        )
        if not ability:
            return {"student_id": student_id, "unit_id": unit_id, "ability_score": 0.0, "difficulty": 1}
        return {
            "student_id": student_id,
            "unit_id": unit_id,
            "ability_score": round(ability.ability_score, 3),
            "difficulty": ability.current_difficulty,
            "total_questions": ability.total_questions,
            "correct_answers": ability.correct_answers,
        }

    # Return all units for the student
    abilities = await StudentAbilityModel.find(
        StudentAbilityModel.student_id == student_id,
    ).to_list()

    return [
        {
            "unit_id": a.unit_id,
            "ability_score": round(a.ability_score, 3),
            "difficulty": a.current_difficulty,
            "total_questions": a.total_questions,
            "correct_answers": a.correct_answers,
        }
        for a in abilities
    ]
