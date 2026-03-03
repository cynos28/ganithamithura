from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import certifi

async def main():
    client = AsyncIOMotorClient("mongodb+srv://nethmi:nethmi@itpm.nbiremo.mongodb.net/", tlsCAFile=certifi.where())
    db = client["ganithamithura"]
    
    # Check all collections
    cols = await db.list_collection_names()
    print("Collections:", cols)
    
    for c in cols:
        count = await db[c].count_documents({})
        print(f"{c}: {count} docs")
        
        if c == 'symbol_scores' or 'score' in c or 'leaderboard' in c:
            docs = await db[c].find().to_list(10)
            print(f"Sample from {c}: {docs}")

if __name__ == "__main__":
    asyncio.run(main())
