# Ganithamithura RAG Service

This is the backend RAG (Retrieval-Augmented Generation) microservice for the Ganithamithura application. It handles document embeddings using ChromaDB and vector database integrations to adaptively generate math questions.

## Prerequisites

Before starting the server, ensure you have the following installed on your system:
- **Python 3.10 or higher**
- **MongoDB** (Ensure MongoDB is running locally or provide a connection URI in your `.env` file)
- An **OpenAI API Key** (for embedding generation and language models)

## Setup Instructions

### 1. Clone the repository and navigate to the directory
```bash
git clone <repository_url>
cd ganithamithura/unit-rag-service
```

### 2. Create and activate a virtual environment
For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
Run the following command to install the required Python packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to create your own configuration file:
```bash
cp .env.example .env
```
Inside your new `.env` file, replace the placeholder for `OPENAI_API_KEY` with your actual OpenAI key, and modify MongoDB URLs as needed.

### 5. Start the Application
To run Uvicorn and start the FASTAPI backend server directly, execute the following command:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Testing & Documentation
Once the server is running, the API handles its own self-documentation.
You can view all the routes and interact with them using FastAPI's Swagger UI:
- **Swagger Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Project Dependencies
Below are some of the core dependencies used in this project:
- `fastapi` & `uvicorn` for the high-performance async web framework and server
- `langchain` & `openai` for handling AI modeling and RAG chains
- `chromadb` for storing generated text embeddings
- `beanie` & `motor` for asynchronous MongoDB integration
- `numpy<2.0` (Pinned explicitly due to backward compatibility requirement in ChromaDB)
- `sentence-transformers` for local embedding support

Check the `requirements.txt` file for the exact locked package versions.
