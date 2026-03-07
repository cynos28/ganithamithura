from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import certifi

async def main():
    client = AsyncIOMotorClient("mongodb+srv://nethmi:nethmi@itpm.nbiremo.mongodb.net/", tlsCAFile=certifi.where())
    db = client["ganithamithura"]
    
    # Check leaderboard
    scores = await db["leaderboard"].find().to_list(length=10)
    for s in scores:
        print(f"Before reset: {s['user_id']} -> {s.get('score', 0)}")
        
    # Reset all scores to 0
    result = await db["leaderboard"].update_many({}, {"$set": {"score": 0}})
    print(f"Reset {result.modified_count} scores to 0.")

if __name__ == "__main__":
    asyncio.run(main())
