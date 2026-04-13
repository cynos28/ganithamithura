#!/usr/bin/env python3
"""
Test image-based question generation for all measurement topics
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.image_question_generator import ImageQuestionGenerator


async def test_all_topics():
    """Test question generation for all topics"""
    gen = ImageQuestionGenerator()
    
    topics = ["length", "area", "volume", "weight"]
    grade = 2  # Test with grade 2
    
    print("🧪 Testing image-based question generation for all topics\n")
    print(f"📊 Grade Level: {grade}")
    print(f"📝 Questions per topic: 2 (for quick test)\n")
    print("="*70)
    
    for topic in topics:
        print(f"\n🔍 Testing {topic.upper()}...")
        
        try:
            # Generate 2 questions for this topic
            questions = await gen.generate_image_based_questions(
                topic=topic.lower(),
                grade_level=grade,
                total_questions=2,
                document_context="This is test context about measurement concepts."
            )
            
            print(f"✅ Generated {len(questions)} questions for {topic}")
            
            for i, q in enumerate(questions, 1):
                print(f"\n   Question {i}:")
                print(f"   📝 {q['question_text']}")
                print(f"   📷 Image: {q.get('image_url', 'No image')}")
                print(f"   ✓ Correct: {q['correct_answer']}")
                print(f"   📊 Difficulty: {q['difficulty_level']}")
                
        except Exception as e:
            print(f"❌ Error generating {topic} questions: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("✨ Test complete!")


if __name__ == "__main__":
    asyncio.run(test_all_topics())
