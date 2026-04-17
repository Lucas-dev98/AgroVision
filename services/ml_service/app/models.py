from pydantic import BaseModel, Field
from typing import Optional, List, Dict
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


class TrackingDocument(BaseModel):
    """MongoDB document for tracking data"""
    id: Optional[PyObjectId] = Field(alias="_id")
    frame_id: str
    timestamp: datetime
    camera_id: str
    tracks: List[dict] = Field(default_factory=list)
    behaviors: List[dict] = Field(default_factory=list)
    anomalies: List[dict] = Field(default_factory=list)
    processing_time_ms: float
    model_version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class AnimalReIdDocument(BaseModel):
    """MongoDB document for re-identification results"""
    id: Optional[PyObjectId] = Field(alias="_id")
    animal_id: str
    primary_camera_id: str
    secondary_camera_id: str
    similarity_score: float
    confirmed: bool
    color_descriptor: Optional[List[float]] = None
    pattern_descriptor: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class AnimalHealthDocument(BaseModel):
    """MongoDB document for animal health data"""
    id: Optional[PyObjectId] = Field(alias="_id")
    animal_id: str
    timestamp: datetime
    behaviors: List[dict] = Field(default_factory=list)
    anomalies: List[dict] = Field(default_factory=list)
    health_score: float
    risk_level: str
    recommendations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class BehaviorPatternDocument(BaseModel):
    """MongoDB document for behavior patterns"""
    id: Optional[PyObjectId] = Field(alias="_id")
    animal_id: str
    behavior_type: str
    total_occurrences: int
    average_duration_seconds: float
    last_observed: datetime
    first_observed: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
