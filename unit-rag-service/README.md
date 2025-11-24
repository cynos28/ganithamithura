# Ganithamithura Unit RAG Service

Adaptive learning question generation system using RAG (Retrieval-Augmented Generation) and IRT (Item Response Theory).

## Features

- 📄 **Document Processing**: Upload PDF, DOCX, or TXT files
- 🧠 **RAG-based Question Generation**: Generate grade-appropriate questions using LLM
- 🎯 **Adaptive Learning**: IRT-based algorithm adjusts difficulty in real-time
- 📊 **Analytics**: Track student progress and concept mastery
- 🔄 **Multi-grade Support**: Generate questions for grades 1-4
- 🎓 **Bloom's Taxonomy**: Questions aligned with learning objectives

## Tech Stack

- **FastAPI**: High-performance Python web framework
- **LangChain**: RAG framework
- **ChromaDB**: Vector database for embeddings
- **OpenAI GPT-4**: Question generation
- **MongoDB**: Flexible NoSQL database for documents and progress
- **Beanie ODM**: Async MongoDB ORM for Python
- **Motor**: Async MongoDB driver

## Quick Start

### 1. Prerequisites

- Python 3.9+
- MongoDB 7.0+ (or MongoDB Atlas free tier)
- OpenAI API key

📖 **See [MONGODB_SETUP.md](./MONGODB_SETUP.md) for detailed MongoDB installation**

### 2. Installation

```bash
# Clone the repository
cd unit-rag-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup MongoDB

```bash
# macOS
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Ubuntu/Debian
sudo apt install mongodb-org
sudo systemctl start mongod

# Or use MongoDB Atlas (cloud) - see MONGODB_SETUP.md
```

### 4. Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Required environment variables:
```
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=postgresql://postgres:password@localhost:5432/ganithamithura_rag
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb ganithamithura_rag

# Database tables will be created automatically on first run
```

### 5. Run the Server

```bash
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## API Endpoints

### Document Upload

```bash
POST /api/v1/upload/
- Upload a document (PDF/DOCX/TXT)
- Extracts text and creates embeddings

GET /api/v1/upload/{document_id}
- Get document details

GET /api/v1/upload/
- List all documents

DELETE /api/v1/upload/{document_id}
- Delete a document
```

### Question Generation

```bash
POST /api/v1/questions/generate
- Generate questions from document
- Supports multiple grade levels
- Background task processing

GET /api/v1/questions/document/{document_id}
- Get all questions for a document

GET /api/v1/questions/{question_id}
- Get specific question

PUT /api/v1/questions/{question_id}
- Update a question

DELETE /api/v1/questions/{question_id}
- Delete a question
```

### Adaptive Learning

```bash
GET /api/v1/adaptive/next-question
- Get next adaptive question for student
- Parameters: student_id, unit_id, grade_level

POST /api/v1/adaptive/submit-answer
- Submit answer and get feedback
- Updates student ability score

GET /api/v1/adaptive/analytics/{student_id}
- Get student analytics and progress

POST /api/v1/adaptive/reset-progress
- Reset student progress (testing)
```

## Usage Examples

### 1. Upload a Document

```python
import requests

url = "http://localhost:8000/api/v1/upload/"

files = {'file': open('mathematics_lesson.pdf', 'rb')}
data = {
    'title': 'Introduction to Measurements',
    'grade_levels': '1,2,3,4',
    'topic': 'measurements',
    'uploaded_by': 'teacher_123'
}

response = requests.post(url, files=files, data=data)
document = response.json()
print(f"Document uploaded: {document['id']}")
```

### 2. Generate Questions

```python
import requests

url = "http://localhost:8000/api/v1/questions/generate"

data = {
    "document_id": 1,
    "grade_levels": [1, 2, 3, 4],
    "questions_per_grade": 10,
    "question_types": ["mcq", "short_answer"]
}

response = requests.post(url, json=data)
print(response.json())
```

### 3. Get Adaptive Question

```python
import requests

url = "http://localhost:8000/api/v1/adaptive/next-question"

params = {
    'student_id': 'student_456',
    'unit_id': 1,
    'grade_level': 2
}

response = requests.get(url, params=params)
question = response.json()
print(f"Question: {question['question_text']}")
print(f"Difficulty: {question['difficulty']}")
```

### 4. Submit Answer

```python
import requests

url = "http://localhost:8000/api/v1/adaptive/submit-answer"

data = {
    "student_id": "student_456",
    "question_id": 123,
    "answer": "100",
    "time_taken": 15
}

response = requests.post(url, json=data)
feedback = response.json()
print(f"Correct: {feedback['is_correct']}")
print(f"New ability: {feedback['ability_score']}")
print(f"Next difficulty: {feedback['next_difficulty']}")
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Teacher Dashboard (Next.js)      │
│         OR Mobile App (Flutter)          │
└───────────────┬─────────────────────────┘
                │ HTTP/REST
                ↓
┌─────────────────────────────────────────┐
│         FastAPI Application              │
│  ┌──────────────────────────────────┐   │
│  │  Routes (Upload, Questions, etc) │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │  Services                        │   │
│  │  • RAG Service                   │   │
│  │  • Question Generator            │   │
│  │  • Adaptive Engine (IRT)         │   │
│  │  • Embeddings Service            │   │
│  └──────────────────────────────────┘   │
└────┬──────────────────────┬──────────────┘
     │                      │
     ↓                      ↓
┌──────────┐          ┌───────────┐
│ChromaDB  │          │PostgreSQL │
│(Vectors) │          │(Questions)│
└──────────┘          └───────────┘
```

## Adaptive Learning Algorithm

The system uses **Item Response Theory (IRT)** with a 1-Parameter Logistic Model:

```
P(correct) = 1 / (1 + exp(-(ability - difficulty)))
```

**Ability Update Formula:**
```
new_ability = current_ability + learning_rate * (actual - predicted)
```

**Optimal Difficulty Selection:**
```
For 70% target success rate:
optimal_difficulty = ability - 0.85
```

## Question Generation Prompts

Questions are generated with grade-specific guidelines:

- **Grade 1**: Simple recognition, 5-10 words, visual focus
- **Grade 2**: Basic comprehension, simple calculations
- **Grade 3**: Application, multi-step problems
- **Grade 4**: Analysis, reasoning, word problems

Each question includes:
- Question text
- Multiple choice options (for MCQ)
- Correct answer
- Difficulty level (1-5)
- Bloom's taxonomy level
- Concept tags
- Explanation
- Helpful hints

## Testing

```bash
# Run tests (when implemented)
pytest

# Test specific endpoint
curl http://localhost:8000/health
```

## Deployment

### Docker (Coming Soon)

```bash
docker build -t ganithamithura-rag .
docker run -p 8000:8000 ganithamithura-rag
```

### Production

1. Set `ENVIRONMENT=production` in `.env`
2. Use a production WSGI server (Gunicorn)
3. Set up proper PostgreSQL instance
4. Configure HTTPS/SSL
5. Set up monitoring and logging

## Troubleshooting

**Database connection error:**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

**OpenAI API errors:**
- Verify OPENAI_API_KEY is correct
- Check API quota/billing
- Ensure model name is correct

**ChromaDB errors:**
- Check write permissions for vectorstore directory
- Clear vectorstore and restart if corrupted

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License

## Support

For issues and questions, please create an issue on GitHub.
