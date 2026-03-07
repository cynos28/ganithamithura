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

## Connecting the Flutter App

To allow the Flutter App running on a physical device to connect to this backend, you must configure the central IP address in the frontend codebase.

1. **Find your computer's local IP address**
   - **macOS**: Open Terminal and run: `ifconfig | grep "inet " | grep -v 127.0.0.1` (Look for the `192.168.x.x` or `10.x.x.x` address)
   - **Windows**: Open Command Prompt and run: `ipconfig` (Look for "IPv4 Address")

2. **Update the Flutter App**
   - Open the `gmfrontend/lib/services/api/io_config.dart` file in the Flutter project.
   - Change the `symIp` constant to your local IP address:
     ```dart
     static const String symIp = '192.168.8.x'; // Replace with your IP
     ```

3. **Restart the Flutter App**
   - Note: A hot reload (`r`) will not work because the IP is cached on startup. You must **Hot Restart** (`R`) or completely stop and run `flutter run` again.
   - **Important**: Your computer and your mobile device MUST be connected to the exact same Wi-Fi network.

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
