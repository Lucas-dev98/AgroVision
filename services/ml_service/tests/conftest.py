import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def async_db():
    """Mock async MongoDB database"""
    db = AsyncMock()
    db.__getitem__ = lambda self, key: AsyncMock()
    return db
