import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from app.repositories import TrackingRepository, ReIdRepository, HealthRepository
from app.schemas import AnimalTrack, BehaviorClassification


@pytest.fixture
def mock_db():
    """Mock async database"""
    db = AsyncMock()
    db.__getitem__ = MagicMock(return_value=AsyncMock())
    return db


class TestTrackingRepository:
    """Test tracking repository"""
    
    @pytest.mark.asyncio
    async def test_create_tracking(self, mock_db):
        """Test creating tracking document"""
        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="123")
        )
        mock_db.__getitem__.return_value = mock_collection
        
        repo = TrackingRepository(mock_db)
        
        now = datetime.utcnow()
        track = AnimalTrack(
            track_id=1,
            confidence=0.9,
            current_position={"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.15},
            frames_count=1,
            first_seen=now,
            last_seen=now,
        )
        
        result = await repo.create(
            frame_id="frame-001",
            camera_id="camera-1",
            tracks=[track],
            behaviors=[],
            anomalies=[],
        )
        
        assert result == "123"
        mock_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_frame(self, mock_db):
        """Test getting tracking by frame"""
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(
            return_value={"frame_id": "frame-001"}
        )
        mock_db.__getitem__.return_value = mock_collection
        
        repo = TrackingRepository(mock_db)
        result = await repo.get_by_frame("frame-001")
        
        assert result is not None
        assert result["frame_id"] == "frame-001"
    
    @pytest.mark.asyncio
    async def test_get_by_camera(self, mock_db):
        """Test getting tracking by camera"""
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[{"camera_id": "camera-1"}])
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_db.__getitem__.return_value = mock_collection
        
        repo = TrackingRepository(mock_db)
        results = await repo.get_by_camera("camera-1")
        
        assert len(results) == 1
        assert results[0]["camera_id"] == "camera-1"


class TestReIdRepository:
    """Test re-identification repository"""
    
    @pytest.mark.asyncio
    async def test_create_reid(self, mock_db):
        """Test creating re-identification document"""
        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="456")
        )
        mock_db.__getitem__.return_value = mock_collection
        
        repo = ReIdRepository(mock_db)
        
        result = await repo.create(
            animal_id="RFID-001",
            primary_camera="camera-1",
            secondary_camera="camera-2",
            similarity_score=0.85,
            confirmed=True,
        )
        
        assert result == "456"
    
    @pytest.mark.asyncio
    async def test_get_by_animal(self, mock_db):
        """Test getting re-id results by animal"""
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[{"animal_id": "RFID-001", "similarity_score": 0.85}]
        )
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_db.__getitem__.return_value = mock_collection
        
        repo = ReIdRepository(mock_db)
        results = await repo.get_by_animal("RFID-001")
        
        assert len(results) == 1
        assert results[0]["animal_id"] == "RFID-001"
    
    @pytest.mark.asyncio
    async def test_get_matches(self, mock_db):
        """Test getting confirmed matches"""
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[{"animal_id": "RFID-001", "confirmed": True}]
        )
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_db.__getitem__.return_value = mock_collection
        
        repo = ReIdRepository(mock_db)
        results = await repo.get_matches("RFID-001", confidence_threshold=0.7)
        
        assert len(results) == 1


class TestHealthRepository:
    """Test health repository"""
    
    @pytest.mark.asyncio
    async def test_create_health(self, mock_db):
        """Test creating health document"""
        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="789")
        )
        mock_db.__getitem__.return_value = mock_collection
        
        repo = HealthRepository(mock_db)
        
        result = await repo.create(
            animal_id="RFID-001",
            health_score=0.85,
            risk_level="low",
            recommendations=["Monitor", "Feed normally"],
        )
        
        assert result == "789"
    
    @pytest.mark.asyncio
    async def test_get_latest(self, mock_db):
        """Test getting latest health record"""
        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(
            return_value={"animal_id": "RFID-001", "health_score": 0.85}
        )
        mock_db.__getitem__.return_value = mock_collection
        
        repo = HealthRepository(mock_db)
        result = await repo.get_latest("RFID-001")
        
        assert result is not None
        assert result["health_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_get_history(self, mock_db):
        """Test getting health history"""
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"animal_id": "RFID-001", "health_score": 0.85},
                {"animal_id": "RFID-001", "health_score": 0.8},
            ]
        )
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_db.__getitem__.return_value = mock_collection
        
        repo = HealthRepository(mock_db)
        results = await repo.get_history("RFID-001")
        
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_get_critical_animals(self, mock_db):
        """Test getting critical animals"""
        mock_collection = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(
            return_value=[{"animal_id": "RFID-001", "risk_level": "critical"}]
        )
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_db.__getitem__.return_value = mock_collection
        
        repo = HealthRepository(mock_db)
        results = await repo.get_critical_animals()
        
        assert len(results) == 1
        assert results[0]["risk_level"] == "critical"
