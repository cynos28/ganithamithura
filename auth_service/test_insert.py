import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
print(f"Loaded URL: {MONGODB_URL}")

try:
    client = MongoClient(MONGODB_URL)
    db = client["ganithamithura"]
    print("Users currently in DB:")
    for user in db["users"].find({}):
        print(f"- {user.get('email', 'No email')}")
except Exception as e:
    print(f"Error: {e}")

