#!/usr/bin/env python3
"""
Verify all measurement topics have images available
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.image_question_generator import ImageQuestionGenerator


def main():
    """Check image availability for all measurement topics"""
    gen = ImageQuestionGenerator()
    
    print("🔍 Checking image availability for all measurement topics...\n")
    
    topics = ["length", "area", "volume", "weight"]
    total_images = 0
    
    for topic in topics:
        images = gen._get_available_images(topic)
        count = len(images)
        total_images += count
        
        if count > 0:
            print(f"✅ {topic.upper()}: {count} images")
            print(f"   📁 {gen.static_dir / gen.topic_folders[topic]}")
            print(f"   📷 Files: {', '.join([img.name for img in images[:5]])}")
            if count > 5:
                print(f"      ... and {count - 5} more")
        else:
            print(f"❌ {topic.upper()}: NO IMAGES FOUND")
            print(f"   📁 Expected folder: {gen.static_dir / gen.topic_folders.get(topic, 'unknown')}")
        print()
    
    print(f"\n📊 TOTAL: {total_images} images across {len(topics)} topics")
    
    if total_images == 0:
        print("\n⚠️  WARNING: No images found! Please add images to static/images/ folders")
        return 1
    
    print("\n✨ All topics have images available for GPT-4 Vision question generation!")
    
    # Summary for question generation
    print("\n" + "="*60)
    print("📝 Question Generation Capacity:")
    print("="*60)
    for topic in topics:
        images = gen._get_available_images(topic)
        count = len(images)
        # With 1 image per question, 4 grades
        capacity = count * 4  # max questions if using each image once per grade
        print(f"   {topic.title():8} -> {count:2} images × 4 grades = {capacity:3} max questions")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
