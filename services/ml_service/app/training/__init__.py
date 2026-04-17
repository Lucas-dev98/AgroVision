import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from typing import List, Tuple, Dict, Optional
import numpy as np
from abc import ABC, abstractmethod


class BehaviorDataset(Dataset):
    """Dataset for behavior classification"""
    
    def __init__(self, frames: List[np.ndarray], behaviors: List[int]):
        """
        Initialize dataset
        
        Args:
            frames: List of frame arrays (H, W, 3)
            behaviors: List of behavior class indices
        """
        self.frames = frames
        self.behaviors = behaviors
    
    def __len__(self) -> int:
        return len(self.frames)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        frame = torch.tensor(self.frames[idx], dtype=torch.float32).permute(2, 0, 1)
        frame = frame / 255.0  # Normalize to [0, 1]
        behavior = torch.tensor(self.behaviors[idx], dtype=torch.long)
        
        return frame, behavior


class AnomalyDataset(Dataset):
    """Dataset for anomaly detection"""
    
    def __init__(self, features: List[np.ndarray], labels: List[int]):
        """
        Initialize dataset
        
        Args:
            features: List of feature arrays
            labels: List of labels (0=normal, 1=anomaly)
        """
        self.features = features
        self.labels = labels
    
    def __len__(self) -> int:
        return len(self.features)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        feature = torch.tensor(self.features[idx], dtype=torch.float32)
        label = torch.tensor(self.labels[idx], dtype=torch.long)
        
        return feature, label


class TemporalDataset(Dataset):
    """Dataset for temporal sequence modeling"""
    
    def __init__(self, sequences: List[np.ndarray], behaviors: List[int], seq_len: int = 10):
        """
        Initialize dataset
        
        Args:
            sequences: List of sequences (seq_len, feature_dim)
            behaviors: List of target behaviors
            seq_len: Sequence length
        """
        self.sequences = sequences
        self.behaviors = behaviors
        self.seq_len = seq_len
    
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        seq = torch.tensor(self.sequences[idx], dtype=torch.float32)
        behavior = torch.tensor(self.behaviors[idx], dtype=torch.long)
        
        return seq, behavior


class ModelTrainer(ABC):
    """Base class for model training"""
    
    def __init__(
        self,
        model: nn.Module,
        device: torch.device = torch.device("cpu"),
        learning_rate: float = 1e-3,
    ):
        """
        Initialize trainer
        
        Args:
            model: PyTorch model
            device: Device to train on
            learning_rate: Learning rate
        """
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
        self.history = {"train_loss": [], "val_loss": []}
    
    @abstractmethod
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        pass
    
    @abstractmethod
    def validate(self, val_loader: DataLoader) -> float:
        """Validate model"""
        pass
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 10,
        patience: int = 3,
        learning_rate: Optional[float] = None,
    ) -> Dict:
        """
        Train model
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            patience: Patience for early stopping
            learning_rate: Optional learning rate (overrides constructor value)
            
        Returns:
            Training history
        """
        # Update learning rate if provided
        if learning_rate is not None:
            for param_group in self.optimizer.param_groups:
                param_group["lr"] = learning_rate
        
        best_val_loss = float("inf")
        patience_count = 0
        
        for epoch in range(epochs):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)
            
            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)
            
            if (epoch + 1) % 2 == 0:
                print(f"Epoch {epoch+1}/{epochs} | Train loss: {train_loss:.4f} | Val loss: {val_loss:.4f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_count = 0
            else:
                patience_count += 1
                if patience_count >= patience:
                    print(f"Early stopping at epoch {epoch}")
                    break
        
        return self.history


class BehaviorClassifierTrainer(ModelTrainer):
    """Trainer for behavior classifier"""
    
    def __init__(self, model: nn.Module, device: torch.device = None, learning_rate: float = 1e-3):
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        super().__init__(model, device, learning_rate)
        self.criterion = nn.CrossEntropyLoss()
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        
        for frames, behaviors in train_loader:
            frames = frames.to(self.device)
            behaviors = behaviors.to(self.device)
            
            self.optimizer.zero_grad()
            logits, _ = self.model(frames)
            loss = self.criterion(logits, behaviors)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader: DataLoader) -> float:
        """Validate model"""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for frames, behaviors in val_loader:
                frames = frames.to(self.device)
                behaviors = behaviors.to(self.device)
                
                logits, _ = self.model(frames)
                loss = self.criterion(logits, behaviors)
                total_loss += loss.item()
        
        return total_loss / len(val_loader)


class AnomalyDetectorTrainer(ModelTrainer):
    """Trainer for anomaly detector"""
    
    def __init__(self, model: nn.Module, device: torch.device = None, learning_rate: float = 1e-3):
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        super().__init__(model, device, learning_rate)
        self.criterion = nn.MSELoss()
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        
        for features, _ in train_loader:
            features = features.to(self.device)
            
            self.optimizer.zero_grad()
            reconstruction, _ = self.model(features)
            loss = self.criterion(reconstruction, features)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader: DataLoader) -> float:
        """Validate model"""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for features, _ in val_loader:
                features = features.to(self.device)
                reconstruction, _ = self.model(features)
                loss = self.criterion(reconstruction, features)
                total_loss += loss.item()
        
        return total_loss / len(val_loader)


class TemporalAnalyzerTrainer(ModelTrainer):
    """Trainer for temporal analyzer"""
    
    def __init__(self, model: nn.Module, device: torch.device = None, learning_rate: float = 1e-3):
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        super().__init__(model, device, learning_rate)
        self.criterion = nn.CrossEntropyLoss()
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        
        for sequences, behaviors in train_loader:
            sequences = sequences.to(self.device)
            behaviors = behaviors.to(self.device)
            
            self.optimizer.zero_grad()
            logits, _ = self.model(sequences)
            loss = self.criterion(logits, behaviors)
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader: DataLoader) -> float:
        """Validate model"""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for sequences, behaviors in val_loader:
                sequences = sequences.to(self.device)
                behaviors = behaviors.to(self.device)
                
                logits, _ = self.model(sequences)
                loss = self.criterion(logits, behaviors)
                total_loss += loss.item()
        
        return total_loss / len(val_loader)
