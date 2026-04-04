from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson.objectid import ObjectId

# Import database connection dependencies
from src.database.mongodb_connection import get_collection, get_database

router = APIRouter()

class CharacterUpdate(BaseModel):
    character_name: str

class ScoreUpdate(BaseModel):
    game_name: str
    score: int
    level: int = 1

@router.post("/api/users/{user_id}/character")
async def save_character(user_id: str, char_data: CharacterUpdate):
    collection = get_collection("user_profiles")
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    collection.update_one(
        {"user_id": user_id},
        {"$set": {
            "character_name": char_data.character_name, 
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )
    return {"status": "success", "character_name": char_data.character_name}

@router.get("/api/users/{user_id}/character")
async def get_character(user_id: str):
    collection = get_collection("user_profiles")
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    user = collection.find_one({"user_id": user_id})
    if user and "character_name" in user:
        return {"character_name": user["character_name"]}
    else:
        raise HTTPException(status_code=404, detail="Character not found")

@router.post("/api/users/{user_id}/scores")
async def save_score(user_id: str, score_data: ScoreUpdate):
    collection = get_collection("sym_game_scores")
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    collection.update_one(
        {"user_id": user_id, "game_name": score_data.game_name},
        {
            "$inc": {"score": score_data.score},
            "$max": {"level": score_data.level},
            "$set": {"timestamp": datetime.utcnow()}
        },
        upsert=True
    )
    
    # Store into unified activity collection
    activity_col = get_collection("sym_activity")
    if activity_col is not None:
        activity_col.insert_one({
            "user_id": user_id,
            "activity_type": "gaming",
            "game_name": score_data.game_name,
            "level": score_data.level,
            "score": score_data.score,
            "timestamp": datetime.utcnow()
        })
        
    return {"status": "success", "score": score_data.score}

@router.get("/api/game/leaderboard")
async def get_leaderboard():
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    scores_collection = db["sym_game_scores"]
    users_collection = db["users"]
    profiles_collection = db["user_profiles"]
    
    # Group by user_id to only show each user's best score
    pipeline = [
        {"$sort": {"score": -1}},
        {"$group": {
            "_id": "$user_id",
            "score": {"$max": "$score"},
            "level": {"$first": "$level"}
        }},
        {"$sort": {"score": -1}},
        {"$limit": 10}
    ]
    
    top_scores = list(scores_collection.aggregate(pipeline))
    leaderboard = []
    
    for item in top_scores:
        user_id_str = item["_id"]
        if not user_id_str:
            continue
            
        user_name = "Unknown Player"
        try:
            if len(user_id_str) == 24: # Check if it might be a valid ObjectId
                user = users_collection.find_one({"_id": ObjectId(user_id_str)})
                if user and "name" in user:
                    user_name = user["name"]
        except Exception:
            pass
            
        char_name = "Cat"
        profile = profiles_collection.find_one({"user_id": user_id_str})
        if profile and "character_name" in profile:
            char_name = profile["character_name"]
            
        leaderboard.append({
            "user_id": user_id_str,
            "name": user_name,
            "character_name": char_name,
            "score": item["score"],
            "level": item["level"]
        })
        
    return {"leaderboard": leaderboard}
