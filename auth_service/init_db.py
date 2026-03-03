from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    print("No URL found")
else:
    client = MongoClient(MONGODB_URL)
    db = client.ganithmithura
    
    for coll in ["users", "game_scores", "user_profiles"]:
        if coll not in db.list_collection_names():
            db.create_collection(coll)
            print(f"Created collection: {coll}")
        else:
            print(f"Collection already exists: {coll}")
