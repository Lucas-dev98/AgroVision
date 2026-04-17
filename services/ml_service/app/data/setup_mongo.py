"""
MongoDB Setup Script for FASE 3
================================

Initializes MongoDB collections and indexes for real data integration.
Run with: python -m app.data.setup_mongo

Creates:
- tracking collection (position data)
- behavior_patterns collection (behavior labels)
- animal_health collection (health metrics)
- animal_reid collection (image metadata)
"""

import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBSetup:
    """Setup MongoDB collections and indexes."""

    def __init__(self, connection_string: str, database_name: str = "agrovision_ml"):
        """
        Initialize MongoDB setup.

        Args:
            connection_string: MongoDB connection string
            database_name: Database name to create
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None

    async def connect(self):
        """Connect to MongoDB."""
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client[self.database_name]
        logger.info(f"Connected to MongoDB database: {self.database_name}")

    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def setup_tracking_collection(self):
        """Setup tracking collection for cattle position data."""
        collection = self.db.tracking

        # Create compound index for efficient queries
        await collection.create_index([("animal_id", 1), ("timestamp", -1)])
        await collection.create_index([("camera_id", 1)])
        await collection.create_index([("timestamp", -1)])

        logger.info("✅ Tracking collection indexes created")

    async def setup_behavior_collection(self):
        """Setup behavior_patterns collection for annotated behaviors."""
        collection = self.db.behavior_patterns

        # Create indexes
        await collection.create_index([("animal_id", 1), ("timestamp", -1)])
        await collection.create_index([("behavior_type", 1)])
        await collection.create_index([("duration_seconds", 1)])

        logger.info("✅ Behavior patterns collection indexes created")

    async def setup_health_collection(self):
        """Setup animal_health collection for health metrics and anomalies."""
        collection = self.db.animal_health

        # Create indexes
        await collection.create_index([("animal_id", 1), ("timestamp", -1)])
        await collection.create_index([("is_anomaly", 1)])
        await collection.create_index([("anomaly_type", 1)])
        await collection.create_index([("timestamp", -1)])

        logger.info("✅ Animal health collection indexes created")

    async def setup_reid_collection(self):
        """Setup animal_reid collection for multi-camera images."""
        collection = self.db.animal_reid

        # Create indexes
        await collection.create_index([("animal_id", 1)])
        await collection.create_index([("camera_id", 1)])
        await collection.create_index([("animal_id", 1), ("camera_id", 1)])
        await collection.create_index([("timestamp", -1)])

        logger.info("✅ Animal Re-ID collection indexes created")

    async def seed_sample_data(self):
        """Insert sample data for testing."""
        try:
            # Sample tracking data
            tracking = self.db.tracking
            await tracking.delete_many({})
            sample_tracking = [
                {
                    "animal_id": "cow_001",
                    "camera_id": "cam_001",
                    "position": {"x": 100, "y": 200},
                    "timestamp": datetime.utcnow(),
                    "confidence": 0.95,
                },
                {
                    "animal_id": "cow_002",
                    "camera_id": "cam_001",
                    "position": {"x": 150, "y": 250},
                    "timestamp": datetime.utcnow(),
                    "confidence": 0.92,
                },
            ]
            await tracking.insert_many(sample_tracking)
            logger.info(f"✅ Seeded {len(sample_tracking)} tracking records")

            # Sample behavior data
            behavior = self.db.behavior_patterns
            await behavior.delete_many({})
            sample_behavior = [
                {
                    "animal_id": "cow_001",
                    "behavior_type": "grazing",
                    "timestamp": datetime.utcnow(),
                    "duration_seconds": 300,
                    "confidence": 0.9,
                },
                {
                    "animal_id": "cow_001",
                    "behavior_type": "walking",
                    "timestamp": datetime.utcnow(),
                    "duration_seconds": 60,
                    "confidence": 0.85,
                },
                {
                    "animal_id": "cow_002",
                    "behavior_type": "resting",
                    "timestamp": datetime.utcnow(),
                    "duration_seconds": 1800,
                    "confidence": 0.95,
                },
            ]
            await behavior.insert_many(sample_behavior)
            logger.info(f"✅ Seeded {len(sample_behavior)} behavior records")

            # Sample health data
            health = self.db.animal_health
            await health.delete_many({})
            sample_health = [
                {
                    "animal_id": "cow_001",
                    "timestamp": datetime.utcnow(),
                    "activity_level": 0.7,
                    "movement_distance": 150,
                    "heart_rate": 60,
                    "body_temperature": 38.5,
                    "feed_consumption": 10,
                    "water_consumption": 20,
                    "is_anomaly": False,
                },
                {
                    "animal_id": "cow_002",
                    "timestamp": datetime.utcnow(),
                    "activity_level": 0.3,
                    "movement_distance": 20,
                    "heart_rate": 55,
                    "body_temperature": 38.2,
                    "feed_consumption": 8,
                    "water_consumption": 15,
                    "is_anomaly": False,
                },
            ]
            await health.insert_many(sample_health)
            logger.info(f"✅ Seeded {len(sample_health)} health records")

            # Sample Re-ID data
            reid = self.db.animal_reid
            await reid.delete_many({})
            sample_reid = [
                {
                    "animal_id": "cow_001",
                    "camera_id": "cam_001",
                    "image_path": "/storage/images/cow_001_cam_001_001.jpg",
                    "timestamp": datetime.utcnow(),
                    "quality_score": 0.95,
                },
                {
                    "animal_id": "cow_001",
                    "camera_id": "cam_002",
                    "image_path": "/storage/images/cow_001_cam_002_001.jpg",
                    "timestamp": datetime.utcnow(),
                    "quality_score": 0.92,
                },
                {
                    "animal_id": "cow_002",
                    "camera_id": "cam_001",
                    "image_path": "/storage/images/cow_002_cam_001_001.jpg",
                    "timestamp": datetime.utcnow(),
                    "quality_score": 0.90,
                },
            ]
            await reid.insert_many(sample_reid)
            logger.info(f"✅ Seeded {len(sample_reid)} Re-ID records")

        except Exception as e:
            logger.error(f"❌ Error seeding data: {e}")

    async def verify_setup(self):
        """Verify all collections are created."""
        collections = await self.db.list_collection_names()
        required = {"tracking", "behavior_patterns", "animal_health", "animal_reid"}

        created = set(collections) & required
        missing = required - created

        if missing:
            logger.warning(f"⚠️ Missing collections: {missing}")
        else:
            logger.info("✅ All required collections exist")

        # Count documents in each
        for coll_name in created:
            collection = self.db[coll_name]
            count = await collection.count_documents({})
            logger.info(f"   - {coll_name}: {count} documents")

    async def drop_all_collections(self):
        """Drop all collections (use with caution!)."""
        logger.warning("⚠️ Dropping all collections...")
        collections = await self.db.list_collection_names()
        for coll_name in collections:
            await self.db[coll_name].drop()
            logger.info(f"   - Dropped: {coll_name}")

    async def setup(self, drop_existing: bool = False, seed_data: bool = True):
        """
        Full setup procedure.

        Args:
            drop_existing: Whether to drop existing collections
            seed_data: Whether to seed sample data
        """
        try:
            await self.connect()

            if drop_existing:
                await self.drop_all_collections()

            # Create collections
            await self.setup_tracking_collection()
            await self.setup_behavior_collection()
            await self.setup_health_collection()
            await self.setup_reid_collection()

            # Verify
            await self.verify_setup()

            # Seed sample data
            if seed_data:
                await self.seed_sample_data()

            logger.info("✅ MongoDB setup complete!")

        finally:
            await self.disconnect()


async def main():
    """Run MongoDB setup."""
    # Get connection string from environment or use default
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DATABASE", "agrovision_ml")

    logger.info(f"Setting up MongoDB: {mongo_url}/{db_name}")

    setup = MongoDBSetup(mongo_url, db_name)
    await setup.setup(drop_existing=False, seed_data=True)


if __name__ == "__main__":
    asyncio.run(main())
