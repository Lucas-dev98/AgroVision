from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class DetectionDocument(BaseModel):
    """MongoDB document for detections"""
    id: Optional[PyObjectId] = Field(alias="_id")
    frame_id: str
    timestamp: datetime
    camera_id: str
    detections: list = Field(default_factory=list)
    total_animals: int
    trough_status: str
    processing_time_ms: float
    model_version: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "frame_id": "frame-2026-04-16-001",
                "timestamp": "2026-04-16T10:30:00Z",
                "camera_id": "camera-1",
                "detections": [],
                "total_animals": 5,
                "trough_status": "full",
                "processing_time_ms": 45.3,
            }
        }


class AnimalLocationDocument(BaseModel):
    """MongoDB document for animal locations"""
    id: Optional[PyObjectId] = Field(alias="_id")
    animal_id: str
    timestamp: datetime
    camera_id: str
    location: dict  # {x_min, y_min, x_max, y_max}
    confidence: float
    frame_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class CameraCalibrationDocument(BaseModel):
    """MongoDB document for camera calibrations"""
    id: Optional[PyObjectId] = Field(alias="_id")
    camera_id: str
    location: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    calibration_data: dict = Field(default_factory=dict)
    yolo_confidence_threshold: float = 0.5
    last_calibrated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
