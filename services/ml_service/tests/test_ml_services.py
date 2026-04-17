import pytest
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.tracking import TrackingService
from app.services.reid import ReIdentificationService
from app.services.behavior import BehaviorAnalysisService
from app.services.anomaly import AnomalyDetectionService
from app.schemas import AnimalBehavior


@pytest.fixture
def sample_frame():
    """Create sample test frame"""
    return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def tracking_service():
    """Create tracking service"""
    with patch("app.services.tracking.YOLO"):
        service = TrackingService("yolov8n.pt")
        service.model = Mock()
        return service


@pytest.fixture
def reid_service():
    """Create re-identification service"""
    return ReIdentificationService()


@pytest.fixture
def behavior_service():
    """Create behavior analysis service"""
    return BehaviorAnalysisService()


@pytest.fixture
def anomaly_service():
    """Create anomaly detection service"""
    return AnomalyDetectionService()


# ==================== TRACKING SERVICE TESTS ====================

class TestTrackingService:
    """Test YOLO tracking service"""
    
    def test_initialization(self, tracking_service):
        """Test service initialization"""
        assert tracking_service.model is not None
        assert tracking_service.tracker is not None
        assert tracking_service.model_version == "YOLO v8 + ByteTrack"
    
    def test_track_empty_frame(self, tracking_service, sample_frame):
        """Test tracking empty frame (no detections)"""
        tracking_service.model.return_value = [Mock(boxes=[], names={})]
        
        tracks, processing_time = tracking_service.track_frame(sample_frame, "camera-1")
        
        assert isinstance(tracks, list)
        assert processing_time > 0
    
    def test_active_tracks_storage(self, tracking_service):
        """Test active tracks storage"""
        assert tracking_service.get_track_count() == 0
        
        # Simulate adding a track
        tracking_service.active_tracks[1] = Mock(animal_id="RFID-001")
        
        assert tracking_service.get_track_count() == 1
        assert tracking_service.get_track(1) is not None
    
    def test_update_animal_id(self, tracking_service):
        """Test updating animal RFID ID for track"""
        tracking_service.active_tracks[1] = Mock(animal_id=None)
        
        result = tracking_service.update_animal_id(1, "RFID-001")
        
        assert result is True
        assert tracking_service.active_tracks[1].animal_id == "RFID-001"
    
    def test_update_nonexistent_track(self, tracking_service):
        """Test updating non-existent track"""
        result = tracking_service.update_animal_id(999, "RFID-001")
        
        assert result is False
    
    def test_get_active_tracks(self, tracking_service):
        """Test getting all active tracks"""
        from app.schemas import AnimalTrack
        
        track1 = AnimalTrack(
            track_id=1,
            confidence=0.9,
            current_position={"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.2},
            frames_count=1,
            last_seen=datetime.utcnow(),
            first_seen=datetime.utcnow(),
        )
        track2 = AnimalTrack(
            track_id=2,
            confidence=0.85,
            current_position={"x": 0.5, "y": 0.6, "w": 0.1, "h": 0.2},
            frames_count=1,
            last_seen=datetime.utcnow(),
            first_seen=datetime.utcnow(),
        )
        
        tracking_service.active_tracks[1] = track1
        tracking_service.active_tracks[2] = track2
        
        active = tracking_service.get_active_tracks()
        
        assert len(active) == 2


# ==================== RE-IDENTIFICATION SERVICE TESTS ====================

class TestReIdentificationService:
    """Test re-identification service"""
    
    def test_color_descriptor_extraction(self, reid_service):
        """Test color descriptor extraction"""
        region = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        descriptor = reid_service.extract_color_descriptor(region)
        
        assert descriptor.shape == (9,)
        assert np.all(descriptor >= 0)
        assert np.all(descriptor <= 1)
    
    def test_color_descriptor_empty_region(self, reid_service):
        """Test color descriptor with empty region"""
        region = np.array([], dtype=np.uint8).reshape(0, 0, 3)
        
        descriptor = reid_service.extract_color_descriptor(region)
        
        assert descriptor.shape == (9,)
        assert np.allclose(descriptor, 0)
    
    def test_pattern_descriptor_extraction(self, reid_service):
        """Test pattern descriptor extraction"""
        region = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        descriptor = reid_service.extract_pattern_descriptor(region)
        
        assert descriptor.shape == (8,)
        assert np.all(descriptor >= 0)
    
    def test_register_animal(self, reid_service):
        """Test animal registration"""
        region = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = reid_service.register_animal("RFID-001", "camera-1", region)
        
        assert result is True
        assert "RFID-001" in reid_service.animal_descriptors
        assert "camera-1" in reid_service.animal_descriptors["RFID-001"]
    
    def test_match_unregistered_animal(self, reid_service):
        """Test matching unregistered animal"""
        region = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        similarity, is_match = reid_service.match_animal(
            "RFID-999",
            "camera-1",
            region,
        )
        
        assert similarity == 0.0
        assert is_match is False
    
    def test_find_matches(self, reid_service):
        """Test finding matches across cameras"""
        # Register animal on primary camera
        primary_region = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        reid_service.register_animal("RFID-001", "camera-1", primary_region)
        
        # Create regions for secondary cameras
        secondary_regions = {
            "camera-2": np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8),
            "camera-3": np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8),
        }
        
        results = reid_service.find_matches(
            "RFID-001",
            "camera-1",
            ["camera-2", "camera-3"],
            secondary_regions,
        )
        
        assert len(results) == 2
        assert all(r.animal_id == "RFID-001" for r in results)


# ==================== BEHAVIOR ANALYSIS SERVICE TESTS ====================

class TestBehaviorAnalysisService:
    """Test behavior analysis service"""
    
    def test_classify_static_behavior(self, behavior_service):
        """Test classifying static behavior"""
        classification = behavior_service.classify_behavior(
            track_id=1,
            position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.15},
            velocity={"vx": 0, "vy": 0},
        )
        
        assert classification.behavior in [
            AnimalBehavior.STANDING,
            AnimalBehavior.GRAZING,
            AnimalBehavior.RESTING,
        ]
        assert classification.confidence > 0
    
    def test_classify_walking_behavior(self, behavior_service):
        """Test classifying walking behavior"""
        classification = behavior_service.classify_behavior(
            track_id=1,
            position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.15},
            velocity={"vx": 0.015, "vy": 0},
        )
        
        assert classification.behavior == AnimalBehavior.WALKING
    
    def test_classify_running_behavior(self, behavior_service):
        """Test classifying running behavior"""
        classification = behavior_service.classify_behavior(
            track_id=1,
            position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.15},
            velocity={"vx": 0.05, "vy": 0},
        )
        
        assert classification.behavior == AnimalBehavior.RUNNING
    
    def test_behavior_history_tracking(self, behavior_service):
        """Test behavior history tracking"""
        for i in range(5):
            behavior_service.classify_behavior(
                track_id=1,
                position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.15},
                velocity={"vx": 0, "vy": 0},
            )
        
        history = behavior_service.get_behavior_history(1)
        
        assert len(history) == 5
    
    def test_get_dominant_behavior(self, behavior_service):
        """Test getting dominant behavior"""
        # Add several grazing behaviors
        for i in range(7):
            behavior_service.classify_behavior(
                track_id=1,
                position={"x": 0.5, "y": 0.7, "w": 0.1, "h": 0.15},
                velocity={"vx": 0, "vy": 0},
            )
        
        # Add some walking
        for i in range(3):
            behavior_service.classify_behavior(
                track_id=1,
                position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.15},
                velocity={"vx": 0.02, "vy": 0},
            )
        
        dominant, count = behavior_service.get_dominant_behavior(1, time_window=10)
        
        assert count >= 3
    
    def test_analyze_behavior_sequence(self, behavior_service):
        """Test behavior sequence analysis"""
        for i in range(20):
            behavior_service.classify_behavior(
                track_id=1,
                position={"x": 0.5, "y": 0.5 + i*0.01, "w": 0.1, "h": 0.15},
                velocity={"vx": 0.01, "vy": 0.01},
            )
        
        analysis = behavior_service.analyze_behavior_sequence(1)
        
        assert "total_frames" in analysis
        assert "behavior_percentages" in analysis
        assert analysis["total_frames"] == 20


# ==================== ANOMALY DETECTION SERVICE TESTS ====================

class TestAnomalyDetectionService:
    """Test anomaly detection service"""
    
    def test_establish_baseline(self, anomaly_service):
        """Test baseline establishment"""
        behavior_data = {
            "unique_behaviors": 3,
            "behavior_percentages": {
                str(AnimalBehavior.GRAZING): 50,
                str(AnimalBehavior.WALKING): 30,
                str(AnimalBehavior.RESTING): 20,
            }
        }
        
        result = anomaly_service.establish_baseline(
            "RFID-001",
            behavior_data,
        )
        
        assert result is True
        assert "RFID-001" in anomaly_service.animal_baselines
    
    def test_detect_lethargy(self, anomaly_service):
        """Test lethargy detection"""
        # Establish baseline
        baseline = {
            "unique_behaviors": 3,
            "behavior_percentages": {
                str(AnimalBehavior.GRAZING): 40,
                str(AnimalBehavior.WALKING): 40,
                str(AnimalBehavior.RESTING): 20,
            }
        }
        anomaly_service.establish_baseline("RFID-001", baseline)
        
        # Current behavior (lethargic)
        current = {
            "unique_behaviors": 1,
            "behavior_percentages": {
                str(AnimalBehavior.RESTING): 85,
            }
        }
        
        anomalies = anomaly_service.detect_anomalies(
            "RFID-001",
            current,
            {"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.15},
            1,
        )
        
        assert len(anomalies) > 0
    
    def test_get_anomaly_history(self, anomaly_service):
        """Test anomaly history retrieval"""
        baseline = {
            "unique_behaviors": 3,
            "behavior_percentages": {}
        }
        anomaly_service.establish_baseline("RFID-001", baseline)
        
        # Detect some anomalies
        anomaly_service.detect_anomalies(
            "RFID-001",
            {"unique_behaviors": 1, "behavior_percentages": {str(AnimalBehavior.RESTING): 90}},
            {"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.15},
            1,
        )
        
        history = anomaly_service.get_anomaly_history("RFID-001", hours=1)
        
        assert isinstance(history, list)
    
    def test_calculate_health_score(self, anomaly_service):
        """Test health score calculation"""
        baseline = {"unique_behaviors": 3, "behavior_percentages": {}}
        anomaly_service.establish_baseline("RFID-001", baseline)
        
        score, risk = anomaly_service.calculate_health_score("RFID-001")
        
        assert 0 <= score <= 1
        assert risk in ["low", "medium", "high", "critical"]
    
    def test_health_score_with_anomalies(self, anomaly_service):
        """Test health score with detected anomalies"""
        baseline = {"unique_behaviors": 3, "behavior_percentages": {}}
        anomaly_service.establish_baseline("RFID-001", baseline)
        
        # Detect multiple anomalies
        anomaly_service.detect_anomalies(
            "RFID-001",
            {"unique_behaviors": 1, "behavior_percentages": {}},
            {"x": 0.1, "y": 0.9, "w": 0.1, "h": 0.15},
            1,
        )
        
        score, risk = anomaly_service.calculate_health_score("RFID-001")
        
        assert score < 1.0  # Decreased from baseline
        assert risk in ["medium", "high", "critical"]
