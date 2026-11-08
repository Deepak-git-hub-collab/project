import time
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health & Diagnostics"])

START_TIME = time.time()

@router.get("")
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "engine": "ShieldPlus Sub-10ms Hybrid Ensemble",
        "version": "1.0.0"
    }
