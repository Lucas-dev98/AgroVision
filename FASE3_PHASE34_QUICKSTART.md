# FASE 3.4 Task 1: Real-time Prediction API - Quick Start Guide

## Overview

The `PredictionService` provides a production-ready async API for real-time inference on cattle farm computer vision models. It supports 4 model types with batch and streaming prediction capabilities.

## Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install torch torchvision pydantic fastapi uvicorn

# Navigate to ml_service
cd services/ml_service
```

## Basic Usage

### 1. Initialize PredictionService

```python
import torch
from app.services.prediction_service import PredictionService
import numpy as np

# Load your trained models
behavior_model = torch.load("models/behavior_classifier.pt")
anomaly_model = torch.load("models/anomaly_detector.pt")
reid_model = torch.load("models/reid_encoder.pt")
temporal_model = torch.load("models/temporal_analyzer.pt")

# Create service
service = PredictionService(
    behavior_model=behavior_model,
    anomaly_model=anomaly_model,
    reid_model=reid_model,
    temporal_model=temporal_model,
    device="cuda"  # or "cpu"
)
```

### 2. Batch Predictions

```python
import asyncio
from app.services.prediction_service import BatchPredictionRequest

async def predict_batch():
    # Prepare input data
    images = [
        np.random.randn(3, 240, 240).astype(np.float32)  # RGB image
        for _ in range(10)
    ]
    
    # Create request
    request = BatchPredictionRequest(
        model_type="behavior",
        inputs=images
    )
    
    # Get predictions
    response = await service.batch_predict(request)
    
    # Parse results
    for i, pred in enumerate(response.predictions):
        print(f"Sample {i}: {pred['class']} (confidence: {pred['confidence']:.2f})")
    
    print(f"Processing time: {response.processing_time_ms:.2f}ms")

# Run
asyncio.run(predict_batch())
```

### 3. Streaming Predictions

```python
async def stream_predictions():
    # Prepare inputs
    images = [np.random.randn(3, 240, 240).astype(np.float32) for _ in range(100)]
    
    # Stream predictions (batches of 32)
    async for prediction in service.stream_predict(
        model_type="behavior",
        inputs=images,
        batch_size=32
    ):
        print(f"Predicted: {prediction['class']} ({prediction['confidence']:.2f})")

asyncio.run(stream_predictions())
```

### 4. Get Model Information

```python
# Single model info
behavior_info = service.get_model_info("behavior")
print(f"Input shape: {behavior_info.input_shape}")
print(f"Classes: {behavior_info.output_classes}")

# All models info
all_models = service.get_all_models_info()
for model_type, info in all_models.items():
    print(f"{model_type}: {info.input_shape} → {info.output_shape}")
```

### 5. Health Check

```python
async def check_health():
    # Basic health check
    health = await service.health_check()
    print(f"Status: {health['status']}")
    print(f"Models loaded: {health['models_loaded']}/4")
    
    # With test inference
    health = await service.health_check(run_inference=True)
    print(f"Inference time: {health['inference_time_ms']:.2f}ms")

asyncio.run(check_health())
```

## Model Types & Input Formats

### Behavior Classification
```python
# Input: RGB image (3×240×240)
request = BatchPredictionRequest(
    model_type="behavior",
    inputs=[np.random.randn(3, 240, 240).astype(np.float32)]
)
# Output: 8 behavior classes (grazing, resting, drinking, etc)
```

### Anomaly Detection
```python
# Input: 6-d feature vector
request = BatchPredictionRequest(
    model_type="anomaly",
    inputs=[np.random.randn(6).astype(np.float32)]
)
# Output: Anomaly score [0, 1]
```

### Re-Identification
```python
# Input: RGB image (3×224×224)
request = BatchPredictionRequest(
    model_type="reid",
    inputs=[np.random.randn(3, 224, 224).astype(np.float32)]
)
# Output: 256-d embedding vector
```

### Temporal Analysis
```python
# Input: Time series (30×128) - 30 frames, 128 features each
request = BatchPredictionRequest(
    model_type="temporal",
    inputs=[np.random.randn(30, 128).astype(np.float32)]
)
# Output: 8 behavior classes
```

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Single prediction latency | <100ms |
| Batch size | Up to 1000 samples |
| Device support | CPU, CUDA (with fallback) |
| Concurrent requests | Fully async |

## Integration with FastAPI

```python
from fastapi import FastAPI
from app.services.prediction_service import PredictionService, BatchPredictionRequest

app = FastAPI()
service = PredictionService(...)  # Initialize as shown above

@app.post("/predict/batch")
async def batch_predict(request: BatchPredictionRequest):
    response = await service.batch_predict(request)
    return response.model_dump()

@app.get("/health")
async def health():
    return await service.health_check(run_inference=False)

@app.get("/models/info")
async def models_info():
    return service.get_all_models_info()

# Run: uvicorn app.main:app --reload
```

## Error Handling

```python
from app.services.prediction_service import BatchPredictionRequest

async def safe_predict():
    try:
        # Invalid model type
        request = BatchPredictionRequest(
            model_type="invalid",
            inputs=[np.random.randn(3, 240, 240)]
        )  # Raises ValueError during construction
    except ValueError as e:
        print(f"Validation error: {e}")
    
    try:
        # Empty inputs
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[]
        )  # Raises ValueError
    except ValueError as e:
        print(f"Validation error: {e}")
    
    try:
        # Inference error
        request = BatchPredictionRequest(
            model_type="behavior",
            inputs=[np.random.randn(3, 240, 240)]
        )
        response = await service.batch_predict(request)
    except RuntimeError as e:
        print(f"Inference error: {e}")
```

## Running Tests

```bash
# All tests
pytest tests/test_phase34_prediction_api.py -v

# Specific test class
pytest tests/test_phase34_prediction_api.py::TestPredictionServiceBatch -v

# Single test
pytest tests/test_phase34_prediction_api.py::TestPredictionServiceBatch::test_batch_predict_behavior -v

# With coverage
pytest tests/test_phase34_prediction_api.py --cov=app.services.prediction_service
```

## Async/Await Pattern

```python
import asyncio

async def main():
    # All PredictionService methods that do inference are async
    
    # Single batch
    response = await service.batch_predict(request)
    
    # Stream (AsyncGenerator)
    async for prediction in service.stream_predict(...):
        print(prediction)
    
    # Health check
    health = await service.health_check()

# Main entry point
if __name__ == "__main__":
    asyncio.run(main())
```

## Device Management

```python
# CPU (default)
service = PredictionService(..., device="cpu")

# CUDA (if available)
service = PredictionService(..., device="cuda")

# Auto-fallback: Will use CUDA if available, fall back to CPU
service = PredictionService(...)  # Checks torch.cuda.is_available()
```

## Batch Size Recommendations

```python
# Small batch (responsive): 1-8 samples
# Medium batch (efficient): 16-64 samples
# Large batch (throughput): 128-512 samples
# Max batch: 1000 samples (enforced limit)

# Streaming with automatic batching
async for pred in service.stream_predict(
    model_type="behavior",
    inputs=images,
    batch_size=32  # Automatically batch into groups of 32
):
    print(pred)
```

## Monitoring & Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("app.services.prediction_service")

# Health check includes timing information
health = await service.health_check(run_inference=True)
print(f"Service healthy: {health['status'] == 'healthy'}")
print(f"Inference time: {health['inference_time_ms']:.2f}ms")
print(f"Models available: {sum(health['models'].values())}/4")
```

## Next Steps

1. **Wrap with FastAPI**: Create REST endpoints for the service
2. **Model Optimization**: Export to ONNX, quantize, optimize with TensorRT
3. **Edge Deployment**: Package models for mobile/edge devices
4. **Monitoring**: Add Prometheus metrics and Grafana dashboards

## References

- Main implementation: `app/services/prediction_service.py`
- Data models: `app/services/prediction_service.py` (Dataclasses section)
- Tests: `tests/test_phase34_prediction_api.py`
- Pydantic docs: https://docs.pydantic.dev/
