from fastapi import FastAPI
from app.endpoints import endpoints
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Shape Patterns Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to Shape Patterns Backend 🚀"}


app.include_router(endpoints.router)
