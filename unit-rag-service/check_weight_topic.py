import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_weight():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ganitha_mithura_rag']
    
    # Find a sample Weight question
    weight_q = await db.questions.find_one({'topic': {'$regex': 'weight', '$options': 'i'}})
    
    if weight_q:
        print(f"Sample Weight Question:")
        print(f"  ID: {weight_q['_id']}")
        print(f"  Topic: '{weight_q.get('topic')}'")
        print(f"  Unit ID: '{weight_q.get('unit_id')}'")
        print(f"  Grade: {weight_q.get('grade_level')}")
        print(f"  Question: {weight_q.get('question_text')[:80]}...")
        print(f"  Image: {weight_q.get('image_url')}")
    
    # Count by exact topic
    weight_capital = await db.questions.count_documents({'topic': 'Weight'})
    weight_lower = await db.questions.count_documents({'topic': 'weight'})
    
    print(f"\nQuestion counts:")
    print(f"  'Weight' (capital): {weight_capital}")
    print(f"  'weight' (lowercase): {weight_lower}")
    
    client.close()

asyncio.run(check_weight())
