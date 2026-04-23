"""Integration tests for FASE 2 models and endpoints"""

import pytest
import numpy as np
import torch
import base64
import cv2
from typing import Dict

from app.models.deep_learning import (
    CNNBehaviorClassifier,
    AnomalyDetectionAutoencoder,
    ResNetReID,
    LSTMTemporalAnalyzer,
)
from app.models.checkpoints import ModelCheckpoint
from app.services.advanced import (
    AdvancedBehaviorService,
    AdvancedAnomalyService,
    AdvancedReIDService,
)
from app.training.train import TrainingPipeline


class TestModelCheckpoints:
    """Test checkpoint save/load functionality"""

    def test_save_and_load_checkpoint(self, tmp_path):
        """Test saving and loading training checkpoints"""
        manager = ModelCheckpoint(str(tmp_path))

        # Create model and optimizer
        model = CNNBehaviorClassifier(num_classes=8)
        optimizer = torch.optim.Adam(model.parameters())

        # Save checkpoint
        metrics = {"train_loss": 0.5, "val_loss": 0.6}
        path = manager.save_checkpoint(
            model, optimizer, epoch=5, metrics=metrics, checkpoint_name="test_model"
        )

        assert path is not None
        assert "test_model" in path

    def test_save_and_load_model(self, tmp_path):
        """Test saving and loading inference model"""
        manager = ModelCheckpoint(str(tmp_path))

        # Create and save model
        model = CNNBehaviorClassifier(num_classes=8)
        model_path = manager.save_model(model, "behavior_model")

        assert model_path is not None

        # Load model
        loaded_model = CNNBehaviorClassifier(num_classes=8)
        loaded_model = manager.load_model(loaded_model, "behavior_model")

        assert loaded_model is not None

    def test_get_best_checkpoint(self, tmp_path):
        """Test getting best checkpoint by metric"""
        manager = ModelCheckpoint(str(tmp_path))

        model = CNNBehaviorClassifier(num_classes=8)
        optimizer = torch.optim.Adam(model.parameters())

        # Save multiple checkpoints with different metrics
        for epoch in [1, 2, 3]:
            manager.save_checkpoint(
                model,
                optimizer,
                epoch=epoch,
                metrics={"val_loss": 1.0 / epoch},  # Best at epoch 3
                checkpoint_name="test",
            )

        best = manager.get_best_checkpoint("test", metric="val_loss")
        assert best is not None
        assert "epoch3" in best


class TestAdvancedServicesIntegration:
    """Test advanced services with deep learning models"""

    def test_behavior_service_end_to_end(self):
        """Test behavior service with full pipeline"""
        service = AdvancedBehaviorService(device="cpu")

        # Create dummy bbox image
        bbox_image = np.random.randint(0, 255, (240, 240, 3), dtype=np.uint8)

        # Classify
        classification = service.classify_from_bbox(
            bbox_image,
            track_id=1,
            position={"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.2},
        )

        assert classification is not None
        assert hasattr(classification, "behavior")
        assert hasattr(classification, "confidence")

    def test_anomaly_service_end_to_end(self):
        """Test anomaly service with full pipeline"""
        service = AdvancedAnomalyService(device="cpu")

        animal_id = "RFID-001"
        baseline_features = np.random.randn(128)
        test_features = np.random.randn(128)

        # Establish baseline
        service.establish_baseline(animal_id, baseline_features)

        # Detect anomaly
        is_anomaly, score = service.detect_anomaly(animal_id, test_features)

        assert isinstance(is_anomaly, bool)
        assert 0 <= score <= 2

    def test_reid_service_end_to_end(self):
        """Test Re-ID service with full pipeline"""
        service = AdvancedReIDService(device="cpu")

        # Extract features from image
        bbox_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        features = service.extract_features(bbox_image)

        assert features.shape == (256,)

        # Register animal
        service.register_animal("RFID-001", "camera-1", features)

        # Match features
        similarity, is_match = service.match_features(
            "RFID-001", "camera-1", features
        )

        assert 0 <= similarity <= 1
        assert isinstance(is_match, bool)


class TestTrainingPipeline:
    """Test model training"""

    def test_behavior_training(self):
        """Test behavior model training"""
        pipeline = TrainingPipeline(device="cpu")

        history = pipeline.train_behavior_model(
            epochs=2, batch_size=16, use_synthetic=True
        )

        assert "train_loss" in history
        assert "val_loss" in history
        assert len(history["train_loss"]) == 2

    def test_anomaly_training(self):
        """Test anomaly model training"""
        pipeline = TrainingPipeline(device="cpu")

        history = pipeline.train_anomaly_model(
            epochs=2, batch_size=16, use_synthetic=True
        )

        assert "train_loss" in history
        assert "val_loss" in history

    def test_temporal_training(self):
        """Test temporal model training"""
        pipeline = TrainingPipeline(device="cpu")

        history = pipeline.train_temporal_model(
            epochs=2, batch_size=16, use_synthetic=True
        )

        assert "train_loss" in history
        assert "val_loss" in history

    def test_reid_training(self):
        """Test Re-ID model training"""
        pipeline = TrainingPipeline(device="cpu")

        history = pipeline.train_reid_model(
            epochs=2, batch_size=16, use_synthetic=True
        )

        assert "train_loss" in history
        assert "val_loss" in history

    def test_train_all_models(self):
        """Test training all models together"""
        pipeline = TrainingPipeline(device="cpu")

        results = pipeline.train_all_models(epochs=1, batch_size=16)

        assert "behavior" in results
        assert "anomaly" in results
        assert "reid" in results
        assert "temporal" in results


class TestFullPipelineIntegration:
    """Test full ML pipeline from frame to predictions"""

    def test_frame_to_behavior_classification(self):
        """Test full pipeline: frame -> behavior"""
        # Create behavior service
        behavior_service = AdvancedBehaviorService(device="cpu")

        # Create dummy frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        bbox = frame[100:340, 100:340]  # 240x240 region

        # Classify
        classification = behavior_service.classify_from_bbox(
            bbox,
            track_id=1,
            position={"x": 0.2, "y": 0.2, "w": 0.375, "h": 0.375},
        )

        assert classification is not None

    def test_frame_to_reid_features(self):
        """Test full pipeline: frame -> Re-ID features"""
        reid_service = AdvancedReIDService(device="cpu")

        # Create dummy frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        bbox = cv2.resize(frame[100:340, 100:340], (224, 224))

        # Extract features
        features = reid_service.extract_features(bbox)

        assert features.shape == (256,)
        assert np.allclose(np.linalg.norm(features), 1.0)  # Normalized

    def test_multi_camera_reid(self):
        """Test Re-ID matching across multiple cameras"""
        reid_service = AdvancedReIDService(device="cpu")

        # Create dummy frames from two cameras
        frame1 = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        frame2 = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)

        # Extract features
        features1 = reid_service.extract_features(frame1)
        features2 = reid_service.extract_features(frame2)

        # Register from camera 1
        reid_service.register_animal("RFID-001", "camera-1", features1)

        # Match from camera 2
        similarity, is_match = reid_service.match_features(
            "RFID-001", "camera-1", features2
        )

        assert 0 <= similarity <= 1

    def test_anomaly_detection_workflow(self):
        """Test anomaly detection workflow"""
        anomaly_service = AdvancedAnomalyService(device="cpu")

        # Simulate baseline collection
        animal_id = "RFID-001"
        baseline_samples = [np.random.randn(128) * 0.1 for _ in range(5)]
        baseline_features = np.mean(baseline_samples, axis=0)

        # Establish baseline
        anomaly_service.establish_baseline(animal_id, baseline_features)

        # Normal samples
        for _ in range(3):
            normal_features = baseline_features + np.random.randn(128) * 0.05
            is_anomaly, score = anomaly_service.detect_anomaly(
                animal_id, normal_features
            )
            assert not is_anomaly or score < 1.0

        # Anomalous sample
        anomalous_features = baseline_features + np.random.randn(128) * 2.0
        is_anomaly, score = anomaly_service.detect_anomaly(
            animal_id, anomalous_features
        )
        assert isinstance(is_anomaly, bool)


class TestModelSerialization:
    """Test model serialization for deployment"""

    def test_behavior_model_inference(self):
        """Test behavior model can do inference"""
        model = CNNBehaviorClassifier(num_classes=8)
        model.eval()

        # Dummy input
        x = torch.randn(4, 3, 240, 240)

        with torch.no_grad():
            logits, probs = model(x)

        assert logits.shape == (4, 8)
        assert probs.shape == (4, 8)

    def test_autoencoder_inference(self):
        """Test autoencoder can encode/decode"""
        model = AnomalyDetectionAutoencoder(feature_dim=128, latent_dim=32)
        model.eval()

        # Dummy input
        x = torch.randn(4, 128)

        with torch.no_grad():
            reconstruction, latent = model(x)

        assert reconstruction.shape == (4, 128)
        assert latent.shape == (4, 32)

    def test_resnet_inference(self):
        """Test ResNet can extract features"""
        model = ResNetReID(feature_dim=256)
        model.eval()

        # Dummy input
        x = torch.randn(4, 3, 224, 224)

        with torch.no_grad():
            features = model(x)

        assert features.shape == (4, 256)

    def test_lstm_inference(self):
        """Test LSTM can process sequences"""
        model = LSTMTemporalAnalyzer(input_size=128, hidden_size=256, num_classes=8)
        model.eval()

        # Dummy input
        x = torch.randn(4, 10, 128)

        with torch.no_grad():
            logits, attention = model(x)

        assert logits.shape == (4, 8)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
