import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple


class CNNBehaviorClassifier(nn.Module):
    """CNN-based behavior classifier for animal activity recognition"""
    
    def __init__(self, num_classes: int = 8, input_channels: int = 3):
        """
        Initialize CNN behavior classifier
        
        Args:
            num_classes: Number of behavior classes
            input_channels: Input image channels (3 for RGB)
        """
        super().__init__()
        
        # Feature extraction
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(128 * 30 * 30, 256)
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, 128)
        self.dropout2 = nn.Dropout(0.5)
        self.fc3 = nn.Linear(128, num_classes)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input tensor (batch_size, 3, 240, 240)
            
        Returns:
            Tuple of (logits, probabilities)
        """
        # Conv blocks
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # FC layers
        x = self.dropout1(F.relu(self.fc1(x)))
        x = self.dropout2(F.relu(self.fc2(x)))
        logits = self.fc3(x)
        
        # Probabilities
        probs = F.softmax(logits, dim=1)
        
        return logits, probs


class AnomalyDetectionAutoencoder(nn.Module):
    """Autoencoder for anomaly detection in animal behavior"""
    
    def __init__(self, feature_dim: int = 128, latent_dim: int = 32):
        """
        Initialize autoencoder
        
        Args:
            feature_dim: Dimension of input features
            latent_dim: Dimension of latent space
        """
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(feature_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            
            nn.Linear(64, latent_dim),
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            
            nn.Linear(256, feature_dim),
        )
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode to latent space"""
        return self.encoder(x)
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode from latent space"""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input features (batch_size, feature_dim)
            
        Returns:
            Tuple of (reconstruction, latent)
        """
        latent = self.encode(x)
        reconstruction = self.decode(latent)
        
        return reconstruction, latent


class ResNetReID(nn.Module):
    """ResNet-based Re-ID model for cross-camera animal matching"""
    
    def __init__(self, feature_dim: int = 256):
        """
        Initialize ResNet Re-ID
        
        Args:
            feature_dim: Dimension of feature embedding
        """
        super().__init__()
        
        # Backbone (simplified ResNet)
        self.backbone = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
            
            # ResBlock 1
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            
            # ResBlock 2
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
        )
        
        # Global average pooling
        self.gap = nn.AdaptiveAvgPool2d((1, 1))
        
        # Feature embedding
        self.feat_bn = nn.BatchNorm1d(128)
        self.feat_bn.bias.requires_grad_(False)
        
        self.feat_fc = nn.Linear(128, feature_dim, bias=False)
        self.feat_bn_out = nn.BatchNorm1d(feature_dim)
        self.feat_bn_out.bias.requires_grad_(False)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input image (batch_size, 3, 224, 224)
            
        Returns:
            Feature embedding (batch_size, feature_dim)
        """
        # Backbone
        x = self.backbone(x)
        
        # Global pooling
        x = self.gap(x)
        x = x.view(x.size(0), -1)
        
        # Feature embedding
        x = self.feat_bn(x)
        x = self.feat_fc(x)
        x = self.feat_bn_out(x)
        
        # L2 normalization
        x = F.normalize(x, p=2, dim=1)
        
        return x


class LSTMTemporalAnalyzer(nn.Module):
    """LSTM for temporal behavior analysis"""
    
    def __init__(
        self,
        input_size: int = 128,
        hidden_size: int = 256,
        num_layers: int = 2,
        num_classes: int = 8,
    ):
        """
        Initialize LSTM temporal analyzer
        
        Args:
            input_size: Size of input features
            hidden_size: Size of hidden state
            num_layers: Number of LSTM layers
            num_classes: Number of behavior classes
        """
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.3 if num_layers > 1 else 0,
            bidirectional=True,
        )
        
        # Attention layer
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size * 2,
            num_heads=4,
            batch_first=True,
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input sequence (batch_size, seq_len, input_size)
            
        Returns:
            Tuple of (logits, attention_weights)
        """
        # LSTM
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Attention
        attn_out, attn_weights = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Use last output for classification
        last_output = attn_out[:, -1, :]
        
        # Classification
        logits = self.classifier(last_output)
        
        return logits, attn_weights
