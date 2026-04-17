"""
Tests for FASE 3 - Real Data Integration
==========================================

Tests for data loaders, preprocessors, and datasets.
Run with: pytest tests/test_data_loaders.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import numpy as np
import torch

from app.data.loaders import (
    TrackingDataLoader,
    BehaviorDataLoader,
    AnomalyDataLoader,
    ReIDDataLoader,
)
from app.data.preprocessors import (
    BehaviorPreprocessor,
    AnomalyPreprocessor,
    ReIDPreprocessor,
    TemporalPreprocessor,
)
from app.data.datasets import (
    RealBehaviorDataset,
    RealAnomalyDataset,
    RealReIDDataset,
    RealTemporalDataset,
)


class TestBehaviorPreprocessor:
    """Test behavior data preprocessing."""

    def test_validate_valid_behavior_record(self):
        """Test validation of valid behavior record."""
        record = {
            "animal_id": "cow_001",
            "behavior_type": "grazing",
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": 300,
        }
        is_valid, error = BehaviorPreprocessor.validate_behavior_record(record)
        assert is_valid is True
        assert error == ""

    def test_validate_missing_required_field(self):
        """Test validation fails for missing required field."""
        record = {
            "animal_id": "cow_001",
            "behavior_type": "grazing",
            # missing timestamp and duration_seconds
        }
        is_valid, error = BehaviorPreprocessor.validate_behavior_record(record)
        assert is_valid is False
        assert "Missing required field" in error

    def test_validate_invalid_behavior_type(self):
        """Test validation fails for invalid behavior type."""
        record = {
            "animal_id": "cow_001",
            "behavior_type": "invalid_behavior",
            "timestamp": datetime.utcnow().isoformat(),
            "duration_seconds": 300,
        }
        is_valid, error = BehaviorPreprocessor.validate_behavior_record(record)
        assert is_valid is False
        assert "Invalid behavior type" in error

    def test_normalize_sequences(self):
        """Test sequence normalization."""
        sequences = [
            [
                {"behavior_type": "grazing"},
                {"behavior_type": "walking"},
                {"behavior_type": "resting"},
            ]
        ]
        normalized = BehaviorPreprocessor.normalize_sequences(sequences)
        assert len(normalized) > 0
        assert normalized[0].shape == (30,)  # MAX_SEQUENCE_LENGTH

    def test_extract_temporal_features(self):
        """Test temporal feature extraction."""
        records = [
            {
                "behavior_type": "grazing",
                "duration_seconds": 300,
            },
            {
                "behavior_type": "walking",
                "duration_seconds": 60,
            },
        ]
        features = BehaviorPreprocessor.extract_temporal_features(records)
        assert features["total_duration"] == 360
        assert features["avg_duration"] == 180
        assert features["unique_behaviors"] == 2


class TestAnomalyPreprocessor:
    """Test anomaly data preprocessing."""

    def test_validate_valid_health_record(self):
        """Test validation of valid health record."""
        record = {
            "animal_id": "cow_001",
            "timestamp": datetime.utcnow().isoformat(),
            "activity_level": 0.7,
        }
        is_valid, error = AnomalyPreprocessor.validate_health_record(record)
        assert is_valid is True
        assert error == ""

    def test_validate_missing_features(self):
        """Test validation fails without features."""
        record = {
            "animal_id": "cow_001",
            "timestamp": datetime.utcnow().isoformat(),
        }
        is_valid, error = AnomalyPreprocessor.validate_health_record(record)
        assert is_valid is False
        assert "No valid features" in error

    def test_normalize_features(self):
        """Test feature normalization."""
        records = [
            {
                "animal_id": "cow_001",
                "activity_level": 0.5,
                "movement_distance": 100,
                "heart_rate": 60,
                "body_temperature": 38.5,
                "feed_consumption": 10,
                "water_consumption": 20,
            },
            {
                "animal_id": "cow_001",
                "activity_level": 0.7,
                "movement_distance": 150,
                "heart_rate": 70,
                "body_temperature": 38.6,
                "feed_consumption": 12,
                "water_consumption": 22,
            },
        ]
        normalized, params = AnomalyPreprocessor.normalize_features(records)
        assert normalized.shape == (2, 6)
        assert len(params) == 6
        # Normalized values should have mean ~0, std ~1
        assert np.abs(np.mean(normalized)) < 0.5
        assert np.abs(np.std(normalized) - 1.0) < 0.5

    def test_compute_anomaly_scores(self):
        """Test anomaly score computation."""
        errors = np.array([0.1, 0.15, 0.2, 0.25, 0.3, 0.5, 0.7, 0.9, 1.0, 2.0])
        scores = AnomalyPreprocessor.compute_anomaly_scores(errors, percentile=95)
        assert "threshold" in scores
        assert "mean_error" in scores
        assert "std_error" in scores
        assert scores["threshold"] > 0


class TestReIDPreprocessor:
    """Test Re-ID data preprocessing."""

    def test_validate_valid_image_record(self):
        """Test validation of valid image record."""
        record = {
            "animal_id": "cow_001",
            "camera_id": "cam_001",
            "image_path": "/path/to/image.jpg",
            "timestamp": datetime.utcnow().isoformat(),
        }
        is_valid, error = ReIDPreprocessor.validate_image_record(record)
        assert is_valid is True
        assert error == ""

    def test_validate_invalid_format(self):
        """Test validation fails for invalid format."""
        record = {
            "animal_id": "cow_001",
            "camera_id": "cam_001",
            "image_path": "/path/to/image.txt",
            "timestamp": datetime.utcnow().isoformat(),
        }
        is_valid, error = ReIDPreprocessor.validate_image_record(record)
        assert is_valid is False
        assert "Invalid image format" in error

    def test_prepare_triplets(self):
        """Test triplet preparation."""
        positive_pairs = [
            ({"image_path": "pos1.jpg"}, {"image_path": "pos2.jpg"}),
        ]
        hard_negatives = [
            ({"image_path": "neg1.jpg"}, {"image_path": "neg2.jpg"}),
        ]
        triplets = ReIDPreprocessor.prepare_triplets(
            positive_pairs, hard_negatives, max_triplets=10
        )
        assert len(triplets) > 0
        assert all(len(t) == 3 for t in triplets)


class TestTemporalPreprocessor:
    """Test temporal data preprocessing."""

    def test_create_sliding_windows(self):
        """Test sliding window creation."""
        features = np.random.randn(100, 5)
        windows = TemporalPreprocessor.create_sliding_windows(
            features, window_size=30, stride=1
        )
        assert len(windows) == 100 - 30 + 1
        assert all(w.shape == (30, 5) for w in windows)

    def test_pad_sequences(self):
        """Test sequence padding."""
        seq1 = np.random.randn(20, 5)
        seq2 = np.random.randn(35, 5)
        sequences = [seq1, seq2]
        padded = TemporalPreprocessor.pad_sequences(sequences, target_length=30)
        assert padded.shape == (2, 30, 5)

    def test_normalize_temporal_features(self):
        """Test temporal feature normalization."""
        seq1 = np.random.randn(20, 5)
        seq2 = np.random.randn(20, 5)
        sequences = [seq1, seq2]
        normalized, params = (
            TemporalPreprocessor.normalize_temporal_features(sequences)
        )
        assert normalized.shape == (2, 20, 5)
        assert len(params) == 5


class TestRealBehaviorDataset:
    """Test real behavior dataset."""

    def test_dataset_creation(self):
        """Test dataset creation."""
        records = [
            {
                "animal_id": "cow_001",
                "behavior_type": "grazing",
                "timestamp": datetime.utcnow().isoformat(),
                "duration_seconds": 300,
            },
            {
                "animal_id": "cow_001",
                "behavior_type": "walking",
                "timestamp": datetime.utcnow().isoformat(),
                "duration_seconds": 60,
            },
        ]
        dataset = RealBehaviorDataset(records)
        assert len(dataset) == 2

    def test_dataset_getitem(self):
        """Test dataset item retrieval."""
        records = [
            {
                "animal_id": "cow_001",
                "behavior_type": "grazing",
                "timestamp": datetime.utcnow().isoformat(),
                "duration_seconds": 300,
            },
        ]
        dataset = RealBehaviorDataset(records)
        frame, label = dataset[0]
        assert isinstance(frame, torch.Tensor)
        assert frame.shape == (3, 240, 240)
        assert isinstance(label, torch.Tensor)
        assert label.dtype == torch.long


class TestRealAnomalyDataset:
    """Test real anomaly dataset."""

    def test_dataset_creation_normal(self):
        """Test dataset creation for normal records."""
        records = [
            {
                "animal_id": "cow_001",
                "timestamp": datetime.utcnow().isoformat(),
                "activity_level": 0.7,
                "movement_distance": 100,
                "heart_rate": 60,
                "body_temperature": 38.5,
                "feed_consumption": 10,
                "water_consumption": 20,
            },
        ]
        dataset = RealAnomalyDataset(records, is_anomaly=False)
        assert len(dataset) == 1

    def test_dataset_getitem_normal(self):
        """Test dataset item retrieval for normal records."""
        records = [
            {
                "animal_id": "cow_001",
                "timestamp": datetime.utcnow().isoformat(),
                "activity_level": 0.7,
                "movement_distance": 100,
                "heart_rate": 60,
                "body_temperature": 38.5,
                "feed_consumption": 10,
                "water_consumption": 20,
            },
        ]
        dataset = RealAnomalyDataset(records, is_anomaly=False)
        features, label = dataset[0]
        assert isinstance(features, torch.Tensor)
        assert features.shape == (6,)  # 6 features
        assert label.item() == 0  # Normal


class TestRealReIDDataset:
    """Test real Re-ID dataset."""

    def test_dataset_creation(self):
        """Test dataset creation."""
        triplets = [
            ("img1.jpg", "img2.jpg", "img3.jpg"),
            ("img4.jpg", "img5.jpg", "img6.jpg"),
        ]
        dataset = RealReIDDataset(triplets)
        assert len(dataset) == 2

    def test_dataset_getitem(self):
        """Test dataset item retrieval."""
        triplets = [
            ("img1.jpg", "img2.jpg", "img3.jpg"),
        ]
        dataset = RealReIDDataset(triplets)
        anchor, positive, negative = dataset[0]
        assert isinstance(anchor, torch.Tensor)
        assert anchor.shape == (3, 224, 224)
        assert positive.shape == (3, 224, 224)
        assert negative.shape == (3, 224, 224)


class TestRealTemporalDataset:
    """Test real temporal dataset."""

    def test_dataset_creation(self):
        """Test dataset creation."""
        sequences = [
            [
                {"behavior_type": "grazing"},
                {"behavior_type": "walking"},
                {"behavior_type": "resting"},
            ] * 15  # Create enough for min sequence
        ]
        dataset = RealTemporalDataset(sequences)
        assert len(dataset) > 0

    def test_dataset_getitem(self):
        """Test dataset item retrieval."""
        sequences = [
            [
                {"behavior_type": "grazing"},
                {"behavior_type": "walking"},
                {"behavior_type": "resting"},
            ] * 15
        ]
        dataset = RealTemporalDataset(sequences)
        if len(dataset) > 0:
            sequence, label = dataset[0]
            assert isinstance(sequence, torch.Tensor)
            assert sequence.shape[1] == 128  # Feature dimension
            assert isinstance(label, torch.Tensor)


# Async tests for loaders
@pytest.mark.asyncio
class TestDataLoaders:
    """Test MongoDB data loaders."""

    async def test_tracking_loader_init(self):
        """Test tracking loader initialization."""
        mock_db = AsyncMock()
        loader = TrackingDataLoader(mock_db)
        assert loader.db is not None
        assert loader.collection is not None

    async def test_behavior_loader_init(self):
        """Test behavior loader initialization."""
        mock_db = AsyncMock()
        loader = BehaviorDataLoader(mock_db)
        assert loader.db is not None

    async def test_anomaly_loader_init(self):
        """Test anomaly loader initialization."""
        mock_db = AsyncMock()
        loader = AnomalyDataLoader(mock_db)
        assert loader.db is not None

    async def test_reid_loader_init(self):
        """Test Re-ID loader initialization."""
        mock_db = AsyncMock()
        loader = ReIDDataLoader(mock_db)
        assert loader.db is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
