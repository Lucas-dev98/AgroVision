import torch
import torch.nn.functional as F
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from app.schemas import BehaviorClassification, AnimalBehavior
from app.models.deep_learning import (
    CNNBehaviorClassifier,
    AnomalyDetectionAutoencoder,
    ResNetReID,
    LSTMTemporalAnalyzer,
)


class AdvancedBehaviorService:
    """Advanced behavior analysis using CNN + LSTM"""
    
    def __init__(self, device: str = "cpu"):
        """Initialize advanced behavior service"""
        self.device = torch.device(device)
        self.cnn_model = CNNBehaviorClassifier(num_classes=8).to(self.device)
        self.lstm_model = LSTMTemporalAnalyzer(input_size=128, hidden_size=256).to(self.device)
        self.cnn_model.eval()
        self.lstm_model.eval()
        
        # Behavior mapping
        self.behavior_map = {
            0: AnimalBehavior.GRAZING,
            1: AnimalBehavior.RESTING,
            2: AnimalBehavior.DRINKING,
            3: AnimalBehavior.WALKING,
            4: AnimalBehavior.RUNNING,
            5: AnimalBehavior.STANDING,
            6: AnimalBehavior.EATING,
            7: AnimalBehavior.UNKNOWN,
        }
        
        # Sequence storage for LSTM
        self.sequences: Dict[int, List[np.ndarray]] = {}
        self.seq_len = 10
    
    def classify_from_bbox(
        self,
        bbox_image: np.ndarray,
        track_id: int,
        position: Dict[str, float],
    ) -> BehaviorClassification:
        """
        Classify behavior from bounding box image using CNN
        
        Args:
            bbox_image: Bounding box image (H, W, 3)
            track_id: Track ID
            position: Position dictionary
            
        Returns:
            BehaviorClassification
        """
        try:
            # Preprocess image
            if bbox_image.shape[0] < 240 or bbox_image.shape[1] < 240:
                # Resize if needed
                import cv2
                bbox_image = cv2.resize(bbox_image, (240, 240))
            
            # Convert to tensor
            img_tensor = torch.tensor(bbox_image, dtype=torch.float32).permute(2, 0, 1) / 255.0
            img_tensor = img_tensor.unsqueeze(0).to(self.device)
            
            # Inference
            with torch.no_grad():
                logits, probs = self.cnn_model(img_tensor)
            
            # Get prediction
            pred_idx = torch.argmax(probs, dim=1).item()
            confidence = float(probs[0, pred_idx])
            behavior = self.behavior_map.get(pred_idx, AnimalBehavior.UNKNOWN)
            
            # Extract features for LSTM
            features = logits[0].cpu().numpy()
            
            # Store for temporal analysis
            if track_id not in self.sequences:
                self.sequences[track_id] = []
            self.sequences[track_id].append(features)
            
            # Keep only last seq_len
            if len(self.sequences[track_id]) > self.seq_len:
                self.sequences[track_id] = self.sequences[track_id][-self.seq_len:]
            
            return BehaviorClassification(
                behavior=behavior,
                confidence=confidence,
                position=position,
            )
        
        except Exception as e:
            print(f"❌ CNN behavior classification failed: {e}")
            return BehaviorClassification(
                behavior=AnimalBehavior.UNKNOWN,
                confidence=0.0,
                position=position,
            )
    
    def classify_temporal(
        self,
        track_id: int,
        position: Dict[str, float],
    ) -> BehaviorClassification:
        """
        Classify behavior using temporal LSTM
        
        Args:
            track_id: Track ID
            position: Position dictionary
            
        Returns:
            BehaviorClassification
        """
        if track_id not in self.sequences or len(self.sequences[track_id]) < 5:
            return BehaviorClassification(
                behavior=AnimalBehavior.UNKNOWN,
                confidence=0.0,
                position=position,
            )
        
        try:
            # Prepare sequence
            seq = np.array(self.sequences[track_id])
            seq_tensor = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            # Inference
            with torch.no_grad():
                logits, _ = self.lstm_model(seq_tensor)
            
            # Get prediction
            probs = torch.softmax(logits, dim=1)
            pred_idx = torch.argmax(probs, dim=1).item()
            confidence = float(probs[0, pred_idx])
            behavior = self.behavior_map.get(pred_idx, AnimalBehavior.UNKNOWN)
            
            return BehaviorClassification(
                behavior=behavior,
                confidence=confidence,
                position=position,
            )
        
        except Exception as e:
            print(f"❌ LSTM behavior classification failed: {e}")
            return BehaviorClassification(
                behavior=AnimalBehavior.UNKNOWN,
                confidence=0.0,
                position=position,
            )
    
    def get_behavior_confidence(
        self,
        track_id: int,
    ) -> Dict[str, float]:
        """Get confidence scores for all behaviors"""
        if track_id not in self.sequences or len(self.sequences[track_id]) == 0:
            return {}
        
        try:
            seq = np.array(self.sequences[track_id])
            seq_tensor = torch.tensor(seq, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                logits, _ = self.lstm_model(seq_tensor)
                probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
            
            return {str(self.behavior_map[i]): float(prob) for i, prob in enumerate(probs)}
        
        except Exception:
            return {}


class AdvancedAnomalyService:
    """Advanced anomaly detection using Autoencoder"""
    
    def __init__(self, device: str = "cpu"):
        """Initialize advanced anomaly service"""
        self.device = torch.device(device)
        from app.models.deep_learning import AnomalyDetectionAutoencoder
        
        self.autoencoder = AnomalyDetectionAutoencoder(
            feature_dim=128,
            latent_dim=32
        ).to(self.device)
        self.autoencoder.eval()
        
        # Baseline reconstructions
        self.baselines: Dict[str, float] = {}
        self.anomaly_threshold = 0.7
    
    def establish_baseline(
        self,
        animal_id: str,
        features: np.ndarray,
    ) -> float:
        """
        Establish baseline reconstruction error
        
        Args:
            animal_id: Animal ID
            features: Feature vector (128,)
            
        Returns:
            Reconstruction error
        """
        try:
            feat_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                reconstruction, _ = self.autoencoder(feat_tensor)
                error = float(F.mse_loss(reconstruction, feat_tensor))
            
            # Store baseline (slightly above actual)
            self.baselines[animal_id] = error * 1.2
            
            return error
        
        except Exception as e:
            print(f"❌ Baseline establishment failed: {e}")
            return 0.0
    
    def detect_anomaly(
        self,
        animal_id: str,
        features: np.ndarray,
    ) -> Tuple[bool, float]:
        """
        Detect anomaly using reconstruction error
        
        Args:
            animal_id: Animal ID
            features: Feature vector (128,)
            
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        try:
            if animal_id not in self.baselines:
                self.establish_baseline(animal_id, features)
            
            feat_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                reconstruction, latent = self.autoencoder(feat_tensor)
                error = float(F.mse_loss(reconstruction, feat_tensor))
            
            baseline = self.baselines.get(animal_id, error)
            anomaly_score = min(error / (baseline + 1e-6), 2.0)  # Clamp to [0, 2]
            is_anomaly = anomaly_score > self.anomaly_threshold
            
            return is_anomaly, anomaly_score
        
        except Exception as e:
            print(f"❌ Anomaly detection failed: {e}")
            return False, 0.0


class AdvancedReIDService:
    """Advanced Re-ID using ResNet features"""
    
    def __init__(self, device: str = "cpu"):
        """Initialize advanced Re-ID service"""
        self.device = torch.device(device)
        from app.models.deep_learning import ResNetReID
        
        self.resnet_model = ResNetReID(feature_dim=256).to(self.device)
        self.resnet_model.eval()
        
        # Feature database
        self.features_db: Dict[str, np.ndarray] = {}
        self.similarity_threshold = 0.7
    
    def extract_features(self, bbox_image: np.ndarray) -> np.ndarray:
        """
        Extract feature embedding from bbox image
        
        Args:
            bbox_image: Bounding box image (H, W, 3)
            
        Returns:
            Feature embedding (256,)
        """
        try:
            import cv2
            
            # Resize to 224x224
            if bbox_image.shape[:2] != (224, 224):
                bbox_image = cv2.resize(bbox_image, (224, 224))
            
            # Convert to tensor
            img_tensor = torch.tensor(bbox_image, dtype=torch.float32).permute(2, 0, 1) / 255.0
            img_tensor = img_tensor.unsqueeze(0).to(self.device)
            
            # Extract features
            with torch.no_grad():
                features = self.resnet_model(img_tensor)
            
            return features[0].cpu().numpy()
        
        except Exception as e:
            print(f"❌ Feature extraction failed: {e}")
            return np.zeros(256)
    
    def register_animal(
        self,
        animal_id: str,
        camera_id: str,
        features: np.ndarray,
    ) -> bool:
        """Register animal features"""
        key = f"{animal_id}_{camera_id}"
        self.features_db[key] = features
        return True
    
    def match_features(
        self,
        animal_id: str,
        primary_camera: str,
        secondary_features: np.ndarray,
    ) -> Tuple[float, bool]:
        """
        Match features across cameras
        
        Args:
            animal_id: Animal ID
            primary_camera: Primary camera
            secondary_features: Features from secondary camera
            
        Returns:
            Tuple of (similarity, is_match)
        """
        key = f"{animal_id}_{primary_camera}"
        
        if key not in self.features_db:
            return 0.0, False
        
        primary_features = self.features_db[key]
        
        # Cosine similarity
        similarity = float(
            np.dot(primary_features, secondary_features) /
            (np.linalg.norm(primary_features) * np.linalg.norm(secondary_features) + 1e-6)
        )
        
        is_match = similarity >= self.similarity_threshold
        
        return similarity, is_match
