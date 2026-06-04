"""Health check and readiness probe endpoints."""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/api/v1/health")
async def health_check():
    """Liveness probe -- is the service running?"""
    return {"status": "healthy", "service": "pothole-backend"}


@router.get("/api/v1/health/ready")
async def readiness_check():
    """Readiness probe -- can the service accept traffic?

    In production, this would check DB connectivity and Redis.
    For now, it returns healthy.
    """
    return {"status": "ready"}
