import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DB_NAME]

def get_database():
    return database
