import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.user_controller import user_controller

app = FastAPI(title="User Management Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_controller.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the User Management Service"}
