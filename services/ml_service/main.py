"""
ML Service - Deep Learning for Cattle Analysis
FastAPI endpoints for tracking, behavior analysis, anomaly detection
"""

import os
import json
import numpy as np
import base64
from datetime import datetime, timezone
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
import cv2

from app.services import (
    TrackingService,
    BehaviorAnalysisService,
    AnomalyDetectionService,
    ReIdentificationService,
)
from app.services.advanced import (
    AdvancedBehaviorService,
    AdvancedAnomalyService,
    AdvancedReIDService,
)
from app.repositories import TrackingRepository, ReIdRepository, HealthRepository
from app.schemas import (
    TrackingFrameResult,
    AnimalHealthReport,
    AnimalTrack,
    BehaviorClassification,
)
from app.core import MongoDBConnection, get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

# Initialize FastAPI app
app = FastAPI(
    title="ML Service",
    description="Deep Learning for Cattle Analysis - Tracking, Behavior, Anomaly Detection",
    version="1.0.0",
)

# Global services
tracking_service: Optional[TrackingService] = None
behavior_service: Optional[BehaviorAnalysisService] = None
anomaly_service: Optional[AnomalyDetectionService] = None
reid_service: Optional[ReIdentificationService] = None

# Advanced services
advanced_behavior_service: Optional[AdvancedBehaviorService] = None
advanced_anomaly_service: Optional[AdvancedAnomalyService] = None
advanced_reid_service: Optional[AdvancedReIDService] = None


@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    global tracking_service, behavior_service, anomaly_service, reid_service
    global advanced_behavior_service, advanced_anomaly_service, advanced_reid_service
    
    # Connect to MongoDB
    await MongoDBConnection.connect()
    
    # Initialize services
    tracking_service = TrackingService("yolov8n.pt")
    behavior_service = BehaviorAnalysisService()
    anomaly_service = AnomalyDetectionService()
    reid_service = ReIdentificationService()
    
    # Initialize advanced services (deep learning)
    advanced_behavior_service = AdvancedBehaviorService(device="cpu")
    advanced_anomaly_service = AdvancedAnomalyService(device="cpu")
    advanced_reid_service = AdvancedReIDService(device="cpu")
    
    print("✅ ML Service started (standard + advanced deep learning models)")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await MongoDBConnection.disconnect()
    print("✅ ML Service stopped")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ml_service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/ml/track")
async def track_animals(
    camera_id: str,
    frame_base64: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict:
    """
    Track animals in frame
    
    Args:
        camera_id: Camera identifier
        frame_base64: Base64 encoded frame
        
    Returns:
        Tracking result with tracks and behaviors
    """
    try:
        if not tracking_service:
            raise HTTPException(status_code=503, detail="Tracking service not ready")
        
        # Decode frame
        frame_data = base64.b64decode(frame_base64)
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid frame data")
        
        # Track animals
        tracks, tracking_time = tracking_service.track_frame(frame, camera_id)
        
        # Analyze behavior for each track
        behaviors = []
        for track in tracks:
            behavior = behavior_service.classify_behavior(
                track_id=track.track_id,
                position=track.current_position,
                velocity=track.velocity,
            )
            behaviors.append(behavior)
        
        # Detect anomalies
        anomalies = []
        for track in tracks:
            if track.animal_id:
                animal_behaviors = behavior_service.analyze_behavior_sequence(track.track_id)
                track_anomalies = anomaly_service.detect_anomalies(
                    animal_id=track.animal_id,
                    current_behavior=animal_behaviors,
                    current_position=track.current_position,
                    track_id=track.track_id,
                )
                anomalies.extend(track_anomalies)
        
        # Create result
        frame_id = f"{camera_id}-{datetime.now(timezone.utc).timestamp()}"
        result = TrackingFrameResult(
            frame_id=frame_id,
            camera_id=camera_id,
            timestamp=datetime.now(timezone.utc),
            tracks=tracks,
            behaviors=behaviors,
            anomalies=anomalies,
            processing_time_ms=tracking_time,
        )
        
        # Store in MongoDB
        repo = TrackingRepository(db)
        await repo.create(
            frame_id=frame_id,
            camera_id=camera_id,
            tracks=tracks,
            behaviors=behaviors,
            anomalies=anomalies,
        )
        
        return result.dict()
        
    except Exception as e:
        print(f"❌ Tracking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ml/analyze-behavior")
async def analyze_behavior(
    track_id: int,
    time_window: int = 30,
) -> Dict:
    """
    Analyze behavior sequence for track
    
    Args:
        track_id: Track ID
        time_window: Time window in frames
        
    Returns:
        Behavior analysis
    """
    try:
        if not behavior_service:
            raise HTTPException(status_code=503, detail="Behavior service not ready")
        
        analysis = behavior_service.analyze_behavior_sequence(track_id)
        
        return analysis
        
    except Exception as e:
        print(f"❌ Behavior analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ml/detect-anomalies")
async def detect_anomalies(
    animal_id: str,
    behavior_analysis: Dict,
    position: Dict,
    track_id: int,
) -> List[Dict]:
    """
    Detect health anomalies for animal
    
    Args:
        animal_id: Animal RFID ID
        behavior_analysis: Behavior analysis data
        position: Current position
        track_id: Track ID
        
    Returns:
        List of detected anomalies
    """
    try:
        if not anomaly_service:
            raise HTTPException(status_code=503, detail="Anomaly service not ready")
        
        anomalies = anomaly_service.detect_anomalies(
            animal_id=animal_id,
            current_behavior=behavior_analysis,
            current_position=position,
            track_id=track_id,
        )
        
        return [a.dict() for a in anomalies]
        
    except Exception as e:
        print(f"❌ Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ml/re-identify")
async def re_identify_animal(
    animal_id: str,
    primary_camera: str,
    secondary_cameras: List[str],
    secondary_regions_base64: Dict[str, str],
) -> List[Dict]:
    """
    Re-identify animal across cameras
    
    Args:
        animal_id: Animal ID
        primary_camera: Primary camera
        secondary_cameras: Secondary cameras
        secondary_regions_base64: Dict of {camera: base64_region}
        
    Returns:
        List of re-identification results
    """
    try:
        if not reid_service:
            raise HTTPException(status_code=503, detail="Re-ID service not ready")
        
        # Decode regions
        secondary_regions = {}
        for camera, region_b64 in secondary_regions_base64.items():
            data = base64.b64decode(region_b64)
            nparr = np.frombuffer(data, np.uint8)
            region = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if region is not None:
                secondary_regions[camera] = region
        
        # Find matches
        results = reid_service.find_matches(
            animal_id=animal_id,
            primary_camera=primary_camera,
            secondary_cameras=secondary_cameras,
            secondary_bbox_regions=secondary_regions,
        )
        
        return [r.dict() for r in results]
        
    except Exception as e:
        print(f"❌ Re-identification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ml/animals/{animal_id}/health")
async def get_animal_health(
    animal_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict:
    """
    Get health report for animal
    
    Args:
        animal_id: Animal ID
        
    Returns:
        Health report
    """
    try:
        if not anomaly_service:
            raise HTTPException(status_code=503, detail="Anomaly service not ready")
        
        # Get health score
        score, risk = anomaly_service.calculate_health_score(animal_id, hours=24)
        
        # Get latest health record from DB
        repo = HealthRepository(db)
        health_doc = await repo.get_latest(animal_id)
        
        if health_doc:
            recommendations = health_doc.get("recommendations", [])
        else:
            recommendations = ["Continue monitoring"]
        
        report = AnimalHealthReport(
            animal_id=animal_id,
            health_score=score,
            risk_level=risk,
            recommendations=recommendations,
        )
        
        return report.dict()
        
    except Exception as e:
        print(f"❌ Health report failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ml/animals/critical")
async def get_critical_animals(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> List[Dict]:
    """
    Get all animals with critical health status
    
    Returns:
        List of critical animals
    """
    try:
        repo = HealthRepository(db)
        critical = await repo.get_critical_animals()
        
        return critical
        
    except Exception as e:
        print(f"❌ Critical animals retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ml/tracks/active")
async def get_active_tracks() -> List[Dict]:
    """
    Get all active tracks
    
    Returns:
        List of active tracks
    """
    try:
        if not tracking_service:
            raise HTTPException(status_code=503, detail="Tracking service not ready")
        
        tracks = tracking_service.get_active_tracks()
        
        return [t.dict() for t in tracks]
        
    except Exception as e:
        print(f"❌ Active tracks retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADVANCED DEEP LEARNING ENDPOINTS ====================

@app.post("/api/v1/ml/classify-behavior-advanced")
async def classify_behavior_advanced(
    track_id: int,
    bbox_image_base64: str,
    position: Dict,
    use_temporal: bool = False,
) -> Dict:
    """
    Classify behavior using advanced CNN/LSTM model
    
    Args:
        track_id: Track ID
        bbox_image_base64: Base64 encoded bbox image
        position: Position dictionary
        use_temporal: Use LSTM for temporal analysis
        
    Returns:
        Behavior classification
    """
    try:
        if not advanced_behavior_service:
            raise HTTPException(status_code=503, detail="Advanced behavior service not ready")
        
        # Decode image
        img_data = base64.b64decode(bbox_image_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        bbox_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if bbox_image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Classify
        if use_temporal and track_id in advanced_behavior_service.sequences:
            classification = advanced_behavior_service.classify_temporal(track_id, position)
        else:
            classification = advanced_behavior_service.classify_from_bbox(
                bbox_image,
                track_id,
                position,
            )
        
        return classification.dict()
        
    except Exception as e:
        print(f"❌ Advanced behavior classification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ml/behavior-confidence/{track_id}")
async def get_behavior_confidence(track_id: int) -> Dict:
    """Get confidence scores for all behaviors"""
    try:
        if not advanced_behavior_service:
            raise HTTPException(status_code=503, detail="Advanced behavior service not ready")
        
        confidence = advanced_behavior_service.get_behavior_confidence(track_id)
        
        return {"track_id": track_id, "confidence_scores": confidence}
        
    except Exception as e:
        print(f"❌ Confidence retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ml/detect-anomaly-advanced")
async def detect_anomaly_advanced(
    animal_id: str,
    features_base64: str,
) -> Dict:
    """
    Detect anomaly using advanced autoencoder
    
    Args:
        animal_id: Animal ID
        features_base64: Base64 encoded feature vector
        
    Returns:
        Anomaly detection result
    """
    try:
        if not advanced_anomaly_service:
            raise HTTPException(status_code=503, detail="Advanced anomaly service not ready")
        
        # Decode features
        feat_data = base64.b64decode(features_base64)
        features = np.frombuffer(feat_data, dtype=np.float32)
        
        # Detect
        is_anomaly, anomaly_score = advanced_anomaly_service.detect_anomaly(
            animal_id,
            features,
        )
        
        return {
            "animal_id": animal_id,
            "is_anomaly": is_anomaly,
            "anomaly_score": float(anomaly_score),
        }
        
    except Exception as e:
        print(f"❌ Advanced anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ml/extract-reid-features")
async def extract_reid_features(
    bbox_image_base64: str,
) -> Dict:
    """
    Extract Re-ID features using advanced ResNet model
    
    Args:
        bbox_image_base64: Base64 encoded bbox image
        
    Returns:
        Feature vector
    """
    try:
        if not advanced_reid_service:
            raise HTTPException(status_code=503, detail="Advanced Re-ID service not ready")
        
        # Decode image
        img_data = base64.b64decode(bbox_image_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        bbox_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if bbox_image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Extract features
        features = advanced_reid_service.extract_features(bbox_image)
        
        return {
            "features": features.tolist(),
            "feature_dim": len(features),
        }
        
    except Exception as e:
        print(f"❌ Feature extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ml/match-reid-features")
async def match_reid_features(
    animal_id: str,
    primary_camera: str,
    secondary_features_base64: str,
) -> Dict:
    """
    Match Re-ID features across cameras
    
    Args:
        animal_id: Animal ID
        primary_camera: Primary camera
        secondary_features_base64: Base64 encoded secondary features
        
    Returns:
        Matching result
    """
    try:
        if not advanced_reid_service:
            raise HTTPException(status_code=503, detail="Advanced Re-ID service not ready")
        
        # Decode features
        feat_data = base64.b64decode(secondary_features_base64)
        secondary_features = np.frombuffer(feat_data, dtype=np.float32)
        
        # Match
        similarity, is_match = advanced_reid_service.match_features(
            animal_id,
            primary_camera,
            secondary_features,
        )
        
        return {
            "animal_id": animal_id,
            "similarity": float(similarity),
            "is_match": is_match,
        }
        
    except Exception as e:
        print(f"❌ Feature matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("ML_SERVICE_PORT", 8004))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
