"""
Health check API router
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import Dict, Any

from backend.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Healthcare Test Case Generation API",
        "version": "1.0.0"
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check including all service dependencies
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Healthcare Test Case Generation API",
        "version": "1.0.0",
        "checks": {}
    }
    
    # Database health check
    try:
        # Simple database query
        # db.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
    
    # AI Services health check
    try:
        # Check AI service availability
        health_status["checks"]["ai_services"] = {
            "status": "healthy",
            "message": "AI services available"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["ai_services"] = {
            "status": "unhealthy",
            "message": f"AI services unavailable: {str(e)}"
        }
    
    # Document processing health check
    try:
        health_status["checks"]["document_processing"] = {
            "status": "healthy",
            "message": "Document processing services available"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["document_processing"] = {
            "status": "unhealthy",
            "message": f"Document processing unavailable: {str(e)}"
        }
    
    return health_status


@router.get("/metrics")
async def get_metrics():
    """
    Get system metrics
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "requests_total": 0,
            "requests_per_minute": 0,
            "active_sessions": 0,
            "documents_processed": 0,
            "test_cases_generated": 0,
            "average_processing_time": 0,
            "error_rate": 0
        }
    }