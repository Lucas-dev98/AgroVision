import os
from typing import Optional
from motor.motor_asyncio import AsyncClient, AsyncDatabase
from pymongo.errors import ConnectionFailure
import asyncio

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "agrovision_ml")


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
        
        # Tracking indexes
        tracking_col = cls.db["tracking"]
        await tracking_col.create_index("frame_id", unique=True)
        await tracking_col.create_index("camera_id")
        await tracking_col.create_index("timestamp")
        
        # Re-identification indexes
        reid_col = cls.db["animal_reid"]
        await reid_col.create_index("animal_id")
        await reid_col.create_index([("primary_camera_id", 1), ("secondary_camera_id", 1)])
        
        # Health documents indexes
        health_col = cls.db["animal_health"]
        await health_col.create_index("animal_id")
        await health_col.create_index("timestamp")
        await health_col.create_index([("animal_id", 1), ("timestamp", -1)])
        
        # Behavior patterns indexes
        behavior_col = cls.db["behavior_patterns"]
        await behavior_col.create_index("animal_id")
        await behavior_col.create_index("behavior_type")
        
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
