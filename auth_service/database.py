import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Connect to the local MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "shapes_and_patterns2")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DB_NAME]
users_collection = database["users"]

print(users_collection)

async def get_database():
    return database
