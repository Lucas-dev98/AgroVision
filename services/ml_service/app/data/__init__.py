"""
Data module for FASE 3 - Real Data Integration
===============================================

Handles loading, preprocessing, and validation of real cattle tracking data
from MongoDB for model training and inference.

Components:
- loaders.py: MongoDB data loaders (tracking, behavior, anomalies, re-id)
- preprocessors.py: Data validation, normalization, and preprocessing
- datasets.py: Real training datasets from MongoDB
"""

from .loaders import (
    TrackingDataLoader,
    BehaviorDataLoader,
    AnomalyDataLoader,
    ReIDDataLoader,
)

from .preprocessors import (
    BehaviorPreprocessor,
    AnomalyPreprocessor,
    ReIDPreprocessor,
    TemporalPreprocessor,
)

__all__ = [
    "TrackingDataLoader",
    "BehaviorDataLoader",
    "AnomalyDataLoader",
    "ReIDDataLoader",
    "BehaviorPreprocessor",
    "AnomalyPreprocessor",
    "ReIDPreprocessor",
    "TemporalPreprocessor",
]
