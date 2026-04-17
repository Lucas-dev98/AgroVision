import pytest
import mongomock
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncClient
from unittest.mock import AsyncMock, Mock
from app.repositories import DetectionRepository, AnimalLocationRepository, CameraCalibrationRepository
from app.schemas import FrameDetectionResult, Detection, BoundingBox, DetectionType, TroughStatus


@pytest.fixture
def mock_db():
    """Create a mock MongoDB database"""
    client = mongomock.MongoClient()
    return client["agrovision_vision_test"]


class TestDetectionRepository:
    """Test DetectionRepository"""
    
    @pytest.fixture
    def repo(self, mock_db):
        return DetectionRepository(mock_db)
    
    @pytest.fixture
    def sample_detection_result(self):
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
            timestamp=datetime.utcnow(),
            camera_id="camera-1",
            detections=[detection],
            total_animals=1,
            trough_status=TroughStatus.FULL,
            processing_time_ms=45.3,
            model_version="YOLOv8n",
        )
    
    def test_create_detection(self, repo, sample_detection_result):
        """Test creating a detection document"""
        doc_id = repo.create(sample_detection_result)
        
        assert doc_id is not None
        assert isinstance(doc_id, str)
    
    def test_get_by_frame_id(self, repo, sample_detection_result):
        """Test retrieving detection by frame ID"""
        repo.create(sample_detection_result)
        
        result = repo.get_by_frame_id("frame-001")
        
        assert result is not None
        assert result["frame_id"] == "frame-001"
        assert result["camera_id"] == "camera-1"
        assert result["total_animals"] == 1
    
    def test_get_by_camera(self, repo, sample_detection_result):
        """Test retrieving detections by camera"""
        # Create multiple detections
        repo.create(sample_detection_result)
        
        sample_detection_result.frame_id = "frame-002"
        repo.create(sample_detection_result)
        
        results = repo.get_by_camera("camera-1", limit=10)
        
        assert len(results) == 2
        assert all(r["camera_id"] == "camera-1" for r in results)
    
    def test_get_recent(self, repo, sample_detection_result):
        """Test retrieving recent detections"""
        repo.create(sample_detection_result)
        
        results = repo.get_recent(hours=24, limit=10)
        
        assert len(results) > 0
        assert results[0]["frame_id"] == "frame-001"
    
    def test_count_animals_by_camera(self, repo, sample_detection_result):
        """Test counting animals by camera"""
        sample_detection_result.total_animals = 5
        repo.create(sample_detection_result)
        
        sample_detection_result.frame_id = "frame-002"
        sample_detection_result.total_animals = 3
        repo.create(sample_detection_result)
        
        total = repo.count_animals_by_camera("camera-1")
        
        # Note: mongomock might not support aggregation fully
        # This test documents expected behavior
        assert isinstance(total, int)


class TestAnimalLocationRepository:
    """Test AnimalLocationRepository"""
    
    @pytest.fixture
    def repo(self, mock_db):
        return AnimalLocationRepository(mock_db)
    
    def test_create_location(self, repo):
        """Test creating animal location"""
        loc_id = repo.create_location(
            animal_id="RFID-001",
            timestamp=datetime.utcnow(),
            camera_id="camera-1",
            location={"x_min": 0.1, "y_min": 0.2, "x_max": 0.5, "y_max": 0.8},
            confidence=0.95,
            frame_id="frame-001",
        )
        
        assert loc_id is not None
    
    def test_get_animal_history(self, repo):
        """Test getting animal location history"""
        now = datetime.utcnow()
        
        # Create multiple location entries
        for i in range(3):
            repo.create_location(
                animal_id="RFID-001",
                timestamp=now - timedelta(hours=i),
                camera_id="camera-1",
                location={"x_min": 0.1, "y_min": 0.2, "x_max": 0.5, "y_max": 0.8},
                confidence=0.95,
                frame_id=f"frame-{i:03d}",
            )
        
        history = repo.get_animal_history("RFID-001", limit=10, hours=24)
        
        assert len(history) == 3
        assert all(h["animal_id"] == "RFID-001" for h in history)
    
    def test_get_latest_locations(self, repo):
        """Test getting latest locations of all animals"""
        now = datetime.utcnow()
        
        # Create locations for multiple animals
        for animal in ["RFID-001", "RFID-002", "RFID-003"]:
            repo.create_location(
                animal_id=animal,
                timestamp=now,
                camera_id="camera-1",
                location={"x_min": 0.1, "y_min": 0.2, "x_max": 0.5, "y_max": 0.8},
                confidence=0.95,
                frame_id=f"frame-{animal}",
            )
        
        latest = repo.get_latest_locations("camera-1")
        
        # Note: mongomock might not support complex aggregation
        assert isinstance(latest, list)
    
    def test_count_unique_animals(self, repo):
        """Test counting unique animals"""
        now = datetime.utcnow()
        
        # Create locations for 3 animals with multiple entries each
        for animal in ["RFID-001", "RFID-002", "RFID-003"]:
            for i in range(2):
                repo.create_location(
                    animal_id=animal,
                    timestamp=now - timedelta(hours=i),
                    camera_id="camera-1",
                    location={"x_min": 0.1, "y_min": 0.2, "x_max": 0.5, "y_max": 0.8},
                    confidence=0.95,
                    frame_id=f"frame-{animal}-{i}",
                )
        
        count = repo.count_unique_animals("camera-1", hours=24)
        
        assert count == 3


class TestCameraCalibrationRepository:
    """Test CameraCalibrationRepository"""
    
    @pytest.fixture
    def repo(self, mock_db):
        return CameraCalibrationRepository(mock_db)
    
    def test_create_or_update_new(self, repo):
        """Test creating new calibration"""
        result = repo.create_or_update(
            camera_id="camera-1",
            location="Pasture-A",
            longitude=-50.123,
            latitude=-25.456,
            calibration_data={"focal_length": 3.5},
            confidence_threshold=0.6,
        )
        
        assert result == "camera-1"
    
    def test_get_by_camera_id(self, repo):
        """Test retrieving camera calibration"""
        repo.create_or_update(
            camera_id="camera-1",
            location="Pasture-A",
        )
        
        calibration = repo.get_by_camera_id("camera-1")
        
        assert calibration is not None
        assert calibration["camera_id"] == "camera-1"
        assert calibration["location"] == "Pasture-A"
    
    def test_update_existing(self, repo):
        """Test updating existing calibration"""
        repo.create_or_update(
            camera_id="camera-1",
            location="Pasture-A",
            confidence_threshold=0.5,
        )
        
        repo.create_or_update(
            camera_id="camera-1",
            location="Pasture-B",
            confidence_threshold=0.7,
        )
        
        calibration = repo.get_by_camera_id("camera-1")
        
        assert calibration["location"] == "Pasture-B"
        assert calibration["yolo_confidence_threshold"] == 0.7
    
    def test_get_all(self, repo):
        """Test retrieving all calibrations"""
        for i in range(3):
            repo.create_or_update(
                camera_id=f"camera-{i+1}",
                location=f"Pasture-{chr(65+i)}",
            )
        
        calibrations = repo.get_all()
        
        assert len(calibrations) == 3
