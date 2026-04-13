import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_volume_questions():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['ganitha_mithura_rag']
    
    # Check all volume questions
    volume_questions = await db.questions.count_documents({'topic': {'$regex': 'volume', '$options': 'i'}})
    print(f'📊 Total Volume questions in database: {volume_questions}')
    
    # Check by grade
    for grade in [1, 2, 3, 4]:
        count = await db.questions.count_documents({
            'topic': {'$regex': 'volume', '$options': 'i'},
            'grade_level': grade
        })
        with_images = await db.questions.count_documents({
            'topic': {'$regex': 'volume', '$options': 'i'},
            'grade_level': grade,
            'image_url': {'$ne': None, '$exists': True, '$ne': ''}
        })
        print(f'   Grade {grade}: {count} total, {with_images} with images')
    
    # Check Volume documents
    volume_docs = await db.documents.find({'topic': {'$regex': 'volume', '$options': 'i'}}).to_list(None)
    print(f'\n📄 Volume documents: {len(volume_docs)}')
    for doc in volume_docs:
        print(f'   - {doc["title"]} (ID: {doc["_id"]}, Questions: {doc.get("questions_count", 0)})')
    
    client.close()

asyncio.run(check_volume_questions())
