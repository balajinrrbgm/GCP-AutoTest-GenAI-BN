"""
Database configuration and utilities for the Healthcare Test Case Generation System
"""

import logging
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator

from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Database engine
engine = None
SessionLocal = None
Base = declarative_base()


def get_database_url() -> str:
    """Get database URL from environment or config"""
    return os.getenv("DATABASE_URL", DATABASE_URL)


def create_database_engine():
    """Create database engine"""
    global engine, SessionLocal
    
    database_url = get_database_url()
    
    # Configure engine based on database type
    if database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info(f"Database engine created for: {database_url.split('@')[-1] if '@' in database_url else database_url}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    if SessionLocal is None:
        create_database_engine()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database and create tables"""
    try:
        if engine is None:
            create_database_engine()
        
        # Import all models to ensure they are registered
        from backend.models.requirements import (
            RequirementDocumentDB, RequirementDB, TestCaseDB
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


async def close_db():
    """Close database connections"""
    try:
        if engine:
            engine.dispose()
            logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {str(e)}")


def get_db_session() -> Session:
    """Get a database session (for use outside of FastAPI dependency injection)"""
    if SessionLocal is None:
        create_database_engine()
    return SessionLocal()


# Health check function
async def check_database_health() -> dict:
    """Check database health"""
    try:
        db = get_db_session()
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }


# Export main components
__all__ = [
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    'init_db',
    'close_db',
    'get_db_session',
    'check_database_health'
]