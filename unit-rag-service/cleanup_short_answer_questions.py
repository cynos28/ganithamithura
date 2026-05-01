"""
Clean up short_answer questions from database
Only keep MCQ and true_false questions for Flutter UI compatibility
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def cleanup_questions():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb+srv://shehancynos:1234@unitrag.svzpsnc.mongodb.net/")
    db = client["ganithamithura_rag"]
    questions_collection = db["questions"]
    
    # Find short_answer questions
    short_answer_questions = await questions_collection.count_documents(
        {"question_type": "short_answer"}
    )
    
    print(f"📊 Found {short_answer_questions} short_answer questions in database")
    
    if short_answer_questions > 0:
        # Delete them
        result = await questions_collection.delete_many(
            {"question_type": "short_answer"}
        )
        print(f"🗑️  Deleted {result.deleted_count} short_answer questions")
    else:
        print("✅ No short_answer questions to delete")
    
    # Show remaining questions by type
    pipeline = [
        {
            "$group": {
                "_id": "$question_type",
                "count": {"$sum": 1}
            }
        }
    ]
    
    question_types = await questions_collection.aggregate(pipeline).to_list(None)
    
    print("\n📈 Questions by type:")
    for qt in question_types:
        print(f"   {qt['_id']}: {qt['count']} questions")
    
    # Show total
    total = await questions_collection.count_documents({})
    print(f"\n✅ Total questions remaining: {total}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_questions())
