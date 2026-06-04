"""ML Service - FastAPI application entry point.

This service exposes endpoints for:
- Pothole detection using YOLOv8
- Agentic AI analysis pipeline
- Model info and health checks
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

from src.agents.orchestrator import AgentOrchestrator

from src.config import settings
from src.schemas import InferenceResponse
import src.detector as detector_module
orchestrator: AgentOrchestrator | None = None

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown.

    Startup: load the YOLO model into memory once.
    Shutdown: release resources.
    """
    logger.info("Starting ML service...")
    
    # Initialize the YOLO model singleton
    # This takes a few seconds, but it only happens once when the server boots!
    detector_module.detector = detector_module.PotholeDetector()
    # Initialize the Agentic AI orchestrator
    global orchestrator
    orchestrator = AgentOrchestrator()

    logger.info("ML service ready.")
    yield
    logger.info("Shutting down ML service...")
    detector_module.detector = None
    orchestrator = None

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Pothole detection and agentic AI analysis service",
    lifespan=lifespan,
)

# Prometheus metrics - exposes /metrics endpoint automatically
Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health_check():
    """Liveness probe for Docker and Kubernetes."""
    return {"status": "healthy", "service": settings.app_name}


@app.get("/model/info")
async def model_info():
    """Return metadata about the loaded model."""
    status = "loaded" if detector_module.detector and detector_module.detector.model else "not_loaded"
    return {
        "model_path": settings.model_path,
        "confidence_threshold": settings.confidence_threshold,
        "iou_threshold": settings.iou_threshold,
        "status": status,
    }


@app.post("/detect", response_model=InferenceResponse)
async def detect_potholes(file: UploadFile = File(...)):
    """Run YOLOv8 inference on an uploaded image file."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    try:
        # Read the raw image bytes directly from the HTTP request
        image_bytes = await file.read()
        
        # Ensure detector is loaded (defensive programming)
        if detector_module.detector is None:
            raise HTTPException(status_code=503, detail="Model is not loaded yet.")
            
        # Run inference using our singleton detector
        result = detector_module.detector.detect(image_bytes)
        return result
        
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@app.post("/analyze")
async def analyze_potholes(file: UploadFile = File(...)):
    """Run detection + full agentic AI analysis pipeline.

    This endpoint chains:
    1. YOLO detection (find potholes)
    2. Perception Agent (estimate size and characteristics)
    3. Severity Agent (score danger level)
    4. Prioritization Agent (recommend repair timeline and cost)
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        image_bytes = await file.read()

        if detector_module.detector is None:
            raise HTTPException(status_code=503, detail="Model is not loaded yet.")

        if orchestrator is None:
            raise HTTPException(status_code=503, detail="AI pipeline is not initialized.")

        # Step 1: Run YOLO detection
        inference_result = detector_module.detector.detect(image_bytes)

        # Step 2: Run the full agentic AI pipeline on the detection results
        analysis = orchestrator.run_pipeline(inference_result)

        return {
            "detection": inference_result.model_dump(),
            "analysis": analysis,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
