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
        with open(file_path, 'r', encoding='utf-8') as f:
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
            activities = get_activities_for_number_from_data(level, number+(10*(level-1)))  # Adjust number range based on level
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
    
    Returns 8 easy questions from JSON activity data in unified ProgressTestQuestion format.
    Same question types as learning sessions (trace, show/count, say, read/select).
    Passing score (60%+) unlocks intermediate.
    """
    try:
        questions = []
        
        # Get 2 easy questions from each JSON activity type
        for activity_type in ['trace', 'show', 'say', 'read']:
            json_qs = get_activity_questions_from_json(activity_type, difficulty='easy', count=2)
            for q in json_qs:
                questions.append(convert_json_to_test_question(q, activity_type, q['number']))
        
        # Fallback: generate if not enough from JSON
        while len(questions) < 8:
            questions.append(generate_select_answer_question())
        
        random.shuffle(questions)
        
        return {
            "test_type": "beginner",
            "total_questions": min(len(questions), 8),
            "questions": questions[:8],
            "passing_score": 5,
            "next_unlock": "intermediate",
            "scoring": {
                "pass": {"min_score": 5, "unlocks": ["beginner", "intermediate"]},
                "fail": {"min_score": 0, "max_score": 4, "unlocks": ["beginner"]},
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating beginner test: {str(e)}"
        )


@app.get("/test/intermediate")
async def get_intermediate_test():
    """
    GET /test/intermediate
    
    Returns 10 medium-difficulty questions in interactive format.
    Uses medium JSON questions with transformed structures + new types:
    - show → drag_drop_count (drag N objects into box instead of just selecting)
    - say → say with image (show image with objects, say the count)
    - read → matching (match numbers to words instead of MCQ)
    - trace → trace with fewer guides
    Plus: pattern_fill, drag_drop_order, sequencing, comparison
    Passing (60%+) unlocks advanced.
    """
    try:
        questions = []
        
        # Medium difficulty trace from JSON
        trace_qs = get_activity_questions_from_json('trace', difficulty='medium', count=1)
        for q in trace_qs:
            questions.append(convert_json_to_test_question(q, 'trace', q['number']))
        
        # Medium show → transform to drag_drop_count (interactive counting)
        show_qs = get_activity_questions_from_json('show', difficulty='medium', count=2)
        for q in show_qs:
            count = q.get('correct_answer', q['number'])
            obj = random.choice(COUNTING_OBJECTS)
            questions.append({
                "id": f"dragdrop_count_{q['number']}_{random.randint(100,999)}",
                "type": "drag_drop_count",
                "difficulty": "medium",
                "points": 15,
                "question": f"Drag exactly {count} {obj['name']} into the box",
                "instruction": f"Pick {count} {obj['name']}",
                "object_name": obj["name"],
                "object_emoji": obj["emoji"],
                "object_image": obj["image"].replace("{n}", str(count)),
                "available_count": count + random.randint(2, 4),
                "correct_count": count,
            })
        
        # Medium say → show image with objects, say the count
        say_qs = get_activity_questions_from_json('say', difficulty='medium', count=1)
        for q in say_qs:
            questions.append(convert_json_to_test_question(q, 'say', q['number']))
        
        # Medium read → transform to matching (match numbers to words)
        questions.append(generate_matching_question())
        
        # New interactive types
        questions.append(generate_drag_drop_ordering_question())
        questions.append(generate_pattern_fill_question())
        questions.append(generate_image_counting_question())
        
        # Object detection question (camera-based counting)
        questions.append(generate_object_detection_question(difficulty='medium'))
        
        # Sequencing & comparison questions (medium difficulty)
        intermediate_qs = generate_intermediate_questions()
        for iq in intermediate_qs[:2]:
            questions.append({
                "id": iq.get('id', f"int_{random.randint(100,999)}"),
                "type": "select",
                "difficulty": "medium",
                "points": iq.get('points', 15),
                "question": iq['question'],
                "options": iq.get('options', []),
                "correct_answer": iq.get('correct_answer', ''),
            })
        
        random.shuffle(questions)
        
        return {
            "test_type": "intermediate",
            "total_questions": min(len(questions), 10),
            "questions": questions[:10],
            "passing_score": 6,
            "next_unlock": "advanced",
            "scoring": {
                "pass": {"min_score": 6, "unlocks": ["beginner", "intermediate", "advanced"]},
                "fail": {"min_score": 0, "max_score": 5, "unlocks": ["beginner", "intermediate"]},
            }
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
    
    Returns 10 hard-difficulty questions with all question types.
    Uses hard JSON questions + word problems, estimation, complex patterns.
    """
    try:
        questions = []
        
        # Hard difficulty questions from JSON
        for activity_type in ['trace', 'show', 'say', 'read']:
            json_qs = get_activity_questions_from_json(activity_type, difficulty='hard', count=1)
            for q in json_qs:
                questions.append(convert_json_to_test_question(q, activity_type, q['number']))
        
        # New interactive types (harder variants)
        questions.append(generate_matching_question())
        questions.append(generate_drag_drop_ordering_question())
        questions.append(generate_drag_drop_counting_question())
        questions.append(generate_pattern_fill_question())
        
        # Object detection question (camera-based counting, harder)
        questions.append(generate_object_detection_question(difficulty='hard'))
        
        # Word problems and estimation from advanced generator
        advanced_qs = generate_advanced_questions()
        for aq in advanced_qs[:2]:
            questions.append({
                "id": aq.get('id', f"adv_{random.randint(100,999)}"),
                "type": "select",
                "difficulty": "hard",
                "points": aq.get('points', 20),
                "question": aq['question'],
                "options": aq.get('options', []),
                "correct_answer": aq.get('correct_answer', ''),
            })
        
        random.shuffle(questions)
        
        return {
            "test_type": "advanced",
            "total_questions": min(len(questions), 10),
            "questions": questions[:10],
            "scoring": {
                "pass": {"min_score": 7, "unlocks": ["beginner", "intermediate", "advanced"]},
            }
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


# ==================== Progress Test Endpoint ====================

# Number-word mappings for matching/drag-drop questions
NUMBER_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
    6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"
}

# Object images for counting questions
COUNTING_OBJECTS = [
    {"name": "apples", "emoji": "🍎", "image": "assets/images/apple_{n}.png"},
    {"name": "stars", "emoji": "⭐", "image": "assets/images/star_{n}.png"},
    {"name": "bananas", "emoji": "🍌", "image": "assets/images/banana_{n}.png"},
    {"name": "balls", "emoji": "🏀", "image": "assets/images/ball_{n}.png"},
    {"name": "flowers", "emoji": "🌸", "image": "assets/images/flower_{n}.png"},
    {"name": "birds", "emoji": "🐦", "image": "assets/images/bird_{n}.png"},
    {"name": "fish", "emoji": "🐟", "image": "assets/images/fish_{n}.png"},
    {"name": "butterflies", "emoji": "🦋", "image": "assets/images/butterfly_{n}.png"},
]

# Objects suitable for real-world camera detection (YOLO COCO dataset)
# Only use these for counts 1-5 in tests
DETECTABLE_OBJECTS = [
    "bottle", "cup", "book", "spoon", "fork", "knife", "bowl",
    "banana", "orange", "carrot",
    "chair", "keyboard", "mouse", "remote", "cell phone",
    "scissors", "toothbrush", "pen", "pencil",
]


def generate_object_detection_question(difficulty: str = "medium") -> Dict[str, Any]:
    """Generate a camera-based object detection question.
    
    The child needs to point the camera at real-world objects and 
    the YOLO model will detect and count them.
    """
    if difficulty == "medium":
        target_count = random.randint(1, 3)
    else:  # hard
        target_count = random.randint(2, 5)

    # Sometimes use 'any' object (just count anything), sometimes specific
    use_specific = random.choice([True, False])
    
    if use_specific:
        target_object = random.choice(DETECTABLE_OBJECTS)
        question_text = f"Find and photograph {target_count} {target_object}{'s' if target_count > 1 else ''} around you"
        instruction_text = f"Point your camera at {target_count} {target_object}{'s' if target_count > 1 else ''} and capture"
    else:
        target_object = "any"
        question_text = f"Find and photograph {target_count} object{'s' if target_count > 1 else ''} around you"
        instruction_text = f"Point your camera at {target_count} object{'s' if target_count > 1 else ''} and capture"

    return {
        "id": f"object_detection_{target_object}_{target_count}_{random.randint(100,999)}",
        "type": "object_detection",
        "difficulty": difficulty,
        "points": 20 if difficulty == "hard" else 15,
        "question": question_text,
        "instruction": instruction_text,
        "object_name": target_object,
        "object_count": target_count,
        "expected_number": target_count,
    }


def generate_matching_question() -> Dict[str, Any]:
    """Generate a matching question: match numbers to their words"""
    count = random.choice([3, 4, 5])
    numbers = random.sample(range(1, 11), count)
    
    # Create pairs: number -> word
    pairs = [{"number": str(n), "word": NUMBER_WORDS[n]} for n in numbers]
    
    # Shuffled words for the right side
    shuffled_words = [p["word"] for p in pairs]
    random.shuffle(shuffled_words)
    
    return {
        "id": f"match_{'_'.join(map(str, numbers))}_{random.randint(100,999)}",
        "type": "matching",
        "difficulty": "medium",
        "points": 15,
        "question": "Match each number with its word",
        "instruction": "Draw lines to match the numbers on the left with the words on the right",
        "left_items": [str(n) for n in numbers],
        "right_items": shuffled_words,
        "correct_pairs": {str(n): NUMBER_WORDS[n] for n in numbers},
    }


def generate_drag_drop_ordering_question() -> Dict[str, Any]:
    """Generate a drag-and-drop ordering question"""
    start = random.randint(1, 6)
    count = random.choice([4, 5])
    correct_order = list(range(start, start + count))
    shuffled = correct_order.copy()
    random.shuffle(shuffled)
    
    # Ensure shuffled is actually different from correct
    while shuffled == correct_order:
        random.shuffle(shuffled)
    
    variant = random.choice(["ascending", "descending"])
    if variant == "descending":
        correct_order = list(reversed(correct_order))
    
    return {
        "id": f"dragdrop_order_{start}_{count}_{random.randint(100,999)}",
        "type": "drag_drop_order",
        "difficulty": "medium",
        "points": 15,
        "question": f"Drag the numbers to arrange them from {'smallest to biggest' if variant == 'ascending' else 'biggest to smallest'}",
        "instruction": f"Put these numbers in order ({variant})",
        "items": [str(n) for n in shuffled],
        "correct_order": [str(n) for n in correct_order],
    }


def generate_drag_drop_counting_question() -> Dict[str, Any]:
    """Generate a drag-and-drop counting question: drag correct count of objects"""
    target_count = random.randint(2, 8)
    obj = random.choice(COUNTING_OBJECTS)
    available_count = target_count + random.randint(2, 4)
    
    return {
        "id": f"dragdrop_count_{obj['name']}_{target_count}_{random.randint(100,999)}",
        "type": "drag_drop_count",
        "difficulty": "medium",
        "points": 15,
        "question": f"Drag exactly {target_count} {obj['name']} into the box",
        "instruction": f"Pick {target_count} {obj['name']}",
        "object_name": obj["name"],
        "object_emoji": obj["emoji"],
        "object_image": obj["image"].replace("{n}", str(target_count)),
        "available_count": available_count,
        "correct_count": target_count,
    }


def generate_image_counting_question() -> Dict[str, Any]:
    """Generate question: show image with N objects, ask user to identify the count"""
    count = random.randint(1, 10)
    obj = random.choice(COUNTING_OBJECTS)
    
    # Generate wrong options
    options = list(set([count, max(1, count - 1), count + 1, max(1, count - 2)]))
    while len(options) < 4:
        options.append(count + len(options))
    options = [str(o) for o in sorted(options[:4])]
    
    question_variants = [
        f"How many {obj['name']} do you see in the picture?",
        f"Count the {obj['name']}. How many are there?",
        f"Look at the picture. How many {obj['name']} can you count?",
    ]
    
    return {
        "id": f"img_count_{obj['name']}_{count}_{random.randint(100,999)}",
        "type": "image_counting",
        "difficulty": "easy",
        "points": 10,
        "question": random.choice(question_variants),
        "instruction": f"Count the {obj['name']} in the image",
        "object_name": obj["name"],
        "object_emoji": obj["emoji"],
        "object_image": obj["image"].replace("{n}", str(count)),
        "object_count": count,
        "options": options,
        "correct_answer": str(count),
    }


def generate_pattern_fill_question() -> Dict[str, Any]:
    """Generate a number pattern with a blank to fill"""
    pattern_templates = [
        # (start, step, length, description)
        (1, 1, 5, "counting by 1"),
        (2, 2, 5, "counting by 2"),
        (1, 3, 4, "counting by 3"),
        (5, 5, 4, "counting by 5"),
        (10, -1, 5, "counting down by 1"),
        (10, -2, 4, "counting down by 2"),
        (1, 1, 6, "counting by 1"),
        (3, 2, 5, "odd numbers from 3"),
    ]
    
    template = random.choice(pattern_templates)
    start, step, length, desc = template
    
    sequence = [start + i * step for i in range(length)]
    blank_pos = random.randint(1, length - 2)  # Don't blank first or last
    
    correct_answer = sequence[blank_pos]
    display = [str(n) if i != blank_pos else "___" for i, n in enumerate(sequence)]
    
    options = list(set([correct_answer, correct_answer + step, correct_answer - step, correct_answer + 1]))
    options = [str(o) for o in sorted(options[:4])]
    
    return {
        "id": f"pattern_fill_{start}_{step}_{blank_pos}_{random.randint(100,999)}",
        "type": "pattern_fill",
        "difficulty": "medium",
        "points": 15,
        "question": f"Fill in the blank: {', '.join(display)}",
        "instruction": "Find the missing number in the pattern",
        "sequence": [str(n) for n in sequence],
        "blank_position": blank_pos,
        "display_sequence": display,
        "options": options,
        "correct_answer": str(correct_answer),
    }


def generate_tracing_question() -> Dict[str, Any]:
    """Generate a tracing/drawing question for the progress test"""
    number = random.randint(1, 10)
    
    return {
        "id": f"trace_test_{number}_{random.randint(100,999)}",
        "type": "trace",
        "difficulty": "easy",
        "points": 10,
        "question": f"Draw the number {number}",
        "instruction": f"Write the number {number} in the box below",
        "expected_number": number,
        "word": NUMBER_WORDS[number],
    }


def generate_say_question() -> Dict[str, Any]:
    """Generate a say/speak question for the progress test"""
    number = random.randint(1, 10)
    obj = random.choice(COUNTING_OBJECTS)
    
    return {
        "id": f"say_test_{number}_{random.randint(100,999)}",
        "type": "say",
        "difficulty": "easy",
        "points": 10,
        "question": f"How many {obj['name']} do you see? Say the number!",
        "instruction": "Say the number out loud",
        "object_name": obj["name"],
        "object_emoji": obj["emoji"],
        "object_image": obj["image"].replace("{n}", str(number)),
        "object_count": number,
        "correct_answer": str(number),
        "alternatives": [str(number), NUMBER_WORDS[number].lower()],
    }


def generate_select_answer_question() -> Dict[str, Any]:
    """Generate a multiple-choice select question"""
    variant = random.choice(["number_to_word", "word_to_number", "count_objects"])
    
    if variant == "number_to_word":
        number = random.randint(1, 10)
        correct = NUMBER_WORDS[number]
        wrong = random.sample([w for n, w in NUMBER_WORDS.items() if n != number], 3)
        options = [correct] + wrong
        random.shuffle(options)
        return {
            "id": f"select_n2w_{number}_{random.randint(100,999)}",
            "type": "select",
            "difficulty": "easy",
            "points": 10,
            "question": f"What is the word for the number {number}?",
            "options": options,
            "correct_answer": correct,
        }
    elif variant == "word_to_number":
        number = random.randint(1, 10)
        word = NUMBER_WORDS[number]
        wrong = random.sample([str(n) for n in range(1, 11) if n != number], 3)
        options = [str(number)] + wrong
        random.shuffle(options)
        return {
            "id": f"select_w2n_{number}_{random.randint(100,999)}",
            "type": "select",
            "difficulty": "easy",
            "points": 10,
            "question": f"Which number is '{word}'?",
            "options": options,
            "correct_answer": str(number),
        }
    else:
        count = random.randint(1, 10)
        obj = random.choice(COUNTING_OBJECTS)
        wrong = random.sample([str(n) for n in range(1, 11) if n != count], 3)
        options = [str(count)] + wrong
        random.shuffle(options)
        return {
            "id": f"select_count_{count}_{random.randint(100,999)}",
            "type": "select",
            "difficulty": "easy",
            "points": 10,
            "question": f"How many {obj['name']} are shown?",
            "object_name": obj["name"],
            "object_emoji": obj["emoji"],
            "object_image": obj["image"].replace("{n}", str(count)),
            "object_count": count,
            "options": options,
            "correct_answer": str(count),
        }


class ProgressTestSubmission(BaseModel):
    score: int
    total_questions: int
    test_type: str = "placement"  # placement, beginner, intermediate, advanced
    answers: List[Dict[str, Any]]


def get_activity_questions_from_json(activity_type: str, difficulty: str = None, count: int = 1) -> List[Dict[str, Any]]:
    """Extract questions from existing JSON activity data"""
    questions = []
    
    try:
        # Load both levels
        level1_data = load_activities_data(1)
        level2_data = load_activities_data(2)
        
        # Collect all numbers from both levels
        all_numbers = {}
        all_numbers.update(level1_data.get('numbers', {}))
        all_numbers.update(level2_data.get('numbers', {}))
        
        # Extract questions of the specified type
        available_questions = []
        for number_str, number_data in all_numbers.items():
            if activity_type in number_data and number_data[activity_type]:
                activity_questions = number_data[activity_type].get('questions', [])
                for q in activity_questions:
                    if difficulty is None or q.get('difficulty') == difficulty:
                        # Add number context to the question
                        q_copy = q.copy()
                        q_copy['number'] = int(number_str)
                        q_copy['type'] = activity_type
                        available_questions.append(q_copy)
        
        # Randomly select the requested count
        if available_questions:
            selected = random.sample(
                available_questions, 
                min(count, len(available_questions))
            )
            questions.extend(selected)
    
    except Exception as e:
        print(f"Error loading {activity_type} questions: {e}")
    
    return questions


def convert_json_to_test_question(q: Dict, activity_type: str, number: int) -> Dict[str, Any]:
    """Convert a raw JSON activity question to unified ProgressTestQuestion format.
    
    Maps each activity type (trace, show, say, read) to the widget-compatible format
    used by the Flutter question_widgets.dart.
    """
    if activity_type == 'trace':
        return {
            "id": q.get('id', f"trace_{number}_{q.get('difficulty', 'easy')}"),
            "type": "trace",
            "difficulty": q.get('difficulty', 'easy'),
            "points": q.get('points', 10),
            "question": f"Draw the number {number}",
            "instruction": q.get('instruction', f"Write the number {number}"),
            "expected_number": number,
            "word": NUMBER_WORDS.get(number, str(number)),
            "template_image": q.get('template_image'),
        }
    
    elif activity_type == 'show':
        count = q.get('correct_answer', number)
        
        # For numbers > 10, use image_counting (emojis) instead of camera detection
        # Camera detection is impractical for large quantities
        if count > 10:
            options = sorted(list(set([
                str(count), str(max(1, count - 1)), 
                str(count + 1), str(max(1, count - 2))
            ])))[:4]
            
            object_name = q.get('object_name', 'objects')
            # Don't reveal the answer in the question!
            return {
                "id": q.get('id', f"show_{number}_{q.get('difficulty', 'easy')}"),
                "type": "image_counting",
                "difficulty": q.get('difficulty', 'easy'),
                "points": q.get('points', 10),
                "question": f"How many {object_name} do you see?",
                "instruction": "Count the objects",
                "object_name": object_name,
                "object_emoji": q.get('object_emoji'),
                "object_count": count,
                "options": options,
                "correct_answer": str(count),
            }
        
        # For counts 1-10, use camera detection
        object_name = q.get('object_name', 'any')
        # Remove plural 's' for detection (e.g., 'apples' -> 'apple')
        if object_name.endswith('s') and len(object_name) > 1:
            object_name = object_name[:-1]
        
        return {
            "id": q.get('id', f"show_{number}_{q.get('difficulty', 'easy')}"),
            "type": "object_detection",
            "difficulty": q.get('difficulty', 'easy'),
            "points": q.get('points', 10),
            "question": q.get('question', f"Show me {count} {object_name}(s) using the camera"),
            "instruction": "Use camera to show the objects",
            "object_name": object_name,
            "object_count": count,
            "object_emoji": q.get('object_emoji'),
        }
    
    elif activity_type == 'say':
        return {
            "id": q.get('id', f"say_{number}_{q.get('difficulty', 'easy')}"),
            "type": "say",
            "difficulty": q.get('difficulty', 'easy'),
            "points": q.get('points', 10),
            "question": q.get('question', f"Say the number!"),
            "instruction": "Say the number out loud",
            "object_image": q.get('image'),
            "object_name": q.get('object_name'),
            "object_emoji": q.get('object_emoji'),
            "object_count": q.get('correct_answer', number),
            "correct_answer": str(q.get('correct_answer', number)),
            "alternatives": q.get('alternatives', [str(number), NUMBER_WORDS.get(number, '').lower()]),
            "pronounce": q.get('pronounce'),
        }
    
    elif activity_type == 'read':
        return {
            "id": q.get('id', f"read_{number}_{q.get('difficulty', 'easy')}"),
            "type": "select",
            "difficulty": q.get('difficulty', 'easy'),
            "points": q.get('points', 10),
            "question": q.get('question', ''),
            "options": q.get('options', []),
            "correct_answer": q.get('correct_answer', ''),
        }
    
    # Fallback
    return {
        "id": f"unknown_{number}_{random.randint(100,999)}",
        "type": "select",
        "difficulty": q.get('difficulty', 'easy'),
        "points": q.get('points', 10),
        "question": f"What number is this: {number}?",
        "options": [str(number)],
        "correct_answer": str(number),
    }


@app.get("/test/progress")
async def get_progress_test():
    """
    GET /test/progress
    
    Small placement quiz (5 questions) to determine starting difficulty level.
    Uses easy questions from JSON activity data - one from each activity type.
    
    Based on score:
    - 0-2 correct: Beginner only
    - 3-4 correct: Beginner + Intermediate unlocked
    - 5 correct: All levels unlocked
    """
    try:
        questions = []
        
        # Get 1 easy question from each JSON activity type
        for activity_type in ['trace', 'show', 'say', 'read']:
            json_qs = get_activity_questions_from_json(activity_type, difficulty='easy', count=1)
            for q in json_qs:
                questions.append(convert_json_to_test_question(q, activity_type, q['number']))
        
        # Add 1 select question for variety
        questions.append(generate_select_answer_question())
        
        random.shuffle(questions)
        
        return {
            "test_type": "placement",
            "total_questions": len(questions),
            "questions": questions,
            "scoring": {
                "beginner": {"min_score": 0, "max_score": 2, "unlocks": ["beginner"]},
                "intermediate": {"min_score": 3, "max_score": 4, "unlocks": ["beginner", "intermediate"]},
                "advanced": {"min_score": 5, "max_score": 5, "unlocks": ["beginner", "intermediate", "advanced"]},
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating placement quiz: {str(e)}"
        )


@app.post("/test/evaluate")
async def evaluate_test(submission: ProgressTestSubmission):
    """
    POST /test/evaluate
    
    Generic test evaluation. Handles placement quiz, beginner, intermediate, and advanced tests.
    Returns unlocked levels based on test type and score.
    """
    score = submission.score
    total = submission.total_questions
    test_type = submission.test_type
    percentage = (score / total) * 100 if total > 0 else 0
    
    if test_type == "placement":
        if score >= 5:
            difficulty_level = "advanced"
            unlocked_levels = [1, 2, 3]
            message = "Excellent! All difficulty levels are unlocked!"
        elif score >= 3:
            difficulty_level = "intermediate"
            unlocked_levels = [1, 2]
            message = "Good job! Beginner and Intermediate are unlocked!"
        else:
            difficulty_level = "beginner"
            unlocked_levels = [1]
            message = "Let's start from the basics! Beginner level is ready."
    
    elif test_type == "beginner":
        if score >= 5:  # 5 out of 8 = 62.5%
            difficulty_level = "intermediate"
            unlocked_levels = [1, 2]
            message = "Great work! You've unlocked Intermediate level!"
        else:
            difficulty_level = "beginner"
            unlocked_levels = [1]
            message = "Keep practicing! Try again to unlock Intermediate."
    
    elif test_type == "intermediate":
        if score >= 6:  # 6 out of 10 = 60%
            difficulty_level = "advanced"
            unlocked_levels = [1, 2, 3]
            message = "Amazing! You've unlocked Advanced level!"
        else:
            difficulty_level = "intermediate"
            unlocked_levels = [1, 2]
            message = "Good effort! Practice more to unlock Advanced."
    
    elif test_type == "advanced":
        difficulty_level = "advanced"
        unlocked_levels = [1, 2, 3]
        if score >= 7:
            message = "Outstanding! You've mastered all levels!"
        else:
            message = "Great attempt! Keep practicing the advanced topics."
    
    else:
        difficulty_level = "beginner"
        unlocked_levels = [1]
        message = "Test completed."
    
    return {
        "score": score,
        "total": total,
        "percentage": round(percentage, 1),
        "difficulty_level": difficulty_level,
        "unlocked_levels": unlocked_levels,
        "message": message,
        "test_type": test_type,
        "timestamp": datetime.now().isoformat()
    }


# Keep legacy endpoint for backward compatibility
@app.post("/test/progress/evaluate")
async def evaluate_progress_test(submission: ProgressTestSubmission):
    """Legacy endpoint - redirects to unified evaluate"""
    return await evaluate_test(submission)


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
    expected_digit: Optional[int] = None  # For validation (supports multi-digit numbers)
    confidence_threshold: Optional[float] = 0.7


@app.post("/recognize/digit")
async def recognize_digit(request: DigitRecognitionRequest):
    """
    POST /recognize/digit
    
    Recognize handwritten digit/number from image using ML model.
    Automatically uses multi-digit recognition when expected_digit >= 10.
    
    Request body:
    {
        "image": "base64_encoded_image_string",
        "expected_digit": 5,  // Optional: for validation (supports multi-digit)
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
        
        # Determine if we need multi-digit recognition
        use_multi_digit = (
            request.expected_digit is not None and request.expected_digit >= 10
        )
        
        if use_multi_digit:
            # Multi-digit recognition path
            if request.expected_digit is not None:
                # Validation mode for multi-digit numbers
                import base64 as b64
                import os
                from datetime import datetime
                
                image_data = b64.b64decode(request.image)
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    raise HTTPException(status_code=400, detail="Failed to decode image")
                
                # Save debug image for multi-digit validation
                debug_dir = "debug_images"
                os.makedirs(debug_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                debug_path_original = os.path.join(debug_dir, f"validate_number_{request.expected_digit}_{timestamp}.png")
                debug_path_segmented = os.path.join(debug_dir, f"validate_number_{request.expected_digit}_{timestamp}_segmented.png")
                cv2.imwrite(debug_path_original, image)
                logger.info(f"💾 Saved validation image to: {debug_path_original}")
                
                validation_result = recognition_service.validate_number(
                    image=image,
                    expected_number=request.expected_digit,
                    confidence_threshold=request.confidence_threshold,
                    save_debug=True,
                    debug_path=debug_path_segmented
                )
                
                if 'error' in validation_result and validation_result.get('predicted') == -1:
                    raise HTTPException(status_code=400, detail=validation_result['error'])
                
                return {
                    'predicted_digit': validation_result['predicted'],
                    'confidence': validation_result['confidence'],
                    'probabilities': [],
                    'top_3_predictions': [],
                    'is_correct': validation_result['is_correct'],
                    'expected': validation_result['expected'],
                    'feedback': validation_result['feedback'],
                    'digit_results': validation_result.get('digit_results', []),
                    'num_digits': validation_result.get('num_digits', 0)
                }
            else:
                # Recognition only for multi-digit
                result = recognition_service.recognize_number_from_base64(request.image)
                
                if 'error' in result and result.get('predicted_number') == -1:
                    raise HTTPException(status_code=400, detail=result['error'])
                
                return {
                    'predicted_digit': result['predicted_number'],
                    'confidence': result['confidence'],
                    'probabilities': [],
                    'top_3_predictions': [],
                    'digit_results': result.get('digit_results', []),
                    'num_digits': result.get('num_digits', 0)
                }
        else:
            # Single digit recognition path (original behavior)
            if request.expected_digit is not None:
                # Validation mode
                recognition_result = recognition_service.recognize_from_base64(request.image)
                
                if 'error' in recognition_result:
                    raise HTTPException(status_code=400, detail=recognition_result['error'])
                
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


@app.post("/recognize/number")
async def recognize_number(request: DigitRecognitionRequest):
    """
    POST /recognize/number
    
    Recognize handwritten multi-digit number from image.
    Segments the image into individual digits, recognizes each, and combines.
    
    Request body:
    {
        "image": "base64_encoded_image_string",
        "expected_digit": 42,  // Optional: for validation
        "confidence_threshold": 0.7
    }
    
    Returns:
    {
        "predicted_number": 42,
        "confidence": 0.92,
        "digit_results": [...],
        "num_digits": 2,
        "is_correct": true,  // If expected_digit provided
        "feedback": "..."
    }
    """
    try:
        recognition_service = get_recognition_service()
        
        if request.expected_digit is not None:
            import base64 as b64
            image_data = b64.b64decode(request.image)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise HTTPException(status_code=400, detail="Failed to decode image")
            
            result = recognition_service.validate_number(
                image=image,
                expected_number=request.expected_digit,
                confidence_threshold=request.confidence_threshold
            )
        else:
            result = recognition_service.recognize_number_from_base64(request.image)
        
        if 'error' in result and result.get('predicted_number', result.get('predicted', -1)) == -1:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during number recognition: {str(e)}"
        )


# Removed unused endpoint: /recognize/digit/upload

# TODO: Phase 2 - Additional endpoints
# @app.post("/progress/sync")
# @app.get("/user/{user_id}/progress")
# @app.post("/user/{user_id}/activity/{activity_id}/complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
