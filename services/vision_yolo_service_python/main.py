"""
Vision YOLO Service
Fast API + ultralytics/yolov8 for animal detection
"""
import os
import io
import json
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import numpy as np
from ultralytics import YOLO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Vision YOLO Service", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLO model
try:
    MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
    logger.info(f"Loading YOLO model from {MODEL_PATH}")
    model = YOLO(MODEL_PATH)
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    model = None


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "vision-yolo-service",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH
    }


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    """
    Detect animals in uploaded image using YOLO
    
    Args:
        file: Image file (jpg, png, etc)
    
    Returns:
        JSON with detections including class, confidence, and bounding box
    """
    if model is None:
        raise HTTPException(status_code=503, detail="YOLO model not loaded")
    
    try:
        # Read image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        logger.info(f"Processing image: {file.filename}, size: {image.size}")
        
        # Run YOLO inference
        results = model(image_array, conf=0.25, verbose=False)
        
        # Parse detections
        detections = []
        if results and len(results) > 0:
            result = results[0]
            
            # Get boxes data
            if result.boxes:
                for box in result.boxes:
                    # Extract coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Extract confidence and class
                    conf = float(box.conf[0].cpu().numpy())
                    cls = int(box.cls[0].cpu().numpy())
                    class_name = result.names[cls]
                    
                    # Check if it's an animal-related class
                    # COCO classes 15-24 are animals, add custom logic if needed
                    if "animal" in class_name.lower() or cls in [15, 16, 17, 18, 19, 20, 21, 22, 23, 24]:
                        detection = {
                            "class": class_name,
                            "confidence": round(conf, 3),
                            "bbox": [
                                round(float(x1), 2),
                                round(float(y1), 2),
                                round(float(x2), 2),
                                round(float(y2), 2)
                            ]
                        }
                        detections.append(detection)
        
        logger.info(f"Found {len(detections)} detections")
        
        return {
            "id": f"detect_{datetime.utcnow().timestamp()}",
            "image_url": f"image_{file.filename}",
            "detections": detections,
            "model_used": "yolov8n",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/models")
async def get_models():
    """Get available YOLO models"""
    return {
        "available_models": [
            {"name": "yolov8n", "size": "nano", "speed": "fast", "accuracy": "medium"},
            {"name": "yolov8s", "size": "small", "speed": "medium", "accuracy": "medium-high"},
            {"name": "yolov8m", "size": "medium", "speed": "medium", "accuracy": "high"},
            {"name": "yolov8l", "size": "large", "speed": "slow", "accuracy": "high"},
            {"name": "yolov8x", "size": "xlarge", "speed": "very_slow", "accuracy": "very_high"},
        ],
        "current_model": MODEL_PATH
    }


if __name__ == "__main__":
    port = int(os.getenv("VISION_YOLO_PORT", 8005))
    host = os.getenv("VISION_YOLO_HOST", "0.0.0.0")
    
    logger.info(f"Starting Vision YOLO Service on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
