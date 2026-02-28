from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from database import get_database

load_dotenv()

from routes import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database collections if they don't exist
    db = await get_database()
    collections = await db.list_collection_names()
    if "users" not in collections:
        await db.create_collection("users")
        print("Initialized 'users' collection in MongoDB.")
    yield

app = FastAPI(title="Ganithamithura Auth Service", lifespan=lifespan)

# Allow CORS for flutter app and other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ganithamithura Auth Service"}

# Run with: uvicorn main:app --reload --port 8001
