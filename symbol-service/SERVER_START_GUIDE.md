# Symbol Hunter Server - Startup Guide

This guide explains how to start the Python backend server for the Symbol Hunter application.

## Prerequisites

Ensure you are in the `ganithamithura/symbol-service` directory.

## Step 1: Activate Virtual Environment

Before running the server, you must activate the Python virtual environment.

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
.\venv\Scripts\activate
```

## Step 2: Run the Server

Use `uvicorn` to start the FastAPI server.

**Development Mode (Auto-Reloading):**
Use this command during development. The server will restart automatically when you change code.
```bash
symboleservice directry :  e.g ganithamithura/symbol-service %
uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
```

**Production/Stable Mode:**
Use this command for a stable run without auto-reloading.
```bash
uvicorn src.server:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Error: `[Errno 48] Address already in use`
This means another process is already running on port 8000. To fix this:

1.  **Kill the process occupying the port (Mac/Linux):**
    ```bash
    lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
    ```

2.  **Restart the server:**
    ```bash
    uvicorn src.server:app --host 0.0.0.0 --port 8000 --reload
    ```

### Error: `ModuleNotFoundError` or `directory not found`
Ensure you are running the command from the **root** `symbol-service` directory, NOT inside `src/` or `src/components/`.
```bash
cd /path/to/ganithamithura/symbol-service
```
