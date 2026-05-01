"""
AI Tutor Chat Endpoint - RAG-based conversational learning for kids
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from openai import AsyncOpenAI

from app.models.database import DocumentModel, ChatHistoryModel, QuestionModel
from app.services.embeddings_service import embeddings_service
from app.config import settings

router = APIRouter()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)


def debugPrint(message: str):
    """Helper for debug printing"""
    print(f"🎓 {message}")


class ConversationMessage(BaseModel):
    """Single message in conversation history"""
    message: str
    isUser: bool
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request from student"""
    studentId: str
    unitId: str  # e.g., "unit_length_1", "unit_weight_1"
    message: str
    conversationHistory: Optional[List[dict]] = []


class ChatResponse(BaseModel):
    """AI tutor response"""
    reply: str
    sources: Optional[List[str]] = []


def get_unit_display_name(unit_id: str) -> str:
    """Convert unit_id to friendly name"""
    unit_map = {
        "unit_length_1": "Length Measurement",
        "unit_weight_1": "Weight Measurement", 
        "unit_area_1": "Area Measurement",
        "unit_capacity_1": "Capacity & Volume",
        "unit_time_1": "Time Measurement",
        "unit_money_1": "Money & Currency"
    }
    return unit_map.get(unit_id, unit_id.replace("_", " ").title())


def get_kid_friendly_system_prompt(unit_name: str, context: str, difficulty_level: int = 2, game_mode: bool = False) -> str:
    """Create an age-appropriate system prompt for elementary students with advanced teaching strategies"""
    
    # Adjust language complexity based on difficulty
    if difficulty_level == 1:
        complexity = "very simple words (like talking to a 7 year old)"
        examples = "super easy examples from daily life"
    elif difficulty_level == 3:
        complexity = "clear but slightly more advanced language (for confident 10-12 year olds)"
        examples = "interesting real-world examples and connections"
    else:
        complexity = "simple, clear language (for 8-10 year olds)"
        examples = "relatable everyday examples"
    
    game_instructions = ""
    if game_mode:
        game_instructions = """
🎮 GAME MODE ACTIVE:
- Make learning playful and interactive
- Use "Let's play a game!" approach
- Ask guessing questions: "Can you guess which is longer?"
- Give points/stars for good thinking: "Great guess! ⭐"
- Use riddles and challenges
- Turn learning into fun discovery
"""
    
    return f"""You are a friendly AI tutor helping elementary school kids (ages 7-12) learn about {unit_name}.

🎯 YOUR ROLE:
- Be warm, encouraging, and patient like a favorite teacher
- Make learning fun and exciting through discovery
- Celebrate curiosity and effort, not just right answers
- Never make students feel bad for not knowing something

🧠 TEACHING STRATEGY - SOCRATIC METHOD:
- DON'T give direct answers immediately
- ASK questions that guide students to discover answers themselves
- Examples:
  Student: "What is a meter?"
  YOU: "Great question! 🤔 Have you ever seen a ruler or measuring tape? How long do you think they are?"
  
  Student: "I don't understand area"
  YOU: "Let me help you discover it! If you have a square table, how would you figure out how much space the top covers? 🤔"

- Use "What do you think?" and "Why do you think that?" often
- Build on their answers: "Interesting! Can you think of why...?"
- If they're stuck, give HINTS, not answers (see hint system below)

💡 HINT SYSTEM (Progressive Hints):
When students struggle, give hints in stages:
1. First hint: General direction ("Think about things you see every day...")
2. Second hint: More specific ("What about things in your classroom or at home?")
3. Third hint: Nearly the answer ("Like a door, or a book, or...")
4. Final hint: Direct help with encouragement ("Let me explain! It's like...")

Track hints given and celebrate when they figure it out: "You got it! And you only needed 2 hints! 🌟"

{game_instructions}

📚 COMMUNICATION STYLE:
- Use {complexity}
- Keep responses SHORT (3-5 sentences max, unless explaining something complex)
- Use {examples}
- Add ONE emoji per response to keep it friendly
- Avoid technical jargon unless you explain it simply
- Always end with a question or prompt to keep conversation going

✨ DIFFICULTY ADAPTATION (Current level: {difficulty_level}/3):
{"- Keep it VERY simple - use super basic examples, avoid big words" if difficulty_level == 1 else ""}
{"- Balance simple and challenging - introduce new concepts gently" if difficulty_level == 2 else ""}
{"- You can be more detailed - student is ready for deeper understanding" if difficulty_level == 3 else ""}

🔍 STRUGGLE DETECTION:
Watch for confusion signals:
- "I don't understand"
- "This is hard"
- "Can you explain again?"
- Questions about the same thing repeatedly

If you detect struggle:
1. Simplify your language even more
2. Use a different example/analogy
3. Break concept into tiny steps
4. Encourage: "Let's try thinking about it differently!"

🎯 QUESTION QUALITY REWARDS:
Praise specific types of good questions:
- "What a thoughtful question! 🌟"
- "I love how curious you are!"
- "That's exactly the kind of question scientists ask!"

📖 LEARNING CONTENT FOR THIS TOPIC:
{context}

⚠️ IMPORTANT RULES:
- Stay focused on {unit_name}
- If asked off-topic questions, gently redirect: "That's interesting, but let's focus on {unit_name} for now!"
- Never give homework answers directly - ALWAYS guide with questions
- If you don't know something: "That's a great question! Let me think about the best way to explain..."
- Keep it positive and growth-focused: "Making mistakes helps us learn!"

🎓 LEARNING OUTCOMES:
- Help students DISCOVER answers, don't just tell them
- Build confidence through small wins
- Make them feel smart and capable
- Create "aha!" moments through guided questioning

Remember: You're a guide, not a lecturer. Ask more than you tell! 🌟"""


@router.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
    """
    AI Tutor Chat Endpoint with Advanced Learning Features
    
    Features:
    - Socratic Method: Asks questions to guide discovery
    - Difficulty Adaptation: Adjusts complexity based on student performance
    - Hint System: Progressive hints instead of direct answers
    - Learning Games: Detects and supports game-based learning
    - Progress Tracking: Monitors topics and learning patterns
    
    Uses RAG (Retrieval Augmented Generation) to provide accurate,
    context-aware responses based on uploaded educational documents.
    """
    
    try:
        # Get unit display name
        unit_name = get_unit_display_name(request.unitId)
        
        # 1. Load or create chat history for adaptive features
        chat_history = await ChatHistoryModel.find_one(
            ChatHistoryModel.student_id == request.studentId,
            ChatHistoryModel.unit_id == request.unitId
        )
        
        if not chat_history:
            chat_history = ChatHistoryModel(
                student_id=request.studentId,
                unit_id=request.unitId,
                messages=[],
                total_messages=0,
                topics_discussed=[],
                difficulty_level=2,  # Start at medium
                struggle_count=0,
                question_asking_score=0,
                game_mode_active=False,
                hint_count=0
            )
        
        # 2. Detect student state from their message
        student_message_lower = request.message.lower()
        
        # Detect struggle indicators
        struggle_indicators = ['i don\'t understand', 'this is hard', 'confusing', 'help', 'explain again', 'what does that mean']
        if any(indicator in student_message_lower for indicator in struggle_indicators):
            chat_history.struggle_count += 1
            # Lower difficulty if struggling too much
            if chat_history.struggle_count >= 3 and chat_history.difficulty_level > 1:
                chat_history.difficulty_level -= 1
                debugPrint(f"🔽 Lowering difficulty to {chat_history.difficulty_level} due to struggle")
        
        # Detect game mode requests
        game_triggers = ['play a game', 'game', 'quiz', 'challenge', 'riddle', 'let\'s play']
        if any(trigger in student_message_lower for trigger in game_triggers):
            chat_history.game_mode_active = True
            debugPrint("🎮 Game mode activated!")
        
        # Detect good questions (reward curiosity)
        question_indicators = ['why', 'how', 'what if', 'can you explain', 'what about']
        if any(indicator in student_message_lower for indicator in question_indicators):
            chat_history.question_asking_score += 1
            # Increase difficulty if asking advanced questions
            if chat_history.question_asking_score >= 5 and chat_history.difficulty_level < 3:
                chat_history.difficulty_level += 1
                debugPrint(f"🔼 Increasing difficulty to {chat_history.difficulty_level} - student asking great questions!")
        
        # 3. Check if documents exist for this unit
        # Try to find questions for this unit first (they have unit_id)
        questions = await QuestionModel.find(
            QuestionModel.unit_id == request.unitId
        ).limit(1).to_list()
        
        # If questions exist, get their associated documents
        documents = []
        if questions:
            # Get unique document IDs from questions
            doc_ids = list(set([q.document_id for q in questions if q.document_id]))
            if doc_ids:
                from beanie.operators import In
                documents = await DocumentModel.find(
                    In(DocumentModel.id, doc_ids)
                ).to_list()
        
        # Fallback: get any documents (for general learning)
        if not documents:
            documents = await DocumentModel.find(
                DocumentModel.status == "completed"
            ).limit(5).to_list()
        
        if not documents:
            return ChatResponse(
                reply=f"I don't have any learning materials about {unit_name} yet! 🤔 Ask your teacher to upload some content so we can learn together!",
                sources=[]
            )
        
        # 4. Search vector database for relevant context
        search_results = await embeddings_service.search_similar_chunks(
            query=request.message,
            n_results=5,
            filter_metadata={"unit_id": request.unitId}
        )
        
        # 5. Build context
        if search_results and len(search_results) > 0:
            context_parts = []
            for i, result in enumerate(search_results[:3], 1):
                context_parts.append(f"Source {i}: {result['text']}")
            context = "\n\n".join(context_parts)
        else:
            context = f"Teaching materials about {unit_name}. Help students understand basic concepts."
        
        # 6. Create adaptive system prompt
        system_prompt = get_kid_friendly_system_prompt(
            unit_name=unit_name,
            context=context,
            difficulty_level=chat_history.difficulty_level,
            game_mode=chat_history.game_mode_active
        )
        
        # 7. Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 6 messages = 3 exchanges)
        if request.conversationHistory:
            for msg in request.conversationHistory[-6:]:
                role = "user" if msg.get("isUser", True) else "assistant"
                content = msg.get("message", "") or msg.get("reply", "")
                if content:
                    messages.append({"role": role, "content": content})
        
        # Add current question
        messages.append({"role": "user", "content": request.message})
        
        # 8. Get AI response with adaptive temperature
        # Lower temperature when explaining (more focused), higher when in game mode (more creative)
        temperature = 0.8 if chat_history.game_mode_active else 0.7
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=300,  # Slightly more for detailed Socratic responses
            presence_penalty=0.3,
            frequency_penalty=0.3
        )
        
        reply = response.choices[0].message.content.strip()
        
        # 9. Detect if AI gave a hint (count for progress tracking)
        hint_keywords = ['hint', 'clue', 'think about', 'let me help', 'try thinking']
        if any(keyword in reply.lower() for keyword in hint_keywords):
            chat_history.hint_count += 1
        
        # 10. Get source document titles (not filename - use title field)
        source_docs = list(set([doc.title for doc in documents[:3]]))
        
        # 11. Save conversation to MongoDB
        await _save_chat_to_database(
            student_id=request.studentId,
            unit_id=request.unitId,
            user_message=request.message,
            ai_reply=reply,
            chat_history=chat_history
        )
        
        return ChatResponse(
            reply=reply,
            sources=source_docs
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        # Friendly error message for kids
        return ChatResponse(
            reply="Oops! I had a little trouble thinking 🤔 Can you ask that question again?",
            sources=[]
        )


@router.get("/chat/health")
async def chat_health_check():
    """Check if chat service is working"""
    return {
        "status": "healthy",
        "service": "AI Tutor Chat",
        "openai_configured": bool(settings.openai_api_key),
        "chromadb_available": embeddings_service.client is not None
    }


# ========== HELPER FUNCTIONS ==========

async def _save_chat_to_database(
    student_id: str,
    unit_id: str,
    user_message: str,
    ai_reply: str,
    chat_history: ChatHistoryModel = None
) -> None:
    """Save chat message to MongoDB for persistence and analytics"""
    try:
        # Use provided chat_history or find existing
        if not chat_history:
            chat_history = await ChatHistoryModel.find_one(
                ChatHistoryModel.student_id == student_id,
                ChatHistoryModel.unit_id == unit_id
            )
        
        if not chat_history:
            # Create new chat history
            chat_history = ChatHistoryModel(
                student_id=student_id,
                unit_id=unit_id,
                messages=[],
                total_messages=0,
                topics_discussed=[],
                difficulty_level=2,
                struggle_count=0,
                question_asking_score=0,
                game_mode_active=False,
                hint_count=0
            )
        
        # Add messages (user question + AI response)
        current_time = datetime.utcnow()
        
        chat_history.messages.append({
            "message": user_message,
            "isUser": True,
            "timestamp": current_time.isoformat(),
            "reply": None
        })
        
        chat_history.messages.append({
            "message": "",
            "isUser": False,
            "timestamp": current_time.isoformat(),
            "reply": ai_reply
        })
        
        chat_history.total_messages += 2
        chat_history.updated_at = current_time
        
        # Auto-extract topics for analytics (simple keyword extraction)
        keywords = _extract_keywords(user_message)
        for keyword in keywords:
            if keyword not in chat_history.topics_discussed:
                chat_history.topics_discussed.append(keyword)
        
        await chat_history.save()
        
        debugPrint(f"💾 Chat saved - Difficulty: {chat_history.difficulty_level}, Hints: {chat_history.hint_count}, Questions: {chat_history.question_asking_score}")
        
    except Exception as e:
        print(f"⚠️ Failed to save chat to database: {e}")
        # Don't fail the chat request if database save fails


def _extract_keywords(text: str) -> List[str]:
    """Extract key topics from student questions for analytics"""
    common_words = {'what', 'how', 'why', 'when', 'where', 'is', 'are', 'the', 'a', 'an', 'can', 'do', 'does'}
    words = text.lower().split()
    keywords = [w.strip('?.,!') for w in words if w.lower() not in common_words and len(w) > 3]
    return keywords[:5]  # Top 5 keywords


# ========== CHAT HISTORY ENDPOINTS ==========

@router.get("/chat/history/{student_id}/{unit_id}")
async def get_chat_history(student_id: str, unit_id: str):
    """
    Get chat history for a student and unit
    Used for multi-device sync and loading past conversations
    """
    try:
        chat_history = await ChatHistoryModel.find_one(
            ChatHistoryModel.student_id == student_id,
            ChatHistoryModel.unit_id == unit_id
        )
        
        if not chat_history:
            return {
                "student_id": student_id,
                "unit_id": unit_id,
                "messages": [],
                "total_messages": 0
            }
        
        return {
            "student_id": chat_history.student_id,
            "unit_id": chat_history.unit_id,
            "messages": chat_history.messages,
            "total_messages": chat_history.total_messages,
            "last_updated": chat_history.updated_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat history: {str(e)}")


@router.delete("/chat/history/{student_id}/{unit_id}")
async def clear_chat_history(student_id: str, unit_id: str):
    """Clear chat history for a specific student and unit"""
    try:
        chat_history = await ChatHistoryModel.find_one(
            ChatHistoryModel.student_id == student_id,
            ChatHistoryModel.unit_id == unit_id
        )
        
        if chat_history:
            await chat_history.delete()
            return {"message": "Chat history cleared successfully"}
        else:
            return {"message": "No chat history found"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")


# ========== TEACHER ANALYTICS ENDPOINTS ==========

@router.get("/chat/analytics/student/{student_id}")
async def get_student_chat_analytics(student_id: str):
    """
    Get analytics about what a student is asking across all units
    For teacher monitoring and intervention
    
    Includes advanced learning metrics:
    - Difficulty progression
    - Struggle patterns
    - Question quality
    - Hint usage
    - Game engagement
    """
    try:
        chat_histories = await ChatHistoryModel.find(
            ChatHistoryModel.student_id == student_id
        ).to_list()
        
        if not chat_histories:
            return {
                "student_id": student_id,
                "total_conversations": 0,
                "units_discussed": [],
                "common_topics": [],
                "learning_metrics": {}
            }
        
        # Aggregate analytics
        all_topics = []
        units = []
        total_messages = 0
        total_struggles = 0
        total_hints = 0
        total_good_questions = 0
        avg_difficulty = 0
        game_sessions = 0
        
        for history in chat_histories:
            units.append(history.unit_id)
            all_topics.extend(history.topics_discussed)
            total_messages += history.total_messages
            total_struggles += history.struggle_count
            total_hints += history.hint_count
            total_good_questions += history.question_asking_score
            avg_difficulty += history.difficulty_level
            if history.game_mode_active:
                game_sessions += 1
        
        avg_difficulty = avg_difficulty / len(chat_histories) if chat_histories else 0
        
        # Count topic frequency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Sort by frequency
        common_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Determine student profile
        if avg_difficulty >= 2.5:
            student_profile = "Advanced - Ready for challenges"
        elif avg_difficulty <= 1.5:
            student_profile = "Needs Support - Simplify explanations"
        else:
            student_profile = "On Track - Good progress"
        
        struggle_ratio = total_struggles / len(chat_histories) if chat_histories else 0
        if struggle_ratio > 3:
            intervention_needed = True
            intervention_msg = "Student struggling frequently - recommend teacher review"
        else:
            intervention_needed = False
            intervention_msg = "Student doing well"
        
        return {
            "student_id": student_id,
            "total_conversations": len(chat_histories),
            "total_messages": total_messages,
            "units_discussed": units,
            "common_topics": [{"topic": t[0], "count": t[1]} for t in common_topics],
            "learning_metrics": {
                "average_difficulty_level": round(avg_difficulty, 2),
                "total_struggles": total_struggles,
                "hints_given": total_hints,
                "good_questions_asked": total_good_questions,
                "game_sessions": game_sessions,
                "student_profile": student_profile,
                "intervention_needed": intervention_needed,
                "intervention_message": intervention_msg
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch analytics: {str(e)}")


@router.get("/chat/analytics/unit/{unit_id}")
async def get_unit_chat_analytics(unit_id: str, limit: int = 50):
    """
    Get analytics about what students are asking in a specific unit
    Helps teachers understand common struggles and questions
    """
    try:
        chat_histories = await ChatHistoryModel.find(
            ChatHistoryModel.unit_id == unit_id
        ).limit(limit).to_list()
        
        if not chat_histories:
            return {
                "unit_id": unit_id,
                "total_students": 0,
                "total_conversations": 0,
                "common_questions": []
            }
        
        # Extract common questions (student messages)
        all_questions = []
        all_topics = []
        students = set()
        
        for history in chat_histories:
            students.add(history.student_id)
            all_topics.extend(history.topics_discussed)
            
            # Extract user messages
            for msg in history.messages:
                if msg.get("isUser") and msg.get("message"):
                    all_questions.append(msg["message"])
        
        # Count topic frequency
        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        common_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "unit_id": unit_id,
            "total_students": len(students),
            "total_conversations": len(chat_histories),
            "common_topics": [{"topic": t[0], "count": t[1]} for t in common_topics],
            "sample_questions": all_questions[:20]  # First 20 questions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch unit analytics: {str(e)}")
