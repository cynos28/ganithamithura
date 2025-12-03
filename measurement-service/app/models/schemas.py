"""
Request/Response models for measurement service
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class MeasurementType(str, Enum):
    """Types of measurements"""
    LENGTH = "length"
    CAPACITY = "capacity"
    WEIGHT = "weight"
    AREA = "area"


class Unit(str, Enum):
    """Measurement units"""
    # Length
    MM = "mm"
    CM = "cm"
    M = "m"
    KM = "km"
    
    # Capacity
    ML = "ml"
    L = "l"
    
    # Weight
    G = "g"
    KG = "kg"
    
    # Area
    CM2 = "cm²"
    M2 = "m²"


class ARMeasurementRequest(BaseModel):
    """Request from Flutter AR measurement with object detection"""
    measurement_type: MeasurementType = Field(..., description="Type of measurement")
    value: float = Field(..., description="Measured value", gt=0)
    unit: Unit = Field(..., description="Unit of measurement")
    object_name: str = Field(..., description="Detected or manually selected object name")
    student_id: str = Field(..., description="Student identifier")
    grade: int = Field(default=1, ge=1, le=5, description="Student grade level")
    
    # Object detection metadata
    detection_confidence: Optional[float] = Field(None, description="ML detection confidence (0-1)")
    manually_corrected: bool = Field(False, description="Whether student corrected the detection")
    session_id: Optional[str] = Field(None, description="AR session identifier for tracking")
    
    # AR measurement metadata
    measurement_method: Optional[str] = Field("tap", description="How measured: tap, drag, area")
    photo_path: Optional[str] = Field(None, description="Path to captured AR photo")


class MeasurementContext(BaseModel):
    """Context generated from AR measurement"""
    measurement_type: MeasurementType
    value: float
    unit: str
    object_name: str
    context_description: str = Field(..., description="Human-readable context for questions")
    topic: str = Field(..., description="Curriculum topic (Length, Capacity, Weight, Area)")
    suggested_grade: int = Field(..., description="Recommended grade level based on measurement")
    difficulty_hints: List[str] = Field(default_factory=list, description="Suggested question types")
    personalized_prompt: str = Field(..., description="Prompt snippet for LLM")


class ContextualQuestionRequest(BaseModel):
    """Request to RAG service for contextual questions"""
    student_id: str
    measurement_context: MeasurementContext
    num_questions: int = Field(default=5, ge=1, le=10)
    grade: int = Field(default=1, ge=1, le=5)
