from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncDatabase, AsyncCollection
from app.models import DetectionDocument, AnimalLocationDocument, CameraCalibrationDocument
from app.schemas import FrameDetectionResult


class DetectionRepository:
    """Repository for detection documents in MongoDB"""
    
    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.collection: AsyncCollection = db["detections"]
    
    async def create(self, frame_result: FrameDetectionResult) -> str:
        """
        Create a new detection document
        
        Args:
            frame_result: FrameDetectionResult to store
            
        Returns:
            MongoDB document ID
        """
        doc = {
            "frame_id": frame_result.frame_id,
            "timestamp": frame_result.timestamp,
            "camera_id": frame_result.camera_id,
            "detections": [det.dict() for det in frame_result.detections],
            "total_animals": frame_result.total_animals,
            "trough_status": frame_result.trough_status.value,
            "processing_time_ms": frame_result.processing_time_ms,
            "model_version": frame_result.model_version,
            "image_url": frame_result.image_url,
            "created_at": datetime.utcnow(),
        }
        
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_by_frame_id(self, frame_id: str) -> Optional[dict]:
        """Get detection by frame ID"""
        return await self.collection.find_one({"frame_id": frame_id})
    
    async def get_by_camera(
        self,
        camera_id: str,
        limit: int = 100,
        skip: int = 0,
    ) -> List[dict]:
        """Get detections by camera ID with pagination"""
        cursor = self.collection.find({"camera_id": camera_id})
        cursor = cursor.sort("timestamp", -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_recent(self, hours: int = 24, limit: int = 100) -> List[dict]:
        """Get recent detections"""
        since = datetime.utcnow() - timedelta(hours=hours)
        cursor = self.collection.find({"timestamp": {"$gte": since}})
        cursor = cursor.sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def count_animals_by_camera(self, camera_id: str) -> int:
        """Count total animals detected by camera"""
        result = await self.collection.aggregate([
            {"$match": {"camera_id": camera_id}},
            {"$group": {"_id": None, "total": {"$sum": "$total_animals"}}},
        ]).to_list(length=1)
        
        return result[0]["total"] if result else 0


class AnimalLocationRepository:
    """Repository for animal location documents in MongoDB"""
    
    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.collection: AsyncCollection = db["animal_locations"]
    
    async def create_location(
        self,
        animal_id: str,
        timestamp: datetime,
        camera_id: str,
        location: dict,
        confidence: float,
        frame_id: str,
    ) -> str:
        """Create a new animal location record"""
        doc = {
            "animal_id": animal_id,
            "timestamp": timestamp,
            "camera_id": camera_id,
            "location": location,
            "confidence": confidence,
            "frame_id": frame_id,
            "created_at": datetime.utcnow(),
        }
        
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_animal_history(
        self,
        animal_id: str,
        limit: int = 100,
        hours: int = 24,
    ) -> List[dict]:
        """Get animal location history"""
        since = datetime.utcnow() - timedelta(hours=hours)
        cursor = self.collection.find({
            "animal_id": animal_id,
            "timestamp": {"$gte": since},
        })
        cursor = cursor.sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_latest_locations(self, camera_id: str) -> List[dict]:
        """Get latest locations of all animals in a camera"""
        # Group by animal_id and get the latest entry
        pipeline = [
            {"$match": {"camera_id": camera_id}},
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$animal_id",
                "latest": {"$first": "$$ROOT"},
            }},
            {"$replaceRoot": {"newRoot": "$latest"}},
        ]
        
        return await self.collection.aggregate(pipeline).to_list(length=None)
    
    async def count_unique_animals(self, camera_id: str, hours: int = 24) -> int:
        """Count unique animals detected in camera during period"""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self.collection.distinct(
            "animal_id",
            {"camera_id": camera_id, "timestamp": {"$gte": since}},
        )
        return len(result)


class CameraCalibrationRepository:
    """Repository for camera calibration documents in MongoDB"""
    
    def __init__(self, db: AsyncDatabase):
        self.db = db
        self.collection: AsyncCollection = db["camera_calibrations"]
    
    async def create_or_update(
        self,
        camera_id: str,
        location: str,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        calibration_data: Optional[dict] = None,
        confidence_threshold: float = 0.5,
    ) -> str:
        """Create or update camera calibration"""
        doc = {
            "camera_id": camera_id,
            "location": location,
            "longitude": longitude,
            "latitude": latitude,
            "calibration_data": calibration_data or {},
            "yolo_confidence_threshold": confidence_threshold,
            "last_calibrated": datetime.utcnow(),
        }
        
        result = await self.collection.update_one(
            {"camera_id": camera_id},
            {"$set": doc},
            upsert=True,
        )
        
        return camera_id
    
    async def get_by_camera_id(self, camera_id: str) -> Optional[dict]:
        """Get camera calibration"""
        return await self.collection.find_one({"camera_id": camera_id})
    
    async def get_all(self) -> List[dict]:
        """Get all camera calibrations"""
        cursor = self.collection.find()
        return await cursor.to_list(length=None)
