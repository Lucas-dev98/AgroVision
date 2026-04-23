import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import timezone, datetime, timedelta
from app.schemas import AnomalyType, AnomalyDetection, AnimalBehavior


class AnomalyDetectionService:
    """Service for detecting animal health anomalies"""
    
    def __init__(self):
        """Initialize anomaly detection service"""
        self.animal_baselines: Dict[str, Dict[str, any]] = {}
        self.anomaly_history: Dict[str, List[AnomalyDetection]] = {}
    
    def establish_baseline(
        self,
        animal_id: str,
        behavior_data: Dict[str, any],
        weight: Optional[float] = None,
    ) -> bool:
        """
        Establish behavioral baseline for animal
        
        Args:
            animal_id: Animal ID
            behavior_data: Behavior analysis data
            weight: Optional weight measurement
            
        Returns:
            True if successful
        """
        try:
            self.animal_baselines[animal_id] = {
                "behavior_data": behavior_data,
                "weight": weight,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            return True
        except Exception as e:
            print(f"❌ Baseline establishment failed: {e}")
            return False
    
    def detect_anomalies(
        self,
        animal_id: str,
        current_behavior: Dict[str, any],
        current_position: Dict[str, float],
        track_id: int,
    ) -> List[AnomalyDetection]:
        """
        Detect anomalies based on behavior deviation
        
        Args:
            animal_id: Animal ID
            current_behavior: Current behavior analysis
            current_position: Current position
            track_id: Track ID
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check if we have baseline
        if animal_id not in self.animal_baselines:
            # Try to establish from current data
            self.establish_baseline(animal_id, current_behavior)
            return anomalies
        
        baseline = self.animal_baselines[animal_id]
        current_time = datetime.now(timezone.utc)
        
        # Anomaly 1: Unusual behavior (lethargy)
        lethargy = self._check_lethargy(
            animal_id,
            current_behavior,
            baseline["behavior_data"],
        )
        if lethargy:
            anomalies.append(AnomalyDetection(
                animal_id=animal_id,
                anomaly_type=AnomalyType.LETHARGY,
                severity="medium",
                confidence=0.75,
                description="Animal showing reduced activity levels (lethargy detected)",
                recommended_action="Monitor closely for health changes",
                timestamp=current_time,
            ))
        
        # Anomaly 2: Abnormal posture/lameness
        lameness = self._check_lameness(current_position, track_id)
        if lameness:
            anomalies.append(AnomalyDetection(
                animal_id=animal_id,
                anomaly_type=AnomalyType.LAMENESS,
                severity="high",
                confidence=0.8,
                description="Detected abnormal gait pattern suggesting lameness",
                recommended_action="Schedule veterinary examination for leg/hoof issues",
                timestamp=current_time,
            ))
        
        # Anomaly 3: Excessive movement/stress
        stress = self._check_stress(
            animal_id,
            current_behavior,
            baseline["behavior_data"],
        )
        if stress:
            anomalies.append(AnomalyDetection(
                animal_id=animal_id,
                anomaly_type=AnomalyType.UNUSUAL_MOVEMENT,
                severity="medium",
                confidence=0.7,
                description="Excessive movement and running detected",
                recommended_action="Check for stressors (predators, heat, etc)",
                timestamp=current_time,
            ))
        
        # Store anomalies
        if animal_id not in self.anomaly_history:
            self.anomaly_history[animal_id] = []
        self.anomaly_history[animal_id].extend(anomalies)
        
        # Keep last 100 anomalies
        if len(self.anomaly_history[animal_id]) > 100:
            self.anomaly_history[animal_id] = self.anomaly_history[animal_id][-100:]
        
        return anomalies
    
    def _check_lethargy(
        self,
        animal_id: str,
        current_behavior: Dict[str, any],
        baseline_behavior: Dict[str, any],
    ) -> bool:
        """Check for lethargy (reduced activity)"""
        current_activity = current_behavior.get("unique_behaviors", 0)
        baseline_activity = baseline_behavior.get("unique_behaviors", 0)
        
        # If activity is <50% of baseline
        if baseline_activity > 0 and current_activity < baseline_activity * 0.5:
            return True
        
        # Check if mostly resting
        current_resting_pct = current_behavior.get("behavior_percentages", {}).get(
            str(AnimalBehavior.RESTING), 0
        )
        if current_resting_pct > 70:
            return True
        
        return False
    
    def _check_lameness(
        self,
        current_position: Dict[str, float],
        track_id: int,
    ) -> bool:
        """Check for lameness (abnormal gait)"""
        # Simplified check: if movement is jerky/inconsistent
        # This would need velocity history for proper analysis
        
        # Check if position is at odd locations (limping tendency)
        x_pos = current_position.get("x", 0.5)
        y_pos = current_position.get("y", 0.5)
        
        # Animals at extreme edges might indicate abnormal movement
        if (x_pos < 0.1 or x_pos > 0.9) and (y_pos < 0.1 or y_pos > 0.9):
            return True
        
        return False
    
    def _check_stress(
        self,
        animal_id: str,
        current_behavior: Dict[str, any],
        baseline_behavior: Dict[str, any],
    ) -> bool:
        """Check for stress (excessive movement)"""
        current_running_pct = current_behavior.get("behavior_percentages", {}).get(
            str(AnimalBehavior.RUNNING), 0
        )
        baseline_running_pct = baseline_behavior.get("behavior_percentages", {}).get(
            str(AnimalBehavior.RUNNING), 0
        )
        
        # If running >3x baseline
        if baseline_running_pct > 0:
            if current_running_pct > baseline_running_pct * 3:
                return True
        elif current_running_pct > 20:
            # If no baseline data, flag if excessive running
            return True
        
        return False
    
    def get_anomaly_history(
        self,
        animal_id: str,
        hours: int = 24,
    ) -> List[AnomalyDetection]:
        """Get anomaly history for animal"""
        if animal_id not in self.anomaly_history:
            return []
        
        history = self.anomaly_history[animal_id]
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return [a for a in history if a.timestamp >= cutoff_time]
    
    def calculate_health_score(
        self,
        animal_id: str,
        hours: int = 24,
    ) -> Tuple[float, str]:
        """
        Calculate health score for animal
        
        Args:
            animal_id: Animal ID
            hours: Time period to consider
            
        Returns:
            Tuple of (score 0-1, risk_level)
        """
        anomalies = self.get_anomaly_history(animal_id, hours=hours)
        
        if not anomalies:
            return 1.0, "low"
        
        # Calculate score based on anomalies
        total_confidence = sum(a.confidence for a in anomalies)
        score = max(0.0, 1.0 - (total_confidence / len(anomalies)) * 0.5)
        
        # Determine risk level
        if score >= 0.85:
            risk = "low"
        elif score >= 0.7:
            risk = "medium"
        elif score >= 0.5:
            risk = "high"
        else:
            risk = "critical"
        
        return score, risk
