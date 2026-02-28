from fastapi import APIRouter, HTTPException, Depends, Response
from datetime import timedelta
from database import get_database
from models import UserSignup, UserLogin
from auth import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/api/auth/signup")
async def signup(user_data: UserSignup, response: Response):
    db = await get_database()
    users_collection = db["users"]
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        return {
            "success": False,
            "message": "Email already registered",
            "user": None,
            "token": None
        }

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "grade": user_data.grade,
        "game_status": "not_attempt",
        "role": "student"
    }
    
    insert_result = await users_collection.insert_one(new_user)
    
    # Automatically login after signup
    access_token_expires = timedelta(minutes=120)
    access_token = create_access_token(
        data={"sub": user_data.email}, expires_delta=access_token_expires
    )
    
    # Prepare user dict to return to frontend
    user_response = {
        "id": str(insert_result.inserted_id),
        "name": user_data.name,
        "email": user_data.email,
        "grade": user_data.grade,
    }
    
    return {
        "success": True,
        "message": "User created successfully",
        "token": access_token,
        "user": user_response
    }


@router.post("/api/auth/signin")
async def login(user_data: UserLogin, response: Response):
    db = await get_database()
    users_collection = db["users"]
    
    # Check if user exists and verify password
    user = await users_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        return {
            "success": False,
            "message": "Incorrect email or password",
            "user": None,
            "token": None
        }
        
    access_token_expires = timedelta(minutes=120)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Prepare user dict to return to frontend (excluding password)
    user_response = {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user["email"],
        "grade": user.get("grade", 1),
    }
    
    return {
        "success": True,
        "message": "Login successful",
        "token": access_token,
        "user": user_response
    }
