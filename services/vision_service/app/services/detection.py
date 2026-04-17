import base64
import io
import time
from typing import List, Tuple, Optional
from datetime import datetime
import numpy as np
import cv2
from ultralytics import YOLO
from app.schemas import Detection, FrameDetectionResult, TroughStatus, DetectionType, BoundingBox


class YOLODetectionService:
    """Service for YOLO-based object detection"""
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize YOLO model
        
        Args:
            model_path: Path to YOLO model (default: YOLOv8 nano)
        """
        self.model = YOLO(model_path)
        self.model_version = "YOLOv8n"
        self.confidence_threshold = 0.5
        
        # Class mappings (from COCO dataset)
        self.class_names = {
            16: "dog",      # Might detect dogs/animals
            17: "cat",      # Might detect animals
            # Custom: we'll add animal detection
        }
        
        self.animal_classes = [16, 17, 19]  # Dog-like animals
        self.trough_keywords = ["bowl", "container", "cup", "sink"]

    def decode_frame(self, frame_data: str) -> Optional[np.ndarray]:
        """
        Decode base64 encoded image data
        
        Args:
            frame_data: Base64 encoded image
            
        Returns:
            Numpy array of image or None if decoding fails
        """
        try:
            image_data = base64.b64decode(frame_data)
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Image decode resulted in None")
            
            return frame
        except Exception as e:
            print(f"❌ Frame decoding failed: {e}")
            return None

    def encode_frame(self, frame: np.ndarray) -> str:
        """
        Encode frame to base64 string
        
        Args:
            frame: Numpy array of image
            
        Returns:
            Base64 encoded string
        """
        try:
            _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            image_data = base64.b64encode(buffer).decode()
            return image_data
        except Exception as e:
            print(f"❌ Frame encoding failed: {e}")
            return ""

    def detect_objects(self, frame: np.ndarray) -> Tuple[List[dict], int]:
        """
        Detect objects in frame using YOLO
        
        Args:
            frame: Numpy array of image
            
        Returns:
            Tuple of (detections list, animal count)
        """
        try:
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            
            detections = []
            animal_count = 0
            
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf)
                    cls_id = int(box.cls)
                    
                    # Normalize bounding box coordinates (0-1)
                    x_min = float(box.xyxy[0][0] / frame.shape[1])
                    y_min = float(box.xyxy[0][1] / frame.shape[0])
                    x_max = float(box.xyxy[0][2] / frame.shape[1])
                    y_max = float(box.xyxy[0][3] / frame.shape[0])
                    
                    detection = {
                        "class_id": cls_id,
                        "class_name": result.names.get(cls_id, "unknown"),
                        "confidence": conf,
                        "bbox": {
                            "x_min": max(0.0, min(1.0, x_min)),
                            "y_min": max(0.0, min(1.0, y_min)),
                            "x_max": max(0.0, min(1.0, x_max)),
                            "y_max": max(0.0, min(1.0, y_max)),
                        }
                    }
                    
                    detections.append(detection)
                    
                    # Count potential animals (dogs, cats, or other animal-like objects)
                    if cls_id in self.animal_classes or conf > 0.7:
                        animal_count += 1
            
            return detections, animal_count
        except Exception as e:
            print(f"❌ YOLO detection failed: {e}")
            return [], 0

    def classify_trough_status(self, frame: np.ndarray, detections: List[dict]) -> TroughStatus:
        """
        Classify trough (cocho) status based on detections and image analysis
        
        Args:
            frame: Numpy array of image
            detections: List of detected objects
            
        Returns:
            TroughStatus enum
        """
        try:
            # Analyze frame histogram to determine if it's likely filled with food
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            
            # If lower intensities (darker) dominate, likely empty/less full
            dark_pixels = np.sum(hist[:100])
            total_pixels = np.sum(hist)
            darkness_ratio = dark_pixels / total_pixels if total_pixels > 0 else 0
            
            # Simple heuristic
            if darkness_ratio > 0.7:
                return TroughStatus.EMPTY
            elif darkness_ratio > 0.5:
                return TroughStatus.PARTIALLY_FULL
            else:
                return TroughStatus.FULL
        except Exception as e:
            print(f"⚠️ Trough classification failed: {e}")
            return TroughStatus.UNKNOWN

    def process_frame(
        self,
        frame_data: str,
        camera_id: str,
        frame_id: str,
        timestamp: Optional[datetime] = None,
    ) -> Optional[FrameDetectionResult]:
        """
        Process a single frame and return detection results
        
        Args:
            frame_data: Base64 encoded image
            camera_id: Camera identifier
            frame_id: Unique frame identifier
            timestamp: Timestamp of frame (default: now)
            
        Returns:
            FrameDetectionResult or None if processing fails
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        start_time = time.time()
        
        # Decode frame
        frame = self.decode_frame(frame_data)
        if frame is None:
            return None
        
        # Detect objects
        detections_raw, animal_count = self.detect_objects(frame)
        
        # Convert to schema detections
        detections = []
        for det in detections_raw:
            bbox = det["bbox"]
            detection = Detection(
                detection_type=DetectionType.ANIMAL,
                confidence=det["confidence"],
                bounding_box=BoundingBox(**bbox),
                animal_color=None,
                animal_breed=None,
                metadata={"class_name": det["class_name"]},
            )
            detections.append(detection)
        
        # Classify trough status
        trough_status = self.classify_trough_status(frame, detections_raw)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Create result
        result = FrameDetectionResult(
            frame_id=frame_id,
            timestamp=timestamp,
            camera_id=camera_id,
            detections=detections,
            total_animals=animal_count,
            trough_status=trough_status,
            processing_time_ms=processing_time_ms,
            model_version=self.model_version,
        )
        
        return result
