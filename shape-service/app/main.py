import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import FastAPI
from app.endpoints import endpoints
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Shape Patterns Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

app.include_router(endpoints.router, prefix="/shapes-patterns")

@app.get("/")
async def root():
    return {"message": "Welcome to Shape Patterns Backend 🚀"}
