"""
Performance Routes - Save and retrieve student performance from learning curve sessions.

Endpoints:
- POST /api/users/{user_id}/performance — Save typing/telling session performance
- GET  /api/users/{user_id}/performance — Get performance history
- GET  /api/users/{user_id}/performance/summary — Aggregated stats + latest ML prediction
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import logging

from src.database.mongodb_connection import get_collection, get_database

logger = logging.getLogger("PerformanceRoutes")

router = APIRouter()


# --- Pydantic Models ---

class PerformanceInput(BaseModel):
    """Input model for saving a session performance record."""
    grade: int = Field(ge=1, le=3, description="Student grade (1-3)")
    session_type: Optional[str] = Field(default="unknown", description="Optional session type")
    level: int = Field(ge=1, le=3, description="Performance level (1-3)")
    sublevel: str = Field(default="Starter", description="Starter/Explorer/Solver/Champion")
    total_questions: int = Field(ge=1, description="Total questions in session")
    correct_answers: int = Field(ge=0, description="Number of correct answers")
    avg_time_per_question: Optional[float] = Field(default=None, description="Average time per question in seconds")


class PerformanceRecord(BaseModel):
    """Output model for a performance record."""
    user_id: str
    grade: int
    session_type: Optional[str] = "unknown"
    level: int
    sublevel: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    score_percentage: float
    predicted_level: Optional[int] = None
    predicted_sublevel: Optional[str] = None
    confidence: Optional[float] = None
    recommendation: Optional[str] = None
    timestamp: str


# --- Helper: Run ML Prediction ---

def _run_prediction(user_id: str, avg_score: float, avg_time: float, grade: int) -> dict:
    """
    Run the ML PerformancePredictor to classify a student.
    Returns prediction dict or empty dict on failure.
    """
    try:
        import os
        model_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'performance_metrics')
        
        if not os.path.exists(model_dir):
            logger.warning(f"Model directory not found: {model_dir}. Skipping prediction.")
            return {}
        
        from src.performance_metrics import PerformancePredictor
        predictor = PerformancePredictor()
        predictor.load_models(model_dir)
        
        result = predictor.predict({
            'user_id': user_id,
            'avg_score': avg_score,
            'avg_time': avg_time,
            'grade': grade
        })
        
        return result
    except Exception as e:
        logger.error(f"ML prediction failed: {e}")
        return {}


# --- Endpoints ---

@router.post("/api/users/{user_id}/performance")
async def save_performance(user_id: str, data: PerformanceInput):
    """
    Save a learning curve session performance record.
    Called by Flutter after completing a typing or telling session.
    """
    collection = get_collection("sym_performance")
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    # Validate sublevel
    valid_sublevels = ["Starter", "Explorer", "Solver", "Champion"]
    if data.sublevel not in valid_sublevels:
        raise HTTPException(status_code=400, detail=f"sublevel must be one of {valid_sublevels}")
    
    # Validate correct_answers <= total_questions
    if data.correct_answers > data.total_questions:
        raise HTTPException(status_code=400, detail="correct_answers cannot exceed total_questions")
    
    # Calculate derived fields for current session
    wrong_answers = data.total_questions - data.correct_answers
    current_score_percentage = (data.correct_answers / data.total_questions) * 100 if data.total_questions > 0 else 0
    avg_time = data.avg_time_per_question if data.avg_time_per_question else 15.0  # Default 15s
    
    # Calculate CUMULATIVE historical score
    previous_records = list(collection.find({"user_id": user_id}))
    historical_total_questions = sum(r.get("total_questions", 0) for r in previous_records)
    historical_correct_answers = sum(r.get("correct_answers", 0) for r in previous_records)
    
    cumulative_total_questions = historical_total_questions + data.total_questions
    cumulative_correct_answers = historical_correct_answers + data.correct_answers
    
    cumulative_score_percentage = (cumulative_correct_answers / cumulative_total_questions) * 100 if cumulative_total_questions > 0 else 0
    
    # Run ML prediction using Cumulative Score
    prediction = _run_prediction(
        user_id=user_id,
        avg_score=cumulative_score_percentage,
        avg_time=avg_time,
        grade=data.grade
    )
    
    predicted_level = prediction.get('level', None)
    predicted_sublevel = prediction.get('sublevel_name', None)
    confidence = prediction.get('overall_confidence', None)
    recommendation = prediction.get('recommendation', None)
    
    # Build performance document
    performance_doc = {
        "user_id": user_id,
        "grade": data.grade,
        "session_type": data.session_type,
        "level": data.level,
        "sublevel": data.sublevel,
        "total_questions": data.total_questions,
        "correct_answers": data.correct_answers,
        "wrong_answers": wrong_answers,
        "score_percentage": round(current_score_percentage, 1),
        "cumulative_score_percentage": round(cumulative_score_percentage, 1),
        "cumulative_total_questions": cumulative_total_questions,
        "avg_time_per_question": avg_time,
        "predicted_level": predicted_level,
        "predicted_sublevel": predicted_sublevel,
        "confidence": round(confidence, 4) if confidence else None,
        "recommendation": recommendation,
        "timestamp": datetime.utcnow()
    }
    
    # Insert into MongoDB
    result = collection.insert_one(performance_doc)
    
    logger.info(f"Saved performance for user {user_id}. Current: {current_score_percentage:.0f}%, "
                f"Cumulative: {cumulative_score_percentage:.0f}% (Level {data.level})")
    
    return {
        "status": "success",
        "performance": {
            "user_id": user_id,
            "score_percentage": round(current_score_percentage, 1),
            "cumulative_score_percentage": round(cumulative_score_percentage, 1),
            "correct_answers": data.correct_answers,
            "total_questions": data.total_questions,
            "predicted_level": predicted_level,
            "predicted_sublevel": predicted_sublevel,
            "confidence": round(confidence, 4) if confidence else None,
            "recommendation": recommendation,
        }
    }


@router.get("/api/users/{user_id}/performance")
async def get_performance_history(user_id: str, limit: int = 20):
    """
    Get performance history for a user, most recent first.
    """
    collection = get_collection("sym_performance")
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    records = list(
        collection.find(
            {"user_id": user_id},
            {"_id": 0}  # Exclude MongoDB ObjectId
        )
        .sort("timestamp", -1)
        .limit(limit)
    )
    
    # Convert datetime to string for JSON serialization
    for record in records:
        if isinstance(record.get("timestamp"), datetime):
            record["timestamp"] = record["timestamp"].isoformat()
    
    return {
        "user_id": user_id,
        "total_records": len(records),
        "history": records
    }


@router.get("/api/users/{user_id}/performance/summary")
async def get_performance_summary(user_id: str):
    """
    Get aggregated performance summary for a user.
    Includes: total sessions, avg score, best score, latest prediction.
    """
    collection = get_collection("sym_performance")
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    # Aggregation pipeline
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$user_id",
            "total_sessions": {"$sum": 1},
            "total_questions_answered": {"$sum": "$total_questions"},
            "total_correct": {"$sum": "$correct_answers"},
            "avg_score": {"$avg": "$score_percentage"},
            "best_score": {"$max": "$score_percentage"},
            "typing_sessions": {
                "$sum": {"$cond": [{"$eq": ["$session_type", "typing"]}, 1, 0]}
            },
            "telling_sessions": {
                "$sum": {"$cond": [{"$eq": ["$session_type", "telling"]}, 1, 0]}
            },
        }}
    ]
    
    results = list(collection.aggregate(pipeline))
    
    if not results:
        return {
            "user_id": user_id,
            "total_sessions": 0,
            "summary": None,
            "latest_prediction": None
        }
    
    summary = results[0]
    summary.pop("_id", None)
    
    # Round values
    if summary.get("avg_score"):
        summary["avg_score"] = round(summary["avg_score"], 1)
    
    # Calculate strict sequential unlocked_level and sublevel
    unlocked_level = 1
    unlocked_sublevel_index = 0
    sublevels = ["Starter", "Explorer", "Solver", "Champion"]
    
    user_history = list(collection.find({"user_id": user_id}).sort("timestamp", 1))
    for r in user_history:
        played_lvl = r.get("level", 1)
        played_sublvl = r.get("sublevel", "Starter")
        score = r.get("score_percentage", 0)
        
        try:
            played_idx = sublevels.index(played_sublvl)
        except ValueError:
            played_idx = 0
            
        # Only advance if they beat their highest currently unlocked challenge
        if played_lvl == unlocked_level and played_idx == unlocked_sublevel_index and score >= 50:
            if unlocked_sublevel_index < 3:
                # Advance one sublevel
                unlocked_sublevel_index += 1
            else:
                # Beat Champion, so advance to next level's Starter
                unlocked_level = min(3, unlocked_level + 1)
                unlocked_sublevel_index = 0
                
    final_sublevel = sublevels[unlocked_sublevel_index]
    
    # Get latest record for prediction info
    latest = collection.find_one(
        {"user_id": user_id},
        {"_id": 0},
        sort=[("timestamp", -1)]
    )
    
    latest_prediction = None
    if latest:
        if isinstance(latest.get("timestamp"), datetime):
            latest["timestamp"] = latest["timestamp"].isoformat()
        latest_prediction = {
            "predicted_level": unlocked_level,          # Strict unlocked progression for Flutter
            "predicted_sublevel": final_sublevel,       # Strict unlocked sublevel
            "raw_predicted_level": latest.get("predicted_level"),
            "raw_predicted_sublevel": latest.get("predicted_sublevel"),
            "confidence": latest.get("confidence"),
            "recommendation": latest.get("recommendation"),
            "last_session_type": latest.get("session_type"),
            "last_score": latest.get("score_percentage"),
            "timestamp": latest.get("timestamp"),
        }
    
    return {
        "user_id": user_id,
        "summary": summary,
        "latest_prediction": latest_prediction
    }
