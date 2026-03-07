from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import certifi

async def main():
    client = AsyncIOMotorClient("mongodb+srv://admin:admin123@ganithamithura.79etlwh.mongodb.net/", tlsCAFile=certifi.where())
    db = client["ganithamithura"]
    cols = await db.list_collection_names()
    print("Cols:", cols)
    for c in cols:
        count = await db[c].count_documents({})
        print(f"--- {c} ({count} docs) ---")
        if count > 0:
            docs = await db[c].find().to_list(20)
            for d in docs:
                print(d)

asyncio.run(main())
