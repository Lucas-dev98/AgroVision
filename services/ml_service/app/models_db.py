from pydantic import BaseModel, Field, field_validator, GetJsonSchemaHandler
from typing import Optional, List, Dict, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema


class PyObjectId(str):
    """Custom ObjectId for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )
    
    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        json_schema = handler(_core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema.update(type="string")
        return json_schema
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError(f"Invalid ObjectId: {v}")


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

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


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

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


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

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


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

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
