"""
Contextual questions generation based on AR measurements
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.services.question_generator import question_generator
from app.services.embeddings_service import embeddings_service
from app.models.database import QuestionModel

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
        
        # Save questions to database
        saved_questions = []
        for q_data in questions:
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
    num_questions: int
) -> List[dict]:
    """Generate questions using LLM with AR measurement context"""
    
    from app.utils.llm_client import llm_client
    import json
    
    # Build personalized prompt
    prompt = f"""Generate {num_questions} educational questions based on this REAL measurement by a student:

STUDENT'S MEASUREMENT:
{measurement_context.personalized_prompt}
Object: {measurement_context.object_name}
Exact measurement: {measurement_context.value}{measurement_context.unit}
Topic: {measurement_context.topic}
Grade Level: {grade}

CURRICULUM CONTEXT:
{curriculum_context[:2000]}

CRITICAL RULES FOR AR-BASED QUESTIONS:
1. Use "YOUR {measurement_context.object_name}" to make it personal
2. Reference the EXACT measurement ({measurement_context.value}{measurement_context.unit})
3. Make questions conversational, like talking about THEIR object
4. Progress from easy to hard
5. Include these difficulty hints: {', '.join(measurement_context.difficulty_hints[:3])}

EXAMPLE GOOD QUESTIONS:
✅ "Your {measurement_context.object_name} is {measurement_context.value}{measurement_context.unit}. How many millimeters is that?"
✅ "If you have 3 {measurement_context.object_name}s like yours, what is the total length?"
✅ "Your {measurement_context.object_name} is {measurement_context.value}{measurement_context.unit}. Is it longer or shorter than 20cm?"

AVOID GENERIC QUESTIONS:
❌ "A pencil is X cm. Convert to mm." (too generic)
❌ "What is the length?" (doesn't use their measurement)

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
        print(f"🤖 Calling LLM for question generation...")
        response = await llm_client.generate_completion(
            prompt=prompt,
            system_message=f"You are an expert math teacher creating personalized questions about a student's REAL measurement. Grade {grade}.",
            temperature=0.8,
            max_tokens=2000
        )
        
        print(f"📝 LLM Response received: {response[:200]}...")
        
        # Parse JSON response
        response_text = response.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        questions_data = json.loads(response_text.strip())
        
        print(f"✅ Successfully parsed {len(questions_data.get('questions', []))} questions from LLM")
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
    """Generate varied adaptive fallback questions if LLM fails"""
    
    import random
    
    questions = []
    value = context.value
    unit = context.unit
    obj = context.object_name
    measurement_type = context.measurement_type
    
    # Create a pool of question templates with variations
    question_pool = []
    
    # 1. Unit Conversion Questions (varied approaches)
    if measurement_type == "length" and unit == "cm":
        question_pool.extend([
            {
                "question_text": f"Your {obj} is {value}cm long. How many millimeters is that?",
                "question_type": "mcq",
                "correct_answer": f"{value * 10}mm",
                "options": [f"{value * 10}mm", f"{value * 100}mm", f"{value}mm", f"{value / 10}mm"],
                "difficulty_level": 2,
                "explanation": f"1 cm = 10 mm, so {value}cm = {value * 10}mm",
                "hints": ["Remember: 1 centimeter = 10 millimeters"]
            },
            {
                "question_text": f"If your {obj} is {value}cm, what is its length in meters?",
                "question_type": "mcq",
                "correct_answer": f"{value / 100}m",
                "options": [f"{value / 100}m", f"{value / 10}m", f"{value * 100}m", f"{value}m"],
                "difficulty_level": 3,
                "explanation": f"1 meter = 100 cm, so {value}cm = {value / 100}m",
                "hints": ["Divide by 100 to convert cm to meters"]
            },
        ])
    
    # 2. Multiplication Questions (varied multipliers)
    multipliers = [2, 3, 4, 5]
    random.shuffle(multipliers)
    for mult in multipliers[:2]:  # Pick 2 random multipliers
        question_pool.append({
            "question_text": f"If you have {mult} {obj}s like yours ({value}{unit} each), what is the total {measurement_type}?",
            "question_type": "mcq",
            "correct_answer": f"{value * mult}{unit}",
            "options": _generate_mcq_options(value * mult, unit, spread=value),
            "difficulty_level": 1 + (mult // 3),
            "explanation": f"{value} × {mult} = {value * mult}{unit}",
            "hints": [f"Multiply {value} by {mult}"]
        })
    
    # 3. Division/Fraction Questions
    if value >= 2:
        divisors = [2, 4] if value >= 4 else [2]
        for div in divisors:
            if value % div == 0 or grade >= 3:  # Whole numbers for lower grades
                question_pool.append({
                    "question_text": f"If you divide your {obj} ({value}{unit}) into {div} equal parts, how long is each part?",
                    "question_type": "mcq",
                    "correct_answer": f"{value / div}{unit}",
                    "options": _generate_mcq_options(value / div, unit, spread=value / 4),
                    "difficulty_level": 2 + div // 2,
                    "explanation": f"{value} ÷ {div} = {value / div}{unit}",
                    "hints": [f"Divide the total by {div}"]
                })
    
    # 4. Comparison Questions (dynamic comparisons)
    comparison_values = [
        value + random.randint(5, 15),
        value - random.randint(5, min(15, int(value - 1))) if value > 15 else value + 10,
        value * 2,
    ]
    for comp_val in comparison_values[:2]:
        longer_obj = f"your {obj}" if value > comp_val else "the other object"
        question_pool.append({
            "question_text": f"Your {obj} is {value}{unit}. Compare it with an object that is {comp_val}{unit}. Which is longer?",
            "question_type": "mcq",
            "correct_answer": f"Your {obj} ({value}{unit})" if value > comp_val else f"The other object ({comp_val}{unit})",
            "options": [
                f"Your {obj} ({value}{unit})",
                f"The other object ({comp_val}{unit})",
                "They are equal",
                "Cannot determine"
            ],
            "difficulty_level": 1,
            "explanation": f"{max(value, comp_val)}{unit} is longer than {min(value, comp_val)}{unit}",
            "hints": ["Compare the two numbers to see which is bigger"]
        })
    
    # 5. Addition Questions (varied additions)
    add_values = [5, 10, 15, 20] if value > 20 else [5, 10]
    random.shuffle(add_values)
    for add_val in add_values[:2]:
        question_pool.append({
            "question_text": f"Your {obj} is {value}{unit}. If you add {add_val}{unit} more, what is the new {measurement_type}?",
            "question_type": "mcq",
            "correct_answer": f"{value + add_val}{unit}",
            "options": _generate_mcq_options(value + add_val, unit, spread=10),
            "difficulty_level": 2,
            "explanation": f"{value} + {add_val} = {value + add_val}{unit}",
            "hints": ["Add the two lengths together"]
        })
    
    # 6. Subtraction Questions
    if value > 10:
        sub_values = [5, 10] if value > 20 else [5]
        for sub_val in sub_values:
            if value > sub_val:
                question_pool.append({
                    "question_text": f"Your {obj} is {value}{unit}. If you remove {sub_val}{unit}, what remains?",
                    "question_type": "mcq",
                    "correct_answer": f"{value - sub_val}{unit}",
                    "options": _generate_mcq_options(value - sub_val, unit, spread=10),
                    "difficulty_level": 2,
                    "explanation": f"{value} - {sub_val} = {value - sub_val}{unit}",
                    "hints": ["Subtract to find what's left"]
                })
    
    # 7. Real-world application questions
    real_world = [
        {
            "question_text": f"Your {obj} is {value}{unit}. How many {obj}s would you need to make {value * 5}{unit}?",
            "question_type": "mcq",
            "correct_answer": "5",
            "options": ["5", "4", "6", "3"],
            "difficulty_level": 3,
            "explanation": f"{value * 5} ÷ {value} = 5",
            "hints": ["Divide the target length by the length of one object"]
        },
        {
            "question_text": f"Which of these is closest to your {obj}'s {measurement_type} of {value}{unit}?",
            "question_type": "mcq",
            "correct_answer": f"{value + 2}{unit}",
            "options": [f"{value + 2}{unit}", f"{value + 20}{unit}", f"{value - 20}{unit}" if value > 20 else f"{value // 2}{unit}", f"{value * 2}{unit}"],
            "difficulty_level": 1,
            "explanation": f"{value + 2}{unit} is closest to {value}{unit}",
            "hints": ["Look for the number closest to your measurement"]
        },
    ]
    question_pool.extend(real_world)
    
    # 8. Estimation questions
    if value >= 10:
        estimation_range = (int(value * 0.8), int(value * 1.2))
        question_pool.append({
            "question_text": f"Your {obj} is exactly {value}{unit}. Estimate: Is it closer to {estimation_range[0]}{unit} or {estimation_range[1]}{unit}?",
            "question_type": "mcq",
            "correct_answer": f"{estimation_range[1]}{unit}" if abs(value - estimation_range[1]) < abs(value - estimation_range[0]) else f"{estimation_range[0]}{unit}",
            "options": [f"{estimation_range[0]}{unit}", f"{estimation_range[1]}{unit}", f"{value * 2}{unit}", f"{value // 2}{unit}"],
            "difficulty_level": 2,
            "explanation": f"Compare distances: {value} is closer to the selected answer",
            "hints": ["Find which number is closer to your measurement"]
        })
    
    # Shuffle and select requested number of questions
    random.shuffle(question_pool)
    questions = question_pool[:num_questions]
    
    # Ensure variety by difficulty
    questions.sort(key=lambda q: q['difficulty_level'])
    
    print(f"📝 Generated {len(questions)} adaptive fallback questions")
    return questions

def _generate_mcq_options(correct: float, unit: str, spread: float = 10) -> List[str]:
    """Generate realistic MCQ options around the correct answer"""
    import random
    
    options = [f"{correct}{unit}"]
    
    # Add plausible wrong answers
    wrong_answers = [
        correct + spread,
        correct - spread if correct > spread else correct + spread * 2,
        correct * 2,
    ]
    
    # Shuffle and pick 3 unique wrong answers
    random.shuffle(wrong_answers)
    for ans in wrong_answers[:3]:
        if ans > 0 and f"{ans}{unit}" not in options:
            options.append(f"{ans}{unit}")
    
    # Fill remaining if needed
    while len(options) < 4:
        rand_val = correct + random.randint(-int(spread), int(spread))
        if rand_val > 0 and f"{rand_val}{unit}" not in options:
            options.append(f"{rand_val}{unit}")
    
    random.shuffle(options)
    return options[:4]
