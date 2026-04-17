from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class AnimalBehavior(str, Enum):
    """Animal behaviors"""
    GRAZING = "grazing"
    RESTING = "resting"
    DRINKING = "drinking"
    WALKING = "walking"
    RUNNING = "running"
    STANDING = "standing"
    EATING = "eating"
    UNKNOWN = "unknown"


class AnomalyType(str, Enum):
    """Types of detected anomalies"""
    LAMENESS = "lameness"
    LETHARGY = "lethargy"
    ABNORMAL_POSTURE = "abnormal_posture"
    EXCESSIVE_SALIVATION = "excessive_salivation"
    UNUSUAL_MOVEMENT = "unusual_movement"
    WEIGHT_CHANGE = "weight_change"
    BEHAVIORAL_CHANGE = "behavioral_change"
    UNKNOWN = "unknown"


class AnimalTrack(BaseModel):
    """Tracked animal across frames"""
    track_id: int
    animal_id: Optional[str] = None  # RFID ID when known
    confidence: float = Field(..., ge=0.0, le=1.0)
    current_position: Dict[str, float]  # x, y, width, height
    velocity: Optional[Dict[str, float]] = None  # vx, vy
    frames_count: int = Field(default=1)
    last_seen: datetime
    first_seen: datetime

    class Config:
        schema_extra = {
            "example": {
                "track_id": 1,
                "animal_id": "RFID-001",
                "confidence": 0.95,
                "current_position": {"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.2},
                "velocity": {"vx": 0.01, "vy": -0.02},
                "frames_count": 45,
                "last_seen": "2026-04-16T10:30:00Z",
                "first_seen": "2026-04-16T10:25:00Z",
            }
        }


class BehaviorClassification(BaseModel):
    """Behavior classification result"""
    behavior: AnimalBehavior
    confidence: float = Field(..., ge=0.0, le=1.0)
    duration_seconds: Optional[float] = None
    position: Dict[str, float]

    class Config:
        schema_extra = {
            "example": {
                "behavior": "grazing",
                "confidence": 0.92,
                "duration_seconds": 180.5,
                "position": {"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.2},
            }
        }


class AnimalReIdentification(BaseModel):
    """Re-identification result for same animal across cameras"""
    animal_id: str
    primary_camera_id: str
    secondary_camera_id: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    confirmed: bool = False
    color_descriptor: Optional[List[float]] = None
    pattern_descriptor: Optional[List[float]] = None

    class Config:
        schema_extra = {
            "example": {
                "animal_id": "RFID-001",
                "primary_camera_id": "camera-1",
                "secondary_camera_id": "camera-2",
                "similarity_score": 0.89,
                "confirmed": True,
                "color_descriptor": [0.8, 0.6, 0.4],
                "pattern_descriptor": [0.5, 0.7, 0.3],
            }
        }


class AnomalyDetection(BaseModel):
    """Anomaly detection result"""
    animal_id: str
    anomaly_type: AnomalyType
    severity: str = Field(..., regex="^(low|medium|high|critical)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    description: str
    recommended_action: Optional[str] = None
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "animal_id": "RFID-001",
                "anomaly_type": "lameness",
                "severity": "high",
                "confidence": 0.87,
                "description": "Detected abnormal gait in right rear leg",
                "recommended_action": "Schedule veterinary examination",
                "timestamp": "2026-04-16T10:30:00Z",
            }
        }


class TrackingFrameResult(BaseModel):
    """Result of tracking frame with all ML analysis"""
    frame_id: str
    timestamp: datetime
    camera_id: str
    tracks: List[AnimalTrack]
    behaviors: List[BehaviorClassification]
    anomalies: List[AnomalyDetection]
    processing_time_ms: float
    model_version: str = "YOLO v8 + ByteTrack"

    class Config:
        schema_extra = {
            "example": {
                "frame_id": "frame-camera-1-001",
                "timestamp": "2026-04-16T10:30:00Z",
                "camera_id": "camera-1",
                "tracks": [],
                "behaviors": [],
                "anomalies": [],
                "processing_time_ms": 85.3,
                "model_version": "YOLO v8 + ByteTrack",
            }
        }


class ReIdentificationRequest(BaseModel):
    """Request for animal re-identification across cameras"""
    animal_id: str
    primary_camera_id: str
    primary_descriptors: Dict[str, List[float]]  # color, pattern, etc
    secondary_cameras: List[str]
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    class Config:
        schema_extra = {
            "example": {
                "animal_id": "RFID-001",
                "primary_camera_id": "camera-1",
                "primary_descriptors": {
                    "color": [0.8, 0.6, 0.4],
                    "pattern": [0.5, 0.7, 0.3],
                },
                "secondary_cameras": ["camera-2", "camera-3"],
                "similarity_threshold": 0.7,
            }
        }


class AnimalHealthReport(BaseModel):
    """Comprehensive health report for animal"""
    animal_id: str
    timestamp: datetime
    recent_behaviors: List[BehaviorClassification]
    detected_anomalies: List[AnomalyDetection]
    health_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., regex="^(low|medium|high|critical)$")
    recommendations: List[str]

    class Config:
        schema_extra = {
            "example": {
                "animal_id": "RFID-001",
                "timestamp": "2026-04-16T10:30:00Z",
                "recent_behaviors": [],
                "detected_anomalies": [],
                "health_score": 0.85,
                "risk_level": "low",
                "recommendations": ["Continue normal monitoring"],
            }
        }
