import numpy as np
from typing import List, Dict, Tuple
from scipy.spatial.distance import cosine
from app.schemas import AnimalReIdentification


class ReIdentificationService:
    """Service for cross-camera animal re-identification"""
    
    def __init__(self):
        """Initialize re-identification service"""
        self.animal_descriptors: Dict[str, Dict[str, np.ndarray]] = {}
    
    def extract_color_descriptor(self, bbox_region: np.ndarray) -> np.ndarray:
        """
        Extract color descriptor from bounding box region
        
        Args:
            bbox_region: Cropped image region
            
        Returns:
            Color histogram descriptor (normalized)
        """
        if bbox_region.size == 0:
            return np.zeros(9)
        
        # Convert to HSV for better color representation
        import cv2
        hsv = cv2.cvtColor(bbox_region, cv2.COLOR_BGR2HSV)
        
        # Calculate histograms for each channel
        hist_h = cv2.calcHist([hsv], [0], None, [3], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [3], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [3], [0, 256])
        
        # Normalize and concatenate
        desc = np.concatenate([
            cv2.normalize(hist_h, hist_h).flatten(),
            cv2.normalize(hist_s, hist_s).flatten(),
            cv2.normalize(hist_v, hist_v).flatten(),
        ])
        
        return desc / (np.linalg.norm(desc) + 1e-6)
    
    def extract_pattern_descriptor(self, bbox_region: np.ndarray) -> np.ndarray:
        """
        Extract pattern/texture descriptor from bounding box region
        
        Args:
            bbox_region: Cropped image region
            
        Returns:
            Pattern descriptor (edge/texture features)
        """
        if bbox_region.size == 0:
            return np.zeros(8)
        
        import cv2
        
        # Convert to grayscale
        gray = cv2.cvtColor(bbox_region, cv2.COLOR_BGR2GRAY)
        
        # Canny edges
        edges = cv2.Canny(gray, 50, 150)
        
        # Divide into grid and count edges in each cell
        h, w = edges.shape
        grid_h, grid_w = 2, 4  # 2x4 grid
        cell_h, cell_w = h // grid_h, w // grid_w
        
        desc = []
        for i in range(grid_h):
            for j in range(grid_w):
                cell = edges[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                edge_count = np.sum(cell > 0)
                desc.append(edge_count)
        
        desc = np.array(desc, dtype=np.float32)
        return desc / (np.linalg.norm(desc) + 1e-6)
    
    def register_animal(
        self,
        animal_id: str,
        camera_id: str,
        bbox_region: np.ndarray,
    ) -> bool:
        """
        Register animal with descriptors
        
        Args:
            animal_id: Animal RFID ID
            camera_id: Camera where seen
            bbox_region: Cropped bounding box region
            
        Returns:
            True if registration successful
        """
        try:
            color_desc = self.extract_color_descriptor(bbox_region)
            pattern_desc = self.extract_pattern_descriptor(bbox_region)
            
            if animal_id not in self.animal_descriptors:
                self.animal_descriptors[animal_id] = {}
            
            self.animal_descriptors[animal_id][camera_id] = {
                "color": color_desc,
                "pattern": pattern_desc,
            }
            
            return True
        except Exception as e:
            print(f"❌ Re-identification registration failed: {e}")
            return False
    
    def match_animal(
        self,
        animal_id: str,
        primary_camera: str,
        secondary_bbox_region: np.ndarray,
        similarity_threshold: float = 0.7,
    ) -> Tuple[float, bool]:
        """
        Match animal across cameras
        
        Args:
            animal_id: Animal to match
            primary_camera: Camera where registered
            secondary_bbox_region: Region from secondary camera
            similarity_threshold: Threshold for match
            
        Returns:
            Tuple of (similarity score, is_match)
        """
        if animal_id not in self.animal_descriptors:
            return 0.0, False
        
        if primary_camera not in self.animal_descriptors[animal_id]:
            return 0.0, False
        
        try:
            # Extract descriptors from secondary camera
            secondary_color = self.extract_color_descriptor(secondary_bbox_region)
            secondary_pattern = self.extract_pattern_descriptor(secondary_bbox_region)
            
            # Get primary descriptors
            primary_desc = self.animal_descriptors[animal_id][primary_camera]
            primary_color = primary_desc["color"]
            primary_pattern = primary_desc["pattern"]
            
            # Calculate similarities
            color_sim = 1.0 - cosine(primary_color, secondary_color)
            pattern_sim = 1.0 - cosine(primary_pattern, secondary_pattern)
            
            # Combined similarity (weighted average)
            similarity = 0.6 * color_sim + 0.4 * pattern_sim
            
            is_match = similarity >= similarity_threshold
            
            return float(similarity), is_match
            
        except Exception as e:
            print(f"❌ Re-identification matching failed: {e}")
            return 0.0, False
    
    def find_matches(
        self,
        animal_id: str,
        primary_camera: str,
        secondary_cameras: List[str],
        secondary_bbox_regions: Dict[str, np.ndarray],
        similarity_threshold: float = 0.7,
    ) -> List[AnimalReIdentification]:
        """
        Find matches across multiple secondary cameras
        
        Args:
            animal_id: Animal ID
            primary_camera: Primary camera
            secondary_cameras: List of secondary cameras
            secondary_bbox_regions: Dict of {camera_id: bbox_region}
            similarity_threshold: Match threshold
            
        Returns:
            List of re-identification results
        """
        results = []
        
        for secondary_camera in secondary_cameras:
            if secondary_camera not in secondary_bbox_regions:
                continue
            
            bbox_region = secondary_bbox_regions[secondary_camera]
            similarity, is_match = self.match_animal(
                animal_id,
                primary_camera,
                bbox_region,
                similarity_threshold,
            )
            
            result = AnimalReIdentification(
                animal_id=animal_id,
                primary_camera_id=primary_camera,
                secondary_camera_id=secondary_camera,
                similarity_score=similarity,
                confirmed=is_match,
                color_descriptor=self.extract_color_descriptor(bbox_region).tolist(),
                pattern_descriptor=self.extract_pattern_descriptor(bbox_region).tolist(),
            )
            
            results.append(result)
        
        return results
    
    def get_animal_descriptors(self, animal_id: str) -> Dict:
        """Get registered descriptors for animal"""
        return self.animal_descriptors.get(animal_id, {})
