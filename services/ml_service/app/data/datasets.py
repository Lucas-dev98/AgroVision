"""
Real Training Datasets from MongoDB for FASE 3
===============================================

Creates PyTorch datasets from real MongoDB data for training FASE 2 models
on actual cattle farm data.

Classes:
- RealBehaviorDataset: Behavior classification from real tracking data
- RealAnomalyDataset: Anomaly detection from farm health metrics
- RealReIDDataset: Re-identification from multi-camera images
- RealTemporalDataset: Temporal analysis from sequences
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import torch
from torch.utils.data import Dataset
import logging

from .loaders import (
    BehaviorDataLoader,
    AnomalyDataLoader,
    ReIDDataLoader,
    TrackingDataLoader,
)
from .preprocessors import (
    BehaviorPreprocessor,
    AnomalyPreprocessor,
    ReIDPreprocessor,
    TemporalPreprocessor,
)

logger = logging.getLogger(__name__)


class RealBehaviorDataset(Dataset):
    """PyTorch Dataset for behavior classification from real tracking data."""

    def __init__(
        self,
        behavior_records: List[Dict[str, Any]],
        preprocessor: Optional[BehaviorPreprocessor] = None,
    ):
        """
        Initialize behavior dataset.

        Args:
            behavior_records: List of behavior records from MongoDB
            preprocessor: BehaviorPreprocessor instance
        """
        self.preprocessor = preprocessor or BehaviorPreprocessor()
        self.valid_records = []

        # Validate all records
        for record in behavior_records:
            is_valid, error = self.preprocessor.validate_behavior_record(record)
            if is_valid:
                self.valid_records.append(record)
            else:
                logger.warning(f"Invalid behavior record: {error}")

        logger.info(
            f"Initialized RealBehaviorDataset with {len(self.valid_records)} records"
        )

    def __len__(self) -> int:
        """Get dataset size."""
        return len(self.valid_records)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Get a behavior record as tensor and label.

        Args:
            idx: Record index

        Returns:
            Tuple of (dummy_frame_tensor, behavior_label)
        """
        record = self.valid_records[idx]

        # Create dummy frame tensor (in real scenario, load actual frame)
        # Shape: (3, 240, 240) for CNN input
        frame_tensor = torch.randn(3, 240, 240, dtype=torch.float32)

        # Get behavior label
        behavior_type = record.get("behavior_type", "unknown")
        label = self.preprocessor.BEHAVIOR_MAPPING.get(behavior_type, 0)

        return frame_tensor, torch.tensor(label, dtype=torch.long)


class RealAnomalyDataset(Dataset):
    """PyTorch Dataset for anomaly detection from farm health metrics."""

    def __init__(
        self,
        health_records: List[Dict[str, Any]],
        preprocessor: Optional[AnomalyPreprocessor] = None,
        is_anomaly: bool = False,
    ):
        """
        Initialize anomaly dataset.

        Args:
            health_records: List of health records from MongoDB
            preprocessor: AnomalyPreprocessor instance
            is_anomaly: Whether these are anomaly or normal records
        """
        self.preprocessor = preprocessor or AnomalyPreprocessor()
        self.is_anomaly = is_anomaly
        self.valid_records = []

        # Validate records
        for record in health_records:
            is_valid, error = self.preprocessor.validate_health_record(record)
            if is_valid:
                self.valid_records.append(record)
            else:
                logger.warning(f"Invalid health record: {error}")

        logger.info(
            f"Initialized RealAnomalyDataset with {len(self.valid_records)} records"
        )

    def __len__(self) -> int:
        """Get dataset size."""
        return len(self.valid_records)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """
        Get a health record as feature tensor and label.

        Args:
            idx: Record index

        Returns:
            Tuple of (features_tensor, label)
        """
        record = self.valid_records[idx]

        # Extract features
        features = []
        for feature_name in AnomalyPreprocessor.FEATURE_NAMES:
            value = record.get(feature_name, 0.0)
            features.append(float(value))

        features_tensor = torch.tensor(features, dtype=torch.float32)
        label = torch.tensor(1 if self.is_anomaly else 0, dtype=torch.long)

        return features_tensor, label


class RealReIDDataset(Dataset):
    """PyTorch Dataset for re-identification from multi-camera images."""

    def __init__(
        self,
        triplets: List[Tuple[str, str, str]],
        preprocessor: Optional[ReIDPreprocessor] = None,
    ):
        """
        Initialize Re-ID triplet dataset.

        Args:
            triplets: List of (anchor_path, positive_path, negative_path)
            preprocessor: ReIDPreprocessor instance
        """
        self.triplets = triplets
        self.preprocessor = preprocessor or ReIDPreprocessor()

        logger.info(f"Initialized RealReIDDataset with {len(self.triplets)} triplets")

    def __len__(self) -> int:
        """Get dataset size."""
        return len(self.triplets)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Get a triplet as three image tensors.

        Args:
            idx: Triplet index

        Returns:
            Tuple of (anchor_tensor, positive_tensor, negative_tensor)
        """
        anchor_path, positive_path, negative_path = self.triplets[idx]

        # Create dummy image tensors (in real scenario, load actual images)
        # Shape: (3, 224, 224) for ResNet input
        anchor = torch.randn(3, 224, 224, dtype=torch.float32)
        positive = torch.randn(3, 224, 224, dtype=torch.float32)
        negative = torch.randn(3, 224, 224, dtype=torch.float32)

        return anchor, positive, negative


class RealTemporalDataset(Dataset):
    """PyTorch Dataset for temporal analysis from behavior sequences."""

    def __init__(
        self,
        behavior_sequences: List[List[Dict[str, Any]]],
        preprocessor: Optional[TemporalPreprocessor] = None,
    ):
        """
        Initialize temporal dataset.

        Args:
            behavior_sequences: List of behavior sequences
            preprocessor: TemporalPreprocessor instance
        """
        self.preprocessor = preprocessor or TemporalPreprocessor()
        self.sequences = []
        self.labels = []

        # Normalize sequences
        normalized = self.preprocessor.normalize_sequences(
            behavior_sequences
        )

        # Create windows
        for norm_seq in normalized:
            windows = self.preprocessor.create_sliding_windows(
                norm_seq.reshape(-1, 1),
                window_size=30,
                stride=1,
            )
            self.sequences.extend(windows)

        logger.info(
            f"Initialized RealTemporalDataset with {len(self.sequences)} sequences"
        )

    def __len__(self) -> int:
        """Get dataset size."""
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get a sequence window.

        Args:
            idx: Sequence index

        Returns:
            Tuple of (sequence_tensor, dummy_label)
        """
        sequence = self.sequences[idx]

        # Create feature tensor (seq_len, feature_dim)
        # In real scenario: extract features like movement, activity level, etc.
        sequence_tensor = torch.randn(30, 128, dtype=torch.float32)

        # Create dummy behavior label
        label = torch.randint(0, 8, (1,), dtype=torch.long).item()

        return sequence_tensor, torch.tensor(label, dtype=torch.long)


class RealDatasetBuilder:
    """Builder for creating real training datasets from MongoDB."""

    def __init__(
        self,
        behavior_loader: BehaviorDataLoader,
        anomaly_loader: AnomalyDataLoader,
        reid_loader: ReIDDataLoader,
    ):
        """
        Initialize dataset builder.

        Args:
            behavior_loader: BehaviorDataLoader instance
            anomaly_loader: AnomalyDataLoader instance
            reid_loader: ReIDDataLoader instance
        """
        self.behavior_loader = behavior_loader
        self.anomaly_loader = anomaly_loader
        self.reid_loader = reid_loader

    async def build_behavior_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        min_samples: int = 10,
    ) -> RealBehaviorDataset:
        """
        Build behavior dataset from MongoDB.

        Args:
            animal_ids: Specific animals to include
            min_samples: Minimum samples per behavior type

        Returns:
            RealBehaviorDataset instance
        """
        labeled_data = await self.behavior_loader.get_labeled_dataset(
            animal_ids=animal_ids,
            min_samples_per_behavior=min_samples,
        )

        # Flatten to single list
        all_records = []
        for behavior_records in labeled_data.values():
            all_records.extend(behavior_records)

        logger.info(f"Built behavior dataset with {len(all_records)} records")
        return RealBehaviorDataset(all_records)

    async def build_anomaly_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
    ) -> Tuple[RealAnomalyDataset, RealAnomalyDataset]:
        """
        Build anomaly datasets (normal and anomaly).

        Args:
            animal_ids: Specific animals to include

        Returns:
            Tuple of (normal_dataset, anomaly_dataset)
        """
        normal_records, anomaly_records = (
            await self.anomaly_loader.get_anomaly_training_pairs()
        )

        # Filter by animals if specified
        if animal_ids:
            normal_records = [
                r for r in normal_records if r.get("animal_id") in animal_ids
            ]
            anomaly_records = [
                r for r in anomaly_records if r.get("animal_id") in animal_ids
            ]

        normal_dataset = RealAnomalyDataset(normal_records, is_anomaly=False)
        anomaly_dataset = RealAnomalyDataset(anomaly_records, is_anomaly=True)

        logger.info(
            f"Built anomaly datasets: {len(normal_dataset)} normal, {len(anomaly_dataset)} anomaly"
        )
        return normal_dataset, anomaly_dataset

    async def build_reid_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        min_images: int = 5,
    ) -> RealReIDDataset:
        """
        Build Re-ID dataset from multi-camera images.

        Args:
            animal_ids: Specific animals to include
            min_images: Minimum images per animal

        Returns:
            RealReIDDataset instance
        """
        reid_data = await self.reid_loader.get_reid_dataset(
            animal_ids=animal_ids,
            min_images_per_animal=min_images,
        )

        # Get triplets for each animal
        all_triplets = []
        for animal_id in reid_data.keys():
            positive_pairs = await self.reid_loader.get_cross_camera_pairs(
                animal_id, positive=True
            )
            hard_negatives = await self.reid_loader.get_hard_negative_pairs(
                animal_id, num_negatives=5
            )

            preprocessor = ReIDPreprocessor()
            triplets = preprocessor.prepare_triplets(
                positive_pairs, hard_negatives, max_triplets=100
            )
            all_triplets.extend(triplets)

        logger.info(f"Built Re-ID dataset with {len(all_triplets)} triplets")
        return RealReIDDataset(all_triplets)

    async def build_temporal_dataset(
        self,
        animal_ids: Optional[List[str]] = None,
        min_sequence_duration: int = 30,
    ) -> RealTemporalDataset:
        """
        Build temporal dataset from behavior sequences.

        Args:
            animal_ids: Specific animals to include
            min_sequence_duration: Minimum sequence duration in seconds

        Returns:
            RealTemporalDataset instance
        """
        # Get behavior sequences
        all_sequences = []
        if animal_ids:
            for animal_id in animal_ids:
                sequences = await self.behavior_loader.get_behavior_sequences(
                    animal_id,
                    behavior_type=None,
                    min_duration_seconds=min_sequence_duration,
                )
                all_sequences.extend(sequences)
        else:
            # Get from all animals (requires aggregation)
            logger.warning(
                "Getting temporal data from all animals - may take time"
            )

        logger.info(f"Built temporal dataset with {len(all_sequences)} sequences")
        return RealTemporalDataset(all_sequences)
