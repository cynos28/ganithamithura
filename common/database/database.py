
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL environment variable is required")
if not DB_NAME:
    raise ValueError("DB_NAME environment variable is required")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DB_NAME]

def get_database():
    return database
