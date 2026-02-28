from common.database.database import get_database
from fastapi import APIRouter, HTTPException, Depends, Response
from authentication_service.auth_service import create_access_token, verify_password, get_password_hash
from datetime import timedelta
from models.model import UserCreate, UserLogin


class UserController:
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db["users"]
        self.router = APIRouter()
        self.router.add_api_route("/users/register", self.register, methods=["POST"])
        self.router.add_api_route("/users/login", self.login, methods=["POST"])

    async def login(self, response: Response, user_data: UserLogin):
        """
        Authenticates a user, returns JSON with token, and sets a JWT access token in an HttpOnly cookie.
        """
        user = await self.users_collection.find_one({"email": user_data.email})
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
        
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            samesite="lax",
            secure=False,  # Set to True in production with HTTPS
            max_age=7200, # 2 hours
        )
        
        # Prepare user dict to return to frontend (excluding password)
        user_response = {
            "id": str(user["_id"]),
            "name": user.get("name", ""),
            "email": user["email"],
        }
        
        return {
            "success": True,
            "message": "Login successful",
            "token": access_token,
            "user": user_response
        }

    async def register(self, user_data: UserCreate, response: Response):
        """
        Registers a new user in the database, automatically logs them in, and returns JSON.
        """
        user = await self.users_collection.find_one({"email": user_data.email})
        if user:
            return {
                "success": False,
                "message": "Email already registered",
                "user": None,
                "token": None
            }

        hashed_password = get_password_hash(user_data.password)
        new_user = {
            "name": user_data.name,
            "email": user_data.email,
            "password": hashed_password,
            "game_status": "not_attempt",
        }
        
        insert_result = await self.users_collection.insert_one(new_user)
        
        # Automatically login after signup
        access_token_expires = timedelta(minutes=120)
        access_token = create_access_token(
            data={"sub": user_data.email}, expires_delta=access_token_expires
        )
        
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=7200,
        )
        
        # Prepare user dict to return to frontend
        user_response = {
            "id": str(insert_result.inserted_id),
            "name": user_data.name,
            "email": user_data.email,
        }
        
        return {
            "success": True,
            "message": "User created successfully",
            "token": access_token,
            "user": user_response
        }

user_controller = UserController()
