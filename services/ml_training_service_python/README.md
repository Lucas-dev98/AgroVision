# ML Training Service - TensorFlow

Real machine learning model training service using TensorFlow/Keras.

## Features

✨ **Real ML Models**
- Animal Detection (CNN with MobileNetV2)
- Behavior Classification (Dense NN)
- Weight Prediction (Regression)

🚀 **Asynchronous Training**
- Background training jobs
- Progress tracking (0-100%)
- Per-epoch metrics (loss, accuracy)

📊 **Training Management**
- Start training jobs with custom parameters
- Query training progress
- Get final metrics (accuracy, F1, precision, recall)
- List all trainings

🐳 **Docker Ready**
- FastAPI + Uvicorn
- TensorFlow 2.14
- Pre-built Dockerfile

## API Endpoints

### Health & Status

```
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "ml-training-service",
  "active_trainings": 2,
  "completed_trainings": 5
}
```

### Start Training

```
POST /train
```

Request:
```json
{
  "model_id": "model_v1",
  "model_type": "animal_detection",
  "epochs": 10,
  "batch_size": 32,
  "learning_rate": 0.001,
  "dataset_size": 100,
  "data_augmentation": true
}
```

Response:
```json
{
  "training_id": "uuid",
  "model_id": "model_v1",
  "status": "pending",
  "message": "Training job started"
}
```

### Get Training Progress

```
GET /training/{training_id}
```

Response:
```json
{
  "training_id": "uuid",
  "model_id": "model_v1",
  "status": "training",
  "progress": 45.0,
  "current_epoch": 4,
  "total_epochs": 10,
  "loss": 0.254,
  "accuracy": 0.89,
  "eta_seconds": 120
}
```

### Get Training Metrics

```
GET /training/{training_id}/metrics
```

Response (when completed):
```json
{
  "training_id": "uuid",
  "model_id": "model_v1",
  "accuracy": 0.9234,
  "loss": 0.0892,
  "val_accuracy": 0.9102,
  "val_loss": 0.1024,
  "precision": 0.9049,
  "recall": 0.8961,
  "f1_score": 0.9004,
  "training_time_seconds": 245.5,
  "epochs_completed": 10
}
```

### List Trainings

```
GET /trainings?status=completed
```

Response:
```json
{
  "total": 5,
  "trainings": [
    {
      "training_id": "uuid1",
      "model_id": "model_v1",
      "model_type": "animal_detection",
      "status": "completed",
      "progress": 100
    },
    ...
  ]
}
```

### List Available Models

```
GET /models
```

Response:
```json
{
  "models": [
    {
      "type": "animal_detection",
      "description": "Detect and classify animals in images",
      "input_shape": [224, 224, 3],
      "classes": 10
    },
    ...
  ]
}
```

## Local Development

### Prerequisites
- Python 3.11+
- TensorFlow 2.14
- 4GB RAM (8GB recommended for training)

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run service
python main.py
```

Service will be available at: `http://localhost:8106`

### Docker

```bash
# Build
docker build -t agrovision-ml-training .

# Run
docker run -p 8106:8106 \
  -e LOG_LEVEL=INFO \
  agrovision-ml-training
```

## Model Types

### 1. Animal Detection (CNN)
- **Input**: Images (224x224 RGB)
- **Output**: 10 animal classes
- **Architecture**: MobileNetV2 base + dense layers
- **Use Case**: Classify animals in farm images

### 2. Behavior Classification (Dense NN)
- **Input**: Sensor data (64 features)
- **Output**: 5 behavior classes (eating, drinking, resting, moving, playing)
- **Architecture**: 3-layer dense network
- **Use Case**: Classify animal behavior from sensors

### 3. Weight Prediction (Regression)
- **Input**: Sensor data (32 features)
- **Output**: Continuous weight (kg)
- **Architecture**: 3-layer dense network
- **Use Case**: Predict animal weight

## Example Workflow

```python
import requests

BASE_URL = "http://localhost:8106"

# 1. Start training
response = requests.post(f"{BASE_URL}/train", json={
    "model_id": "animal_detection_v1",
    "model_type": "animal_detection",
    "epochs": 20,
    "batch_size": 32,
    "learning_rate": 0.001,
    "dataset_size": 500
})
training_id = response.json()["training_id"]
print(f"Training started: {training_id}")

# 2. Poll progress
import time
while True:
    response = requests.get(f"{BASE_URL}/training/{training_id}")
    progress = response.json()
    print(f"Progress: {progress['progress']:.1f}% (Epoch {progress['current_epoch']}/{progress['total_epochs']})")
    
    if progress["status"] == "completed":
        break
    elif progress["status"] == "failed":
        print(f"Training failed: {progress.get('error')}")
        break
    
    time.sleep(5)

# 3. Get metrics
response = requests.get(f"{BASE_URL}/training/{training_id}/metrics")
metrics = response.json()
print(f"Accuracy: {metrics['accuracy']:.4f}")
print(f"F1 Score: {metrics['f1_score']:.4f}")
```

## Integration with ML Service Go

The ML Training Service runs as a background worker. The ML Service Go calls it when training is requested:

```
Frontend
  ↓
ML Service Go (8004)
  ├→ POST /train endpoint receives request
  └→ Calls ML Training Service (8106) to start background job
        ↓
      Returns training_id immediately
      ↓
      Background: TensorFlow trains model
      ↓
      Saves metrics to MongoDB
```

## Performance

| Model | Type | Epochs | Time | Accuracy |
|-------|------|--------|------|----------|
| Animal Detection | CNN | 10 | 2-3 min | ~92% |
| Behavior | Dense | 10 | 30-60s | ~88% |
| Weight Prediction | Regression | 10 | 20-40s | ~0.85 R² |

*Timings on CPU. GPU recommended for production.*

## Troubleshooting

### Out of Memory
- Reduce `batch_size` in training request
- Reduce `dataset_size`
- Use GPU: Set `TF_FORCE_GPU_ALLOW_GROWTH=true`

### Training Too Slow
- Check CPU usage: may need GPU
- Reduce model complexity for quick tests
- Use smaller `dataset_size` for prototyping

### Models Not Saving
- Ensure `/tmp/ml_models` is writable
- Check disk space
- Verify file permissions

## Next Steps

- [ ] GPU support (CUDA/cuDNN)
- [ ] Model versioning & rollback
- [ ] Distributed training (multi-GPU)
- [ ] Transfer learning from pre-trained models
- [ ] Data augmentation pipeline
- [ ] Model export to TensorFlow Lite / ONNX

## License

Part of AgroVision project
