import asyncio
import os
from dotenv import load_dotenv
from database import get_database

load_dotenv()

async def run():
    db = await get_database()
    print(f"Connected to DB name: {db.name}")
    count = await db["users"].count_documents({})
    print(f"Users in collection 'users': {count}")
    
    # Let's see what happens if we insert one
    res = await db["users"].insert_one({"email": "test3@test.com"})
    print(f"Inserted dummy user with id: {res.inserted_id}")
    
    count2 = await db["users"].count_documents({})
    print(f"Users in collection 'users' after insert: {count2}")

asyncio.run(run())
