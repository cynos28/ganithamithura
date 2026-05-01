"""
Test script for image-based question generation
"""
import asyncio
import sys
from pathlib import Path

# Add app to path  
sys.path.insert(0, str(Path(__file__).parent))

from app.services.image_question_generator import image_question_generator
from app.config import settings


async def test_image_generation():
    """Test generating questions from measurement images"""
    
    print("="*70)
    print("🧪 Testing Image Question Generator")
    print("="*70)
    
    # Test configuration
    topic = "length"
    grade_level = 2
    num_questions = 2
    
    print(f"\n📋 Test Parameters:")
    print(f"   Topic: {topic}")
    print(f"   Grade: {grade_level}")
    print(f"   Questions: {num_questions}")
    
    # Check for available images
    print(f"\n🔍 Checking for images...")
    available_images = image_question_generator._get_available_images(topic)
    print(f"   Found {len(available_images)} images in {topic}/ folder")
    
    if not available_images:
        print("   ❌ No images found!")
        return
    
    for img in available_images[:5]:
        print(f"   - {img.name}")
    
    # Test question generation
    print(f"\n📸 Generating questions from images...")
    try:
        questions = await image_question_generator.generate_image_based_questions(
            topic=topic,
            grade_level=grade_level,
            total_questions=num_questions,
            document_context="Students should learn to compare lengths of different objects."
        )
        
        print(f"\n✅ Generated {len(questions)} questions!")
        print("="*70)
        
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}:")
            print(f"  Text: {q.get('question_text')}")
            print(f"  Type: {q.get('question_type')}")
            print(f"  Image: {q.get('image_url', 'NO IMAGE')}")
            print(f"  Options: {q.get('options')}")
            print(f"  Answer: {q.get('correct_answer')}")
            print(f"  Explanation: {q.get('explanation')}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_image_generation())
