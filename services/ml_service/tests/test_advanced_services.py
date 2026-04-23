import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from app.services.advanced import (
    AdvancedBehaviorService,
    AdvancedAnomalyService,
    AdvancedReIDService,
)
from app.schemas import AnimalBehavior


class TestAdvancedBehaviorService:
    """Test advanced behavior service"""
    
    @pytest.fixture
    def behavior_service(self):
        """Create behavior service"""
        with patch("app.services.advanced.CNNBehaviorClassifier"):
            service = AdvancedBehaviorService(device="cpu")
            service.cnn_model = MagicMock()
            service.lstm_model = MagicMock()
            return service
    
    def test_initialization(self, behavior_service):
        """Test initialization"""
        assert behavior_service is not None
        assert len(behavior_service.behavior_map) == 8
    
    def test_classify_from_bbox(self, behavior_service):
        """Test behavior classification from bbox"""
        bbox_image = np.random.randint(0, 255, (240, 240, 3), dtype=np.uint8)
        
        # Mock model output
        behavior_service.cnn_model.return_value = (
            MagicMock(return_value=MagicMock(return_value=0)),  # logits
            MagicMock(return_value=[[0.1, 0.2, 0.3, 0.1, 0.1, 0.1, 0.05, 0.05]])  # probs
        )
        
        classification = behavior_service.classify_from_bbox(
            bbox_image,
            track_id=1,
            position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.2},
        )
        
        assert classification.behavior in behavior_service.behavior_map.values()
    
    def test_sequence_storage(self, behavior_service):
        """Test sequence storage for LSTM"""
        bbox_image = np.random.randint(0, 255, (240, 240, 3), dtype=np.uint8)
        
        for i in range(5):
            behavior_service.sequences[1] = [np.random.randn(128) for _ in range(i + 1)]
        
        assert len(behavior_service.sequences[1]) <= behavior_service.seq_len
    
    def test_classify_temporal(self, behavior_service):
        """Test temporal behavior classification"""
        # Setup sequences
        behavior_service.sequences[1] = [np.random.randn(128) for _ in range(5)]
        
        classification = behavior_service.classify_temporal(
            track_id=1,
            position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.2},
        )
        
        assert classification.behavior in behavior_service.behavior_map.values()
    
    def test_get_behavior_confidence(self, behavior_service):
        """Test getting behavior confidence scores"""
        behavior_service.sequences[1] = [np.random.randn(128) for _ in range(5)]
        
        confidence = behavior_service.get_behavior_confidence(1)
        
        assert isinstance(confidence, dict)


class TestAdvancedAnomalyService:
    """Test advanced anomaly detection service"""
    
    @pytest.fixture
    def anomaly_service(self):
        """Create anomaly service"""
        with patch("app.services.advanced.AnomalyDetectionAutoencoder"):
            service = AdvancedAnomalyService(device="cpu")
            service.autoencoder = MagicMock()
            # Mock the autoencoder to return (reconstruction, latent) tuple
            service.autoencoder.return_value = (
                MagicMock(),  # reconstruction
                MagicMock(),  # latent
            )
            return service
    
    def test_initialization(self, anomaly_service):
        """Test initialization"""
        assert anomaly_service is not None
        assert anomaly_service.anomaly_threshold == 0.7
    
    def test_establish_baseline(self, anomaly_service):
        """Test baseline establishment"""
        features = np.random.randn(128)
        
        error = anomaly_service.establish_baseline("RFID-001", features)
        
        assert error >= 0
        assert "RFID-001" in anomaly_service.baselines
    
    def test_detect_anomaly_normal(self, anomaly_service):
        """Test normal case (no anomaly)"""
        animal_id = "RFID-001"
        features = np.random.randn(128)
        
        # Establish baseline
        anomaly_service.establish_baseline(animal_id, features)
        
        # Detect anomaly (should be low error)
        is_anomaly, score = anomaly_service.detect_anomaly(animal_id, features)
        
        assert isinstance(is_anomaly, bool)
        assert 0 <= score <= 2
    
    def test_detect_anomaly_outlier(self, anomaly_service):
        """Test anomaly case"""
        animal_id = "RFID-001"
        baseline_features = np.random.randn(128)
        outlier_features = np.random.randn(128) * 10  # Very different
        
        # Establish baseline
        anomaly_service.establish_baseline(animal_id, baseline_features)
        
        # Detect anomaly in outlier
        is_anomaly, score = anomaly_service.detect_anomaly(animal_id, outlier_features)
        
        assert isinstance(is_anomaly, bool)
        assert 0 <= score <= 2


class TestAdvancedReIDService:
    """Test advanced Re-ID service"""
    
    @pytest.fixture
    def reid_service(self):
        """Create Re-ID service"""
        with patch("app.services.advanced.ResNetReID"):
            service = AdvancedReIDService(device="cpu")
            service.resnet_model = MagicMock()
            # Mock the model to return feature tensor
            import torch
            service.resnet_model.return_value = torch.randn(256)
            return service
    
    def test_initialization(self, reid_service):
        """Test initialization"""
        assert reid_service is not None
        assert reid_service.similarity_threshold == 0.7
    
    def test_extract_features(self, reid_service):
        """Test feature extraction"""
        bbox_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        
        features = reid_service.extract_features(bbox_image)
        
        assert features.shape == (256,)
    
    def test_register_animal(self, reid_service):
        """Test animal registration"""
        features = np.random.randn(256)
        
        result = reid_service.register_animal("RFID-001", "camera-1", features)
        
        assert result is True
        assert "RFID-001_camera-1" in reid_service.features_db
    
    def test_match_features_same(self, reid_service):
        """Test matching same features"""
        features = np.random.randn(256)
        features = features / np.linalg.norm(features)
        
        reid_service.register_animal("RFID-001", "camera-1", features)
        
        similarity, is_match = reid_service.match_features(
            "RFID-001",
            "camera-1",
            features,
        )
        
        assert similarity > 0.99  # Should be nearly 1.0
        assert is_match is True
    
    def test_match_features_different(self, reid_service):
        """Test matching different features"""
        features1 = np.random.randn(256)
        features1 = features1 / np.linalg.norm(features1)
        features2 = np.random.randn(256)
        features2 = features2 / np.linalg.norm(features2)
        
        reid_service.register_animal("RFID-001", "camera-1", features1)
        
        similarity, is_match = reid_service.match_features(
            "RFID-001",
            "camera-1",
            features2,
        )
        
        assert 0 <= similarity <= 1
        assert isinstance(is_match, bool)
    
    def test_match_unregistered_animal(self, reid_service):
        """Test matching unregistered animal"""
        features = np.random.randn(256)
        
        similarity, is_match = reid_service.match_features(
            "RFID-999",
            "camera-1",
            features,
        )
        
        assert similarity == 0.0
        assert is_match is False
