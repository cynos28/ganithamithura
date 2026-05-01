#!/usr/bin/env python3
"""
Check student answers to see if questions are being reused
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
    answers_col = db['student_answers']
    
    # Get total count
    total = await answers_col.count_documents({})
    print(f"\n{'='*60}")
    print(f"📊 STUDENT ANSWERS STATUS")
    print(f"{'='*60}")
    print(f"Total answers recorded: {total}")
    
    # Get breakdown by student
    by_student = await answers_col.aggregate([
        {'$group': {
            '_id': '$student_id', 
            'count': {'$sum': 1},
            'units': {'$addToSet': '$unit_id'},
            'unique_questions': {'$addToSet': '$question_id'}
        }},
        {'$sort': {'count': -1}}
    ]).to_list(None)
    
    print(f"\n👤 Answers by student:")
    for item in by_student:
        student = item['_id']
        count = item['count']
        unique = len(item['unique_questions'])
        units = item['units']
        print(f"   {student:30} → {count} answers ({unique} unique questions)")
        print(f"      Units: {units}")
    
    # Check for duplicate question answers (same question answered multiple times)
    print(f"\n🔄 Checking for repeated questions...")
    duplicate_check = await answers_col.aggregate([
        {'$group': {
            '_id': {'student_id': '$student_id', 'question_id': '$question_id'},
            'count': {'$sum': 1}
        }},
        {'$match': {'count': {'$gt': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 10}
    ]).to_list(None)
    
    if duplicate_check:
        print(f"   Found {len(duplicate_check)} questions answered multiple times:")
        for dup in duplicate_check[:5]:
            print(f"      Student {dup['_id']['student_id']} answered question {dup['_id']['question_id']} {dup['count']} times")
    else:
        print(f"   ✅ No duplicate answers found - each question answered once")
    
    # Check recent answers
    print(f"\n📝 Most recent 5 answers:")
    recent = await answers_col.find().sort('answered_at', -1).limit(5).to_list(5)
    for ans in recent:
        print(f"   Student: {ans['student_id']}")
        print(f"   Unit: {ans['unit_id']}")
        print(f"   Question: {str(ans['question_id'])[:24]}...")
        print(f"   Correct: {ans['is_correct']}")
        print(f"   Time: {ans.get('answered_at', 'N/A')}")
        print()
    
    print(f"{'='*60}\n")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
