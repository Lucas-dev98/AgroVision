import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas import (
    AnimalTrack,
    BehaviorClassification,
    AnimalReIdentification,
    AnomalyDetection,
    TrackingFrameResult,
    AnimalHealthReport,
    AnimalBehavior,
    AnomalyType,
)


class TestAnimalTrack:
    """Test AnimalTrack schema"""
    
    def test_valid_track(self):
        """Test creating valid animal track"""
        track = AnimalTrack(
            track_id=1,
            animal_id="RFID-001",
            confidence=0.95,
            current_position={"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.15},
            velocity={"vx": 0.01, "vy": 0.02},
            frames_count=10,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
        )
        
        assert track.track_id == 1
        assert track.animal_id == "RFID-001"
        assert track.confidence == 0.95
    
    def test_track_confidence_validation(self):
        """Test confidence bounds validation"""
        with pytest.raises(ValidationError):
            AnimalTrack(
                track_id=1,
                confidence=1.5,  # Invalid
                current_position={"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.15},
                frames_count=1,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
            )
    
    def test_track_optional_animal_id(self):
        """Test animal_id is optional"""
        track = AnimalTrack(
            track_id=1,
            confidence=0.95,
            current_position={"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.15},
            frames_count=1,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
        )
        
        assert track.animal_id is None


class TestBehaviorClassification:
    """Test BehaviorClassification schema"""
    
    def test_valid_classification(self):
        """Test creating valid behavior classification"""
        classification = BehaviorClassification(
            behavior=AnimalBehavior.GRAZING,
            confidence=0.8,
            position={"x": 0.5, "y": 0.6, "w": 0.1, "h": 0.15},
        )
        
        assert classification.behavior == AnimalBehavior.GRAZING
        assert classification.confidence == 0.8
    
    def test_behavior_enum_values(self):
        """Test all behavior enum values"""
        behaviors = [
            AnimalBehavior.GRAZING,
            AnimalBehavior.RESTING,
            AnimalBehavior.DRINKING,
            AnimalBehavior.WALKING,
            AnimalBehavior.RUNNING,
            AnimalBehavior.STANDING,
            AnimalBehavior.EATING,
            AnimalBehavior.UNKNOWN,
        ]
        
        for behavior in behaviors:
            classification = BehaviorClassification(
                behavior=behavior,
                confidence=0.7,
                position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.15},
            )
            assert classification.behavior == behavior


class TestAnimalReIdentification:
    """Test AnimalReIdentification schema"""
    
    def test_valid_reid(self):
        """Test creating valid re-identification result"""
        reid = AnimalReIdentification(
            animal_id="RFID-001",
            primary_camera_id="camera-1",
            secondary_camera_id="camera-2",
            similarity_score=0.85,
            confirmed=True,
            color_descriptor=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
            pattern_descriptor=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
        )
        
        assert reid.animal_id == "RFID-001"
        assert reid.similarity_score == 0.85
        assert reid.confirmed is True
    
    def test_reid_similarity_bounds(self):
        """Test similarity score bounds"""
        with pytest.raises(ValidationError):
            AnimalReIdentification(
                animal_id="RFID-001",
                primary_camera_id="camera-1",
                secondary_camera_id="camera-2",
                similarity_score=1.5,  # Invalid
            )


class TestAnomalyDetection:
    """Test AnomalyDetection schema"""
    
    def test_valid_anomaly(self):
        """Test creating valid anomaly detection"""
        anomaly = AnomalyDetection(
            animal_id="RFID-001",
            anomaly_type=AnomalyType.LAMENESS,
            severity="high",
            confidence=0.85,
            description="Abnormal gait detected",
            recommended_action="Schedule vet check",
            timestamp=datetime.utcnow(),
        )
        
        assert anomaly.animal_id == "RFID-001"
        assert anomaly.anomaly_type == AnomalyType.LAMENESS
        assert anomaly.severity == "high"
    
    def test_anomaly_type_enum(self):
        """Test anomaly type enum values"""
        types = [
            AnomalyType.LAMENESS,
            AnomalyType.LETHARGY,
            AnomalyType.ABNORMAL_POSTURE,
            AnomalyType.EXCESSIVE_SALIVATION,
            AnomalyType.UNUSUAL_MOVEMENT,
            AnomalyType.WEIGHT_CHANGE,
            AnomalyType.BEHAVIORAL_CHANGE,
        ]
        
        for atype in types:
            anomaly = AnomalyDetection(
                animal_id="RFID-001",
                anomaly_type=atype,
                severity="medium",
            )
            assert anomaly.anomaly_type == atype
    
    def test_anomaly_severity_enum(self):
        """Test anomaly severity values"""
        severities = ["low", "medium", "high", "critical"]
        
        for severity in severities:
            anomaly = AnomalyDetection(
                animal_id="RFID-001",
                anomaly_type=AnomalyType.LETHARGY,
                severity=severity,
            )
            assert anomaly.severity == severity


class TestTrackingFrameResult:
    """Test TrackingFrameResult schema"""
    
    def test_valid_frame_result(self):
        """Test creating valid frame result"""
        now = datetime.utcnow()
        track = AnimalTrack(
            track_id=1,
            confidence=0.9,
            current_position={"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.15},
            frames_count=1,
            first_seen=now,
            last_seen=now,
        )
        
        behavior = BehaviorClassification(
            behavior=AnimalBehavior.WALKING,
            confidence=0.8,
            position={"x": 0.3, "y": 0.4, "w": 0.1, "h": 0.15},
        )
        
        result = TrackingFrameResult(
            frame_id="frame-001",
            camera_id="camera-1",
            timestamp=now,
            tracks=[track],
            behaviors=[behavior],
            anomalies=[],
            processing_time_ms=25.5,
        )
        
        assert result.frame_id == "frame-001"
        assert len(result.tracks) == 1
        assert len(result.behaviors) == 1


class TestAnimalHealthReport:
    """Test AnimalHealthReport schema"""
    
    def test_valid_health_report(self):
        """Test creating valid health report"""
        report = AnimalHealthReport(
            animal_id="RFID-001",
            health_score=0.85,
            risk_level="low",
            recommendations=["Continue monitoring", "Feed as normal"],
            last_updated=datetime.utcnow(),
        )
        
        assert report.animal_id == "RFID-001"
        assert report.health_score == 0.85
        assert report.risk_level == "low"
    
    def test_health_score_bounds(self):
        """Test health score bounds"""
        with pytest.raises(ValidationError):
            AnimalHealthReport(
                animal_id="RFID-001",
                health_score=1.5,  # Invalid
                risk_level="low",
            )
    
    def test_risk_level_enum(self):
        """Test risk level values"""
        levels = ["low", "medium", "high", "critical"]
        
        for level in levels:
            report = AnimalHealthReport(
                animal_id="RFID-001",
                health_score=0.7,
                risk_level=level,
            )
            assert report.risk_level == level
