# 🚀 Unit RAG Service - Complete Setup Guide

## Step-by-Step Installation

### Step 1: System Requirements

Ensure you have:
- ✅ Python 3.9 or higher
- ✅ MongoDB 7.0 or higher (or MongoDB Atlas account)
- ✅ OpenAI API key (for GPT-4)
- ✅ At least 2GB free disk space

📖 **For detailed MongoDB installation, see [MONGODB_SETUP.md](./MONGODB_SETUP.md)**

### Step 2: Install MongoDB

**On macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0
```

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

**On Windows:**
Download from https://www.mongodb.com/try/download/community

**Or use MongoDB Atlas (Cloud):**
- Free tier available at https://www.mongodb.com/cloud/atlas
- No installation needed!

### Step 3: Verify MongoDB

### Step 3: Verify MongoDB

```bash
# Check MongoDB is running
brew services list | grep mongodb  # macOS
sudo systemctl status mongod       # Linux

# Connect to MongoDB
mongosh

# You should see:
# test> 
# (This means MongoDB is ready!)

# Exit
exit
```

**Note:** MongoDB creates databases automatically - no manual setup needed!

### Step 4: Clone and Setup Python Environment

```bash
# Navigate to project
cd unit-rag-service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

**Required Configuration:**

```env
# OpenAI - GET YOUR KEY FROM: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# MongoDB (Local)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ganithamithura_rag

# Or MongoDB Atlas (Cloud)
# MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
# MONGODB_DB_NAME=ganithamithura_rag

# Server (defaults are fine for development)
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS (add your frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Step 6: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.9+

# Check PostgreSQL
psql -V

# Check if packages installed
pip list | grep fastapi
pip list | grep langchain
pip list | grep chromadb
```

### Step 7: Initialize Database

MongoDB databases and collections are created automatically when you first use them!  
Just start the server and it will initialize everything.

```bash
# No manual database setup needed!
# Collections will be created on first document upload
```

### Step 8: Start the Server

```bash
# Start the development server
python -m app.main

# You should see:
# ✅ Database initialized
# ✅ Server running on 0.0.0.0:8000
# ✅ Environment: development
# ✅ Docs available at: http://0.0.0.0:8000/docs
```

### Step 9: Test the API

Open your browser and go to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

Or use curl:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "vector_store": {
    "total_chunks": 0,
    "collection_name": "ganithamithura_documents"
  }
}
```

## 🧪 Testing the System

### Test 1: Upload a Document

Create a test file `test.txt`:
```txt
Introduction to Measurements

A meter is a unit of length. One meter equals 100 centimeters.
A centimeter is smaller than a meter. We use centimeters to measure small things like pencils.

Example: A ruler is usually 30 centimeters long.
```

Upload using curl:
```bash
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -H "accept: application/json" \
  -F "file=@test.txt" \
  -F "title=Test Measurements" \
  -F "grade_levels=1,2,3" \
  -F "topic=measurements" \
  -F "uploaded_by=teacher_test"
```

### Test 2: Generate Questions

```bash
curl -X POST "http://localhost:8000/api/v1/questions/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "grade_levels": [1, 2, 3],
    "questions_per_grade": 5,
    "question_types": ["mcq", "short_answer"]
  }'
```

Wait 1-2 minutes for questions to generate, then check:

```bash
curl "http://localhost:8000/api/v1/questions/document/1"
```

### Test 3: Get Adaptive Question

```bash
curl "http://localhost:8000/api/v1/adaptive/next-question?student_id=test_student&unit_id=1&grade_level=2"
```

### Test 4: Submit Answer

```bash
curl -X POST "http://localhost:8000/api/v1/adaptive/submit-answer" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "test_student",
    "question_id": 1,
    "answer": "100",
    "time_taken": 15
  }'
```

## 📊 Using the Interactive API Docs

1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response below

## 🔧 Troubleshooting

### Error: "Import Error" when starting

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Error: "Database connection failed"

**Solution:**
```bash
# Check MongoDB is running
brew services list | grep mongodb  # macOS
sudo systemctl status mongod       # Linux

# Start MongoDB
brew services start mongodb-community@7.0  # macOS
sudo systemctl start mongod                # Linux

# Test connection
mongosh
```

### Error: "Could not connect to MongoDB"

**Solution:**
- Check `.env` has correct `MONGODB_URL`
- For local: `mongodb://localhost:27017`
- For Atlas: Get connection string from MongoDB Atlas dashboard
- Ensure MongoDB service is running

### Error: "OpenAI API Error"

**Solution:**
- Verify API key is correct in `.env`
- Check API quota: https://platform.openai.com/usage
- Ensure you have credits/billing set up

### Error: "ChromaDB permission denied"

**Solution:**
```bash
# Create vectorstore directory with proper permissions
mkdir -p vectorstore
chmod 755 vectorstore
```

### Port 8000 already in use

**Solution:**
```bash
# Change port in .env
PORT=8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

## 🔄 Development Workflow

### Making Changes

1. Edit code files
2. Server auto-reloads (if DEBUG=True)
3. Test using /docs or curl
4. Check logs in terminal

### Adding New Features

```bash
# Create new route file
touch app/routes/new_feature.py

# Add to main.py
# from app.routes import new_feature
# app.include_router(new_feature.router)
```

### Database Changes

```bash
# With MongoDB, schema changes are automatic!
# Just modify your models and restart the server

# To view data:
mongosh
use ganithamithura_rag
show collections
db.documents.find().pretty()
db.questions.find().pretty()
```

### View Database with MongoDB Compass

```bash
# Download MongoDB Compass (GUI):
# https://www.mongodb.com/products/compass

# Connect to: mongodb://localhost:27017
# Browse collections visually!
```

## 📦 Production Deployment

### Using MongoDB Atlas (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker (Coming Soon)

```bash
# Build image
docker build -t ganithamithura-rag .

# Run container
docker run -p 8000:8000 --env-file .env ganithamithura-rag
```

## 📈 Monitoring

### View Logs

```bash
# Real-time logs
tail -f logs/app.log

# Or use terminal output when running
python -m app.main
```

### Check Database Stats

```bash
psql -U postgres -d ganithamithura_rag

# Count documents
SELECT COUNT(*) FROM documents;

# Count questions
SELECT COUNT(*) FROM questions;

# View student progress
SELECT * FROM student_ability;
```

## 🆘 Getting Help

1. Check README.md for general info
2. Review API docs at /docs
3. Check error messages in terminal
4. Review code comments
5. Create GitHub issue if needed

## ✅ Success Checklist

- [ ] PostgreSQL installed and running
- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] OpenAI API key added
- [ ] Database created
- [ ] Server starts without errors
- [ ] /health endpoint returns healthy
- [ ] /docs page loads
- [ ] Test upload works
- [ ] Questions generate successfully

## 🎉 You're Ready!

Your RAG service is now running and ready to:
- Accept document uploads from teacher dashboard
- Generate adaptive questions
- Serve questions to Flutter mobile app
- Track student progress and ability

Next steps:
1. Integrate with Teacher Dashboard (Next.js)
2. Update Flutter app to call these APIs
3. Start uploading real educational content!
