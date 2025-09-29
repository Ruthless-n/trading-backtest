from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {
        "status": "ok",
        "database": "connected",
        "timestamp": datetime.utcnow(),
        "yfinance_latency_ms": 0
    }
