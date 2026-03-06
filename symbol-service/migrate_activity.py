import sys
import os
from datetime import datetime
from pymongo import MongoClient

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.database.mongodb_connection import get_database

def migrate():
    db = get_database()
    if db is None:
        print("Database not connected")
        return
        
    perf_col = db["sym_performance"]
    game_col = db["sym_game_scores"]
    act_col = db["sym_activity"]
    
    print("Migrating performances...")
    for p in perf_col.find({}):
        # check if already migrated
        act = {
            "user_id": p.get("user_id"),
            "activity_type": "learning",
            "level": p.get("level", 1),
            "sublevel": p.get("sublevel", "Starter"),
            "score": p.get("score_percentage", p.get("score", 0)),
            "timestamp": p.get("timestamp", datetime.utcnow())
        }
        act_col.insert_one(act)
        
    print("Migrating games...")
    for g in game_col.find({}):
        act = {
            "user_id": g.get("user_id"),
            "activity_type": "gaming",
            "game_name": g.get("game_name", "Game"),
            "level": g.get("level", 1),
            "score": g.get("score", 0),
            "timestamp": g.get("timestamp", datetime.utcnow())
        }
        act_col.insert_one(act)
        
    print(f"Migration complete. Total activities in sym_activity: {act_col.count_documents({})}")

if __name__ == "__main__":
    migrate()
