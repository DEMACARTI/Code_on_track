"""
Database configuration and session management.
"""
import os
import logging
from typing import Generator, Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session, Session, declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Engine configuration
engine_kwargs = {
    "pool_pre_ping": True,
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_size": 5,
    "max_overflow": 10,
    "echo": os.getenv("SQL_ECHO", "false").lower() == "true"
}

# SQLite specific configuration
if settings.DB_DRIVER == "sqlite":
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create engine
engine = create_engine(settings.DATABASE_URI, **engine_kwargs)

# Session factory
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False
    )
)

# Base class for models
Base = declarative_base()

# Enable WAL mode for SQLite for better concurrency
if settings.DB_DRIVER == "sqlite":
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Dependency for getting a database session with automatic cleanup."""
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()

def init_db() -> None:
    """Initialize the database by creating all tables."""
    try:
        import app.models  # Import models to ensure they are registered with SQLAlchemy
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_db_session() -> Session:
    """Get a database session for use outside of FastAPI dependency injection."""
    return SessionLocal()

def close_db() -> None:
    """Close the database connection."""
    SessionLocal.remove()
    engine.dispose()
