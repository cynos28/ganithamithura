import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

# Connect to the MongoDB cluster provided by the user
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://nethmi:nethmi@itpm.nbiremo.mongodb.net/")

client = AsyncIOMotorClient(MONGODB_URL, tlsCAFile=certifi.where())
database = client["ganithamithura"]
users_collection = database["users"]

async def get_database():
    return database
