import pytest
from unittest.mock import AsyncMock, MagicMock
import torch
from pathlib import Path


@pytest.fixture(scope="session")
def ml_service_path():
    """Get the ML service root path (session scoped)"""
    return str(Path(__file__).parent.parent)


@pytest.fixture
def async_db():
    """Mock async MongoDB database"""
    db = AsyncMock()
    db.__getitem__ = lambda self, key: AsyncMock()
    return db


# ============================================================================
# Fixtures for Phase 3.4 Tests
# ============================================================================

@pytest.fixture
def behavior_model():
    """Mock de modelo de comportamento (8 classes)."""
    def model_forward(x):
        batch_size = x.shape[0] if isinstance(x, torch.Tensor) else len(x)
        return torch.randn(batch_size, 8)
    
    model = MagicMock(side_effect=model_forward)
    model.eval = MagicMock()
    model.to = MagicMock(return_value=model)
    model.train = MagicMock()
    return model


@pytest.fixture
def anomaly_model():
    """Mock de modelo de anomalia (1 score)."""
    def model_forward(x):
        batch_size = x.shape[0] if isinstance(x, torch.Tensor) else len(x)
        return torch.randn(batch_size, 1)
    
    model = MagicMock(side_effect=model_forward)
    model.eval = MagicMock()
    model.to = MagicMock(return_value=model)
    model.train = MagicMock()
    return model


@pytest.fixture
def reid_model():
    """Mock de modelo Re-ID (256-d embedding)."""
    def model_forward(x):
        batch_size = x.shape[0] if isinstance(x, torch.Tensor) else len(x)
        return torch.randn(batch_size, 256)
    
    model = MagicMock(side_effect=model_forward)
    model.eval = MagicMock()
    model.to = MagicMock(return_value=model)
    model.train = MagicMock()
    return model


@pytest.fixture
def temporal_model():
    """Mock de modelo temporal (8 classes)."""
    def model_forward(x):
        batch_size = x.shape[0] if isinstance(x, torch.Tensor) else len(x)
        return torch.randn(batch_size, 8)
    
    model = MagicMock(side_effect=model_forward)
    model.eval = MagicMock()
    model.to = MagicMock(return_value=model)
    model.train = MagicMock()
    return model


@pytest.fixture
def prediction_service(behavior_model, anomaly_model, reid_model, temporal_model):
    """PredictionService com todos os modelos mockados."""
    from app.services.prediction_service import PredictionService
    
    return PredictionService(
        behavior_model=behavior_model,
        anomaly_model=anomaly_model,
        reid_model=reid_model,
        temporal_model=temporal_model,
        device="cpu",
    )


@pytest.fixture
def error_model():
    """Mock de modelo que lança erro."""
    def model_forward(x):
        raise RuntimeError("Model inference error")
    
    model = MagicMock(side_effect=model_forward)
    model.eval = MagicMock()
    model.to = MagicMock(return_value=model)
    return model


@pytest.fixture
def error_prediction_service(error_model):
    """PredictionService com modelos que falham."""
    from app.services.prediction_service import PredictionService
    
    return PredictionService(
        behavior_model=error_model,
        anomaly_model=error_model,
        reid_model=error_model,
        temporal_model=error_model,
        device="cpu",
    )
