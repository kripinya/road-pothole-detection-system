"""Backend API - FastAPI application entry point.

This is the central hub that:
- Registers all routers
- Configures CORS for frontend communication
- Sets up Prometheus monitoring
- Manages database lifecycle
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.config import settings
from src.database import engine, Base

# Import all routers
from src.routers import auth, detections, health

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("Starting backend service...")

    # Create all database tables if they don't exist
    # In production, use Alembic migrations instead
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created.")
    logger.info("Backend service ready.")
    yield
    logger.info("Shutting down backend service...")
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Road Pothole Detection System - Backend API",
    lifespan=lifespan,
)

# CORS -- allow frontend to make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js dev server
        "http://frontend:3000",    # Docker internal
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Register routers
app.include_router(auth.router)
app.include_router(detections.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint -- API info."""
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
    }
