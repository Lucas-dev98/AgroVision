import pytest
from datetime import timezone, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories import DetectionRepository, AnimalLocationRepository, CameraCalibrationRepository
from app.schemas import FrameDetectionResult, Detection, BoundingBox, DetectionType, TroughStatus
from bson import ObjectId


def create_async_mock_cursor(return_value):
    """Helper to create proper async mock cursor"""
    cursor = AsyncMock()
    cursor.to_list = AsyncMock(return_value=return_value)
    cursor.sort = MagicMock(return_value=cursor)
    cursor.skip = MagicMock(return_value=cursor)
    cursor.limit = MagicMock(return_value=cursor)
    return cursor


@pytest.fixture
def mock_db():
    """Create a mock MongoDB database with async methods"""
    db = MagicMock()
    db.__getitem__ = MagicMock(side_effect=lambda x: AsyncMock())
    return db


@pytest.fixture
def sample_detection_result():
    """Create sample detection result"""
    detection = Detection(
        detection_type=DetectionType.ANIMAL,
        confidence=0.95,
        bounding_box=BoundingBox(x_min=0.1, y_min=0.2, x_max=0.5, y_max=0.8),
        animal_color="brown",
        animal_breed="Nelore",
    )
    
    return FrameDetectionResult(
        frame_id="frame-001",
        timestamp=datetime.now(timezone.utc),
        camera_id="camera-1",
        detections=[detection],
        total_animals=1,
        trough_status=TroughStatus.FULL,
        processing_time_ms=45.3,
        model_version="YOLOv8n",
    )


class TestDetectionRepository:
    """Test DetectionRepository with mocked Motor"""
    
    @pytest.fixture
    def repo(self, mock_db):
        """Create repository with mocked db"""
        repo = DetectionRepository(mock_db)
        repo.collection = AsyncMock()
        return repo
    
    @pytest.mark.asyncio
    async def test_create_detection(self, repo, sample_detection_result):
        """Test creating a detection document"""
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()
        repo.collection.insert_one = AsyncMock(return_value=mock_insert_result)
        
        doc_id = await repo.create(sample_detection_result)
        
        assert doc_id is not None
        assert isinstance(doc_id, str)
        repo.collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_frame_id(self, repo):
        """Test retrieving detection by frame ID"""
        mock_doc = {
            "frame_id": "frame-001",
            "camera_id": "camera-1",
            "total_animals": 1,
        }
        repo.collection.find_one = AsyncMock(return_value=mock_doc)
        
        result = await repo.get_by_frame_id("frame-001")
        
        assert result is not None
        assert result["frame_id"] == "frame-001"
        repo.collection.find_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_by_camera(self, repo):
        """Test retrieving detections by camera"""
        mock_docs = [
            {"frame_id": "frame-001", "camera_id": "camera-1"},
            {"frame_id": "frame-002", "camera_id": "camera-1"},
        ]
        
        mock_cursor = create_async_mock_cursor(mock_docs)
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        results = await repo.get_by_camera("camera-1", limit=10)
        
        assert len(results) == 2
        assert all(r["camera_id"] == "camera-1" for r in results)
    
    @pytest.mark.asyncio
    async def test_get_recent(self, repo):
        """Test retrieving recent detections"""
        mock_docs = [{"frame_id": "frame-001"}]
        
        mock_cursor = create_async_mock_cursor(mock_docs)
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        results = await repo.get_recent(hours=24, limit=10)
        
        assert len(results) > 0
        assert results[0]["frame_id"] == "frame-001"
    
    @pytest.mark.asyncio
    async def test_count_animals_by_camera(self, repo):
        """Test counting animals by camera"""
        mock_result = [{"total": 8}]
        
        mock_cursor = create_async_mock_cursor(mock_result)
        mock_aggregate = MagicMock(return_value=mock_cursor)
        repo.collection.aggregate = mock_aggregate
        
        total = await repo.count_animals_by_camera("camera-1")
        
        assert isinstance(total, int)
        assert total == 8


class TestAnimalLocationRepository:
    """Test AnimalLocationRepository"""
    
    @pytest.fixture
    def repo(self, mock_db):
        """Create repository with mocked db"""
        repo = AnimalLocationRepository(mock_db)
        repo.collection = AsyncMock()
        return repo
    
    @pytest.mark.asyncio
    async def test_create_location(self, repo):
        """Test creating a location record"""
        mock_insert_result = MagicMock()
        mock_insert_result.inserted_id = ObjectId()
        repo.collection.insert_one = AsyncMock(return_value=mock_insert_result)
        
        doc_id = await repo.create_location(
            animal_id="001",
            timestamp=datetime.now(timezone.utc),
            camera_id="camera-1",
            location={"x_min": 0.1, "y_min": 0.2, "x_max": 0.5, "y_max": 0.8},
            confidence=0.95,
            frame_id="frame-001",
        )
        
        assert doc_id is not None
        assert isinstance(doc_id, str)
    
    @pytest.mark.asyncio
    async def test_get_animal_history(self, repo):
        """Test retrieving animal history"""
        mock_docs = [
            {"animal_id": "001", "timestamp": datetime.now(timezone.utc)},
        ]
        
        mock_cursor = create_async_mock_cursor(mock_docs)
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        results = await repo.get_animal_history("001", limit=10)
        
        assert len(results) > 0
        assert results[0]["animal_id"] == "001"
    
    @pytest.mark.asyncio
    async def test_get_latest_locations(self, repo):
        """Test getting latest locations"""
        mock_docs = [
            {"animal_id": "001", "camera_id": "camera-1"},
        ]
        
        mock_cursor = create_async_mock_cursor(mock_docs)
        repo.collection.aggregate = MagicMock(return_value=mock_cursor)
        
        results = await repo.get_latest_locations("camera-1")
        
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_count_unique_animals(self, repo):
        """Test counting unique animals"""
        mock_animals = ["001", "002", "003"]
        repo.collection.distinct = AsyncMock(return_value=mock_animals)
        
        count = await repo.count_unique_animals("camera-1", hours=24)
        
        assert count == 3


class TestCameraCalibrationRepository:
    """Test CameraCalibrationRepository"""
    
    @pytest.fixture
    def repo(self, mock_db):
        """Create repository with mocked db"""
        repo = CameraCalibrationRepository(mock_db)
        repo.collection = AsyncMock()
        return repo
    
    @pytest.mark.asyncio
    async def test_create_or_update_new(self, repo):
        """Test creating new calibration"""
        mock_result = MagicMock()
        mock_result.matched_count = 0
        mock_result.upserted_id = ObjectId()
        repo.collection.update_one = AsyncMock(return_value=mock_result)
        
        doc_id = await repo.create_or_update(
            camera_id="camera-1",
            location="pasture-1",
            longitude=None,
            latitude=None,
            calibration_data={},
            confidence_threshold=0.5,
        )
        
        assert doc_id == "camera-1"
    
    @pytest.mark.asyncio
    async def test_get_by_camera_id(self, repo):
        """Test getting calibration by camera"""
        mock_doc = {
            "camera_id": "camera-1",
            "location": "pasture-1",
            "yolo_confidence_threshold": 0.5,
        }
        repo.collection.find_one = AsyncMock(return_value=mock_doc)
        
        result = await repo.get_by_camera_id("camera-1")
        
        assert result is not None
        assert result["camera_id"] == "camera-1"
    
    @pytest.mark.asyncio
    async def test_update_existing(self, repo):
        """Test updating existing calibration"""
        mock_result = MagicMock()
        mock_result.matched_count = 1
        mock_result.modified_count = 1
        repo.collection.update_one = AsyncMock(return_value=mock_result)
        
        doc_id = await repo.create_or_update(
            camera_id="camera-1",
            location="pasture-1-updated",
            longitude=None,
            latitude=None,
            calibration_data={},
            confidence_threshold=0.6,
        )
        
        assert doc_id == "camera-1"
    
    @pytest.mark.asyncio
    async def test_get_all(self, repo):
        """Test getting all calibrations"""
        mock_docs = [
            {"camera_id": "camera-1"},
            {"camera_id": "camera-2"},
        ]
        
        mock_cursor = create_async_mock_cursor(mock_docs)
        repo.collection.find = MagicMock(return_value=mock_cursor)
        
        results = await repo.get_all()
        
        assert len(results) == 2
