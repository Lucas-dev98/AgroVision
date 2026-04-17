import time
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from ultralytics import YOLO
from ultralytics.trackers.byte_tracker import BYTETracker
from app.schemas import AnimalTrack


class TrackingService:
    """Service for YOLO tracking with ByteTrack"""
    
    def __init__(self, model_path: str = "yolov8n.pt"):
        """
        Initialize YOLO + ByteTrack
        
        Args:
            model_path: Path to YOLO model
        """
        self.model = YOLO(model_path)
        self.tracker = BYTETracker(track_thresh=0.5, track_buffer=30, match_thresh=0.8)
        self.model_version = "YOLO v8 + ByteTrack"
        
        # Track store
        self.active_tracks: Dict[int, AnimalTrack] = {}
        self.frame_count = 0

    def track_frame(self, frame: np.ndarray, camera_id: str) -> Tuple[List[AnimalTrack], float]:
        """
        Track objects in frame using YOLO + ByteTrack
        
        Args:
            frame: Numpy array of image
            camera_id: Camera identifier
            
        Returns:
            Tuple of (list of tracks, processing time in ms)
        """
        start_time = time.time()
        self.frame_count += 1
        
        try:
            # YOLO detection
            results = self.model(frame, conf=0.5, verbose=False)
            
            # Extract detections
            detections = []
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf)
                    x1, y1, x2, y2 = box.xyxy[0]
                    
                    # Normalize
                    x1_norm = float(x1 / frame.shape[1])
                    y1_norm = float(y1 / frame.shape[0])
                    x2_norm = float(x2 / frame.shape[1])
                    y2_norm = float(y2 / frame.shape[0])
                    
                    # Create detection for ByteTrack
                    detections.append({
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "conf": conf,
                        "x_norm": x1_norm,
                        "y_norm": y1_norm,
                        "w_norm": x2_norm - x1_norm,
                        "h_norm": y2_norm - y1_norm,
                    })
            
            # ByteTrack
            dets = np.array([det["bbox"] + [det["conf"]] for det in detections], dtype=np.float32)
            tracks = self.tracker.update(dets, frame_id=self.frame_count, img_size=frame.shape[:2])
            
            # Convert to schema
            active_tracks = []
            current_time = datetime.utcnow()
            
            for track in tracks:
                track_id = int(track.track_id)
                x1, y1, x2, y2 = track.bbox
                
                # Normalize position
                x_center = ((x1 + x2) / 2.0) / frame.shape[1]
                y_center = ((y1 + y2) / 2.0) / frame.shape[0]
                width = (x2 - x1) / frame.shape[1]
                height = (y2 - y1) / frame.shape[0]
                
                # Get or create track
                if track_id in self.active_tracks:
                    prev_track = self.active_tracks[track_id]
                    
                    # Calculate velocity
                    prev_x = prev_track.current_position["x"]
                    prev_y = prev_track.current_position["y"]
                    dt = (current_time - prev_track.last_seen).total_seconds()
                    
                    if dt > 0:
                        vx = (x_center - prev_x) / dt if dt > 0 else 0
                        vy = (y_center - prev_y) / dt if dt > 0 else 0
                    else:
                        vx, vy = 0, 0
                    
                    track_obj = AnimalTrack(
                        track_id=track_id,
                        animal_id=prev_track.animal_id,
                        confidence=float(track.conf),
                        current_position={
                            "x": x_center,
                            "y": y_center,
                            "w": width,
                            "h": height,
                        },
                        velocity={"vx": vx, "vy": vy},
                        frames_count=prev_track.frames_count + 1,
                        last_seen=current_time,
                        first_seen=prev_track.first_seen,
                    )
                else:
                    track_obj = AnimalTrack(
                        track_id=track_id,
                        confidence=float(track.conf),
                        current_position={
                            "x": x_center,
                            "y": y_center,
                            "w": width,
                            "h": height,
                        },
                        velocity={"vx": 0, "vy": 0},
                        frames_count=1,
                        last_seen=current_time,
                        first_seen=current_time,
                    )
                
                self.active_tracks[track_id] = track_obj
                active_tracks.append(track_obj)
            
            # Clean old tracks (no seen in 30 frames)
            self.active_tracks = {
                tid: t for tid, t in self.active_tracks.items()
                if self.frame_count - 30 < self.frame_count
            }
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return active_tracks, processing_time_ms
            
        except Exception as e:
            print(f"❌ Tracking failed: {e}")
            processing_time_ms = (time.time() - start_time) * 1000
            return [], processing_time_ms

    def get_track(self, track_id: int) -> Optional[AnimalTrack]:
        """Get track by ID"""
        return self.active_tracks.get(track_id)

    def update_animal_id(self, track_id: int, animal_id: str) -> bool:
        """Update animal RFID ID for track"""
        if track_id in self.active_tracks:
            self.active_tracks[track_id].animal_id = animal_id
            return True
        return False

    def get_active_tracks(self) -> List[AnimalTrack]:
        """Get all active tracks"""
        return list(self.active_tracks.values())

    def get_track_count(self) -> int:
        """Get number of active tracks"""
        return len(self.active_tracks)
