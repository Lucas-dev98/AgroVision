import pytest
import base64
import numpy as np
import cv2
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from app.services.detection import YOLODetectionService
from app.schemas import FrameDetectionResult, TroughStatus, DetectionType


@pytest.fixture
def detection_service():
    """Create detection service instance"""
    with patch("app.services.detection.YOLO"):
        service = YOLODetectionService("yolov8n.pt")
        service.model = Mock()
        return service


@pytest.fixture
def sample_frame():
    """Create a sample test frame (100x100 RGB image)"""
    frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    return frame


@pytest.fixture
def encoded_frame(sample_frame):
    """Create base64 encoded frame"""
    _, buffer = cv2.imencode(".jpg", sample_frame)
    return base64.b64encode(buffer).decode()


class TestYOLODetectionService:
    """Test YOLO detection service"""
    
    def test_decode_frame_valid(self, detection_service, encoded_frame):
        """Test frame decoding with valid base64"""
        frame = detection_service.decode_frame(encoded_frame)
        
        assert frame is not None
        assert isinstance(frame, np.ndarray)
        assert frame.shape[2] == 3  # RGB/BGR
    
    def test_decode_frame_invalid(self, detection_service):
        """Test frame decoding with invalid base64"""
        frame = detection_service.decode_frame("invalid_base64_data")
        
        assert frame is None
    
    def test_encode_frame(self, detection_service, sample_frame):
        """Test frame encoding to base64"""
        encoded = detection_service.encode_frame(sample_frame)
        
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        
        # Should be decodable
        decoded = detection_service.decode_frame(encoded)
        assert decoded is not None
    
    def test_classify_trough_status_empty(self, detection_service):
        """Test trough classification - empty"""
        # Very dark frame (empty trough)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        status = detection_service.classify_trough_status(frame, [])
        
        assert status == TroughStatus.EMPTY
    
    def test_classify_trough_status_full(self, detection_service):
        """Test trough classification - full"""
        # Very bright frame (full trough)
        frame = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        status = detection_service.classify_trough_status(frame, [])
        
        assert status == TroughStatus.FULL
    
    def test_detect_objects_empty_frame(self, detection_service, sample_frame):
        """Test object detection with empty results"""
        detection_service.model.return_value = [Mock(boxes=[], names={})]
        
        detections, animal_count = detection_service.detect_objects(sample_frame)
        
        assert detections == []
        assert animal_count == 0
    
    def test_detect_objects_with_detections(self, detection_service, sample_frame):
        """Test object detection with results"""
        # Mock YOLO result
        mock_box = Mock()
        mock_box.conf = 0.95
        mock_box.cls = 16
        mock_box.xyxy = [[10, 10, 50, 50]]
        
        mock_result = Mock()
        mock_result.boxes = [mock_box]
        mock_result.names = {16: "dog"}
        
        detection_service.model.return_value = [mock_result]
        
        detections, animal_count = detection_service.detect_objects(sample_frame)
        
        assert len(detections) == 1
        assert detections[0]["confidence"] == 0.95
        assert detections[0]["class_name"] == "dog"
        assert "bbox" in detections[0]
    
    def test_process_frame_success(self, detection_service, encoded_frame):
        """Test complete frame processing"""
        # Mock YOLO result
        mock_box = Mock()
        mock_box.conf = 0.85
        mock_box.cls = 16
        mock_box.xyxy = [[10, 10, 50, 50]]
        
        mock_result = Mock()
        mock_result.boxes = [mock_box]
        mock_result.names = {16: "dog"}
        
        detection_service.model.return_value = [mock_result]
        
        result = detection_service.process_frame(
            frame_data=encoded_frame,
            camera_id="camera-1",
            frame_id="frame-001",
        )
        
        assert result is not None
        assert isinstance(result, FrameDetectionResult)
        assert result.camera_id == "camera-1"
        assert result.frame_id == "frame-001"
        assert result.total_animals >= 0
        assert result.processing_time_ms > 0
        assert result.model_version == "YOLOv8n"
    
    def test_process_frame_invalid_data(self, detection_service):
        """Test frame processing with invalid data"""
        result = detection_service.process_frame(
            frame_data="invalid_data",
            camera_id="camera-1",
            frame_id="frame-001",
        )
        
        assert result is None
    
    def test_normalize_bbox_coordinates(self, detection_service, sample_frame):
        """Test bbox normalization to 0-1 range"""
        mock_box = Mock()
        mock_box.conf = 0.9
        mock_box.cls = 16
        # Absolute coordinates
        mock_box.xyxy = [[10, 20, 80, 90]]
        
        mock_result = Mock()
        mock_result.boxes = [mock_box]
        mock_result.names = {16: "dog"}
        
        detection_service.model.return_value = [mock_result]
        
        detections, _ = detection_service.detect_objects(sample_frame)
        
        assert len(detections) == 1
        bbox = detections[0]["bbox"]
        
        # All coordinates should be in 0-1 range
        assert 0.0 <= bbox["x_min"] <= 1.0
        assert 0.0 <= bbox["y_min"] <= 1.0
        assert 0.0 <= bbox["x_max"] <= 1.0
        assert 0.0 <= bbox["y_max"] <= 1.0
    
    def test_model_initialization(self, detection_service):
        """Test model initialization"""
        assert detection_service.model is not None
        assert detection_service.model_version == "YOLOv8n"
        assert detection_service.confidence_threshold == 0.5
    
    def test_animal_count_from_confidence(self, detection_service, sample_frame):
        """Test animal counting based on detection confidence"""
        mock_boxes = []
        for i in range(3):
            box = Mock()
            box.conf = 0.8 + (i * 0.05)  # 0.8, 0.85, 0.9
            box.cls = 16
            box.xyxy = [[10 * i, 10 * i, 50 + 10 * i, 50 + 10 * i]]
            mock_boxes.append(box)
        
        mock_result = Mock()
        mock_result.boxes = mock_boxes
        mock_result.names = {16: "dog"}
        
        detection_service.model.return_value = [mock_result]
        
        detections, animal_count = detection_service.detect_objects(sample_frame)
        
        assert len(detections) == 3
        assert animal_count == 3
