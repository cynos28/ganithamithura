"""
Image-based Question Generator for Measurement Concepts
Uses GPT-4 Vision to analyze measurement images and generate contextual questions
"""

import os
import base64
import random
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.utils.llm_client import llm_client


class ImageQuestionGenerator:
    """Generate questions from measurement images using GPT-4 Vision"""
    
    def __init__(self):
        self.static_dir = Path(__file__).parent.parent.parent / "static" / "images"
        
        # Track recently used images per topic to avoid repetition across batches
        # Stores list of recently used image names per topic
        self._recently_used: Dict[str, List[str]] = {}
        
        # Mapping measurement topics to image folders
        self.topic_folders = {
            "length": "length",
            "area": "area",
            "weight": "Weight",
            "volume": "volume",
            "capacity": "volume" # Capacity is often used interchangeably with Volume
        }
        
        # Grade-specific vision prompts
        self.grade_vision_prompts = {
            1: {
                "system": """You are creating measurement questions for Grade 1 students (ages 6-7) by ANALYZING the image shown.

CRITICAL INSTRUCTIONS:
1. LOOK at the image carefully and identify ALL objects visible
2. Generate questions that compare TWO objects you see in the image
3. Start questions with "Look at the picture" or "Look at the image"
4. Use ONLY simple words: bigger/smaller, taller/shorter, longer/shorter, heavier/lighter, more/less
5. Questions must be 5-10 words long
6. Use the EXACT object names you see (tree, table, car, pencil, etc.)

QUESTION TYPES (use variety):
- "Look at the picture. Which one is taller, the [object1] or the [object2]?"
- "Which one is shorter, the [object1] or the [object2]?"
- "Which one is bigger, the [object1] or the [object2]?"
- "Which object is heavier, the [object1] or the [object2]?"
- "Which one takes more space (Area), the [object1] or the [object2]?"
- "Which container holds more (Volume), the [object1] or the [object2]?"

OUTPUT FORMAT:
- Answer must be one of the objects mentioned
- Explanation: point to visual clues ("The tree is taller because it goes higher in the picture")
- MCQ options: use both object names plus creative wrong answers
- Add one emoji per question 🎉""",
                "difficulty_range": [1, 2],
                "bloom_levels": ["remember", "understand"],
            },
            2: {
                "system": """You are creating measurement questions for Grade 2 students (ages 7-8) by ANALYZING the image shown.

CRITICAL INSTRUCTIONS:
1. EXAMINE the image and identify all visible objects with their sizes/measurements
2. Generate visual comparison questions between objects you see
3. Start with "Look at the picture" or similar visual cue
4. Use clear sentences (10-15 words)
5. Reference EXACT objects visible in the image
6. Include simple numbers when appropriate (1-100)

QUESTION TYPES (analyze image to create):
- "Look at the picture. Which one is taller, the [object1] or the [object2]?"
- "Which object has a larger area, the [object1] or the [object2]?"
- "Which one takes more space, the [object1] or the [object2]?"
- "Which object can hold more things, the [object1] or the [object2]?"
- "If the [object1] is [X] meters and the [object2] is [Y] meters, which is taller?"
- "Which object is usually heavier, a [object1] or a [object2]?"

OUTPUT FORMAT:
- Answer: the correct object name from the image
- Explanation: describe what students see ("The tree is bigger because it covers more space in the picture")
- Include one emoji 😊""",
                "difficulty_range": [2, 3],
                "bloom_levels": ["remember", "understand"],
            },
            3: {
                "system": """You are creating measurement questions for Grade 3 students (ages 8-9) by ANALYZING the image shown.

CRITICAL INSTRUCTIONS:
1. STUDY the image and identify objects with measurable attributes (length, area, volume, weight)
2. Create comparison and estimation questions based on what you see
3. Start with visual prompts: "Look at the picture", "In the image"
4. Use grade-appropriate vocabulary (up to 20 words)
5. Include specific measurements when visible or provide context
6. Numbers up to 1000

QUESTION TYPES (based on image analysis):
- "Look at the picture. Which one is taller/shorter/longer, the [object1] or the [object2]?"
- "Which object has a larger area of shade/coverage, the [object1] or the [object2]?"
- "Which one is bigger in size, the [object1] or the [object2]?"
- "If the [object1] is [X] meters tall and the [object2] is [Y] meters tall, which one is taller?"
- "Which object can hold more things on top, the [object1] or the [object2]?"
- "Which object takes more space, the [object1] or the [object2]?"
- "Estimate: About how much taller is the [object1] compared to the [object2]?"

OUTPUT FORMAT:
- Questions MUST reference objects actually visible in the image
- Answers based on visual evidence or common knowledge
- Explanations: teach measurement concepts using image ("We can see the tree is much taller because...")""",
                "difficulty_range": [3, 4],
                "bloom_levels": ["understand", "apply"],
            },
            4: {
                "system": """You are creating measurement questions for Grade 4 students (ages 9-10) by ANALYZING the image shown.

CRITICAL INSTRUCTIONS:
1. ANALYZE the image deeply - identify all objects, their relative sizes, spatial relationships
2. Create multi-step measurement questions based on visual evidence
3. Use academic vocabulary appropriate for upper elementary
4. Include conversions, estimations, and real-world applications
5. Numbers up to 10,000
6. Reference specific visual details from the image

QUESTION TYPES (analyze image to create):
- "Look at the picture. Which one is taller/longer/bigger, the [object1] or the [object2]? Explain."
- "Which object has a larger area of shade/surface, the [object1] or the [object2]?"
- "If the [object1] is [X] meters tall and the [object2] is [Y] meters tall, which one is taller?"
- "Which object can hold more things on top/inside (Volume), the [object1] or the [object2]? Why?"
- "Which object is usually heavier, a [object1] or a [object2]? Estimate the difference."
- "Calculate or estimate which surface has a larger area: [object1] or [object2]?"
- "Based on the image, estimate the height/length/area/volume of the [object]."

OUTPUT FORMAT:
- Questions MUST describe what's visible: "Look at the picture. You can see a [object1] and a [object2]..."
- Answers: include reasoning based on visual analysis
- Explanations: step-by-step measurement thinking using image evidence""",
                "difficulty_range": [4, 5],
                "bloom_levels": ["apply", "analyze"],
            }
        }
    
    def _encode_image_to_base64(self, image_path: Path) -> str:
        """Encode image file to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _get_available_images(self, topic: str) -> List[Path]:
        """Get list of available images for a measurement topic"""
        folder_name = self.topic_folders.get(topic.lower())
        if not folder_name:
            return []
        
        folder_path = self.static_dir / folder_name
        if not folder_path.exists():
            return []
        
        # Get all PNG images (numbered 1.png, 2.png, etc.)
        images = list(folder_path.glob("*.png"))
        return sorted(images)
    
    def _select_unique_images(self, topic: str, count: int) -> List[Path]:
        """Select unique images, avoiding recently used ones across batches."""
        available = self._get_available_images(topic)
        if not available:
            return []
        
        recently_used = self._recently_used.get(topic, [])
        
        # Prefer images NOT recently used
        fresh = [img for img in available if img.name not in recently_used]
        
        # If not enough fresh images, reset the used list and use all
        if len(fresh) < count:
            self._recently_used[topic] = []
            fresh = available
        
        # Pick `count` unique images (one per question, no duplicates in batch)
        sample_size = min(count, len(fresh))
        selected = random.sample(fresh, sample_size)
        
        # Record these as recently used
        used = self._recently_used.get(topic, [])
        used.extend(img.name for img in selected)
        # Keep only the last N used names to allow cycling
        max_memory = len(available)
        self._recently_used[topic] = used[-max_memory:]
        
        return selected
    
    async def generate_questions_from_image(
        self,
        image_path: Path,
        topic: str,
        grade_level: int,
        num_questions: int = 2,
        document_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate questions from a single image using GPT-4 Vision
        
        Args:
            image_path: Path to the measurement image
            topic: Measurement topic (length, area, weight, volume)
            grade_level: Grade level (1-4)
            num_questions: Number of questions to generate from this image
            document_context: Optional curriculum context from uploaded document
            
        Returns:
            List of question dictionaries
        """
        # Get grade-specific prompt
        grade_config = self.grade_vision_prompts.get(grade_level, self.grade_vision_prompts[3])
        
        # Build the vision prompt
        user_prompt = f"""ANALYZE THE IMAGE CAREFULLY and generate {num_questions} {topic} measurement questions for Grade {grade_level} students.

MEASUREMENT TOPIC: {topic.title()}
GRADE LEVEL: {grade_level}

STEP 1 - IMAGE ANALYSIS:
- Look at the image and identify ALL visible objects
- Note their sizes, positions, and relationships
- Identify measurable attributes (height, length, area, volume, weight)

STEP 2 - QUESTION GENERATION:
- Create comparison questions between TWO objects you see
- Use this format: "Look at the picture. Which one is [taller/shorter/bigger/heavier], the [object1] or the [object2]?"
- ONLY use objects that are ACTUALLY VISIBLE in the image
- Vary question types: taller/shorter, bigger/smaller, heavier/lighter, more space/less space, larger area, can hold more

EXAMPLE QUESTIONS (adapt to what you see in THIS image):
- "Look at the picture. Which one is taller, the [object1] or the [object2]?"
- "Which one is shorter, the [object1] or the [object2]?"
- "Which object has a larger area of shade, the [object1] or the [object2]?"
- "Which one is bigger in size, the [object1] or the [object2]?"
- "If the [object1] is [X] meters and the [object2] is [Y] meters, which one is taller?"
- "Which object can hold more things on top, the [object1] or the [object2]?"
- "Which object is usually heavier, a [object1] or a [object2]?"
- "Which one takes more space, the [object1] or the [object2]?"

REQUIRED OUTPUT FORMAT (JSON):
{{
    "questions": [
        {{
            "question_text": "Look at the picture. Which one is [comparison], the [actual object from image] or the [actual object from image]?",
            "question_type": "mcq",
            "options": ["[object1 name]", "[object2 name]", "Both are the same", "Cannot tell"],
            "correct_answer": "[object name from image]",
            "explanation": "The [object] is [taller/bigger/etc] because [visual evidence from image]",
            "hints": ["Look at how high the [object] reaches in the picture", "Compare the sizes visually"],
            "difficulty_level": {grade_config['difficulty_range'][0]}-{grade_config['difficulty_range'][1]},
            "bloom_level": "{grade_config['bloom_levels'][0]}" or "{grade_config['bloom_levels'][1]}",
            "concepts": ["{topic}", "comparison", "visual measurement"],
            "image_reference": "Describes which objects in image are being compared"
        }}
    ]
}}"""

        if document_context:
            user_prompt += f"\n\nCURRICULUM CONTEXT (align questions with these learning objectives):\n{document_context[:500]}"
        
        user_prompt += f"""

CRITICAL REMINDERS:
1. FIRST: Identify what objects you actually see in this specific image
2. THEN: Create comparison questions between those exact objects
3. Questions MUST start with \"Look at the picture\" or \"Look at the image\"
4. Use the exact object names from the image (e.g., tree, table, car, pencil - whatever is visible)
5. Don't invent objects that aren't in the image
6. Answer must be one of the objects mentioned in the question
7. Explanations should reference visual evidence: \"You can see in the picture that...\"

Generate exactly {num_questions} visual comparison questions now in valid JSON format."""

        # Encode image
        base64_image = self._encode_image_to_base64(image_path)
        
        # Call GPT-4 Vision
        try:
            response = await llm_client.generate_with_vision(
                system_prompt=grade_config['system'],
                user_prompt=user_prompt,
                image_base64=base64_image,
                model="gpt-4o",  # GPT-4 with vision
                temperature=0.7,
                max_tokens=2000
            )
            
            # Clean and parse JSON response
            import json
            import re
            
            # Clean response - remove markdown code blocks if present
            cleaned_response = response.strip()
            
            # Remove markdown JSON code blocks (```json ... ``` or ``` ... ```)
            if cleaned_response.startswith("```"):
                # Extract content between code fences
                match = re.search(r'```(?:json)?\s*\n(.*?)\n```', cleaned_response, re.DOTALL)
                if match:
                    cleaned_response = match.group(1).strip()
                else:
                    # Try removing just the markers
                    cleaned_response = re.sub(r'```(?:json)?', '', cleaned_response).strip()
            
            try:
                questions_data = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                print(f"   Response preview: {cleaned_response[:300]}...")
                raise
            
            # Add image URL to each question
            folder_name = self.topic_folders.get(topic.lower(), topic.lower())
            image_url = f"/static/images/{folder_name}/{image_path.name}"
            
            questions = []
            for q in questions_data.get("questions", []):
                q["image_url"] = image_url
                q["image_path"] = str(image_path)
                q["topic"] = topic
                q["grade_level"] = grade_level
                questions.append(q)
            
            return questions
            
        except Exception as e:
            print(f"❌ Error generating questions from image {image_path.name}: {e}")
            return []
    
    async def generate_image_based_questions(
        self,
        topic: str,
        grade_level: int,
        total_questions: int = 10,
        document_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple questions using different measurement images
        
        Args:
            topic: Measurement topic (length, area, weight, volume)
            grade_level: Grade level (1-4)
            total_questions: Total questions to generate
            document_context: Optional curriculum context
            
        Returns:
            List of all generated questions
        """
        # One unique image per question — no repeats within a batch,
        # and different images from the previous batch
        images = self._select_unique_images(topic, total_questions)
        
        if not images:
            print(f"⚠️ No images found for topic '{topic}'")
            return []
        
        print(f"📂 Selected {len(images)} unique images: {[img.name for img in images]}")
        
        all_questions = []
        for i, image_path in enumerate(images):
            remaining = total_questions - len(all_questions)
            if remaining <= 0:
                break
            
            print(f"📸 Generating 1 question from {image_path.name}...")
            
            questions = await self.generate_questions_from_image(
                image_path=image_path,
                topic=topic,
                grade_level=grade_level,
                num_questions=1,
                document_context=document_context
            )
            
            all_questions.extend(questions)
        
        print(f"✅ Generated {len(all_questions)} image-based questions (each from a different photo)")
        return all_questions
    
    def get_image_statistics(self) -> Dict[str, int]:
        """Get count of available images per topic"""
        stats = {}
        for topic, folder in self.topic_folders.items():
            images = self._get_available_images(topic)
            stats[topic] = len(images)
        return stats


# Singleton instance
image_question_generator = ImageQuestionGenerator()
