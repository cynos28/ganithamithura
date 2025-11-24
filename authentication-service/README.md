# Authentication Service

## Overview

This service provides centralized, token-based authentication for the Ganithamithura project using JSON Web Tokens (JWT). It is designed to be integrated into other microservices that require user authentication.

The service handles:
- Secure password hashing and verification using Argon2.
- Generation and validation of JWT access tokens.
- A reusable FastAPI dependency for protecting endpoints and retrieving the current user.

---

## Prerequisites

Before integrating this service, ensure the following requirements are met:

1.  **Project Structure**: The integrating service must be part of the same parent project that contains the `common` module, where the shared database connection resides.
2.  **Environment Variables**: The following environment variables must be available to the integrating service (e.g., via a `.env` file):
    - `SECRET_KEY`: A strong, unique secret key used for signing JWTs.
    - `MONGODB_URL`: The connection string for your MongoDB instance.
    - `DB_NAME`: The name of the database to use.

---

## How It Works

The authentication flow is as follows:

1.  **Registration**: A user signs up. Their password is not stored in plain text; instead, it is securely hashed using `get_password_hash()`.
2.  **Login**: A user logs in with their username and password. The service verifies their credentials using `verify_password()`.
3.  **Token Generation**: Upon successful login, `create_access_token()` generates a short-lived JWT containing the user's identity.
4.  **Authenticated Requests**: The client application stores this token and sends it in the `Authorization` header for every request to a protected endpoint (e.g., `Authorization: Bearer <token>`).
5.  **Endpoint Protection**: Protected endpoints use the `get_current_user` dependency, which automatically decodes the token, validates its signature and expiration, and fetches the user's details from the database. If the token is invalid or the user doesn't exist, it returns a 401 Unauthorized error.

---

## Integration Guide

Here’s how to integrate the authentication service into another microservice (e.g., `shape-service`).

### Step 1: Ensure Python Path is Correct

For the import system to find the `common` and `authentication_service` modules, the root directory of the project must be in Python's path. You can ensure this by adding the following code to the top of your main application file (e.g., `app/main.py`):

```python
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
```

### Step 2: Implement Registration and Login Endpoints

Your service must provide its own endpoints for user registration and login. These endpoints will use the functions provided by `auth_service.py`. The `shape-service` provides a perfect reference implementation in `app/controllers/user_controller.py`.

**Example: User Registration**

This endpoint hashes the user's password and saves the new user to the database.

```python
# From authentication_service.auth_service import get_password_hash
# From common.database.database import get_database

async def register(user_data: UserCreate):
    db = get_database()
    users_collection = db["users"]
    
    user = await users_collection.find_one({"user_name": user_data.username})
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user_data.password)
    new_user = {
        "user_name": user_data.username,
        "password": hashed_password,
        # ... other fields
    }
    await users_collection.insert_one(new_user)
    return {"message": "User created successfully"}
```

**Example: User Login (Token Generation)**

This endpoint verifies credentials and returns a JWT access token.

```python
# From authentication_service.auth_service import verify_password, create_access_token
# From fastapi.security import OAuth2PasswordRequestForm
# From fastapi import Depends

async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # ... (logic to find user in database)
    user = await self.users_collection.find_one({"user_name": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )
    
    access_token = create_access_token(data={"sub": user["user_name"]})
    return {"access_token": access_token, "token_type": "bearer"}
```

### Step 3: Protect Endpoints

To protect an endpoint, add the `get_current_user` function as a FastAPI dependency. This will ensure that only authenticated users can access the endpoint. The dependency will also provide you with the current user's data.

```python
from fastapi import Depends
from authentication_service.auth_service import get_current_user

@router.get("/profile/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # The code in this endpoint will only execute if the token is valid.
    # The 'current_user' variable will contain the user's document from the database.
    return current_user
```

This setup provides a robust and reusable authentication system for all services in the Ganithamithura project.
