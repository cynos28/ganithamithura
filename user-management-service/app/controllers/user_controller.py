
from common.database.database import get_database
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from authentication_service.auth_service import create_access_token, verify_password, get_password_hash
from datetime import timedelta
from app.models.model import UserCreate


class UserController:
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db["users"]
        self.router = APIRouter()
        self.router.add_api_route("/users/register", self.register, methods=["POST"])
        self.router.add_api_route("/users/login", self.login, methods=["POST"])

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        """
        Authenticates a user and provides a JWT access token.

        Args:
            form_data: The user's login credentials (username and password) from a form.

        Raises:
            HTTPException: 401 if the username or password is incorrect.

        Returns:
            A dictionary containing the access token and token type ("bearer").
        """
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
        """
        Registers a new user in the database.

        Args:
            user_data: The data for the new user, including username and password.

        Raises:
            HTTPException: 400 if the username is already registered.

        Returns:
            A confirmation message indicating successful user creation.
        """
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

user_controller = UserController()
