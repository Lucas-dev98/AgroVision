"""
Real Data Integration with Training Pipeline - FASE 3.2
=========================================================

Integrates real MongoDB data into the training pipeline.

Run training with real data:
python -m app.training.train \\
  --model behavior \\
  --epochs 50 \\
  --use-real-data \\
  --animals cow_001,cow_002,cow_003 \\
  --device cuda
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

from app.data.loaders import (
    BehaviorDataLoader,
    AnomalyDataLoader,
    ReIDDataLoader,
    TrackingDataLoader,
)
from app.data.datasets import (
    RealBehaviorDataset,
    RealAnomalyDataset,
    RealReIDDataset,
    RealTemporalDataset,
    RealDatasetBuilder,
)
from app.training import (
    BehaviorDataset,
    AnomalyDataset,
    TemporalDataset,
)

logger = logging.getLogger(__name__)


class RealDataTrainingManager:
    """Manager for training with real MongoDB data."""

    def __init__(
        self,
        mongodb_url: str = "mongodb://localhost:27017",
        database_name: str = "agrovision_ml",
    ):
        """
        Initialize training manager.

        Args:
            mongodb_url: MongoDB connection URL
            database_name: Database name
        """
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client = None
        self.db = None
        self.builder = None

    async def connect(self):
        """Connect to MongoDB."""
        self.client = AsyncIOMotorClient(self.mongodb_url)
        self.db = self.client[self.database_name]

        self.builder = RealDatasetBuilder(
            behavior_loader=BehaviorDataLoader(self.db),
            anomaly_loader=AnomalyDataLoader(self.db),
            reid_loader=ReIDDataLoader(self.db),
        )

        logger.info(f"Connected to {self.database_name}")

    async def disconnect(self):
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def get_behavior_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        min_samples: int = 10,
        split: Tuple[float, float, float] = (0.7, 0.15, 0.15),
    ) -> Tuple[RealBehaviorDataset, RealBehaviorDataset, RealBehaviorDataset]:
        """
        Get behavior dataset split into train/val/test.

        Args:
            animal_ids: Specific animals to include
            min_samples: Minimum samples per behavior type
            split: (train_ratio, val_ratio, test_ratio)

        Returns:
            Tuple of (train_dataset, val_dataset, test_dataset)
        """
        if not await self._check_data_availability("behavior_patterns"):
            raise RuntimeError(
                "No behavior data available. "
                "Run: python -m app.data.setup_mongo"
            )

        dataset = await self.builder.build_behavior_dataset(
            animal_ids=animal_ids,
            min_samples=min_samples,
        )

        # Split dataset
        train_size = int(len(dataset) * split[0])
        val_size = int(len(dataset) * split[1])

        from torch.utils.data import random_split

        train_ds, val_ds, test_ds = random_split(
            dataset,
            [train_size, val_size, len(dataset) - train_size - val_size],
        )

        logger.info(
            f"Behavior dataset split: "
            f"train={len(train_ds)}, val={len(val_ds)}, test={len(test_ds)}"
        )

        return (
            RealBehaviorDataset(dataset.valid_records[: train_size]),
            RealBehaviorDataset(
                dataset.valid_records[train_size : train_size + val_size]
            ),
            RealBehaviorDataset(dataset.valid_records[train_size + val_size :]),
        )

    async def get_anomaly_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        split: Tuple[float, float, float] = (0.7, 0.15, 0.15),
    ) -> Tuple[
        Tuple[RealAnomalyDataset, RealAnomalyDataset],
        Tuple[RealAnomalyDataset, RealAnomalyDataset],
        Tuple[RealAnomalyDataset, RealAnomalyDataset],
    ]:
        """
        Get anomaly datasets (normal and anomaly) split into train/val/test.

        Args:
            animal_ids: Specific animals to include
            split: (train_ratio, val_ratio, test_ratio)

        Returns:
            Tuple of ((train_normal, train_anomaly), (val_normal, val_anomaly), (test_normal, test_anomaly))
        """
        if not await self._check_data_availability("animal_health"):
            raise RuntimeError(
                "No health data available. "
                "Run: python -m app.data.setup_mongo"
            )

        normal_ds, anomaly_ds = await self.builder.build_anomaly_dataset(
            animal_ids=animal_ids
        )

        from torch.utils.data import random_split

        # Split both datasets
        normal_split_size = int(len(normal_ds) * split[0])
        normal_split_val = int(len(normal_ds) * split[1])

        anomaly_split_size = int(len(anomaly_ds) * split[0])
        anomaly_split_val = int(len(anomaly_ds) * split[1])

        train_normal, val_normal, test_normal = random_split(
            normal_ds,
            [
                normal_split_size,
                normal_split_val,
                len(normal_ds) - normal_split_size - normal_split_val,
            ],
        )

        train_anomaly, val_anomaly, test_anomaly = random_split(
            anomaly_ds,
            [
                anomaly_split_size,
                anomaly_split_val,
                len(anomaly_ds) - anomaly_split_size - anomaly_split_val,
            ],
        )

        logger.info(
            f"Anomaly dataset split: "
            f"train=({len(train_normal)}, {len(train_anomaly)}), "
            f"val=({len(val_normal)}, {len(val_anomaly)}), "
            f"test=({len(test_normal)}, {len(test_anomaly)})"
        )

        return (
            (train_normal, train_anomaly),
            (val_normal, val_anomaly),
            (test_normal, test_anomaly),
        )

    async def get_reid_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        min_images: int = 5,
    ) -> RealReIDDataset:
        """
        Get Re-ID dataset for training.

        Args:
            animal_ids: Specific animals to include
            min_images: Minimum images per animal

        Returns:
            RealReIDDataset instance
        """
        if not await self._check_data_availability("animal_reid"):
            raise RuntimeError(
                "No Re-ID data available. "
                "Run: python -m app.data.setup_mongo"
            )

        dataset = await self.builder.build_reid_dataset(
            animal_ids=animal_ids,
            min_images=min_images,
        )

        logger.info(f"Re-ID dataset loaded: {len(dataset)} triplets")

        return dataset

    async def get_temporal_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        min_duration: int = 30,
    ) -> RealTemporalDataset:
        """
        Get temporal dataset for LSTM training.

        Args:
            animal_ids: Specific animals to include
            min_duration: Minimum sequence duration

        Returns:
            RealTemporalDataset instance
        """
        if not await self._check_data_availability("behavior_patterns"):
            raise RuntimeError(
                "No behavior data available. "
                "Run: python -m app.data.setup_mongo"
            )

        dataset = await self.builder.build_temporal_dataset(
            animal_ids=animal_ids,
            min_sequence_duration=min_duration,
        )

        logger.info(f"Temporal dataset loaded: {len(dataset)} sequences")

        return dataset

    async def _check_data_availability(self, collection_name: str) -> bool:
        """
        Check if collection has data.

        Args:
            collection_name: Collection to check

        Returns:
            True if collection has documents
        """
        collection = self.db[collection_name]
        count = await collection.count_documents({})
        return count > 0

    async def get_data_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available data.

        Returns:
            Dictionary with data statistics
        """
        stats = {}

        # Count documents in each collection
        for coll_name in [
            "tracking",
            "behavior_patterns",
            "animal_health",
            "animal_reid",
        ]:
            collection = self.db[coll_name]
            stats[coll_name] = await collection.count_documents({})

        # Count unique animals
        behavior_collection = self.db.behavior_patterns
        unique_animals = await behavior_collection.distinct("animal_id")
        stats["unique_animals"] = len(unique_animals)

        # Count behavior types
        unique_behaviors = await behavior_collection.distinct("behavior_type")
        stats["behavior_types"] = unique_behaviors

        # Count anomalies
        health_collection = self.db.animal_health
        anomalies = await health_collection.count_documents({"is_anomaly": True})
        stats["anomalies"] = anomalies

        logger.info(f"Data statistics: {stats}")
        return stats

    async def validate_data_quality(self) -> Dict[str, Any]:
        """
        Validate data quality across all collections.

        Returns:
            Dictionary with validation results
        """
        from app.data.preprocessors import (
            BehaviorPreprocessor,
            AnomalyPreprocessor,
            ReIDPreprocessor,
        )

        results = {"valid": {}, "invalid": {}, "warnings": []}

        # Validate behavior data
        behavior_collection = self.db.behavior_patterns
        behavior_records = await behavior_collection.find({}).to_list(None)

        valid_behavior = 0
        invalid_behavior = 0

        for record in behavior_records:
            is_valid, error = BehaviorPreprocessor.validate_behavior_record(record)
            if is_valid:
                valid_behavior += 1
            else:
                invalid_behavior += 1

        results["valid"]["behavior"] = valid_behavior
        results["invalid"]["behavior"] = invalid_behavior

        # Validate health data
        health_collection = self.db.animal_health
        health_records = await health_collection.find({}).to_list(None)

        valid_health = 0
        invalid_health = 0

        for record in health_records:
            is_valid, error = AnomalyPreprocessor.validate_health_record(record)
            if is_valid:
                valid_health += 1
            else:
                invalid_health += 1

        results["valid"]["health"] = valid_health
        results["invalid"]["health"] = invalid_health

        # Validate Re-ID data
        reid_collection = self.db.animal_reid
        reid_records = await reid_collection.find({}).to_list(None)

        valid_reid = 0
        invalid_reid = 0

        for record in reid_records:
            is_valid, error = ReIDPreprocessor.validate_image_record(record)
            if is_valid:
                valid_reid += 1
            else:
                invalid_reid += 1

        results["valid"]["reid"] = valid_reid
        results["invalid"]["reid"] = invalid_reid

        logger.info(f"Data quality validation: {results}")
        return results


async def main():
    """Example usage of RealDataTrainingManager."""
    manager = RealDataTrainingManager()

    try:
        await manager.connect()

        # Get statistics
        stats = await manager.get_data_statistics()
        print(f"📊 Data Statistics: {stats}")

        # Validate data quality
        quality = await manager.validate_data_quality()
        print(f"✅ Data Quality: {quality}")

        # Load datasets
        if stats["behavior_patterns"] > 0:
            train_ds, val_ds, test_ds = await manager.get_behavior_dataset()
            print(f"✅ Behavior Dataset: train={len(train_ds)}, val={len(val_ds)}, test={len(test_ds)}")

        if stats["animal_health"] > 0:
            (train_normal, train_anomaly), _, _ = (
                await manager.get_anomaly_dataset()
            )
            print(
                f"✅ Anomaly Dataset: train_normal={len(train_normal)}, train_anomaly={len(train_anomaly)}"
            )

        if stats["animal_reid"] > 0:
            reid_ds = await manager.get_reid_dataset()
            print(f"✅ Re-ID Dataset: {len(reid_ds)} triplets")

    finally:
        await manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
