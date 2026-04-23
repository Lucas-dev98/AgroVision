"""
MongoDB Data Loaders for FASE 3
================================

Loads real cattle tracking and behavior data from MongoDB for training FASE 2 models.

Classes:
- TrackingDataLoader: Loads tracking records (position, trajectory)
- BehaviorDataLoader: Loads annotated behavior labels and frame sequences
- AnomalyDataLoader: Loads anomaly annotations and baseline features
- ReIDDataLoader: Loads multi-camera cattle images for re-identification training
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import timezone, datetime, timedelta
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class TrackingDataLoader:
    """Loads cattle tracking records from MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize tracking data loader.

        Args:
            db: Motor AsyncIOMotorDatabase instance
        """
        self.db = db
        self.collection = db.tracking

    async def get_animal_trajectories(
        self,
        animal_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get trajectory records for a specific animal.

        Args:
            animal_id: Cattle identifier
            start_date: Start timestamp (default: last 7 days)
            end_date: End timestamp (default: now)
            limit: Maximum records to return

        Returns:
            List of tracking records with position, timestamp, confidence
        """
        if start_date is None:
            start_date = datetime.now(timezone.utc) - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        query = {
            "animal_id": animal_id,
            "timestamp": {"$gte": start_date, "$lte": end_date},
        }

        cursor = self.collection.find(query).limit(limit).sort("timestamp", 1)
        records = await cursor.to_list(length=limit)

        logger.info(
            f"Loaded {len(records)} tracking records for animal {animal_id}"
        )
        return records

    async def get_multi_animal_trajectories(
        self,
        animal_ids: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get trajectories for multiple animals.

        Args:
            animal_ids: List of cattle identifiers
            start_date: Start timestamp
            end_date: End timestamp

        Returns:
            Dictionary mapping animal_id to list of tracking records
        """
        results = {}
        tasks = [
            self.get_animal_trajectories(aid, start_date, end_date)
            for aid in animal_ids
        ]
        trajectories = await asyncio.gather(*tasks)

        for animal_id, trajectory in zip(animal_ids, trajectories):
            results[animal_id] = trajectory

        return results

    async def get_recent_tracking_data(
        self, hours: int = 24, limit: int = 10000
    ) -> List[Dict[str, Any]]:
        """
        Get most recent tracking data across all animals.

        Args:
            hours: Number of hours to look back
            limit: Maximum records to return

        Returns:
            List of recent tracking records
        """
        start_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        query = {"timestamp": {"$gte": start_date}}

        cursor = (
            self.collection.find(query)
            .limit(limit)
            .sort("timestamp", -1)
        )
        records = await cursor.to_list(length=limit)

        logger.info(f"Loaded {len(records)} recent tracking records")
        return records


class BehaviorDataLoader:
    """Loads annotated behavior data from MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize behavior data loader.

        Args:
            db: Motor AsyncIOMotorDatabase instance
        """
        self.db = db
        self.collection = db.behavior_patterns
        self.tracking_collection = db.tracking

    async def get_animal_behavior_patterns(
        self,
        animal_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get behavior pattern annotations for an animal.

        Args:
            animal_id: Cattle identifier
            start_date: Start timestamp
            end_date: End timestamp

        Returns:
            List of behavior records with labels and confidence
        """
        if start_date is None:
            start_date = datetime.now(timezone.utc) - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now(timezone.utc)

        query = {
            "animal_id": animal_id,
            "timestamp": {"$gte": start_date, "$lte": end_date},
        }

        cursor = (
            self.collection.find(query)
            .sort("timestamp", 1)
        )
        records = await cursor.to_list(length=None)

        logger.info(
            f"Loaded {len(records)} behavior patterns for animal {animal_id}"
        )
        return records

    async def get_behavior_sequences(
        self,
        animal_id: str,
        behavior_type: str,
        min_duration_seconds: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get behavior sequences of specific type with minimum duration.

        Args:
            animal_id: Cattle identifier
            behavior_type: Type of behavior (e.g., "grazing", "walking", "resting")
            min_duration_seconds: Minimum sequence duration in seconds

        Returns:
            List of behavior sequences with tracking frames
        """
        behavior_records = await self.collection.find(
            {
                "animal_id": animal_id,
                "behavior_type": behavior_type,
                "duration_seconds": {"$gte": min_duration_seconds},
            }
        ).to_list(length=None)

        logger.info(
            f"Loaded {len(behavior_records)} {behavior_type} sequences for animal {animal_id}"
        )
        return behavior_records

    async def get_labeled_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        behavior_types: Optional[List[str]] = None,
        min_samples_per_behavior: int = 10,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get labeled dataset for training, grouped by behavior type.

        Args:
            animal_ids: Specific animals to include (None = all)
            behavior_types: Behavior types to include (None = all)
            min_samples_per_behavior: Minimum samples per behavior type

        Returns:
            Dictionary mapping behavior_type to list of labeled records
        """
        query = {}
        if animal_ids:
            query["animal_id"] = {"$in": animal_ids}
        if behavior_types:
            query["behavior_type"] = {"$in": behavior_types}

        cursor = self.collection.find(query)
        all_records = await cursor.to_list(length=None)

        # Group by behavior type
        grouped = {}
        for record in all_records:
            behavior = record.get("behavior_type", "unknown")
            if behavior not in grouped:
                grouped[behavior] = []
            grouped[behavior].append(record)

        # Filter by minimum samples
        result = {
            b: records
            for b, records in grouped.items()
            if len(records) >= min_samples_per_behavior
        }

        logger.info(
            f"Loaded labeled dataset: {[(b, len(r)) for b, r in result.items()]}"
        )
        return result


class AnomalyDataLoader:
    """Loads anomaly data from MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize anomaly data loader.

        Args:
            db: Motor AsyncIOMotorDatabase instance
        """
        self.db = db
        self.collection = db.animal_health

    async def get_normal_baselines(
        self,
        animal_id: str,
        window_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Get normal behavior baselines for establishing anomaly thresholds.

        Args:
            animal_id: Cattle identifier
            window_days: Days of normal data to analyze

        Returns:
            Dictionary with baseline metrics (activity, movement, etc.)
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=window_days)
        query = {
            "animal_id": animal_id,
            "timestamp": {"$gte": start_date},
            "is_anomaly": {"$exists": False},  # Non-annotated as anomaly
        }

        records = await self.collection.find(query).to_list(length=None)

        if not records:
            logger.warning(f"No baseline data found for animal {animal_id}")
            return {}

        # Calculate statistics
        activity_levels = [r.get("activity_level", 0) for r in records]
        movement_distances = [r.get("movement_distance", 0) for r in records]

        baseline = {
            "animal_id": animal_id,
            "avg_activity": sum(activity_levels) / len(activity_levels),
            "max_activity": max(activity_levels),
            "avg_movement": sum(movement_distances) / len(movement_distances),
            "max_movement": max(movement_distances),
            "sample_count": len(records),
        }

        logger.info(f"Computed baselines for animal {animal_id}: {baseline}")
        return baseline

    async def get_annotated_anomalies(
        self,
        animal_ids: Optional[List[str]] = None,
        anomaly_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get annotated anomaly records for anomaly detector training.

        Args:
            animal_ids: Specific animals to include
            anomaly_types: Types of anomalies (e.g., "illness", "injury", "stress")

        Returns:
            List of anomaly records with labels
        """
        query = {"is_anomaly": True}
        if animal_ids:
            query["animal_id"] = {"$in": animal_ids}
        if anomaly_types:
            query["anomaly_type"] = {"$in": anomaly_types}

        cursor = self.collection.find(query)
        anomalies = await cursor.to_list(length=None)

        logger.info(f"Loaded {len(anomalies)} annotated anomalies")
        return anomalies

    async def get_anomaly_training_pairs(
        self,
        test_ratio: float = 0.2,
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Get normal and anomaly records for unsupervised training.

        Args:
            test_ratio: Ratio for test split

        Returns:
            Tuple of (normal_records, anomaly_records)
        """
        normal = await self.collection.find(
            {"is_anomaly": {"$ne": True}}
        ).to_list(length=None)
        anomaly = await self.collection.find(
            {"is_anomaly": True}
        ).to_list(length=None)

        logger.info(
            f"Loaded {len(normal)} normal and {len(anomaly)} anomaly records"
        )
        return normal, anomaly


class ReIDDataLoader:
    """Loads multi-camera cattle images for re-identification."""

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize Re-ID data loader.

        Args:
            db: Motor AsyncIOMotorDatabase instance
        """
        self.db = db
        self.collection = db.animal_reid

    async def get_animal_images_by_camera(
        self,
        animal_id: str,
        camera_ids: Optional[List[str]] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all images of an animal from specific cameras.

        Args:
            animal_id: Cattle identifier
            camera_ids: Specific cameras to include (None = all)

        Returns:
            Dictionary mapping camera_id to list of image records
        """
        query = {"animal_id": animal_id}
        if camera_ids:
            query["camera_id"] = {"$in": camera_ids}

        cursor = self.collection.find(query)
        records = await cursor.to_list(length=None)

        # Group by camera
        grouped = {}
        for record in records:
            camera = record.get("camera_id", "unknown")
            if camera not in grouped:
                grouped[camera] = []
            grouped[camera].append(record)

        logger.info(
            f"Loaded {len(records)} Re-ID images for animal {animal_id}"
        )
        return grouped

    async def get_cross_camera_pairs(
        self,
        animal_id: str,
        positive: bool = True,
    ) -> List[Tuple[Dict, Dict]]:
        """
        Get image pairs for triplet loss training.

        Args:
            animal_id: Cattle identifier
            positive: True for same-animal pairs, False for different-animal pairs

        Returns:
            List of (image1, image2) tuples for training
        """
        images_by_camera = await self.get_animal_images_by_camera(
            animal_id
        )
        pairs = []

        if positive:
            # Same animal, different cameras
            cameras = list(images_by_camera.keys())
            for i, cam1 in enumerate(cameras):
                for cam2 in cameras[i + 1 :]:
                    images1 = images_by_camera[cam1]
                    images2 = images_by_camera[cam2]
                    for img1 in images1[:5]:  # Limit to 5 per camera
                        for img2 in images2[:5]:
                            pairs.append((img1, img2))

        logger.info(
            f"Generated {len(pairs)} image pairs for animal {animal_id}"
        )
        return pairs

    async def get_reid_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        min_images_per_animal: int = 5,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get Re-ID dataset with minimum images per animal.

        Args:
            animal_ids: Specific animals to include
            min_images_per_animal: Minimum images per animal

        Returns:
            Dictionary mapping animal_id to list of image records
        """
        if animal_ids:
            query = {"animal_id": {"$in": animal_ids}}
        else:
            query = {}

        cursor = self.collection.find(query)
        records = await cursor.to_list(length=None)

        # Group by animal
        grouped = {}
        for record in records:
            animal = record.get("animal_id", "unknown")
            if animal not in grouped:
                grouped[animal] = []
            grouped[animal].append(record)

        # Filter by minimum images
        result = {
            a: images
            for a, images in grouped.items()
            if len(images) >= min_images_per_animal
        }

        logger.info(
            f"Loaded Re-ID dataset: {[(a, len(i)) for a, i in result.items()]}"
        )
        return result

    async def get_hard_negative_pairs(
        self,
        positive_animal_id: str,
        num_negatives: int = 10,
    ) -> List[Tuple[Dict, Dict]]:
        """
        Get hard negative pairs (similar-looking different animals).

        Args:
            positive_animal_id: Reference animal
            num_negatives: Number of negative animals to include

        Returns:
            List of (positive, negative) image pairs
        """
        # Get positive images
        positive_images = await self.collection.find(
            {"animal_id": positive_animal_id}
        ).to_list(length=None)

        # Get negative images from other animals
        negative_records = await self.collection.find(
            {"animal_id": {"$ne": positive_animal_id}}
        ).to_list(length=None)

        # Group negatives by animal
        negative_by_animal = {}
        for record in negative_records:
            animal = record.get("animal_id")
            if animal not in negative_by_animal:
                negative_by_animal[animal] = []
            negative_by_animal[animal].append(record)

        # Create pairs
        pairs = []
        neg_animals = list(negative_by_animal.keys())[:num_negatives]
        for pos_img in positive_images[:10]:  # Limit positive images
            for neg_animal in neg_animals:
                neg_images = negative_by_animal[neg_animal]
                for neg_img in neg_images[:2]:
                    pairs.append((pos_img, neg_img))

        logger.info(
            f"Generated {len(pairs)} hard negative pairs for {positive_animal_id}"
        )
        return pairs
