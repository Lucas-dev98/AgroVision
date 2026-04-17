import pytest
import torch
import numpy as np
from torch.utils.data import DataLoader

from app.models.deep_learning import (
    CNNBehaviorClassifier,
    AnomalyDetectionAutoencoder,
    ResNetReID,
    LSTMTemporalAnalyzer,
)
from app.training import (
    BehaviorDataset,
    AnomalyDataset,
    TemporalDataset,
    BehaviorClassifierTrainer,
    AnomalyDetectorTrainer,
    TemporalAnalyzerTrainer,
)


class TestCNNBehaviorClassifier:
    """Test CNN behavior classifier"""
    
    def test_model_initialization(self):
        """Test model initialization"""
        model = CNNBehaviorClassifier(num_classes=8)
        assert model is not None
    
    def test_forward_pass(self):
        """Test forward pass"""
        model = CNNBehaviorClassifier(num_classes=8)
        x = torch.randn(4, 3, 240, 240)
        logits, probs = model(x)
        
        assert logits.shape == (4, 8)
        assert probs.shape == (4, 8)
        assert torch.allclose(torch.sum(probs, dim=1), torch.ones(4))
    
    def test_gradient_flow(self):
        """Test gradient flow"""
        model = CNNBehaviorClassifier(num_classes=8)
        x = torch.randn(2, 3, 240, 240, requires_grad=True)
        logits, _ = model(x)
        loss = logits.sum()
        loss.backward()
        
        assert x.grad is not None


class TestAnomalyAutoencoder:
    """Test anomaly detection autoencoder"""
    
    def test_model_initialization(self):
        """Test model initialization"""
        model = AnomalyDetectionAutoencoder(feature_dim=128, latent_dim=32)
        assert model is not None
    
    def test_encode_decode(self):
        """Test encode/decode"""
        model = AnomalyDetectionAutoencoder(feature_dim=128, latent_dim=32)
        x = torch.randn(4, 128)
        
        latent = model.encode(x)
        reconstruction = model.decode(latent)
        
        assert latent.shape == (4, 32)
        assert reconstruction.shape == (4, 128)
    
    def test_forward_pass(self):
        """Test forward pass"""
        model = AnomalyDetectionAutoencoder(feature_dim=128, latent_dim=32)
        x = torch.randn(4, 128)
        
        reconstruction, latent = model(x)
        
        assert reconstruction.shape == (4, 128)
        assert latent.shape == (4, 32)
    
    def test_reconstruction_loss(self):
        """Test reconstruction matches input"""
        model = AnomalyDetectionAutoencoder(feature_dim=128, latent_dim=32)
        model.train()
        
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        x = torch.randn(8, 128)
        
        for _ in range(5):
            reconstruction, _ = model(x)
            loss = torch.nn.functional.mse_loss(reconstruction, x)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        
        model.eval()
        reconstruction, _ = model(x)
        final_loss = torch.nn.functional.mse_loss(reconstruction, x)
        
        assert final_loss < 1.0


class TestResNetReID:
    """Test ResNet Re-ID model"""
    
    def test_model_initialization(self):
        """Test model initialization"""
        model = ResNetReID(feature_dim=256)
        assert model is not None
    
    def test_forward_pass(self):
        """Test forward pass"""
        model = ResNetReID(feature_dim=256)
        x = torch.randn(4, 3, 224, 224)
        
        features = model(x)
        
        assert features.shape == (4, 256)
    
    def test_feature_normalization(self):
        """Test features are normalized"""
        model = ResNetReID(feature_dim=256)
        x = torch.randn(4, 3, 224, 224)
        
        features = model(x)
        norms = torch.norm(features, dim=1)
        
        assert torch.allclose(norms, torch.ones(4), atol=1e-5)


class TestLSTMTemporalAnalyzer:
    """Test LSTM temporal analyzer"""
    
    def test_model_initialization(self):
        """Test model initialization"""
        model = LSTMTemporalAnalyzer(input_size=128, hidden_size=256, num_classes=8)
        assert model is not None
    
    def test_forward_pass(self):
        """Test forward pass"""
        model = LSTMTemporalAnalyzer(input_size=128, hidden_size=256, num_classes=8)
        x = torch.randn(4, 10, 128)  # (batch, seq_len, input_size)
        
        logits, attn_weights = model(x)
        
        assert logits.shape == (4, 8)
    
    def test_different_sequence_lengths(self):
        """Test with different sequence lengths"""
        model = LSTMTemporalAnalyzer(input_size=128, hidden_size=256, num_classes=8)
        
        for seq_len in [5, 10, 20]:
            x = torch.randn(2, seq_len, 128)
            logits, _ = model(x)
            assert logits.shape == (2, 8)


# ==================== DATASET TESTS ====================

class TestBehaviorDataset:
    """Test behavior dataset"""
    
    def test_dataset_creation(self):
        """Test dataset creation"""
        frames = [np.random.randint(0, 255, (240, 240, 3), dtype=np.uint8) for _ in range(10)]
        behaviors = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1]
        
        dataset = BehaviorDataset(frames, behaviors)
        
        assert len(dataset) == 10
    
    def test_getitem(self):
        """Test dataset indexing"""
        frames = [np.random.randint(0, 255, (240, 240, 3), dtype=np.uint8) for _ in range(5)]
        behaviors = [0, 1, 2, 3, 4]
        
        dataset = BehaviorDataset(frames, behaviors)
        frame, behavior = dataset[0]
        
        assert frame.shape == (3, 240, 240)
        assert behavior == 0


class TestAnomalyDataset:
    """Test anomaly dataset"""
    
    def test_dataset_creation(self):
        """Test dataset creation"""
        features = [np.random.randn(128) for _ in range(10)]
        labels = [0, 0, 0, 1, 0, 0, 1, 0, 0, 1]
        
        dataset = AnomalyDataset(features, labels)
        
        assert len(dataset) == 10
    
    def test_getitem(self):
        """Test dataset indexing"""
        features = [np.random.randn(128) for _ in range(5)]
        labels = [0, 1, 0, 1, 0]
        
        dataset = AnomalyDataset(features, labels)
        feature, label = dataset[0]
        
        assert feature.shape == (128,)
        assert label == 0


class TestTemporalDataset:
    """Test temporal dataset"""
    
    def test_dataset_creation(self):
        """Test dataset creation"""
        sequences = [np.random.randn(10, 128) for _ in range(10)]
        behaviors = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1]
        
        dataset = TemporalDataset(sequences, behaviors, seq_len=10)
        
        assert len(dataset) == 10


# ==================== TRAINER TESTS ====================

class TestBehaviorClassifierTrainer:
    """Test behavior classifier trainer"""
    
    def test_trainer_initialization(self):
        """Test trainer initialization"""
        model = CNNBehaviorClassifier(num_classes=8)
        trainer = BehaviorClassifierTrainer(model)
        
        assert trainer is not None
        assert trainer.model is not None
    
    def test_train_epoch(self):
        """Test training epoch"""
        model = CNNBehaviorClassifier(num_classes=8)
        trainer = BehaviorClassifierTrainer(model)
        
        frames = [np.random.randint(0, 255, (240, 240, 3), dtype=np.uint8) for _ in range(4)]
        behaviors = [0, 1, 2, 3]
        
        dataset = BehaviorDataset(frames, behaviors)
        loader = DataLoader(dataset, batch_size=2)
        
        loss = trainer.train_epoch(loader)
        
        assert loss >= 0
    
    def test_validate(self):
        """Test validation"""
        model = CNNBehaviorClassifier(num_classes=8)
        trainer = BehaviorClassifierTrainer(model)
        
        frames = [np.random.randint(0, 255, (240, 240, 3), dtype=np.uint8) for _ in range(4)]
        behaviors = [0, 1, 2, 3]
        
        dataset = BehaviorDataset(frames, behaviors)
        loader = DataLoader(dataset, batch_size=2)
        
        loss = trainer.validate(loader)
        
        assert loss >= 0


class TestAnomalyDetectorTrainer:
    """Test anomaly detector trainer"""
    
    def test_trainer_initialization(self):
        """Test trainer initialization"""
        model = AnomalyDetectionAutoencoder(feature_dim=128, latent_dim=32)
        trainer = AnomalyDetectorTrainer(model)
        
        assert trainer is not None
    
    def test_train_epoch(self):
        """Test training epoch"""
        model = AnomalyDetectionAutoencoder(feature_dim=128, latent_dim=32)
        trainer = AnomalyDetectorTrainer(model)
        
        features = [np.random.randn(128) for _ in range(4)]
        labels = [0, 0, 0, 1]
        
        dataset = AnomalyDataset(features, labels)
        loader = DataLoader(dataset, batch_size=2)
        
        loss = trainer.train_epoch(loader)
        
        assert loss >= 0


class TestTemporalAnalyzerTrainer:
    """Test temporal analyzer trainer"""
    
    def test_trainer_initialization(self):
        """Test trainer initialization"""
        model = LSTMTemporalAnalyzer(input_size=128, hidden_size=256, num_classes=8)
        trainer = TemporalAnalyzerTrainer(model)
        
        assert trainer is not None
    
    def test_train_epoch(self):
        """Test training epoch"""
        model = LSTMTemporalAnalyzer(input_size=128, hidden_size=256, num_classes=8)
        trainer = TemporalAnalyzerTrainer(model)
        
        sequences = [np.random.randn(10, 128) for _ in range(4)]
        behaviors = [0, 1, 2, 3]
        
        dataset = TemporalDataset(sequences, behaviors)
        loader = DataLoader(dataset, batch_size=2)
        
        loss = trainer.train_epoch(loader)
        
        assert loss >= 0
