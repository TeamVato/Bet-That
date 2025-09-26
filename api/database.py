"""Database connection and session management"""
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from .settings import settings, get_database_url, validate_database_path

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None
Base = declarative_base()

def init_database():
    global engine, SessionLocal
    
    if not validate_database_path():
        logger.warning(f"Database file not found at {settings.db_path}")
    
    database_url = get_database_url()
    logger.info(f"Connecting to database: {database_url}")
    
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False, "timeout": 30},
        echo=False
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")).scalar()
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_database_health() -> bool:
    try:
        with get_db_session() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
