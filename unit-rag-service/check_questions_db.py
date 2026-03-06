#!/usr/bin/env python3
"""
Quick script to check what questions exist in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    # Connect to MongoDB
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI') or os.getenv('MONGODB_URL'))
    db = client[os.getenv('MONGODB_DB_NAME', 'ganithamithura_rag')]
    questions_col = db['questions']
    
    # Get total count
    total = await questions_col.count_documents({})
    print(f"\n{'='*60}")
    print(f"📊 QUESTIONS DATABASE STATUS")
    print(f"{'='*60}")
    print(f"Total questions in database: {total}")
    
    if total == 0:
        print("\n❌ NO QUESTIONS FOUND IN DATABASE!")
        print("\n💡 To fix this:")
        print("   1. Upload curriculum documents via:")
        print("      POST http://localhost:8000/api/v1/upload/")
        print("   2. The system will auto-generate adaptive questions")
        print("   3. Questions will be stored with unit_id format: 'unit_<topic>_<grade>'")
        print("\n📄 Example document upload:")
        print("   - File: PDF/DOCX with length curriculum content")
        print("   - Topic: 'Length'")
        print("   - Grade levels: '1,2,3,4'")
        print("   - Result: Generates questions with unit_id='unit_length_1', etc.")
        print(f"{'='*60}\n")
        client.close()
        return
    
    # Get breakdown by unit_id
    print(f"\n📚 Questions by unit_id:")
    by_unit = await questions_col.aggregate([
        {'$group': {
            '_id': '$unit_id', 
            'count': {'$sum': 1},
            'difficulties': {'$addToSet': '$difficulty_level'},
            'topics': {'$addToSet': '$topic'}
        }},
        {'$sort': {'count': -1}}
    ]).to_list(None)
    
    for item in by_unit:
        unit_id = item['_id'] or '(no unit_id)'
        count = item['count']
        difficulties = sorted(item['difficulties']) if item['difficulties'] else []
        topics = item.get('topics', [])
        print(f"   {unit_id:30} → {count:3} questions (difficulties: {difficulties}, topics: {topics})")
    
    # Get breakdown by topic
    print(f"\n🎯 Questions by topic:")
    by_topic = await questions_col.aggregate([
        {'$group': {'_id': '$topic', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]).to_list(None)
    
    for item in by_topic:
        topic = item['_id'] or '(no topic)'
        print(f"   {topic:20} → {item['count']} questions")
    
    # Sample some questions
    print(f"\n📝 Sample questions:")
    sample = await questions_col.find().limit(5).to_list(5)
    for i, q in enumerate(sample, 1):
        print(f"\n   Question {i}:")
        print(f"      Text: {q.get('question_text', 'N/A')[:80]}...")
        print(f"      Unit ID: {q.get('unit_id', 'N/A')}")
        print(f"      Topic: {q.get('topic', 'N/A')}")
        print(f"      Grade: {q.get('grade_level', 'N/A')}")
        print(f"      Difficulty: {q.get('difficulty_level', 'N/A')}")
    
    print(f"\n{'='*60}\n")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
