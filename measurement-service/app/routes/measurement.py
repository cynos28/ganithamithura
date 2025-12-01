"""
API routes for AR measurement processing
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import ARMeasurementRequest, MeasurementContext
from app.services.context_builder import context_builder

router = APIRouter(prefix="/api/v1/measurements", tags=["Measurements"])


@router.post("/process", response_model=MeasurementContext)
async def process_measurement(request: ARMeasurementRequest):
    """
    Process AR measurement and generate context for question generation
    
    This endpoint:
    1. Receives AR measurement data from Flutter
    2. Builds learning context
    3. Returns structured context for RAG service
    """
    
    try:
        context = context_builder.build_context(request)
        return context
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing measurement: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "measurement-service",
        "version": "1.0.0"
    }


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint for debugging connectivity"""
    return {
        "status": "ok",
        "message": "Measurement service is reachable!",
        "timestamp": "2025-12-01T00:00:00Z"
    }
