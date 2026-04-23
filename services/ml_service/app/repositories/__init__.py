from typing import List, Optional, Dict
from datetime import timezone, datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models_db import TrackingDocument, AnimalReIdDocument, AnimalHealthDocument
from app.schemas import AnimalTrack, BehaviorClassification, AnomalyDetection


class TrackingRepository:
    """Repository for tracking documents"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["tracking"]
    
    async def create(
        self,
        frame_id: str,
        camera_id: str,
        tracks: List[AnimalTrack],
        behaviors: List[BehaviorClassification],
        anomalies: List[AnomalyDetection],
    ) -> str:
        """Create tracking document"""
        doc = {
            "frame_id": frame_id,
            "camera_id": camera_id,
            "timestamp": datetime.now(timezone.utc),
            "tracks": [t.dict() for t in tracks],
            "behaviors": [b.dict() for b in behaviors],
            "anomalies": [a.dict() for a in anomalies],
        }
        
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_by_frame(self, frame_id: str) -> Optional[Dict]:
        """Get tracking by frame ID"""
        return await self.collection.find_one({"frame_id": frame_id})
    
    async def get_by_camera(
        self,
        camera_id: str,
        limit: int = 100,
    ) -> List[Dict]:
        """Get tracking records by camera"""
        cursor = self.collection.find({"camera_id": camera_id}).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_recent(
        self,
        hours: int = 1,
        limit: int = 100,
    ) -> List[Dict]:
        """Get recent tracking records"""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        cursor = self.collection.find(
            {"timestamp": {"$gte": cutoff}}
        ).limit(limit)
        
        return await cursor.to_list(length=limit)


class ReIdRepository:
    """Repository for re-identification documents"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["animal_reid"]
    
    async def create(
        self,
        animal_id: str,
        primary_camera: str,
        secondary_camera: str,
        similarity_score: float,
        confirmed: bool,
    ) -> str:
        """Create re-identification document"""
        doc = {
            "animal_id": animal_id,
            "primary_camera_id": primary_camera,
            "secondary_camera_id": secondary_camera,
            "similarity_score": similarity_score,
            "confirmed": confirmed,
            "timestamp": datetime.now(timezone.utc),
        }
        
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_by_animal(self, animal_id: str) -> List[Dict]:
        """Get re-identification results for animal"""
        cursor = self.collection.find({"animal_id": animal_id})
        return await cursor.to_list(length=None)
    
    async def get_matches(
        self,
        animal_id: str,
        confidence_threshold: float = 0.7,
    ) -> List[Dict]:
        """Get confirmed matches above threshold"""
        cursor = self.collection.find({
            "animal_id": animal_id,
            "similarity_score": {"$gte": confidence_threshold},
            "confirmed": True,
        })
        
        return await cursor.to_list(length=None)


class HealthRepository:
    """Repository for animal health documents"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["animal_health"]
    
    async def create(
        self,
        animal_id: str,
        health_score: float,
        risk_level: str,
        recommendations: List[str],
    ) -> str:
        """Create health document"""
        doc = {
            "animal_id": animal_id,
            "health_score": health_score,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "timestamp": datetime.now(timezone.utc),
        }
        
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)
    
    async def get_latest(self, animal_id: str) -> Optional[Dict]:
        """Get latest health record for animal"""
        return await self.collection.find_one(
            {"animal_id": animal_id},
            sort=[("timestamp", -1)],
        )
    
    async def get_history(
        self,
        animal_id: str,
        limit: int = 30,
    ) -> List[Dict]:
        """Get health history for animal"""
        cursor = self.collection.find(
            {"animal_id": animal_id}
        ).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def get_critical_animals(self) -> List[Dict]:
        """Get all animals with critical health status"""
        cursor = self.collection.find(
            {"risk_level": "critical"}
        ).sort("timestamp", -1)
        
        return await cursor.to_list(length=None)
