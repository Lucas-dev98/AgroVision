import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from app.core.database import MongoDBConnection, get_db


@pytest.fixture
async def reset_mongo():
    """Reset MongoDB connection state"""
    MongoDBConnection.client = None
    MongoDBConnection.db = None
    yield
    MongoDBConnection.client = None
    MongoDBConnection.db = None


class TestMongoDBConnection:
    """Test MongoDB async connection"""
    
    @pytest.mark.asyncio
    async def test_connection_initialization(self, reset_mongo):
        """Test MongoDB connection initialization"""
        with patch("app.core.database.AsyncIOMotorClient") as mock_client:
            # Setup mock
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.admin.command = AsyncMock()
            mock_instance.__getitem__ = MagicMock(return_value=MagicMock())
            
            await MongoDBConnection.connect(max_retries=1)
            
            assert MongoDBConnection.client is not None
            assert MongoDBConnection.db is not None
    
    @pytest.mark.asyncio
    async def test_connection_retry_logic(self, reset_mongo):
        """Test connection retry logic"""
        with patch("app.core.database.AsyncIOMotorClient") as mock_client:
            # Simulate connection failures
            mock_client.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception):
                await MongoDBConnection.connect(max_retries=2, retry_interval=0.1)
    
    @pytest.mark.asyncio
    async def test_disconnect(self, reset_mongo):
        """Test MongoDB disconnection"""
        with patch("app.core.database.AsyncIOMotorClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.admin.command = AsyncMock()
            mock_instance.__getitem__ = MagicMock(return_value=MagicMock())
            
            await MongoDBConnection.connect(max_retries=1)
            await MongoDBConnection.disconnect()
            
            mock_instance.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_index_creation(self, reset_mongo):
        """Test MongoDB index creation"""
        with patch("app.core.database.AsyncIOMotorClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.admin.command = AsyncMock()
            
            # Mock database with collections
            mock_db = MagicMock()
            mock_collections = {}
            
            def get_collection(name):
                if name not in mock_collections:
                    mock_collections[name] = AsyncMock()
                return mock_collections[name]
            
            mock_db.__getitem__ = get_collection
            mock_instance.__getitem__ = MagicMock(return_value=mock_db)
            
            await MongoDBConnection.connect(max_retries=1)
            
            # Check that index creation was called
            assert len(mock_collections) > 0
    
    def test_get_db_without_connection(self, reset_mongo):
        """Test get_db raises error without connection"""
        with pytest.raises(RuntimeError):
            get_db()
    
    @pytest.mark.asyncio
    async def test_get_db_with_connection(self, reset_mongo):
        """Test get_db returns database instance"""
        with patch("app.core.database.AsyncIOMotorClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value = mock_instance
            mock_instance.admin.command = AsyncMock()
            mock_db_instance = MagicMock()
            mock_instance.__getitem__ = MagicMock(return_value=mock_db_instance)
            
            await MongoDBConnection.connect(max_retries=1)
            db = get_db()
            
            assert db is not None
