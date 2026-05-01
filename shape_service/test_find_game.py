import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

urls = [
    "mongodb+srv://nethmi:nethmi@itpm.nbiremo.mongodb.net/",
    "mongodb+srv://admin:admin123@ganithamithura.79etlwh.mongodb.net/",
    "mongodb+srv://sathsarasithumb:Kavishka@cluster0.z5wsh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    "mongodb+srv://shehancynos:1234@unitrag.svzpsnc.mongodb.net/"
]

async def check():
    for url in urls:
        print(f"Checking {url}")
        try:
            client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=2000)
            db = client['ganithamithura']
            doc = await db['games'].find_one({"level": 1})
            if doc:
                print(f"FOUND in {url} -> ganithamithura")
                return
            db2 = client['ganithamithura_rag']
            doc2 = await db2['games'].find_one({"level": 1})
            if doc2:
                print(f"FOUND in {url} -> ganithamithura_rag")
                return
        except Exception as e:
            print(f"Failed: {e}")

asyncio.run(check())
