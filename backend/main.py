"""
Main FastAPI application for the AI-powered Healthcare Test Case Generation System
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import List, Optional
import os
from pathlib import Path

from config import (
    API_HOST, API_PORT, DEBUG, CORS_ORIGINS,
    LOGGING_CONFIG, API_VERSION
)

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Test Case Generation API",
    description="AI-powered system for automated healthcare test case generation",
    version="1.0.0",
    docs_url=f"/api/{API_VERSION}/docs",
    redoc_url=f"/api/{API_VERSION}/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Import routers
from backend.api.requirements import router as requirements_router
from backend.api.test_cases import router as test_cases_router
from backend.api.health import router as health_router
from backend.api.auth import router as auth_router
from backend.api.compliance import router as compliance_router
from backend.api.alm_integration import router as alm_router

# Include routers
app.include_router(auth_router, prefix=f"/api/{API_VERSION}/auth", tags=["authentication"])
app.include_router(requirements_router, prefix=f"/api/{API_VERSION}/requirements", tags=["requirements"])
app.include_router(test_cases_router, prefix=f"/api/{API_VERSION}/test-cases", tags=["test-cases"])
app.include_router(compliance_router, prefix=f"/api/{API_VERSION}/compliance", tags=["compliance"])
app.include_router(alm_router, prefix=f"/api/{API_VERSION}/alm", tags=["alm-integration"])
app.include_router(health_router, prefix=f"/api/{API_VERSION}/health", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "AI-powered Healthcare Test Case Generation System",
        "version": "1.0.0",
        "docs": f"/api/{API_VERSION}/docs",
        "health": f"/api/{API_VERSION}/health"
    }


@app.get("/api/{API_VERSION}")
async def api_info():
    """API version information"""
    return {
        "api_version": API_VERSION,
        "title": "Healthcare Test Case Generation API",
        "description": "AI-powered system for automated healthcare test case generation",
        "features": [
            "Multi-format requirement parsing (PDF, Word, XML, Markdown)",
            "AI-powered test case generation using Google Gemini",
            "Healthcare compliance validation (FDA, IEC 62304, ISO standards)",
            "ALM integration (Jira, Polarion, Azure DevOps)",
            "Full requirement-to-test traceability",
            "GDPR-compliant data processing"
        ],
        "supported_standards": [
            "FDA 21 CFR Part 820",
            "IEC 62304",
            "ISO 9001",
            "ISO 13485",
            "ISO 27001",
            "GDPR"
        ]
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Healthcare Test Case Generation API")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"API version: {API_VERSION}")
    
    # Initialize services
    try:
        # Initialize database connections
        from backend.database import init_db
        await init_db()
        logger.info("Database initialized successfully")
        
        logger.info("System ready for service")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Healthcare Test Case Generation API")
    
    # Cleanup resources
    try:
        # Close database connections
        from backend.database import close_db
        await close_db()
        logger.info("Database connections closed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="debug" if DEBUG else "info"
    )