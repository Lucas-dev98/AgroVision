"""
Data Preprocessing and Validation for FASE 3
==============================================

Handles validation, normalization, and preprocessing of real cattle data
before training FASE 2 models.

Classes:
- BehaviorPreprocessor: Validates and preprocesses behavior data
- AnomalyPreprocessor: Normalizes health metrics and anomaly features
- ReIDPreprocessor: Processes and validates cattle images
- TemporalPreprocessor: Handles time-series data normalization
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class BehaviorType(str, Enum):
    """Valid cattle behavior types."""
    GRAZING = "grazing"
    WALKING = "walking"
    RESTING = "resting"
    DRINKING = "drinking"
    EATING = "eating"
    STANDING = "standing"
    RUNNING = "running"
    LYING = "lying"


class BehaviorPreprocessor:
    """Validates and preprocesses behavior data for CNN/LSTM models."""

    BEHAVIOR_MAPPING = {
        "grazing": 0,
        "walking": 1,
        "resting": 2,
        "drinking": 3,
        "eating": 4,
        "standing": 5,
        "running": 6,
        "lying": 7,
    }

    MIN_SEQUENCE_LENGTH = 5
    MAX_SEQUENCE_LENGTH = 30
    REQUIRED_FIELDS = ["animal_id", "behavior_type", "timestamp", "duration_seconds"]

    @classmethod
    def validate_behavior_record(cls, record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a single behavior record.

        Args:
            record: Behavior record from MongoDB

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in record:
                return False, f"Missing required field: {field}"

        # Validate behavior type
        if record["behavior_type"] not in cls.BEHAVIOR_MAPPING:
            return False, f"Invalid behavior type: {record['behavior_type']}"

        # Validate duration
        duration = record.get("duration_seconds", 0)
        if duration <= 0:
            return False, f"Invalid duration: {duration}"

        # Validate timestamp
        try:
            if isinstance(record["timestamp"], str):
                datetime.fromisoformat(record["timestamp"])
        except (ValueError, TypeError):
            return False, f"Invalid timestamp: {record['timestamp']}"

        return True, ""

    @classmethod
    def normalize_sequences(
        cls,
        sequences: List[List[Dict[str, Any]]],
    ) -> List[np.ndarray]:
        """
        Normalize behavior sequences to fixed length.

        Args:
            sequences: List of behavior sequences

        Returns:
            List of normalized behavior indices (padded/truncated to max length)
        """
        normalized = []

        for seq in sequences:
            # Extract behavior indices
            indices = [
                cls.BEHAVIOR_MAPPING.get(record["behavior_type"], -1)
                for record in seq
            ]

            # Filter out invalid indices
            indices = [i for i in indices if i >= 0]

            # Normalize length
            if len(indices) < cls.MIN_SEQUENCE_LENGTH:
                continue  # Skip too short sequences

            if len(indices) > cls.MAX_SEQUENCE_LENGTH:
                indices = indices[:cls.MAX_SEQUENCE_LENGTH]
            else:
                # Pad with zeros
                indices = indices + [0] * (cls.MAX_SEQUENCE_LENGTH - len(indices))

            normalized.append(np.array(indices, dtype=np.int32))

        logger.info(f"Normalized {len(normalized)} sequences")
        return normalized

    @classmethod
    def extract_temporal_features(
        cls,
        records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Extract temporal features from behavior records.

        Args:
            records: Sorted behavior records

        Returns:
            Dictionary with temporal statistics
        """
        if not records:
            return {}

        durations = [r.get("duration_seconds", 0) for r in records]
        behavior_types = [r.get("behavior_type", "") for r in records]

        return {
            "total_duration": sum(durations),
            "avg_duration": np.mean(durations),
            "std_duration": np.std(durations),
            "transition_count": len(records) - 1,
            "unique_behaviors": len(set(behavior_types)),
            "most_common_behavior": max(set(behavior_types), key=behavior_types.count),
        }


class AnomalyPreprocessor:
    """Preprocesses health and anomaly data for autoencoder training."""

    FEATURE_NAMES = [
        "activity_level",
        "movement_distance",
        "heart_rate",
        "body_temperature",
        "feed_consumption",
        "water_consumption",
    ]

    REQUIRED_FEATURES = ["animal_id", "timestamp"]

    @classmethod
    def validate_health_record(cls, record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a health/anomaly record.

        Args:
            record: Health record from MongoDB

        Returns:
            Tuple of (is_valid, error_message)
        """
        for field in cls.REQUIRED_FEATURES:
            if field not in record:
                return False, f"Missing required field: {field}"

        # Check for at least one feature
        has_features = any(f in record for f in cls.FEATURE_NAMES)
        if not has_features:
            return False, "No valid features in record"

        return True, ""

    @classmethod
    def normalize_features(
        cls,
        records: List[Dict[str, Any]],
    ) -> Tuple[np.ndarray, Dict[str, Tuple[float, float]]]:
        """
        Normalize health features using z-score normalization.

        Args:
            records: List of health records

        Returns:
            Tuple of (normalized_features, normalization_params)
        """
        # Extract features
        feature_matrix = []
        for record in records:
            features = []
            for feature_name in cls.FEATURE_NAMES:
                value = record.get(feature_name, 0.0)
                features.append(float(value))
            feature_matrix.append(features)

        features_array = np.array(feature_matrix, dtype=np.float32)

        # Compute normalization parameters
        mean = np.mean(features_array, axis=0)
        std = np.std(features_array, axis=0)
        std[std == 0] = 1.0  # Avoid division by zero

        # Normalize
        normalized = (features_array - mean) / std

        # Store normalization params
        norm_params = {
            cls.FEATURE_NAMES[i]: (float(mean[i]), float(std[i]))
            for i in range(len(cls.FEATURE_NAMES))
        }

        logger.info(f"Normalized {len(records)} health records")
        return normalized, norm_params

    @classmethod
    def compute_anomaly_scores(
        cls,
        reconstruction_errors: np.ndarray,
        percentile: float = 95.0,
    ) -> Dict[str, Any]:
        """
        Compute anomaly threshold and classification statistics.

        Args:
            reconstruction_errors: Reconstruction errors from normal data
            percentile: Percentile for threshold (default 95th)

        Returns:
            Dictionary with threshold and statistics
        """
        threshold = np.percentile(reconstruction_errors, percentile)
        mean_error = float(np.mean(reconstruction_errors))
        std_error = float(np.std(reconstruction_errors))

        return {
            "threshold": float(threshold),
            "mean_error": mean_error,
            "std_error": std_error,
            "percentile": percentile,
        }


class ReIDPreprocessor:
    """Preprocesses cattle images for Re-ID model training."""

    TARGET_SIZE = (224, 224)
    VALID_FORMATS = ["jpg", "jpeg", "png"]
    REQUIRED_FIELDS = ["animal_id", "camera_id", "image_path", "timestamp"]

    @classmethod
    def validate_image_record(cls, record: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate an image record for Re-ID.

        Args:
            record: Image record from MongoDB

        Returns:
            Tuple of (is_valid, error_message)
        """
        for field in cls.REQUIRED_FIELDS:
            if field not in record:
                return False, f"Missing required field: {field}"

        # Validate image format
        image_path = record.get("image_path", "")
        if not any(image_path.lower().endswith(fmt) for fmt in cls.VALID_FORMATS):
            return False, f"Invalid image format: {image_path}"

        return True, ""

    @classmethod
    def validate_image_set(
        cls,
        images_by_camera: Dict[str, List[Dict[str, Any]]],
    ) -> Tuple[int, int]:
        """
        Validate and count images across cameras.

        Args:
            images_by_camera: Images grouped by camera

        Returns:
            Tuple of (valid_images, invalid_images)
        """
        valid_count = 0
        invalid_count = 0

        for camera_id, images in images_by_camera.items():
            for image in images:
                is_valid, error = cls.validate_image_record(image)
                if is_valid:
                    valid_count += 1
                else:
                    invalid_count += 1
                    logger.warning(
                        f"Invalid image in camera {camera_id}: {error}"
                    )

        logger.info(
            f"Validated images: {valid_count} valid, {invalid_count} invalid"
        )
        return valid_count, invalid_count

    @classmethod
    def prepare_triplets(
        cls,
        positive_pairs: List[Tuple[Dict, Dict]],
        hard_negatives: List[Tuple[Dict, Dict]],
        max_triplets: Optional[int] = None,
    ) -> List[Tuple[str, str, str]]:
        """
        Prepare triplet learning data (anchor, positive, negative).

        Args:
            positive_pairs: Same-animal pairs from different cameras
            hard_negatives: Different-animal hard negative pairs
            max_triplets: Maximum number of triplets to create

        Returns:
            List of (anchor_path, positive_path, negative_path) tuples
        """
        triplets = []

        for anchor, positive in positive_pairs:
            for negative_pair in hard_negatives:
                anchor_img, negative = negative_pair
                triplet = (
                    anchor.get("image_path", ""),
                    positive.get("image_path", ""),
                    negative.get("image_path", ""),
                )
                if all(triplet):  # Check all paths are valid
                    triplets.append(triplet)

                if max_triplets and len(triplets) >= max_triplets:
                    break

            if max_triplets and len(triplets) >= max_triplets:
                break

        logger.info(f"Prepared {len(triplets)} triplets for training")
        return triplets


class TemporalPreprocessor:
    """Preprocesses temporal sequences for LSTM models."""

    SEQUENCE_LENGTH = 30
    MIN_SAMPLES = 5

    @classmethod
    def create_sliding_windows(
        cls,
        features: np.ndarray,
        window_size: int = 30,
        stride: int = 1,
    ) -> List[np.ndarray]:
        """
        Create sliding windows from temporal features.

        Args:
            features: Shape (N, feature_dim)
            window_size: Window length
            stride: Step size between windows

        Returns:
            List of windows, each shape (window_size, feature_dim)
        """
        windows = []
        for i in range(0, len(features) - window_size + 1, stride):
            window = features[i : i + window_size]
            windows.append(window)

        logger.info(f"Created {len(windows)} sliding windows")
        return windows

    @classmethod
    def pad_sequences(
        cls,
        sequences: List[np.ndarray],
        target_length: int = 30,
    ) -> np.ndarray:
        """
        Pad sequences to target length.

        Args:
            sequences: List of variable-length sequences
            target_length: Target sequence length

        Returns:
            Array of shape (len(sequences), target_length, feature_dim)
        """
        padded = []
        for seq in sequences:
            if len(seq) >= target_length:
                padded.append(seq[:target_length])
            else:
                # Pad with last value
                padding = np.tile(seq[-1:], (target_length - len(seq), 1))
                padded_seq = np.vstack([seq, padding])
                padded.append(padded_seq)

        logger.info(f"Padded {len(padded)} sequences to length {target_length}")
        return np.array(padded, dtype=np.float32)

    @classmethod
    def normalize_temporal_features(
        cls,
        sequences: List[np.ndarray],
    ) -> Tuple[np.ndarray, Dict[str, Tuple[float, float]]]:
        """
        Normalize temporal features across all sequences.

        Args:
            sequences: List of sequences

        Returns:
            Tuple of (normalized_sequences, normalization_params)
        """
        # Concatenate all sequences
        all_features = np.vstack(sequences)

        # Compute statistics
        mean = np.mean(all_features, axis=0)
        std = np.std(all_features, axis=0)
        std[std == 0] = 1.0  # Avoid division by zero

        # Normalize each sequence
        normalized = []
        for seq in sequences:
            norm_seq = (seq - mean) / std
            normalized.append(norm_seq)

        norm_params = {
            f"feature_{i}": (float(mean[i]), float(std[i]))
            for i in range(len(mean))
        }

        logger.info(f"Normalized {len(normalized)} temporal sequences")
        return np.array(normalized, dtype=np.float32), norm_params
