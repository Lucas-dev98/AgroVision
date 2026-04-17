from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List
import logging
import uuid

from app.core import MongoDBConnection, get_db
from app.services import YOLODetectionService
from app.repositories import (
    DetectionRepository,
    AnimalLocationRepository,
    CameraCalibrationRepository,
)
from app.schemas import (
    ProcessFrameRequest,
    FrameDetectionResult,
    HealthCheckResponse,
    TroughStatus,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global YOLO service instance
yolo_service: Optional[YOLODetectionService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global yolo_service
    
    # Startup
    logger.info("🚀 Starting Vision Service...")
    
    try:
        # Connect to MongoDB
        await MongoDBConnection.connect(max_retries=5, retry_interval=2)
        logger.info("✅ MongoDB connected")
        
        # Initialize YOLO
        logger.info("📦 Loading YOLO model...")
        yolo_service = YOLODetectionService("yolov8n.pt")
        logger.info("✅ YOLO model loaded")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Vision Service...")
    await MongoDBConnection.disconnect()
    logger.info("✅ Vision Service stopped")


# Create FastAPI app
app = FastAPI(
    title="AgroVision Vision Service",
    description="Computer vision service for cattle detection, monitoring, and tracking",
    version="1.0.0",
    lifespan=lifespan,
)


# ==================== HEALTH CHECK ====================


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    db = get_db()
    
    models_loaded = yolo_service is not None
    mongodb_connected = db is not None
    
    status = "healthy" if (models_loaded and mongodb_connected) else "degraded"
    
    return HealthCheckResponse(
        status=status,
        version="1.0.0",
        models_loaded=models_loaded,
        mongodb_connected=mongodb_connected,
        timestamp=datetime.utcnow(),
    )


# ==================== DETECTION ENDPOINTS ====================


@app.post(
    "/api/v1/vision/detect",
    response_model=FrameDetectionResult,
    tags=["Detection"],
    summary="Process frame and detect objects",
    description="Process a camera frame (base64 encoded) and return detection results",
)
async def process_frame(request: ProcessFrameRequest, db=Depends(get_db)):
    """
    Process a frame and detect objects
    
    Args:
        request: ProcessFrameRequest with frame_data, camera_id, etc
        db: MongoDB database instance
    
    Returns:
        FrameDetectionResult with detections and analysis
    """
    if yolo_service is None:
        raise HTTPException(status_code=503, detail="YOLO model not loaded")
    
    try:
        # Generate frame ID
        frame_id = f"frame-{request.camera_id}-{datetime.utcnow().timestamp():.0f}"
        
        # Process frame
        result = yolo_service.process_frame(
            frame_data=request.frame_data,
            camera_id=request.camera_id,
            frame_id=frame_id,
            timestamp=request.timestamp,
        )
        
        if result is None:
            raise HTTPException(status_code=400, detail="Failed to process frame")
        
        # Store detection in MongoDB
        detection_repo = DetectionRepository(db)
        await detection_repo.create(result)
        
        # Store animal locations
        location_repo = AnimalLocationRepository(db)
        for detection in result.detections:
            if detection.animal_id:
                await location_repo.create_location(
                    animal_id=detection.animal_id,
                    timestamp=result.timestamp,
                    camera_id=result.camera_id,
                    location=detection.bounding_box.dict(),
                    confidence=detection.confidence,
                    frame_id=frame_id,
                )
        
        logger.info(f"✅ Processed frame {frame_id}: {result.total_animals} animals detected")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Frame processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/v1/vision/animals",
    tags=["Detection"],
    summary="Get detected animals",
    description="Get list of animals detected by camera in recent period",
)
async def get_animals_detected(
    camera_id: str,
    hours: int = 24,
    limit: int = 100,
    db=Depends(get_db),
):
    """
    Get recently detected animals
    
    Args:
        camera_id: Camera identifier
        hours: Look back hours (default: 24)
        limit: Maximum results (default: 100)
        db: MongoDB database instance
    
    Returns:
        List of recent detections
    """
    try:
        detection_repo = DetectionRepository(db)
        detections = await detection_repo.get_by_camera(camera_id, limit=limit)
        
        return {
            "camera_id": camera_id,
            "detections": detections,
            "count": len(detections),
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"❌ Failed to get animals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/v1/vision/troughs",
    tags=["Detection"],
    summary="Get trough status",
    description="Get current and historical trough (feeding area) status",
)
async def get_trough_status(camera_id: str, db=Depends(get_db)):
    """
    Get trough status for camera
    
    Args:
        camera_id: Camera identifier
        db: MongoDB database instance
    
    Returns:
        Current trough status and recent history
    """
    try:
        detection_repo = DetectionRepository(db)
        recent = await detection_repo.get_by_camera(camera_id, limit=10)
        
        if not recent:
            return {
                "camera_id": camera_id,
                "status": TroughStatus.UNKNOWN.value,
                "history": [],
                "timestamp": datetime.utcnow(),
            }
        
        # Get latest status
        latest = recent[0]
        
        return {
            "camera_id": camera_id,
            "status": latest.get("trough_status", TroughStatus.UNKNOWN.value),
            "history": [r.get("trough_status") for r in recent],
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"❌ Failed to get trough status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ANIMAL LOCATION ENDPOINTS ====================


@app.get(
    "/api/v1/vision/animals/{animal_id}/history",
    tags=["Animal Tracking"],
    summary="Get animal location history",
    description="Get location history for specific animal",
)
async def get_animal_history(
    animal_id: str,
    hours: int = 24,
    limit: int = 100,
    db=Depends(get_db),
):
    """
    Get animal location history
    
    Args:
        animal_id: Animal identifier (RFID)
        hours: Look back hours
        limit: Maximum results
        db: MongoDB database instance
    
    Returns:
        Location history with timestamps and cameras
    """
    try:
        location_repo = AnimalLocationRepository(db)
        history = await location_repo.get_animal_history(
            animal_id,
            limit=limit,
            hours=hours,
        )
        
        return {
            "animal_id": animal_id,
            "locations": history,
            "count": len(history),
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"❌ Failed to get animal history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/v1/vision/animals/latest",
    tags=["Animal Tracking"],
    summary="Get latest animal locations",
    description="Get latest detected location for all animals in camera view",
)
async def get_latest_locations(camera_id: str, db=Depends(get_db)):
    """
    Get latest locations of all animals
    
    Args:
        camera_id: Camera identifier
        db: MongoDB database instance
    
    Returns:
        Latest location for each animal
    """
    try:
        location_repo = AnimalLocationRepository(db)
        locations = await location_repo.get_latest_locations(camera_id)
        
        return {
            "camera_id": camera_id,
            "locations": locations,
            "count": len(locations),
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"❌ Failed to get latest locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CAMERA CALIBRATION ENDPOINTS ====================


@app.post(
    "/api/v1/vision/cameras/calibrate",
    tags=["Camera Management"],
    summary="Calibrate camera",
    description="Set or update camera calibration parameters",
)
async def calibrate_camera(
    camera_id: str,
    location: str,
    longitude: Optional[float] = None,
    latitude: Optional[float] = None,
    confidence_threshold: float = 0.5,
    db=Depends(get_db),
):
    """
    Calibrate camera
    
    Args:
        camera_id: Camera identifier
        location: Physical location name
        longitude: GPS longitude (optional)
        latitude: GPS latitude (optional)
        confidence_threshold: YOLO confidence threshold
        db: MongoDB database instance
    
    Returns:
        Calibration result
    """
    try:
        calib_repo = CameraCalibrationRepository(db)
        await calib_repo.create_or_update(
            camera_id=camera_id,
            location=location,
            longitude=longitude,
            latitude=latitude,
            confidence_threshold=confidence_threshold,
        )
        
        logger.info(f"✅ Camera {camera_id} calibrated at {location}")
        
        return {
            "camera_id": camera_id,
            "location": location,
            "confidence_threshold": confidence_threshold,
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"❌ Camera calibration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/v1/vision/cameras/{camera_id}",
    tags=["Camera Management"],
    summary="Get camera info",
    description="Get camera calibration and status information",
)
async def get_camera_info(camera_id: str, db=Depends(get_db)):
    """
    Get camera information
    
    Args:
        camera_id: Camera identifier
        db: MongoDB database instance
    
    Returns:
        Camera info and recent activity
    """
    try:
        calib_repo = CameraCalibrationRepository(db)
        location_repo = AnimalLocationRepository(db)
        
        calibration = await calib_repo.get_by_camera_id(camera_id)
        
        if calibration is None:
            raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")
        
        unique_animals = await location_repo.count_unique_animals(camera_id, hours=24)
        
        return {
            "camera_id": camera_id,
            "calibration": calibration,
            "unique_animals_24h": unique_animals,
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"❌ Failed to get camera info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/api/v1/vision/cameras",
    tags=["Camera Management"],
    summary="List all cameras",
    description="Get list of all configured cameras",
)
async def list_cameras(db=Depends(get_db)):
    """
    List all cameras
    
    Args:
        db: MongoDB database instance
    
    Returns:
        List of all camera calibrations
    """
    try:
        calib_repo = CameraCalibrationRepository(db)
        cameras = await calib_repo.get_all()
        
        return {
            "cameras": cameras,
            "count": len(cameras),
            "timestamp": datetime.utcnow(),
        }
    except Exception as e:
        logger.error(f"❌ Failed to list cameras: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=False,
    )
