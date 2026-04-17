from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TroughStatus(str, Enum):
    """Trough (cocho) status"""
    EMPTY = "empty"
    PARTIALLY_FULL = "partially_full"
    FULL = "full"
    UNKNOWN = "unknown"


class AnimalStatus(str, Enum):
    """Animal detection status"""
    DETECTED = "detected"
    NOT_DETECTED = "not_detected"
    UNCLEAR = "unclear"


class DetectionType(str, Enum):
    """Types of detection"""
    ANIMAL = "animal"
    TROUGH = "trough"
    WATER = "water"
    SHELTER = "shelter"


class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x_min: float = Field(..., ge=0.0, le=1.0)
    y_min: float = Field(..., ge=0.0, le=1.0)
    x_max: float = Field(..., ge=0.0, le=1.0)
    y_max: float = Field(..., ge=0.0, le=1.0)

    class Config:
        schema_extra = {
            "example": {
                "x_min": 0.1,
                "y_min": 0.2,
                "x_max": 0.5,
                "y_max": 0.8,
            }
        }


class Detection(BaseModel):
    """Single detection result"""
    detection_type: DetectionType
    confidence: float = Field(..., ge=0.0, le=1.0)
    bounding_box: BoundingBox
    animal_id: Optional[str] = None  # RFID or visual ID
    animal_color: Optional[str] = None
    animal_breed: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "detection_type": "animal",
                "confidence": 0.95,
                "bounding_box": {
                    "x_min": 0.1,
                    "y_min": 0.2,
                    "x_max": 0.5,
                    "y_max": 0.8,
                },
                "animal_id": "001-RFID-12345",
                "animal_color": "brown",
                "animal_breed": "Nelore",
                "metadata": {"quality": "high", "occlusion": 0.0},
            }
        }


class FrameDetectionResult(BaseModel):
    """Result of processing a single frame"""
    frame_id: str
    timestamp: datetime
    camera_id: str
    detections: List[Detection]
    total_animals: int
    trough_status: TroughStatus
    processing_time_ms: float
    model_version: str = "YOLOv8n"
    image_url: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "frame_id": "frame-2026-04-16-001",
                "timestamp": "2026-04-16T10:30:00Z",
                "camera_id": "camera-1",
                "detections": [],
                "total_animals": 5,
                "trough_status": "full",
                "processing_time_ms": 45.3,
                "model_version": "YOLOv8n",
                "image_url": "s3://agrovision-images/frame-001.jpg",
            }
        }


class ProcessFrameRequest(BaseModel):
    """Request to process a frame"""
    frame_data: str = Field(..., description="Base64 encoded image data")
    camera_id: str = Field(..., description="Camera identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "frame_data": "iVBORw0KGgoAAAANSUhEUgAAAA...",
                "camera_id": "camera-1",
                "metadata": {"location": "pasture-1", "weather": "sunny"},
            }
        }


class AnimalLocationHistory(BaseModel):
    """Animal location history"""
    animal_id: str
    timestamp: datetime
    camera_id: str
    bounding_box: BoundingBox
    confidence: float


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    models_loaded: bool
    mongodb_connected: bool
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "models_loaded": True,
                "mongodb_connected": True,
                "timestamp": "2026-04-16T10:30:00Z",
            }
        }
