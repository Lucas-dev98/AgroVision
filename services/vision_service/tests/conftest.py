import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from motor.motor_asyncio import AsyncClient
import mongomock


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_mongodb_client():
    """Create mock MongoDB client"""
    return mongomock.MongoClient()


@pytest.fixture
def mock_db(mock_mongodb_client):
    """Get mock database"""
    return mock_mongodb_client["agrovision_vision_test"]


@pytest.fixture
def mock_yolo_model():
    """Create mock YOLO model"""
    model = Mock()
    model.return_value = []
    return model


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset imported modules between tests"""
    import sys
    
    # Store original modules
    original_modules = sys.modules.copy()
    
    yield
    
    # Restore original modules
    sys.modules.clear()
    sys.modules.update(original_modules)
