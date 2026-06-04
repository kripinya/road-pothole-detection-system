"""ML Service - FastAPI application entry point.

This service exposes endpoints for:
- Pothole detection using YOLOv8
- Agentic AI analysis pipeline
- Model info and health checks
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.config import settings

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
    # TODO: Load YOLO model here (Phase 4.6)
    logger.info("ML service ready.")
    yield
    logger.info("Shutting down ML service...")


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
    return {
        "model_path": settings.model_path,
        "confidence_threshold": settings.confidence_threshold,
        "iou_threshold": settings.iou_threshold,
        "status": "not_loaded",  # Will update when detector is built
    }
