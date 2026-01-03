import json
from typing import List, Dict, Any
import asyncio
import hashlib
from datetime import datetime, timedelta
from app.utils.llm_client import llm_client
from app.services.embeddings_service import embeddings_service


class QuestionGenerator:
    """Generate questions from document content using LLM with RAG"""
    
    def __init__(self):
        # Simple in-memory cache: {cache_key: (questions, timestamp)}
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)  # Cache expires after 1 hour
    
    def _get_cache_key(self, context: str, grade_level: int, topic: str, num_questions: int) -> str:
        """Generate cache key from parameters"""
        # Use first 500 chars of context + other params for cache key
        content = f"{context[:500]}|{grade_level}|{topic}|{num_questions}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_questions(self, cache_key: str) -> List[Dict[str, Any]]:
        """Get questions from cache if available and not expired"""
        if cache_key in self._cache:
            questions, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self._cache_ttl:
                print(f"✅ Cache hit! Returning {len(questions)} cached questions")
                return questions
            else:
                # Expired, remove from cache
                del self._cache[cache_key]
                print(f"⏰ Cache expired, regenerating...")
        return None
    
    def _cache_questions(self, cache_key: str, questions: List[Dict[str, Any]]):
        """Store questions in cache"""
        self._cache[cache_key] = (questions, datetime.now())
        print(f"💾 Cached {len(questions)} questions (total cache size: {len(self._cache)})")
        
        # Simple cache size management: keep only last 100 entries
        if len(self._cache) > 100:
            # Remove oldest entries
            sorted_keys = sorted(self._cache.items(), key=lambda x: x[1][1])
            for key, _ in sorted_keys[:20]:  # Remove oldest 20
                del self._cache[key]
    
    async def retrieve_relevant_chunks(
        self,
        document_id: str,
        topic: str,
        grade_level: int,
        num_chunks: int = 5
    ) -> str:
        """
        Retrieve relevant chunks from vector database based on topic and grade.
        Returns concatenated text from most relevant chunks.
        """
        # Create focused query for retrieval
        query = f"{topic} measurement concepts for grade {grade_level} students"
        
        # Search for relevant chunks
        chunks = await embeddings_service.search_similar_chunks(
            query=query,
            n_results=num_chunks,
            filter_metadata={"document_id": document_id}
        )
        
        if not chunks:
            # Fallback: try without filter if no chunks found
            chunks = await embeddings_service.search_similar_chunks(
                query=query,
                n_results=num_chunks
            )
        
        # Concatenate chunk texts
        context = "\n\n".join([chunk['text'] for chunk in chunks])
        return context if context else ""
    
    # Grade-specific prompts
    GRADE_PROMPTS = {
        1: {
            "system": "You are creating questions for Grade 1 students (ages 6-7). Use simple words from the 200 most common English words. Keep questions 5-10 words long. Focus on visual recognition, counting, and basic identification. Use emojis to make it fun!",
            "bloom_levels": ["remember", "understand"],
            "question_types": ["mcq", "true_false"],
            "difficulty_range": [1, 5],  # Full range for adaptive selection
            "base_difficulty": 1  # Starting point for this grade
        },
        2: {
            "system": "You are creating questions for Grade 2 students (ages 7-8). Use simple vocabulary and short sentences. Focus on basic comprehension, simple calculations, and comparison. Make it engaging with emojis!",
            "bloom_levels": ["remember", "understand"],
            "question_types": ["mcq", "true_false"],  # Only MCQ for Flutter UI
            "difficulty_range": [1, 5],  # Full range for adaptive selection
            "base_difficulty": 2  # Starting point for this grade
        },
        3: {
            "system": "You are creating questions for Grade 3 students (ages 8-9). Use grade-appropriate vocabulary. Focus on application, simple problem-solving, and multi-step thinking. Include helpful hints!",
            "bloom_levels": ["understand", "apply"],
            "question_types": ["mcq", "true_false"],  # Only MCQ for Flutter UI
            "difficulty_range": [1, 5],  # Full range for adaptive selection
            "base_difficulty": 3  # Starting point for this grade
        },
        4: {
            "system": "You are creating questions for Grade 4 students (ages 9-10). Focus on analysis, reasoning, word problems, and applying concepts to new situations. Encourage critical thinking!",
            "bloom_levels": ["apply", "analyze"],
            "question_types": ["mcq", "true_false"],  # Only MCQ for Flutter UI
            "difficulty_range": [1, 5],  # Full range for adaptive selection
            "base_difficulty": 4  # Starting point for this grade
        }
    }
    
    async def generate_questions_from_context(
        self,
        context: str,
        grade_level: int,
        topic: str,
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate questions from given context with caching"""
        
        if grade_level not in self.GRADE_PROMPTS:
            raise ValueError(f"Invalid grade level: {grade_level}")
        
        # Check cache first
        cache_key = self._get_cache_key(context, grade_level, topic, num_questions)
        cached = self._get_cached_questions(cache_key)
        if cached:
            return cached
        
        grade_config = self.GRADE_PROMPTS[grade_level]
        
        prompt = f"""
Context about {topic.upper()} measurement:

{context[:1500]}

Generate {num_questions} Grade {grade_level} questions about {topic.upper()} only.

Rules:
- Topic: ONLY {topic.upper()} measurement
- Types: {', '.join(grade_config['question_types'])}
- Difficulty: Mix levels {grade_config['difficulty_range'][0]}-{grade_config['difficulty_range'][1]} (easy, medium, hard)
- MCQ: Exactly 4 options
- Include hints and explanation

JSON format:
{{
  "questions": [
    {{
      "question_text": "...",
      "question_type": "mcq|true_false",
      "correct_answer": "...",
      "options": ["A", "B", "C", "D"],
      "difficulty_level": 1-5,
      "bloom_level": "{grade_config['bloom_levels'][0]}|{grade_config['bloom_levels'][-1]}",
      "concepts": ["concept1"],
      "explanation": "...",
      "hints": ["hint1"]
    }}
  ]
}}
"""
        
        try:
            print(f"📤 Sending request to OpenAI (model: {llm_client.openai_model})...")
            print(f"📊 Optimized prompt: {len(prompt)} chars, Context: {len(context[:1500])} chars")
            
            response = await llm_client.generate_completion(
                prompt=prompt,
                system_message=grade_config['system'],
                temperature=0.7,  # Reduced from 0.8 for faster, more consistent responses
                max_tokens=1000,  # Reduced from 2000 - enough for 5-10 questions
                use_streaming=False,
            )
            
            print(f"📥 Received response from OpenAI ({len(response)} chars)")
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            questions_data = json.loads(response.strip())
            
            # Add grade level to each question
            for q in questions_data.get('questions', []):
                q['grade_level'] = grade_level
            
            questions = questions_data.get('questions', [])
            
            # Cache the results
            self._cache_questions(cache_key, questions)
            
            return questions
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")
    
    async def generate_questions_for_document(
        self,
        document_id: str,
        document_content: str,
        grade_levels: List[int],
        topic: str = "measurement",
        questions_per_grade: int = 10,
        question_types: List[str] = None,
        use_rag: bool = True
    ) -> List[Dict[str, Any]]:
        """Generate questions for a document across multiple grades using RAG - OPTIMIZED with parallel generation"""
        
        if not document_content or len(document_content) < 50:
            raise Exception("Document content is too short or empty")
        
        async def generate_for_grade(grade: int):
            """Helper function to generate questions for a single grade"""
            try:
                print(f"🎯 Generating {questions_per_grade} questions for grade {grade} (Topic: {topic})...")
                
                # Retrieve relevant chunks using RAG if enabled
                if use_rag:
                    print(f"📚 Retrieving relevant chunks for {topic} and grade {grade}...")
                    context = await self.retrieve_relevant_chunks(
                        document_id=document_id,
                        topic=topic,
                        grade_level=grade,
                        num_chunks=5
                    )
                    
                    # Fallback to document content if no chunks found
                    if not context or len(context) < 100:
                        print(f"⚠️  No chunks found, using full document (first 1500 chars)")
                        context = document_content[:1500] if len(document_content) > 1500 else document_content
                    else:
                        print(f"✅ Retrieved {len(context)} characters of relevant context")
                else:
                    # Use document content directly (legacy mode)
                    context = document_content[:1500] if len(document_content) > 1500 else document_content
                
                questions = await self.generate_questions_from_context(
                    context=context,
                    grade_level=grade,
                    topic=topic,
                    num_questions=questions_per_grade
                )
                print(f"✅ Generated {len(questions)} questions for grade {grade}")
                return questions
            except Exception as e:
                print(f"❌ Error generating questions for grade {grade}: {str(e)}")
                return []
        
        # Generate questions for all grades IN PARALLEL instead of serially
        print(f"🚀 Starting parallel generation for {len(grade_levels)} grades...")
        results = await asyncio.gather(*[generate_for_grade(grade) for grade in grade_levels])
        
        # Flatten results
        all_questions = []
        for questions in results:
            all_questions.extend(questions)
        
        print(f"✅ Total questions generated: {len(all_questions)}")
        return all_questions
    
    async def regenerate_question_with_adjustments(
        self,
        original_question: Dict[str, Any],
        adjustments: str
    ) -> Dict[str, Any]:
        """Regenerate a question with specific adjustments"""
        
        prompt = f"""
Original question:
{json.dumps(original_question, indent=2)}

Adjustment request: {adjustments}

Generate an improved version maintaining the same format but applying the requested changes.

Return ONLY valid JSON:
{{
  "question_text": "...",
  "question_type": "...",
  "correct_answer": "...",
  "options": [...],
  "difficulty_level": ...,
  "bloom_level": "...",
  "concepts": [...],
  "explanation": "...",
  "hints": [...]
}}
"""
        
        try:
            response = await llm_client.generate_completion(
                prompt=prompt,
                system_message="You are an expert educational content creator.",
                temperature=0.7
            )
            
            # Clean and parse response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.startswith('```'):
                response = response[3:]
            if response.endswith('```'):
                response = response[:-3]
            
            improved_question = json.loads(response.strip())
            return improved_question
        
        except Exception as e:
            raise Exception(f"Error regenerating question: {str(e)}")


# Singleton instance
question_generator = QuestionGenerator()
