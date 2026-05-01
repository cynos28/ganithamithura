"""
API routes for student progress tracking
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.database import StudentProgressModel

router = APIRouter(prefix="/api/v1/progress", tags=["Progress"])


class RecordAnswerRequest(BaseModel):
    student_id: str
    unit_id: str
    topic: str
    grade: int
    is_correct: bool


class ProgressResponse(BaseModel):
    unit_id: str
    topic: str
    grade: int
    questions_answered: int
    correct_answers: int
    accuracy: float
    stars: int
    last_practiced: datetime


class TopicProgressResponse(BaseModel):
    topic: str
    questions_answered: int
    correct_answers: int
    accuracy: float
    total_stars: int


@router.post("/record-answer")
async def record_answer(request: RecordAnswerRequest):
    """Record a student answer and update progress"""
    
    try:
        # Find or create progress record
        progress = await StudentProgressModel.find_one(
            StudentProgressModel.student_id == request.student_id,
            StudentProgressModel.unit_id == request.unit_id
        )
        
        if not progress:
            # Create new progress record
            progress = StudentProgressModel(
                student_id=request.student_id,
                unit_id=request.unit_id,
                topic=request.topic,
                grade=request.grade,
                questions_answered=0,
                correct_answers=0,
                accuracy=0.0,
                stars=0,
            )
        
        # Update stats
        progress.questions_answered += 1
        if request.is_correct:
            progress.correct_answers += 1
        
        # Calculate accuracy
        progress.accuracy = (progress.correct_answers / progress.questions_answered * 100)
        
        # Calculate stars based on accuracy
        if progress.accuracy >= 90:
            progress.stars = 3
        elif progress.accuracy >= 70:
            progress.stars = 2
        elif progress.accuracy >= 50:
            progress.stars = 1
        else:
            progress.stars = 0
        
        # Update timestamp
        progress.last_practiced = datetime.utcnow()
        
        # Save to database
        await progress.save()
        
        return {
            "success": True,
            "progress": ProgressResponse(
                unit_id=progress.unit_id,
                topic=progress.topic,
                grade=progress.grade,
                questions_answered=progress.questions_answered,
                correct_answers=progress.correct_answers,
                accuracy=progress.accuracy,
                stars=progress.stars,
                last_practiced=progress.last_practiced,
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording answer: {str(e)}")


@router.get("/unit/{student_id}/{unit_id}")
async def get_unit_progress(student_id: str, unit_id: str):
    """Get progress for a specific unit"""
    
    try:
        progress = await StudentProgressModel.find_one(
            StudentProgressModel.student_id == student_id,
            StudentProgressModel.unit_id == unit_id
        )
        
        if not progress:
            return {
                "unit_id": unit_id,
                "questions_answered": 0,
                "correct_answers": 0,
                "accuracy": 0.0,
                "stars": 0,
            }
        
        return ProgressResponse(
            unit_id=progress.unit_id,
            topic=progress.topic,
            grade=progress.grade,
            questions_answered=progress.questions_answered,
            correct_answers=progress.correct_answers,
            accuracy=progress.accuracy,
            stars=progress.stars,
            last_practiced=progress.last_practiced,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")


@router.get("/topic/{student_id}/{topic}")
async def get_topic_progress(student_id: str, topic: str):
    """Get aggregated progress for a topic (all units in that topic)"""
    
    try:
        # Find all progress records for this student and topic
        progress_records = await StudentProgressModel.find(
            StudentProgressModel.student_id == student_id,
            StudentProgressModel.topic == topic
        ).to_list()
        
        if not progress_records:
            return {
                "topic": topic,
                "questions_answered": 0,
                "correct_answers": 0,
                "accuracy": 0.0,
                "total_stars": 0,
            }
        
        # Aggregate data
        total_questions = sum(p.questions_answered for p in progress_records)
        total_correct = sum(p.correct_answers for p in progress_records)
        total_stars = sum(p.stars for p in progress_records)
        
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0.0
        
        return TopicProgressResponse(
            topic=topic,
            questions_answered=total_questions,
            correct_answers=total_correct,
            accuracy=accuracy,
            total_stars=total_stars,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching topic progress: {str(e)}")


@router.get("/all/{student_id}")
async def get_all_progress(student_id: str):
    """Get all progress for a student"""
    
    try:
        progress_records = await StudentProgressModel.find(
            StudentProgressModel.student_id == student_id
        ).to_list()
        
        if not progress_records:
            return {
                "total_questions": 0,
                "total_correct": 0,
                "overall_accuracy": 0.0,
                "total_stars": 0,
                "units": [],
            }
        
        # Convert to response format
        units = [
            ProgressResponse(
                unit_id=p.unit_id,
                topic=p.topic,
                grade=p.grade,
                questions_answered=p.questions_answered,
                correct_answers=p.correct_answers,
                accuracy=p.accuracy,
                stars=p.stars,
                last_practiced=p.last_practiced,
            )
            for p in progress_records
        ]
        
        # Calculate overall stats
        total_questions = sum(p.questions_answered for p in progress_records)
        total_correct = sum(p.correct_answers for p in progress_records)
        total_stars = sum(p.stars for p in progress_records)
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0.0
        
        return {
            "total_questions": total_questions,
            "total_correct": total_correct,
            "overall_accuracy": overall_accuracy,
            "total_stars": total_stars,
            "units": units,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching all progress: {str(e)}")


@router.delete("/reset/{student_id}")
async def reset_progress(student_id: str, unit_id: Optional[str] = None):
    """Reset progress for a student (all units or specific unit)"""
    
    try:
        if unit_id:
            # Reset specific unit
            result = await StudentProgressModel.find(
                StudentProgressModel.student_id == student_id,
                StudentProgressModel.unit_id == unit_id
            ).delete()
            
            return {
                "success": True,
                "message": f"Progress reset for unit {unit_id}",
                "deleted_count": result.deleted_count if result else 0
            }
        else:
            # Reset all progress
            result = await StudentProgressModel.find(
                StudentProgressModel.student_id == student_id
            ).delete()
            
            return {
                "success": True,
                "message": "All progress reset",
                "deleted_count": result.deleted_count if result else 0
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting progress: {str(e)}")
