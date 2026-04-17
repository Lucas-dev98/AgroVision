# ML Service - Deep Learning for Cattle Analysis

Advanced machine learning service for cattle behavior analysis, anomaly detection, and cross-camera re-identification using PyTorch and YOLO.

## Features

### 1. **Multi-Object Tracking (YOLO v8 + ByteTrack)**
- Real-time tracking of multiple cattle
- Position and velocity estimation
- Track persistence across frames
- Confidence-based detection filtering

### 2. **Behavior Classification**
- Grazing, resting, drinking, walking, running, standing, eating
- Temporal behavior analysis
- Dominant behavior identification
- Behavior sequence patterns

### 3. **Anomaly Detection**
- Lethargy detection (reduced activity)
- Lameness detection (abnormal gait)
- Stress detection (excessive movement)
- Health scoring system

### 4. **Cross-Camera Re-Identification (Re-ID)**
- Color descriptor extraction (HSV histograms)
- Pattern descriptor extraction (edge detection)
- Similarity scoring
- Multi-camera matching

## Architecture

```
ML Service (FastAPI)
├── Tracking Service (ByteTrack)
├── Behavior Analysis Service
├── Anomaly Detection Service
├── Re-Identification Service
├── Repositories (MongoDB)
└── Endpoints (/api/v1/ml/*)
```

## Dependencies

### Core ML
- **PyTorch 2.1.2** - Deep learning framework
- **PyTorch Lightning 2.1.0** - Training framework
- **TorchVision 0.16.2** - Computer vision models
- **Ultralytics YOLO 8.0.228** - Object detection

### Data Storage
- **Motor 3.3.2** - Async MongoDB driver
- **MongoDB 7** - Document database

### Image Processing
- **OpenCV 4.8.1.78** - Computer vision library
- **NumPy 1.24.3** - Numerical computing
- **Pillow 10.0.1** - Image manipulation

### API & Server
- **FastAPI 0.104.1** - Web framework
- **Uvicorn 0.24.0** - ASGI server

### ML Utilities
- **SciPy 1.11.4** - Scientific computing
- **scikit-learn 1.3.2** - Machine learning utils

## API Endpoints

### Tracking
```
POST /api/v1/ml/track
- Input: camera_id, frame_base64
- Output: TrackingFrameResult with tracks, behaviors, anomalies

GET /api/v1/ml/tracks/active
- Output: List of currently active tracks
```

### Behavior Analysis
```
POST /api/v1/ml/analyze-behavior
- Input: track_id, time_window
- Output: Behavior analysis statistics

GET /api/v1/ml/animals/{animal_id}/health
- Output: AnimalHealthReport (score, risk_level, recommendations)
```

### Anomaly Detection
```
POST /api/v1/ml/detect-anomalies
- Input: animal_id, behavior_analysis, position, track_id
- Output: List of AnomalyDetection

GET /api/v1/ml/animals/critical
- Output: List of animals with critical health status
```

### Re-Identification
```
POST /api/v1/ml/re-identify
- Input: animal_id, primary_camera, secondary_cameras, regions_base64
- Output: List of AnimalReIdentification results
```

### Health
```
GET /health
- Output: Service health status
```

## Data Schemas

### AnimalTrack
```python
{
    "track_id": int,
    "animal_id": str | null,
    "confidence": float (0-1),
    "current_position": {"x", "y", "w", "h"},
    "velocity": {"vx", "vy"},
    "frames_count": int,
    "first_seen": datetime,
    "last_seen": datetime
}
```

### BehaviorClassification
```python
{
    "behavior": "GRAZING" | "RESTING" | "DRINKING" | ... | "UNKNOWN",
    "confidence": float (0-1),
    "position": {"x", "y", "w", "h"}
}
```

### AnomalyDetection
```python
{
    "animal_id": str,
    "anomaly_type": "LAMENESS" | "LETHARGY" | "ABNORMAL_POSTURE" | ...,
    "severity": "low" | "medium" | "high" | "critical",
    "confidence": float (0-1),
    "description": str,
    "recommended_action": str,
    "timestamp": datetime
}
```

### AnimalHealthReport
```python
{
    "animal_id": str,
    "health_score": float (0-1),
    "risk_level": "low" | "medium" | "high" | "critical",
    "recommendations": [str],
    "last_updated": datetime
}
```

## MongoDB Collections

1. **tracking** - Frame-level tracking results
   - Indexes: frame_id (unique), camera_id, timestamp

2. **animal_reid** - Cross-camera re-identification results
   - Indexes: animal_id, (primary_camera, secondary_camera)

3. **animal_health** - Animal health tracking
   - Indexes: animal_id, timestamp, (animal_id, timestamp)

4. **behavior_patterns** - Aggregated behavior history
   - Indexes: animal_id, behavior_type

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v --cov=app

# Run service
python main.py
```

## Docker

```bash
# Build
docker build -f Dockerfile -t agrovision-ml-service .

# Run
docker run -p 8004:8004 \
  -e MONGODB_URL=mongodb://admin:admin@mongo:27017/agrovision_ml?authSource=admin \
  -e MONGODB_DB=agrovision_ml \
  agrovision-ml-service
```

## Environment Variables

```env
# MongoDB
MONGODB_URL=mongodb://admin:admin@mongo:27017/agrovision_ml?authSource=admin
MONGODB_DB=agrovision_ml

# Service
ML_SERVICE_PORT=8004
LOG_LEVEL=INFO
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ml_services.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run async tests
pytest tests/test_database.py -v
```

## Performance

- **Tracking**: ~25ms per frame (YOLO v8 nano)
- **Behavior Classification**: < 5ms per track
- **Anomaly Detection**: < 10ms per animal
- **Memory**: ~2GB (model + active tracks)

## Configuration

### Behavior Thresholds
- Standing: speed < 0.001
- Walking: speed 0.001 - 0.01
- Running: speed > 0.03

### Anomaly Thresholds
- Lethargy: activity < 50% baseline
- Stress: running > 3x baseline
- Lameness: unusual position patterns

## Future Enhancements

1. **FASE 2: Advanced Models**
   - CNN-based behavior classifier
   - Deep learning anomaly detector
   - Improved Re-ID with ResNet features

2. **FASE 3: Integration**
   - Real-time dashboard
   - Alert system
   - Historical analytics

3. **Optimization**
   - Model quantization
   - Edge deployment
   - Multi-GPU support

## Status

- ✅ FASE 1: Core services implemented (35% complete)
- ⏳ FASE 2: Advanced models (planned)
- ⏳ FASE 3: Integration (planned)

## Contributors

AgroVision Team

## License

Proprietary
