# Vision YOLO Service (Python)

Real YOLO v8 animal detection service using FastAPI and ultralytics.

## 📋 Requisitos

- Python 3.11+
- FastAPI
- ultralytics (YOLOv8)
- Pillow
- numpy

## 🚀 Instalação Rápida

### Local Development

```bash
cd /home/lucasbastos/AgroVision/services/vision_yolo_service_python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env
cp .env.example .env

# Run (will download YOLOv8 model on first run)
python main.py
```

Service will be available at `http://localhost:8005`

### Docker

```bash
docker build -t agrovision/vision-yolo-service .
docker run -p 8005:8005 agrovision/vision-yolo-service
```

## 📡 API Endpoints

### POST /detect
Upload image for YOLO animal detection.

**Request:**
```bash
curl -X POST -F "file=@photo.jpg" http://localhost:8005/detect
```

**Response:**
```json
{
  "id": "detect_1715001000.123",
  "image_url": "image_photo.jpg",
  "detections": [
    {
      "class": "cow",
      "confidence": 0.95,
      "bbox": [100.5, 150.2, 300.8, 450.1]
    },
    {
      "class": "horse",
      "confidence": 0.87,
      "bbox": [320.1, 120.5, 500.3, 400.2]
    }
  ],
  "model_used": "yolov8n",
  "created_at": "2026-05-05T14:30:00.000Z"
}
```

### GET /models
List available YOLO models.

```bash
curl http://localhost:8005/models
```

**Response:**
```json
{
  "available_models": [
    {"name": "yolov8n", "size": "nano", "speed": "fast", "accuracy": "medium"},
    {"name": "yolov8s", "size": "small", "speed": "medium", "accuracy": "medium-high"},
    {"name": "yolov8m", "size": "medium", "speed": "medium", "accuracy": "high"},
    {"name": "yolov8l", "size": "large", "speed": "slow", "accuracy": "high"},
    {"name": "yolov8x", "size": "xlarge", "speed": "very_slow", "accuracy": "very_high"}
  ],
  "current_model": "yolov8n.pt"
}
```

### GET /health
Health check.

```bash
curl http://localhost:8005/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "vision-yolo-service",
  "model_loaded": true,
  "model_path": "yolov8n.pt"
}
```

## 🔧 Configuração

`.env`:
```
VISION_YOLO_PORT=8005
VISION_YOLO_HOST=0.0.0.0
YOLO_MODEL_PATH=yolov8n.pt
```

### YOLO Models Available

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| yolov8n | nano | Very Fast | Medium | Real-time, embedded |
| yolov8s | small | Fast | Medium-High | Real-time |
| yolov8m | medium | Medium | High | Balanced |
| yolov8l | large | Slow | High | Accuracy first |
| yolov8x | xlarge | Very Slow | Very High | Maximum accuracy |

## 📝 Notas

- First run downloads the YOLO model (~100MB)
- Dockerfile pre-downloads model for faster startup
- Detects all COCO classes, filters for animals
- GPU support available (add `device=0` to model call)
- Input images auto-converted to RGB

## 🔌 Integration with Vision Service (Go)

Vision Service Go calls this Python service via HTTP:

```go
// In Vision Service Go
resp, err := http.Post(
    "http://vision-yolo-service:8005/detect",
    "multipart/form-data",
    multipartBody,
)
```

## 🎓 YOLO Output Format

Each detection includes:
- **class**: Object class name (e.g., "cow", "horse", "dog")
- **confidence**: Detection confidence (0-1)
- **bbox**: Bounding box [x1, y1, x2, y2] in pixels

## 💡 Performance Tips

1. Use nano model (yolov8n) for real-time processing
2. Use larger models for higher accuracy
3. GPU recommended for video/batch processing
4. Reduce confidence threshold for more detections

## 🐛 Troubleshooting

### Model not downloading

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### GPU not detected

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Edit main.py to add device parameter
results = model(image_array, device=0)  # device=0 for GPU
```

### Port already in use

```bash
lsof -i :8005
kill -9 <PID>
```
