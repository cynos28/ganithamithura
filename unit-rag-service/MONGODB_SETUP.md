# 🚀 MongoDB Setup Guide for Unit RAG Service

## Why MongoDB?

✅ **Perfect for RAG Systems**: Semi-structured data, flexible schemas  
✅ **Easy to Use**: No complex migrations, instant setup  
✅ **Great Performance**: Fast queries, excellent for document storage  
✅ **Free & Local**: Run locally or use MongoDB Atlas (cloud)  
✅ **Works with Beanie ODM**: Clean, Pythonic async queries  

---

## Quick Start (macOS)

### Step 1: Install MongoDB

```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB service
brew services start mongodb-community@7.0

# Verify it's running
brew services list | grep mongodb
```

### Step 2: Test MongoDB Connection

```bash
# Connect to MongoDB shell
mongosh

# You should see:
# Current Mongosh Log ID:	...
# Connecting to:		mongodb://127.0.0.1:27017
# Using MongoDB:		7.0.x

# Create database (in mongosh)
use ganithamithura_rag

# Exit
exit
```

### Step 3: Install Python Dependencies

```bash
cd unit-rag-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

**Required configuration:**

```env
# OpenAI - GET YOUR KEY FROM: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=ganithamithura_rag
```

### Step 5: Start the Server

```bash
python -m app.main
```

You should see:
```
✅ MongoDB connected: ganithamithura_rag
✅ Server running on 0.0.0.0:8000
✅ Environment: development
✅ Docs available at: http://0.0.0.0:8000/docs
```

---

## MongoDB on Other Systems

### Ubuntu/Debian

```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install
sudo apt update
sudo apt install -y mongodb-org

# Start service
sudo systemctl start mongod
sudo systemctl enable mongod

# Check status
sudo systemctl status mongod
```

### Windows

1. Download MongoDB from: https://www.mongodb.com/try/download/community
2. Run installer (choose "Complete" installation)
3. Install MongoDB as a Windows Service
4. MongoDB will start automatically

---

## Using MongoDB Atlas (Cloud - Free Tier)

If you don't want to install MongoDB locally:

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create free account
3. Create a free cluster (M0 - Free tier)
4. Click "Connect" → "Drivers" → Copy connection string
5. Update `.env`:

```env
MONGODB_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ganithamithura_rag
```

---

## Verify Setup

### Test 1: Check MongoDB is Running

```bash
# Try connecting
mongosh

# Or check process
ps aux | grep mongod
```

### Test 2: Start API Server

```bash
python -m app.main
```

Visit http://localhost:8000/health - Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "vector_store": {...}
}
```

### Test 3: View Database in MongoDB Compass

1. Download MongoDB Compass: https://www.mongodb.com/try/download/compass
2. Connect to `mongodb://localhost:27017`
3. You should see `ganithamithura_rag` database
4. Collections will appear after you upload first document

---

## MongoDB Commands

### View Collections

```bash
mongosh

use ganithamithura_rag

# Show all collections
show collections

# Count documents
db.documents.countDocuments()
db.questions.countDocuments()
db.student_answers.countDocuments()
db.student_ability.countDocuments()

# View a document
db.documents.findOne()
db.questions.findOne()
```

### Clear Data

```bash
mongosh

use ganithamithura_rag

# Drop specific collection
db.questions.drop()

# Drop entire database (careful!)
db.dropDatabase()
```

### Backup & Restore

```bash
# Backup
mongodump --db=ganithamithura_rag --out=./backup

# Restore
mongorestore --db=ganithamithura_rag ./backup/ganithamithura_rag
```

---

## MongoDB vs PostgreSQL Comparison

| Feature | MongoDB | PostgreSQL |
|---------|---------|------------|
| **Setup** | ✅ Instant, no config | ⚠️ Requires setup |
| **Schema** | ✅ Flexible, no migrations | ❌ Fixed, needs migrations |
| **Queries** | ✅ Simple, JSON-like | ⚠️ SQL knowledge needed |
| **Scaling** | ✅ Easy horizontal scaling | ⚠️ Vertical scaling |
| **RAG Systems** | ✅ Perfect for documents | ⚠️ OK but more rigid |
| **Free Tier** | ✅ Yes (Atlas) | ⚠️ Limited options |

---

## Troubleshooting

### Error: "Connection refused to mongodb://localhost:27017"

**Solution:**
```bash
# Check if MongoDB is running
brew services list  # macOS
sudo systemctl status mongod  # Linux

# Start it
brew services start mongodb-community@7.0  # macOS
sudo systemctl start mongod  # Linux
```

### Error: "Authentication failed"

**Solution:**
```bash
# If using MongoDB Atlas, check:
# 1. Username/password in connection string
# 2. Network access allows your IP
# 3. Database user has proper permissions
```

### Error: "Database not found"

**Solution:**
MongoDB creates databases automatically when you first insert data.  
Just start the server and upload a document - database will be created.

### Port 27017 Already in Use

**Solution:**
```bash
# Find what's using the port
lsof -ti:27017

# Kill it
lsof -ti:27017 | xargs kill -9

# Restart MongoDB
brew services restart mongodb-community@7.0
```

---

## Development Workflow

### 1. View Data in Real-Time

Use MongoDB Compass or mongosh:
```bash
mongosh
use ganithamithura_rag
db.documents.find().pretty()
db.questions.find({grade_level: 1}).pretty()
db.student_ability.find().pretty()
```

### 2. Reset Database

```bash
mongosh
use ganithamithura_rag
db.dropDatabase()
```

Restart server to recreate with indexes.

### 3. Monitor Queries

In mongosh:
```bash
db.setProfilingLevel(2)  # Log all queries
db.system.profile.find().pretty()
```

---

## Production Deployment

### Option 1: MongoDB Atlas (Recommended)

1. Create production cluster
2. Set up automated backups
3. Configure IP whitelist
4. Use connection pooling
5. Enable monitoring

### Option 2: Self-Hosted

```bash
# Install MongoDB on server
sudo apt install mongodb-org

# Configure for production
sudo nano /etc/mongod.conf

# Enable authentication
security:
  authorization: enabled

# Create admin user
mongosh
use admin
db.createUser({
  user: "admin",
  pwd: "strongpassword",
  roles: ["root"]
})

# Restart
sudo systemctl restart mongod
```

---

## Benefits for Our RAG System

✅ **Fast Document Storage**: Store uploaded PDFs/DOCX as text  
✅ **Flexible Question Schema**: Easy to add new question types  
✅ **Student Progress**: Track ability scores with nested objects  
✅ **Concept Mastery**: Store as nested JSON (no joins needed)  
✅ **Easy Queries**: Beanie ODM makes it Pythonic  
✅ **Vector Store**: ChromaDB handles embeddings separately  

---

## Next Steps

1. ✅ MongoDB installed and running
2. ✅ Python dependencies installed
3. ✅ Environment configured
4. ✅ Server starts successfully
5. 🚀 **Upload your first document at:** http://localhost:8000/docs

## Support

- **MongoDB Docs**: https://docs.mongodb.com
- **Beanie ODM**: https://beanie-odm.dev
- **MongoDB Compass**: https://www.mongodb.com/products/compass
- **Community**: https://community.mongodb.com
