from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routes import router as auth_router

app = FastAPI(title="Ganithamithura Auth Service")

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
