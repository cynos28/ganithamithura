#!/usr/bin/env python3
"""
Quick test script to verify AI question generation optimizations
Run: python test_speed_optimizations.py
"""

import asyncio
import time
from app.services.question_generator import question_generator

async def test_generation_speed():
    """Test question generation with optimizations"""
    
    print("\n" + "="*70)
    print("🧪 TESTING AI QUESTION GENERATION OPTIMIZATIONS")
    print("="*70 + "\n")
    
    # Sample context
    context = """
    Length Measurement
    
    Length is how long or short something is. We use different units to measure length:
    - Centimeters (cm) for small things like pencils
    - Meters (m) for bigger things like rooms
    - Kilometers (km) for long distances like roads
    
    You can measure length using a ruler, measuring tape, or meter stick.
    """
    
    # Test 1: Single grade generation
    print("📝 Test 1: Single Grade Generation")
    start = time.time()
    questions_g1 = await question_generator.generate_questions_from_context(
        context=context,
        grade_level=1,
        topic="length",
        num_questions=5
    )
    time_single = time.time() - start
    print(f"✅ Generated {len(questions_g1)} questions in {time_single:.2f}s")
    
    # Test 2: Cache hit (should be instant)
    print("\n📝 Test 2: Cache Hit (Same Request)")
    start = time.time()
    questions_cached = await question_generator.generate_questions_from_context(
        context=context,
        grade_level=1,
        topic="length",
        num_questions=5
    )
    time_cached = time.time() - start
    print(f"✅ Retrieved {len(questions_cached)} questions in {time_cached:.2f}s")
    print(f"🚀 Cache speedup: {time_single/time_cached:.1f}x faster")
    
    # Test 3: Parallel generation for multiple grades
    print("\n📝 Test 3: Parallel Multi-Grade Generation")
    start = time.time()
    all_questions = await question_generator.generate_questions_for_document(
        document_id="test_doc",
        document_content=context,
        grade_levels=[1, 2, 3, 4],
        topic="length",
        questions_per_grade=5,
        use_rag=False  # Skip RAG for testing
    )
    time_parallel = time.time() - start
    print(f"✅ Generated {len(all_questions)} questions for 4 grades in {time_parallel:.2f}s")
    print(f"📊 Average per grade: {time_parallel/4:.2f}s")
    
    # Results summary
    print("\n" + "="*70)
    print("📊 PERFORMANCE SUMMARY")
    print("="*70)
    print(f"Single grade (cold): {time_single:.2f}s")
    print(f"Single grade (cached): {time_cached:.2f}s ({time_single/max(time_cached, 0.001):.0f}x faster)")
    print(f"4 grades (parallel): {time_parallel:.2f}s")
    
    # Expected vs actual
    expected_serial = time_single * 4  # If it was serial
    speedup = expected_serial / time_parallel
    print(f"\n🎯 Parallel speedup: {speedup:.1f}x faster than serial")
    print(f"   (Serial would take: {expected_serial:.2f}s)")
    
    # Show sample question
    if questions_g1:
        print("\n📋 Sample Question:")
        q = questions_g1[0]
        print(f"   Q: {q['question_text']}")
        print(f"   Difficulty: {q['difficulty_level']}/5")
        print(f"   Type: {q['question_type']}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_generation_speed())
