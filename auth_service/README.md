# Ganithamithura Auth Service

This is the standalone Authentication Microservice for the Ganithamithura project. It handles user registration and login securely using FastAPI, Motor (Async MongoDB), and JWTs.

## Tech Stack
- **Framework**: FastAPI
- **Database**: MongoDB (via `motor`)
- **Security**: Argon2 for password hashing, python-jose for JWT

## Prerequisites
- Python 3.9+ installed on your system.

## Setup Instructions

### 1. Create a Virtual Environment
It is highly recommended to use a virtual environment to keep dependencies isolated.
Navigate to the `auth_service` directory and run:

```bash
python -m venv .venv
```

### 2. Activate the Virtual Environment
- **On macOS/Linux**:
  ```bash
  source .venv/bin/activate
  ```
- **On Windows**:
  ```bash
  .venv\Scripts\activate
  ```

### 3. Install Dependencies
Once the virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
1. Create a `.env` file in the `auth_service` directory if it does not already exist.
2. Add your MongoDB connection string to the `.env` file:

```env
MONGODB_URL=mongodb+srv://<username>:<password>@cluster/
```
*(Note: Replace the URL with your actual MongoDB connection string)*

## Running the Server

Make sure your virtual environment is activated. Run the FastAPI development server using `uvicorn`:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

The server will start on `http://0.0.0.0:8001`.

## API Endpoints

### `POST /api/auth/signup`
Creates a new user account.
**Request Body (JSON)**:
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "strongpassword123",
  "grade": 2
}
```

### `POST /api/auth/signin`
Logs in an existing user.
**Request Body (JSON)**:
```json
{
  "email": "jane@example.com",
  "password": "strongpassword123"
}
```

Both endpoints return the user's details and a JWT `token` upon success.

### Logout Process (Client-Side)
Because this backend uses **stateless JSON Web Tokens (JWT)** for authentication, there is no explicit `/api/auth/logout` endpoint required on the backend. 

To log a user out:
1. The client (Flutter frontend) simply deletes the saved JWT token from its local Secure Storage.
2. The user is redirected to the Sign In screen.
3. The old token becomes useless on the client, effectively "logging them out".
