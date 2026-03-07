import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb+srv://nethmi:nethmi@itpm.nbiremo.mongodb.net/")
    db = client["ganithmithura"]
    col = db["ganithamithura"]
    
    users = await col.find({}).to_list(length=100)
    print(f"Found {len(users)} users.")
    for u in users:
        print(f"Email: {u.get('email')}, Name: {u.get('name')}, Pass: {u.get('password')[:15]}...")

asyncio.run(main())
