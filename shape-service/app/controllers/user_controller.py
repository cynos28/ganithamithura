from database.database import get_database
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import create_access_token, verify_password, get_password_hash
from datetime import timedelta
from app.models.model import UserCreate


class UserController:
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db["users"]

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        user = await self.users_collection.find_one({"user_name": form_data.username})
        if not user or not verify_password(form_data.password, user["password"]):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user["user_name"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    async def register(self, user_data: UserCreate):
        user = await self.users_collection.find_one({"user_name": user_data.username})
        if user:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = get_password_hash(user_data.password)
        new_user = {
            "user_name": user_data.username,
            "password": hashed_password,
            "game_status": "not_attempt",
        }
        await self.users_collection.insert_one(new_user)
        return {"message": "User created successfully"}
