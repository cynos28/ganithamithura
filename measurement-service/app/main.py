"""
Measurement Service - AR Measurement Context Processing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import measurement

# Initialize FastAPI app
app = FastAPI(
    title="Ganithamithura Measurement Service",
    description="Process AR measurements and build context for contextual questions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(measurement.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Ganithamithura Measurement Service",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "measurement-service", "port": 8001}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
