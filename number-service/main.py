from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import random
from pathlib import Path
from datetime import datetime
import base64
import cv2
import numpy as np
from object_detection_service import get_detection_service
from digit_recognition_service import get_recognition_service

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

# Level configurations - defines valid number ranges per level
LEVEL_CONFIGS = {
    1: {"min": 1, "max": 10, "file": "activities_level1.json"},
    2: {"min": 11, "max": 20, "file": "activities_level2.json"},
    3: {"min": 21, "max": 50, "file": "activities_level3.json"},
    4: {"min": 51, "max": 100, "file": "activities_level4.json"},
    5: {"min": 101, "max": 1000, "file": "activities_level5.json"},
}

# Cache for loaded activity data
activities_cache: Dict[int, Dict[str, Any]] = {}

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


class ScoreSubmission(BaseModel):
    activity_id: str
    score: int
    is_completed: bool
    completed_at: str
    additional_data: Optional[Dict[str, Any]] = None


class ObjectDetectionRequest(BaseModel):
    image_base64: str
    target_object: Optional[str] = None
    expected_count: Optional[int] = None
    confidence_threshold: float = 0.5


class ObjectDetectionResponse(BaseModel):
    total_count: int
    target_count: Optional[int] = None
    target_object: Optional[str] = None
    detections: List[Dict[str, Any]]
    class_counts: Dict[str, int]
    validation: Optional[Dict[str, Any]] = None


# ==================== Helper Functions ====================

def get_level_file_path(level: int) -> Path:
    """Get the activities file path for a given level"""
    if level not in LEVEL_CONFIGS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid level: {level}. Valid levels are 1-5."
        )
    return DATA_DIR / LEVEL_CONFIGS[level]["file"]


def load_activities_data(level: int = 1) -> Dict[str, Any]:
    """Load activities for a specific level (with caching)"""
    # Check cache first
    if level in activities_cache:
        return activities_cache[level]
    
    file_path = get_level_file_path(level)
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            activities_cache[level] = data  # Cache for future use
            return data
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Activities file not found: {file_path}"
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
    data = load_activities_data(level)  # Pass level for dynamic file loading
    
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
    if level not in LEVEL_CONFIGS:
        raise HTTPException(
            status_code=404,
            detail=f"Level {level} not yet implemented. Valid levels are 1-2."
        )
    
    level_config = LEVEL_CONFIGS[level]
    if number < level_config["min"] or number > level_config["max"]:
        raise HTTPException(
            status_code=400,
            detail=f"Number must be between {level_config['min']} and {level_config['max']} for Level {level}"
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
    if level not in [1, 2]:
        raise HTTPException(
            status_code=404,
            detail=f"Level {level} not yet implemented. Valid levels are 1-2."
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
        
        # Randomly select 5 activities - use 'easy' difficulty questions
        test_activities = random.sample(all_activities, 5)
        
        # Filter to only easy questions for beginner
        for activity in test_activities:
            if activity.questions:
                activity.questions = [q for q in activity.questions if q.get('difficulty') == 'easy']
        
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


@app.get("/test/intermediate")
async def get_intermediate_test():
    """
    GET /test/intermediate
    
    Returns 7 random activities for intermediate test.
    Includes all beginner question types plus:
    - Sequencing (what comes before/after)
    - Comparison (which is bigger/smaller)
    - Missing numbers (1, __, 3)
    Uses 'medium' difficulty questions.
    """
    try:
        all_activities = []
        
        # Get all activities from level 1
        for number in range(1, 11):
            activities = get_activities_for_number_from_data(1, number)
            # Exclude videos
            all_activities.extend([a for a in activities if a.type != 'video'])
        
        if len(all_activities) < 7:
            raise HTTPException(
                status_code=500,
                detail="Not enough activities available for intermediate test"
            )
        
        # Randomly select 7 activities
        test_activities = random.sample(all_activities, 7)
        
        # Filter to medium difficulty (includes more challenging variations)
        for activity in test_activities:
            if activity.questions:
                activity.questions = [q for q in activity.questions if q.get('difficulty') in ['easy', 'medium']]
        
        # Add intermediate-specific questions (sequencing, comparison)
        intermediate_questions = generate_intermediate_questions()
        
        return {
            "test_type": "intermediate",
            "count": len(test_activities),
            "activities": [activity.dict() for activity in test_activities],
            "additional_questions": intermediate_questions
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating intermediate test: {str(e)}"
        )


@app.get("/test/advanced")
async def get_advanced_test():
    """
    GET /test/advanced
    
    Returns 10 activities for advanced test.
    Includes all question types plus:
    - Pattern recognition (2, 4, 6, ?)
    - Simple word problems
    - Estimation challenges
    - Place value questions
    Uses 'hard' difficulty questions.
    """
    try:
        all_activities = []
        
        # Get all activities from level 1
        for number in range(1, 11):
            activities = get_activities_for_number_from_data(1, number)
            # Exclude videos
            all_activities.extend([a for a in activities if a.type != 'video'])
        
        if len(all_activities) < 10:
            raise HTTPException(
                status_code=500,
                detail="Not enough activities available for advanced test"
            )
        
        # Randomly select 10 activities
        test_activities = random.sample(all_activities, 10)
        
        # Include all difficulty levels for maximum challenge
        # (questions are already loaded with all difficulties)
        
        # Add advanced-specific questions (patterns, word problems)
        advanced_questions = generate_advanced_questions()
        
        return {
            "test_type": "advanced",
            "count": len(test_activities),
            "activities": [activity.dict() for activity in test_activities],
            "additional_questions": advanced_questions
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating advanced test: {str(e)}"
        )


def generate_intermediate_questions() -> List[Dict[str, Any]]:
    """Generate intermediate-level questions: sequencing, comparison, missing numbers"""
    questions = []
    
    # Sequencing questions
    for num in random.sample(range(2, 10), 3):
        questions.append({
            "id": f"seq_before_{num}",
            "type": "sequencing",
            "difficulty": "medium",
            "points": 15,
            "question": f"What number comes before {num}?",
            "options": [str(num-2), str(num-1), str(num), str(num+1)],
            "correct_answer": str(num-1)
        })
        questions.append({
            "id": f"seq_after_{num}",
            "type": "sequencing", 
            "difficulty": "medium",
            "points": 15,
            "question": f"What number comes after {num}?",
            "options": [str(num-1), str(num), str(num+1), str(num+2)],
            "correct_answer": str(num+1)
        })
    
    # Comparison questions
    for _ in range(3):
        a, b = random.sample(range(1, 11), 2)
        questions.append({
            "id": f"compare_{a}_{b}",
            "type": "comparison",
            "difficulty": "medium", 
            "points": 15,
            "question": f"Which number is bigger: {a} or {b}?",
            "options": [str(a), str(b)],
            "correct_answer": str(max(a, b))
        })
    
    # Missing number questions
    for start in random.sample(range(1, 8), 2):
        missing_pos = random.choice([0, 1, 2])
        sequence = [start + i for i in range(3)]
        display = [str(n) if i != missing_pos else "?" for i, n in enumerate(sequence)]
        questions.append({
            "id": f"missing_{start}_{missing_pos}",
            "type": "missing_number",
            "difficulty": "medium",
            "points": 15,
            "question": f"Fill in the missing number: {', '.join(display)}",
            "options": [str(sequence[missing_pos]-1), str(sequence[missing_pos]), str(sequence[missing_pos]+1)],
            "correct_answer": str(sequence[missing_pos])
        })
    
    random.shuffle(questions)
    return questions[:5]  # Return 5 intermediate questions


def generate_advanced_questions() -> List[Dict[str, Any]]:
    """Generate advanced-level questions: patterns, word problems, estimation"""
    questions = []
    
    # Pattern recognition
    patterns = [
        ([2, 4, 6], 8, "2, 4, 6, ?"),
        ([1, 3, 5], 7, "1, 3, 5, ?"),
        ([5, 4, 3], 2, "5, 4, 3, ?"),
        ([1, 2, 1], 2, "1, 2, 1, ?"),
        ([10, 8, 6], 4, "10, 8, 6, ?"),
    ]
    for seq, answer, display in random.sample(patterns, 3):
        questions.append({
            "id": f"pattern_{'_'.join(map(str, seq))}",
            "type": "pattern",
            "difficulty": "hard",
            "points": 20,
            "question": f"What comes next? {display}",
            "options": [str(answer-1), str(answer), str(answer+1), str(answer+2)],
            "correct_answer": str(answer)
        })
    
    # Simple word problems
    word_problems = [
        ("I have 5 apples. I give 2 to my friend. How many do I have left?", "3"),
        ("There are 3 birds on a tree. 2 more birds come. How many birds now?", "5"),
        ("I see 4 cats and 2 dogs. How many animals in total?", "6"),
        ("Mom has 7 cookies. She eats 3. How many cookies are left?", "4"),
    ]
    for problem, answer in random.sample(word_problems, 2):
        options = [str(int(answer)-1), answer, str(int(answer)+1), str(int(answer)+2)]
        random.shuffle(options)
        questions.append({
            "id": f"word_problem_{answer}",
            "type": "word_problem",
            "difficulty": "hard",
            "points": 20,
            "question": problem,
            "options": options,
            "correct_answer": answer
        })
    
    # Estimation questions
    for num in random.sample([23, 47, 68, 85], 2):
        lower = (num // 10) * 10
        upper = lower + 10
        questions.append({
            "id": f"estimation_{num}",
            "type": "estimation",
            "difficulty": "hard",
            "points": 20,
            "question": f"Is {num} closer to {lower} or {upper}?",
            "options": [str(lower), str(upper)],
            "correct_answer": str(lower if num - lower < upper - num else upper)
        })
    
    random.shuffle(questions)
    return questions[:5]  # Return 5 advanced questions




# Legacy endpoint removed - use /activities/level/{level}/number/{number} instead


# ==================== Object Detection Endpoints ====================

@app.post("/detect/objects")
async def detect_objects(request: ObjectDetectionRequest):
    """
    POST /detect/objects
    
    Detect and count objects in an image using YOLO.
    
    Request body:
    - image_base64: Base64 encoded image
    - target_object: Specific object to count (optional)
    - expected_count: Expected count for validation (optional)
    - confidence_threshold: Detection confidence threshold (default: 0.5)
    
    Returns:
    - Detection results with counts and bounding boxes
    - Validation result if expected_count provided
    """
    try:
        detection_service = get_detection_service()
        
        # Perform detection
        result = detection_service.detect_from_base64(
            base64_image=request.image_base64,
            target_object=request.target_object,
            confidence_threshold=request.confidence_threshold
        )
        
        # Validate if expected count provided
        if request.expected_count is not None:
            detected_count = result['target_count'] if request.target_object else result['total_count']
            validation = detection_service.validate_count(
                detected_count=detected_count,
                expected_count=request.expected_count,
                tolerance=0
            )
            result['validation'] = validation
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during object detection: {str(e)}"
        )


# Removed unused endpoints: /detect/objects/upload, /detect/available-classes


# ==================== Digit Recognition Endpoints ====================

class DigitRecognitionRequest(BaseModel):
    image: str  # Base64 encoded image
    expected_digit: Optional[int] = None  # For validation
    confidence_threshold: Optional[float] = 0.7


@app.post("/recognize/digit")
async def recognize_digit(request: DigitRecognitionRequest):
    """
    POST /recognize/digit
    
    Recognize handwritten digit from image using ML model.
    
    Request body:
    {
        "image": "base64_encoded_image_string",
        "expected_digit": 5,  // Optional: for validation
        "confidence_threshold": 0.7  // Optional: minimum confidence
    }
    
    Returns:
    {
        "predicted_digit": 5,
        "confidence": 0.95,
        "probabilities": [0.01, 0.02, ...],
        "top_3_predictions": [{"digit": 5, "confidence": 0.95}, ...],
        "is_correct": true,  // If expected_digit provided
        "feedback": "Perfect! You drew 5 correctly!"
    }
    """
    try:
        recognition_service = get_recognition_service()
        
        # Recognize digit
        if request.expected_digit is not None:
            # Validation mode
            result = recognition_service.validate_digit(
                image=None,  # Will be processed from base64
                expected_digit=request.expected_digit,
                confidence_threshold=request.confidence_threshold
            )
            # Process base64 separately
            recognition_result = recognition_service.recognize_from_base64(request.image)
            
            if 'error' in recognition_result:
                raise HTTPException(status_code=400, detail=recognition_result['error'])
            
            # Combine results
            is_correct = (
                recognition_result['predicted_digit'] == request.expected_digit and
                recognition_result['confidence'] >= request.confidence_threshold
            )
            
            if is_correct:
                feedback = f"Perfect! You drew {request.expected_digit} correctly!"
            elif recognition_result['predicted_digit'] == request.expected_digit:
                feedback = f"Good try! Your {request.expected_digit} needs a bit more clarity."
            else:
                feedback = f"That looks like {recognition_result['predicted_digit']}. Try drawing {request.expected_digit} again."
            
            return {
                **recognition_result,
                'is_correct': is_correct,
                'expected': request.expected_digit,
                'feedback': feedback
            }
        else:
            # Recognition only mode
            result = recognition_service.recognize_from_base64(request.image)
            
            if 'error' in result:
                raise HTTPException(status_code=400, detail=result['error'])
            
            return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during digit recognition: {str(e)}"
        )


# Removed unused endpoint: /recognize/digit/upload

# TODO: Phase 2 - Additional endpoints
# @app.post("/progress/sync")
# @app.get("/user/{user_id}/progress")
# @app.post("/user/{user_id}/activity/{activity_id}/complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
