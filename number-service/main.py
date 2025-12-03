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
    type: str  # video, trace, show, say, read
    number: int
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    level: int
    order: int
    questions: Optional[List[Dict[str, Any]]] = None  # Array of questions with difficulty levels


class Question(BaseModel):
    """Individual question within an activity"""
    id: str
    difficulty: str  # easy, medium, hard
    points: int
    question: Optional[str] = None
    instruction: Optional[str] = None
    correct_answer: Optional[Any] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    image: Optional[str] = None
    template_image: Optional[str] = None
    help_image: Optional[str] = None
    pronounce: Optional[str] = None
    alternatives: Optional[List[str]] = None
    max_objects: Optional[int] = None
    type: Optional[str] = None  # For read activity: word_to_digit, digit_to_word, mixed


class NumberActivities(BaseModel):
    """Activities for a single number"""
    video: Optional[Dict[str, Any]] = None
    trace: Optional[Dict[str, Any]] = None
    show: Optional[Dict[str, Any]] = None
    say: Optional[Dict[str, Any]] = None
    read: Optional[Dict[str, Any]] = None


class ScoreSubmission(BaseModel):
    activity_id: str
    score: int
    is_completed: bool
    completed_at: str
    additional_data: Optional[Dict[str, Any]] = None


# ==================== Helper Functions ====================

def load_activities_data() -> Dict[str, Any]:
    """Load activities from new JSON structure"""
    try:
        with open(ACTIVITIES_FILE, 'r') as f:
            return json.load(f)
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


def convert_to_activity_format(level: int, number: int, activity_type: str, 
                               activity_data: Dict[str, Any], order: int) -> Activity:
    """Convert new JSON format to Activity model"""
    activity_id = f"level{level}_num{number}_{activity_type}"
    
    # Extract questions array if present
    questions = activity_data.get('questions', [])
    
    # For video, there are no questions
    if activity_type == 'video':
        metadata = {
            'url': activity_data.get('url'),
            'duration': activity_data.get('duration'),
            'title': activity_data.get('title')
        }
    else:
        # For other activities, include base metadata
        metadata = {k: v for k, v in activity_data.items() if k != 'questions'}
    
    return Activity(
        id=activity_id,
        type=activity_type,
        number=number,
        title=f"{activity_type.capitalize()} Number {number}",
        description=activity_data.get('instruction', ''),
        metadata=metadata,
        level=level,
        order=order,
        questions=questions if questions else None
    )


def get_activities_for_number_from_data(level: int, number: int) -> List[Activity]:
    """Get activities for a specific number in proper sequence"""
    data = load_activities_data()
    
    if data.get('level') != level:
        raise HTTPException(
            status_code=404,
            detail=f"Level {level} not found in data"
        )
    
    number_str = str(number)
    if number_str not in data.get('numbers', {}):
        raise HTTPException(
            status_code=404,
            detail=f"Number {number} not found in Level {level}"
        )
    
    number_data = data['numbers'][number_str]
    activities = []
    
    # Define the sequence order
    activity_sequence = ['video', 'trace', 'show', 'say', 'read']
    
    for order, activity_type in enumerate(activity_sequence, start=1):
        if activity_type in number_data and number_data[activity_type]:
            activity = convert_to_activity_format(
                level, number, activity_type, 
                number_data[activity_type], order
            )
            activities.append(activity)
    
    return activities


# ==================== Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "service": "Ganitha Mithura - Number Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/activities/level/{level}/number/{number}")
async def get_activities_for_level_number(level: int, number: int, difficulty: Optional[str] = None):
    """
    GET /activities/level/{level}/number/{number}?difficulty=easy
    
    Returns all activities for a specific number within a level.
    Activities are returned in the correct sequence: video -> trace -> show -> say -> read
    
    Query Parameters:
    - difficulty: Filter questions by difficulty (easy, medium, hard)
                 If 'easy', returns only easy questions for tutorial
                 If omitted, returns all questions
    
    Phase 1: Only level 1 (numbers 1-10) is implemented
    """
    if level != 1:
        raise HTTPException(
            status_code=404,
            detail=f"Level {level} not yet implemented. Only Level 1 is available in Phase 1."
        )
    
    if number < 1 or number > 10:
        raise HTTPException(
            status_code=400,
            detail="Number must be between 1 and 10 for Level 1"
        )
    
    try:
        activities = get_activities_for_number_from_data(level, number)
        
        # Filter questions by difficulty if specified
        if difficulty:
            for activity in activities:
                if activity.questions:
                    activity.questions = [
                        q for q in activity.questions 
                        if q.get('difficulty') == difficulty
                    ]
        
        return {
            "level": level,
            "number": number,
            "difficulty_filter": difficulty,
            "count": len(activities),
            "activities": [activity.dict() for activity in activities]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching activities: {str(e)}"
        )


@app.get("/levels/{level}/activities")
async def get_activities_for_level(level: int):
    """
    GET /levels/{level}/activities
    
    Returns all activities for a specific level (all numbers combined).
    Phase 1: Only level 1 is implemented (numbers 1-10)
    """
    if level != 1:
        raise HTTPException(
            status_code=404,
            detail=f"Level {level} not yet implemented. Only Level 1 is available in Phase 1."
        )
    
    try:
        all_activities = []
        
        # Get activities for all numbers in the level (1-10)
        for number in range(1, 11):
            activities = get_activities_for_number_from_data(level, number)
            all_activities.extend(activities)
        
        return {
            "level": level,
            "count": len(all_activities),
            "activities": [activity.dict() for activity in all_activities]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching activities: {str(e)}"
        )


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
    try:
        all_activities = []
        
        # Get all activities from level 1
        for number in range(1, 11):
            activities = get_activities_for_number_from_data(1, number)
            # Exclude videos
            all_activities.extend([a for a in activities if a.type != 'video'])
        
        if len(all_activities) < 5:
            raise HTTPException(
                status_code=500,
                detail="Not enough activities available for test"
            )
        
        # Randomly select 5 activities
        test_activities = random.sample(all_activities, 5)
        
        return {
            "test_type": "beginner",
            "count": len(test_activities),
            "activities": [activity.dict() for activity in test_activities]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating test: {str(e)}"
        )


@app.get("/activities/number/{number}")
async def get_activities_for_number(number: int, level: int = 1):
    """
    GET /activities/number/{number}
    
    Returns all activities for a specific number within a level.
    Useful for learning flow.
    Legacy endpoint - use /activities/level/{level}/number/{number} instead
    """
    return await get_activities_for_level_number(level, number)


# TODO: Phase 2 - Additional endpoints
# @app.get("/test/intermediate")
# @app.get("/test/advanced")
# @app.post("/progress/sync")
# @app.get("/user/{user_id}/progress")
# @app.post("/user/{user_id}/activity/{activity_id}/complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
