# Shape Service

The Shape Service provides API endpoints for shape detection as part of the Ganithamithura project.

## Quick Start

### 1. Requirements
Ensure you have Python 3.12 (or compatible) installed.

### 2. Set Up Virtual Environment
Create and activate a virtual environment:
```bash
python3 -m venv .venv

# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
Install all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the `shape_service` directory with the following variables:
```env
MONGODB_URL=mongodb+srv://<username>:<password>@cluster/
DB_NAME=<database_name>
```

### 5. Start the Service
You can run the service directly or using the provided startup script (on macOS/Linux).

#### Option A: Using Uvicorn (Universal)
```bash
uvicorn app.main:app --port 8003 --reload
```

#### Option B: Using the Bash Script (macOS / Linux)
```bash
bash start_mac.sh
```

#### Option C: Using PowerShell (Windows)
```powershell
.\start_service.ps1
```

Once running, the service will be accessible at: `http://localhost:8003`

### 6. Testing the Model
To verify that the model is working and correctly detecting shapes, run:
```bash
python test_clip_detection.py
```
