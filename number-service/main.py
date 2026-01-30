from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import random
from pathlib import Path
from datetime import datetime

app = FastAPI(
    title="Ganitha Mithura - Number Service API",
    description="Backend API for Number Learning Module - Phase 1",
    version="1.0.0"
)

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Flutter app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data file path
DATA_DIR = Path(__file__).parent / "data"
ACTIVITIES_FILE = DATA_DIR / "activities_level1.json"

# ==================== Models ====================

class Activity(BaseModel):
    id: str
    type: str  # trace, read, say, object_detection, video
    number: int
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    level: int
    order: int


class ScoreSubmission(BaseModel):
    activity_id: str
    score: int
    is_completed: bool
    completed_at: str
    additional_data: Optional[Dict[str, Any]] = None


# ==================== Helper Functions ====================

def load_activities() -> List[Activity]:
    """Load activities from JSON file"""
    try:
        with open(ACTIVITIES_FILE, 'r') as f:
            data = json.load(f)
            return [Activity(**activity) for activity in data['activities']]
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Activities file not found: {ACTIVITIES_FILE}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading activities: {str(e)}"
        )


# ==================== Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "service": "Ganitha Mithura - Number Service",
        "version": "1.0.0",
        "status": "running",
        "phase": "Phase 1 - 50% MVP"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/levels/{level}/activities")
async def get_activities_for_level(level: int):
    """
    GET /levels/{level}/activities
    
    Returns all activities for a specific level.
    Phase 1: Only level 1 is implemented (numbers 1-10)
    """
    if level != 1:
        raise HTTPException(
            status_code=404,
            detail=f"Level {level} not yet implemented. Only Level 1 is available in Phase 1."
        )
    
    activities = load_activities()
    
    # Filter by level
    level_activities = [a for a in activities if a.level == level]
    
    return {
        "level": level,
        "count": len(level_activities),
        "activities": [a.dict() for a in level_activities]
    }


@app.post("/activity/score")
async def submit_activity_score(submission: ScoreSubmission):
    """
    POST /activity/score
    
    Submit score for a completed activity.
    In Phase 1, this just acknowledges the submission.
    TODO: Phase 2 - Store scores in database
    """
    return {
        "status": "success",
        "message": "Score submitted successfully",
        "activity_id": submission.activity_id,
        "score": submission.score,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/test/beginner")
async def get_beginner_test():
    """
    GET /test/beginner
    
    Returns 5 random activities for beginner test from Level 1.
    Activities are randomly selected and shuffled each time.
    Excludes video lessons.
    """
    activities = load_activities()
    
    # Filter Level 1 activities, exclude videos
    testable_activities = [
        a for a in activities 
        if a.level == 1 and a.type != 'video'
    ]
    
    if len(testable_activities) < 5:
        raise HTTPException(
            status_code=500,
            detail="Not enough activities available for test"
        )
    
    # Randomly select 5 activities
    test_activities = random.sample(testable_activities, 5)
    
    return {
        "test_type": "beginner",
        "count": len(test_activities),
        "activities": [a.dict() for a in test_activities]
    }


@app.get("/activities/number/{number}")
async def get_activities_for_number(number: int, level: int = 1):
    """
    GET /activities/number/{number}
    
    Returns all activities for a specific number within a level.
    Useful for learning flow.
    """
    if level != 1:
        raise HTTPException(
            status_code=404,
            detail=f"Level {level} not yet implemented"
        )
    
    if number < 1 or number > 10:
        raise HTTPException(
            status_code=400,
            detail="Number must be between 1 and 10 for Level 1"
        )
    
    activities = load_activities()
    
    # Filter by level and number
    number_activities = [
        a for a in activities 
        if a.level == level and a.number == number
    ]
    
    # Sort by order
    number_activities.sort(key=lambda x: x.order)
    
    return {
        "level": level,
        "number": number,
        "count": len(number_activities),
        "activities": [a.dict() for a in number_activities]
    }


# TODO: Phase 2 - Additional endpoints
# @app.get("/test/intermediate")
# @app.get("/test/advanced")
# @app.post("/progress/sync")
# @app.get("/user/{user_id}/progress")
# @app.post("/user/{user_id}/activity/{activity_id}/complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
