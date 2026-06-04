"""YOLOv8 Inference Engine for Pothole Detection."""

import io
import time
import logging
from PIL import Image
from ultralytics import YOLO

from src.config import settings
from src.schemas import InferenceResponse, DetectionResult, BoundingBox

logger = logging.getLogger(__name__)

class PotholeDetector:
    """Wrapper for the YOLOv8 object detection model."""
    
    def __init__(self):
        """Initialize and load the model."""
        self.model = None
        self._load_model()
        
    def _load_model(self):
        """Loads the YOLOv8 model weights."""
        logger.info(f"Loading YOLO model from {settings.model_path}")
        try:
            # In production, this loads your trained pothole weights (best.pt)
            self.model = YOLO(settings.model_path)
            logger.info("YOLO model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load custom model: {e}")
            logger.warning("Falling back to base yolov8n.pt for development testing.")
            # If your custom weights aren't trained yet, YOLO downloads the base model
            self.model = YOLO("yolov8n.pt")
            
    def detect(self, image_bytes: bytes) -> InferenceResponse:
        """Run inference on a single image.
        
        Args:
            image_bytes: Raw image file bytes.
            
        Returns:
            InferenceResponse containing bounding boxes and metadata.
        """
        start_time = time.time()
        
        # Convert raw bytes to a PIL Image (standard format for computer vision)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = image.size
        
        # Run YOLO inference
        results = self.model.predict(
            source=image, 
            conf=settings.confidence_threshold,
            iou=settings.iou_threshold,
            verbose=False
        )
        
        detections = []
        
        # We passed a single image, so we take the first result object
        result = results[0]
        
        if result.boxes:
            for box in result.boxes:
                # Extract coordinates (x_min, y_min, x_max, y_max)
                coords = box.xyxy[0].tolist()
                
                detections.append(
                    DetectionResult(
                        class_id=int(box.cls[0].item()),
                        class_name=result.names[int(box.cls[0].item())],
                        confidence=float(box.conf[0].item()),
                        bbox=BoundingBox(
                            x_min=coords[0],
                            y_min=coords[1],
                            x_max=coords[2],
                            y_max=coords[3]
                        )
                    )
                )
                
        inference_time_ms = (time.time() - start_time) * 1000
        
        return InferenceResponse(
            image_width=width,
            image_height=height,
            detections=detections,
            inference_time_ms=inference_time_ms
        )

# Global singleton instance (initialized during FastAPI startup)
detector = None
