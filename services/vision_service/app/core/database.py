import os
from typing import Optional
from motor.motor_asyncio import AsyncClient, AsyncDatabase
from pymongo.errors import ConnectionFailure
import asyncio

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "agrovision_vision")

# YOLO settings
YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE", "0.5"))
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")  # nano model for speed

# Camera settings
MAX_FRAME_SIZE_MB = int(os.getenv("MAX_FRAME_SIZE_MB", "10"))


class MongoDBConnection:
    """MongoDB async connection manager"""
    
    client: Optional[AsyncClient] = None
    db: Optional[AsyncDatabase] = None

    @classmethod
    async def connect(cls, max_retries: int = 5, retry_interval: int = 2):
        """Connect to MongoDB with retry logic"""
        for attempt in range(max_retries):
            try:
                cls.client = AsyncClient(MONGODB_URL)
                cls.db = cls.client[MONGODB_DB]
                
                # Test connection
                await cls.client.admin.command("ping")
                print(f"✅ MongoDB connected: {MONGODB_DB}")
                
                # Create indexes
                await cls._create_indexes()
                return
            except ConnectionFailure as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ MongoDB connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(retry_interval)
                else:
                    print(f"❌ MongoDB connection failed after {max_retries} attempts")
                    raise

    @classmethod
    async def _create_indexes(cls):
        """Create MongoDB indexes"""
        if cls.db is None:
            return
        
        # Detections indexes
        detections_col = cls.db["detections"]
        await detections_col.create_index("frame_id", unique=True)
        await detections_col.create_index("camera_id")
        await detections_col.create_index("timestamp")
        
        # Animal locations indexes
        locations_col = cls.db["animal_locations"]
        await locations_col.create_index("animal_id")
        await locations_col.create_index("timestamp")
        await locations_col.create_index("camera_id")
        await locations_col.create_index([("timestamp", -1)])  # Descending for recent queries
        
        # Camera calibrations indexes
        calibrations_col = cls.db["camera_calibrations"]
        await calibrations_col.create_index("camera_id", unique=True)
        
        print("✅ MongoDB indexes created")

    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            print("✅ MongoDB disconnected")


def get_db() -> AsyncDatabase:
    """Get MongoDB database instance"""
    if MongoDBConnection.db is None:
        raise RuntimeError("MongoDB not connected")
    return MongoDBConnection.db
