import numpy as np
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from app.schemas import AnimalBehavior, BehaviorClassification


class BehaviorAnalysisService:
    """Service for animal behavior classification"""
    
    def __init__(self):
        """Initialize behavior analysis service"""
        self.behavior_history: Dict[int, List[BehaviorClassification]] = {}
    
    def classify_behavior(
        self,
        track_id: int,
        position: Dict[str, float],
        velocity: Optional[Dict[str, float]] = None,
        bbox_area: Optional[float] = None,
    ) -> BehaviorClassification:
        """
        Classify animal behavior based on motion and position
        
        Args:
            track_id: Track ID
            position: Current position (x, y, w, h)
            velocity: Velocity vector (vx, vy)
            bbox_area: Bounding box area (relative to frame)
            
        Returns:
            BehaviorClassification
        """
        if velocity is None:
            velocity = {"vx": 0, "vy": 0}
        
        if bbox_area is None:
            bbox_area = position.get("w", 0) * position.get("h", 0)
        
        # Calculate speed
        speed = np.sqrt(velocity.get("vx", 0)**2 + velocity.get("vy", 0)**2)
        
        # Classify behavior
        behavior, confidence = self._classify(speed, position, bbox_area)
        
        # Store in history
        classification = BehaviorClassification(
            behavior=behavior,
            confidence=confidence,
            position=position,
        )
        
        if track_id not in self.behavior_history:
            self.behavior_history[track_id] = []
        self.behavior_history[track_id].append(classification)
        
        # Keep last 100 classifications
        if len(self.behavior_history[track_id]) > 100:
            self.behavior_history[track_id] = self.behavior_history[track_id][-100:]
        
        return classification
    
    def _classify(
        self,
        speed: float,
        position: Dict[str, float],
        bbox_area: float,
    ) -> Tuple[AnimalBehavior, float]:
        """
        Classify behavior based on features
        
        Args:
            speed: Velocity magnitude
            position: Position
            bbox_area: Bounding box area
            
        Returns:
            Tuple of (behavior, confidence)
        """
        # Speed thresholds
        speed_thresh_walk = 0.01
        speed_thresh_run = 0.03
        
        if speed < 0.001:
            # Static behavior
            if bbox_area < 0.005:  # Small (standing)
                return AnimalBehavior.STANDING, 0.7
            else:  # Larger (resting/eating)
                # Check vertical position for grazing vs resting
                y_pos = position.get("y", 0.5)
                if y_pos > 0.6:  # Lower in frame (likely grazing)
                    return AnimalBehavior.GRAZING, 0.65
                else:  # Upper (likely resting)
                    return AnimalBehavior.RESTING, 0.65
        
        elif speed < speed_thresh_walk:
            return AnimalBehavior.STANDING, 0.6
        
        elif speed < speed_thresh_run:
            return AnimalBehavior.WALKING, 0.75
        
        else:
            return AnimalBehavior.RUNNING, 0.8
    
    def get_behavior_history(
        self,
        track_id: int,
        limit: int = 50,
    ) -> List[BehaviorClassification]:
        """Get behavior history for track"""
        history = self.behavior_history.get(track_id, [])
        return history[-limit:]
    
    def get_dominant_behavior(
        self,
        track_id: int,
        time_window: int = 30,
    ) -> Tuple[AnimalBehavior, int]:
        """
        Get dominant behavior in time window
        
        Args:
            track_id: Track ID
            time_window: Last N classifications to consider
            
        Returns:
            Tuple of (dominant behavior, count)
        """
        history = self.get_behavior_history(track_id, limit=time_window)
        
        if not history:
            return AnimalBehavior.UNKNOWN, 0
        
        # Count behaviors
        behavior_counts = {}
        for classification in history:
            behavior = classification.behavior
            behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
        
        # Find dominant
        dominant = max(behavior_counts.items(), key=lambda x: x[1])
        return dominant[0], dominant[1]
    
    def analyze_behavior_sequence(
        self,
        track_id: int,
    ) -> Dict[str, any]:
        """
        Analyze behavior sequence for track
        
        Args:
            track_id: Track ID
            
        Returns:
            Analysis dict with patterns
        """
        history = self.get_behavior_history(track_id)
        
        if not history:
            return {"status": "insufficient_data"}
        
        # Behavior counts
        behavior_counts = {}
        for classification in history:
            behavior = classification.behavior
            behavior_counts[behavior] = behavior_counts.get(behavior, 0) + 1
        
        total_frames = len(history)
        behavior_percentages = {
            str(b): (count / total_frames) * 100
            for b, count in behavior_counts.items()
        }
        
        # Get dominant
        dominant_behavior, dominant_count = self.get_dominant_behavior(track_id)
        
        return {
            "total_frames": total_frames,
            "behavior_percentages": behavior_percentages,
            "dominant_behavior": str(dominant_behavior),
            "dominant_count": dominant_count,
            "unique_behaviors": len(behavior_counts),
        }
