"""Perception Agent - Analyzes raw detections to extract pothole characteristics."""

import logging
from typing import Any
from src.schemas import InferenceResponse

logger = logging.getLogger(__name__)

class PerceptionAgent:
    """Agent responsible for analyzing physical characteristics of detections."""
    
    def analyze(self, inference: InferenceResponse, image_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """Analyze detections to estimate size, depth, and context.
        
        Args:
            inference: The raw output from the YOLOv8 detector.
            image_metadata: Optional context like camera angle, GPS accuracy, etc.
            
        Returns:
            A dictionary containing the perception report.
        """
        logger.info(f"PerceptionAgent analyzing {len(inference.detections)} detections")
        
        if not inference.detections:
            return {
                "pothole_count": 0,
                "largest_pothole_area": 0,
                "overall_estimated_size": "none",
                "road_type_context": "unknown"
            }
            
        # Calculate bounding box areas relative to image size
        image_area = inference.image_width * inference.image_height
        areas = []
        
        for det in inference.detections:
            box_width = det.bbox.x_max - det.bbox.x_min
            box_height = det.bbox.y_max - det.bbox.y_min
            area_ratio = (box_width * box_height) / image_area
            areas.append(area_ratio)
            
        max_area = max(areas)
        
        # Simple heuristic for size classification based on screen real estate
        # In a production system with drones, you'd calculate actual physical size using altitude
        size_class = "small"
        if max_area > 0.15:
            size_class = "critical"
        elif max_area > 0.05:
            size_class = "large"
        elif max_area > 0.02:
            size_class = "medium"
            
        return {
            "pothole_count": len(inference.detections),
            "largest_pothole_area_ratio": max_area,
            "overall_estimated_size": size_class,
            "road_type_context": image_metadata.get("road_type", "urban") if image_metadata else "urban",
            "confidence_avg": sum(d.confidence for d in inference.detections) / len(inference.detections)
        }
