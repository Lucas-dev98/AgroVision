"""
Production Prediction Service - FASE 3.4 Task 1

Implementação de API de predição rápida para produção com:
- Batch predictions
- Streaming predictions
- Model info
- Health checks
- Validação de inputs
- Tratamento de erros
"""

import logging
import time
import asyncio
from typing import List, Dict, Any, AsyncGenerator, Optional
from dataclasses import dataclass
from datetime import timezone, datetime
import numpy as np

import torch
import torch.nn as nn


logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

@dataclass
class PredictionRequest:
    """Single prediction request."""
    model_type: str
    input_data: np.ndarray
    
    def __post_init__(self):
        """Validate on creation."""
        valid_models = ["behavior", "anomaly", "reid", "temporal"]
        if self.model_type not in valid_models:
            raise ValueError(f"model_type must be one of {valid_models}")
        
        if self.input_data is None or len(self.input_data) == 0:
            raise ValueError("input_data cannot be empty")


@dataclass
class BatchPredictionRequest:
    """Batch prediction request."""
    model_type: str
    inputs: List[np.ndarray]
    max_batch_size: int = 1000
    
    def __post_init__(self):
        """Validate on creation."""
        valid_models = ["behavior", "anomaly", "reid", "temporal"]
        if self.model_type not in valid_models:
            raise ValueError(f"model_type must be one of {valid_models}")
        
        if len(self.inputs) == 0:
            raise ValueError("inputs cannot be empty")
        
        if len(self.inputs) > self.max_batch_size:
            raise ValueError(f"Batch size {len(self.inputs)} exceeds maximum {self.max_batch_size}")


@dataclass
class PredictionResponse:
    """Single prediction response."""
    model_type: str
    prediction: Dict[str, Any]
    confidence: float
    processing_time_ms: float
    model_version: str
    timestamp: str


@dataclass
class BatchPredictionResponse:
    """Batch prediction response."""
    model_type: str
    predictions: List[Dict[str, Any]]
    batch_size: int
    processing_time_ms: float
    model_version: str
    timestamp: str
    
    def __post_init__(self):
        assert len(self.predictions) == self.batch_size


@dataclass
class ModelInfo:
    """Model information."""
    model_type: str
    input_shape: tuple
    output_shape: Optional[tuple]
    output_classes: Optional[int]
    version: str
    device: str
    is_loaded: bool


# ============================================================================
# Prediction Service
# ============================================================================

class PredictionService:
    """
    Production-ready prediction service.
    
    Features:
    - Batch predictions (up to 1000 samples)
    - Streaming predictions
    - Model info endpoints
    - Health checks
    - Input validation
    - Error handling
    - Performance monitoring
    
    Exemplo:
        ```python
        service = PredictionService(
            behavior_model=behavior_model,
            anomaly_model=anomaly_model,
            reid_model=reid_model,
            temporal_model=temporal_model,
            device="cuda"
        )
        
        # Batch predict
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[img1, img2, img3],
        )
        response = await service.batch_predict(request)
        
        # Stream predict
        async for pred in service.stream_predict("behavior", images):
            print(pred)
        
        # Health check
        health = await service.health_check()
        ```
    """
    
    def __init__(
        self,
        behavior_model: nn.Module,
        anomaly_model: nn.Module,
        reid_model: nn.Module,
        temporal_model: nn.Module,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        model_version: str = "1.0",
    ):
        """
        Initialize prediction service.
        
        Args:
            behavior_model: Trained CNN for behavior classification
            anomaly_model: Trained autoencoder for anomaly detection
            reid_model: Trained ResNet for re-identification
            temporal_model: Trained LSTM for temporal analysis
            device: Device to use (cuda/cpu)
            model_version: Version string for models
        """
        self.behavior_model = behavior_model
        self.anomaly_model = anomaly_model
        self.reid_model = reid_model
        self.temporal_model = temporal_model
        
        # Try CUDA, fall back to CPU
        try:
            if device == "cuda" and torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        except:
            self.device = "cpu"
        
        self.model_version = model_version
        
        # Move models to device
        self.behavior_model.to(self.device)
        self.anomaly_model.to(self.device)
        self.reid_model.to(self.device)
        self.temporal_model.to(self.device)
        
        # Set to eval mode
        self.behavior_model.eval()
        self.anomaly_model.eval()
        self.reid_model.eval()
        self.temporal_model.eval()
        
        # Model registry
        self.models = {
            "behavior": self.behavior_model,
            "anomaly": self.anomaly_model,
            "reid": self.reid_model,
            "temporal": self.temporal_model,
        }
        
        # Model configurations
        self.model_configs = {
            "behavior": {
                "input_shape": (3, 240, 240),
                "output_classes": 8,
                "classes": ["grazing", "walking", "resting", "drinking", 
                           "eating", "standing", "running", "lying"],
            },
            "anomaly": {
                "input_shape": (6,),
                "output_shape": (1,),
                "description": "Anomaly score (0-1, 0=normal, 1=anomalous)",
            },
            "reid": {
                "input_shape": (3, 224, 224),
                "output_shape": (256,),
                "description": "Re-ID feature vector (256-d)",
            },
            "temporal": {
                "input_shape": (30, 128),
                "output_classes": 8,
                "classes": ["grazing", "walking", "resting", "drinking",
                           "eating", "standing", "running", "lying"],
            },
        }
        
        logger.info(f"PredictionService initialized on {self.device}")
    
    async def batch_predict(
        self,
        request: BatchPredictionRequest,
    ) -> BatchPredictionResponse:
        """
        Perform batch predictions.
        
        Args:
            request: BatchPredictionRequest with model_type and inputs
            
        Returns:
            BatchPredictionResponse with predictions
        """
        start_time = time.time()
        
        logger.info(f"Batch prediction: {request.model_type}, {len(request.inputs)} samples")
        
        # Get model
        model = self.models.get(request.model_type)
        if model is None:
            raise ValueError(f"Unknown model type: {request.model_type}")
        
        # Convert inputs to tensors
        try:
            input_tensors = []
            for inp in request.inputs:
                if isinstance(inp, np.ndarray):
                    tensor = torch.from_numpy(inp).to(self.device)
                else:
                    tensor = inp.to(self.device)
                
                # Add batch dimension if needed
                if tensor.dim() == 3 and request.model_type in ["behavior", "reid"]:
                    tensor = tensor.unsqueeze(0)
                elif tensor.dim() == 1 and request.model_type == "anomaly":
                    tensor = tensor.unsqueeze(0)
                elif tensor.dim() == 2 and request.model_type == "temporal":
                    tensor = tensor.unsqueeze(0)
                
                input_tensors.append(tensor)
            
            # Stack tensors
            batch_input = torch.cat(input_tensors, dim=0)
        except Exception as e:
            logger.error(f"Error converting inputs to tensors: {e}")
            raise
        
        # Inference
        with torch.no_grad():
            try:
                outputs = model(batch_input)
            except Exception as e:
                logger.error(f"Error during inference: {e}")
                raise
        
        # Process outputs
        predictions = []
        if request.model_type == "behavior":
            # Classification - softmax probabilities
            probs = torch.softmax(outputs, dim=1)
            for i in range(outputs.size(0)):
                class_idx = torch.argmax(probs[i]).item()
                confidence = probs[i, class_idx].item()
                
                predictions.append({
                    "class": self.model_configs["behavior"]["classes"][class_idx],
                    "class_index": class_idx,
                    "confidence": float(confidence),
                    "probabilities": probs[i].cpu().numpy().tolist(),
                })
        
        elif request.model_type == "anomaly":
            # Anomaly score (0-1)
            for i in range(outputs.size(0)):
                score = torch.sigmoid(outputs[i]).item()
                
                predictions.append({
                    "anomaly_score": float(score),
                    "is_anomalous": bool(score > 0.5),
                    "risk_level": "high" if score > 0.7 else "medium" if score > 0.5 else "low",
                })
        
        elif request.model_type == "reid":
            # Re-ID features
            for i in range(outputs.size(0)):
                features = outputs[i].cpu().numpy().tolist()
                
                predictions.append({
                    "features": features,
                    "feature_dim": len(features),
                })
        
        elif request.model_type == "temporal":
            # Temporal classification
            probs = torch.softmax(outputs, dim=1)
            for i in range(outputs.size(0)):
                class_idx = torch.argmax(probs[i]).item()
                confidence = probs[i, class_idx].item()
                
                predictions.append({
                    "class": self.model_configs["temporal"]["classes"][class_idx],
                    "class_index": class_idx,
                    "confidence": float(confidence),
                    "probabilities": probs[i].cpu().numpy().tolist(),
                })
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Batch prediction complete: {elapsed_ms:.2f}ms for {len(request.inputs)} samples")
        
        return BatchPredictionResponse(
            model_type=request.model_type,
            predictions=predictions,
            batch_size=len(request.inputs),
            processing_time_ms=elapsed_ms,
            model_version=self.model_version,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    
    async def stream_predict(
        self,
        model_type: str,
        inputs: List[np.ndarray],
        batch_size: int = 32,
        timeout_seconds: Optional[float] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream predictions as they complete.
        
        Args:
            model_type: Type of model
            inputs: List of input samples
            batch_size: Batch size for processing
            timeout_seconds: Optional timeout
            
        Yields:
            Prediction dictionaries
        """
        total_batches = (len(inputs) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start = batch_idx * batch_size
            end = min((batch_idx + 1) * batch_size, len(inputs))
            
            batch_inputs = inputs[start:end]
            
            request = BatchPredictionRequest(
                model_type=model_type,
                inputs=batch_inputs,
            )
            
            response = await asyncio.wait_for(
                self.batch_predict(request),
                timeout=timeout_seconds,
            )
            
            for pred in response.predictions:
                yield pred
    
    def get_model_info(self, model_type: str) -> ModelInfo:
        """
        Get information about a model.
        
        Args:
            model_type: Type of model (behavior, anomaly, reid, temporal)
            
        Returns:
            ModelInfo with model details
        """
        if model_type not in self.models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        config = self.model_configs[model_type]
        
        return ModelInfo(
            model_type=model_type,
            input_shape=config.get("input_shape"),
            output_shape=config.get("output_shape"),
            output_classes=config.get("output_classes"),
            version=self.model_version,
            device=self.device,
            is_loaded=True,
        )
    
    def get_all_models_info(self) -> Dict[str, ModelInfo]:
        """
        Get information about all models.
        
        Returns:
            Dictionary of model_type -> ModelInfo
        """
        return {
            model_type: self.get_model_info(model_type)
            for model_type in self.models.keys()
        }
    
    async def health_check(
        self,
        run_inference: bool = False,
    ) -> Dict[str, Any]:
        """
        Check service health.
        
        Args:
            run_inference: If True, run actual inference to test
            
        Returns:
            Health status dictionary
        """
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device": self.device,
            "models_loaded": len(self.models),
            "models": {
                model_type: model is not None
                for model_type, model in self.models.items()
            },
            "model_version": self.model_version,
        }
        
        # Run inference test
        if run_inference:
            start_time = time.time()
            try:
                # Test with small sample
                test_input = np.random.randn(1, 3, 240, 240).astype(np.float32)
                request = BatchPredictionRequest(
                    model_type="behavior",
                    inputs=[test_input],
                )
                await self.batch_predict(request)
                
                inference_time_ms = (time.time() - start_time) * 1000
                health["inference_time_ms"] = inference_time_ms
                
                if inference_time_ms > 1000:
                    health["status"] = "degraded"
                    
            except Exception as e:
                logger.error(f"Health check inference failed: {e}")
                health["status"] = "unhealthy"
                health["error"] = str(e)
        
        return health
