from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.database import init_db
from app.routes import upload, questions, adaptive

# Initialize FastAPI app
app = FastAPI(
    title="Ganithamithura RAG Service",
    description="Adaptive learning question generation using RAG",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(questions.router)
app.include_router(adaptive.router)

# Add legacy/alias routes for backward compatibility
app.include_router(upload.router, prefix="/upload", tags=["upload-legacy"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print(f"✅ Server running on {settings.host}:{settings.port}")
    print(f"✅ Environment: {settings.environment}")
    print(f"✅ Docs available at: http://{settings.host}:{settings.port}/docs")


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Ganithamithura RAG Service",
        "status": "running",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from app.services.embeddings_service import embeddings_service
    
    try:
        # Check vector database
        stats = embeddings_service.get_collection_stats()
        
        return {
            "status": "healthy",
            "database": "connected",
            "vector_store": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
