from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DisconnectionError, OperationalError
import logging
from app.core.config import settings

"""
Database configuration and session management with connection pooling.

This module initializes the SQLAlchemy engine with optimized settings for
production use, including connection pooling, automatic reconnection, and
performance monitoring.
"""

logger = logging.getLogger(__name__)

# Enhanced engine configuration for sustainability
engine = create_engine(
    settings.DATABASE_URL,
    # Connection pooling settings
    poolclass=QueuePool,
    pool_size=10,          # Maximum connections in pool
    max_overflow=20,       # Maximum overflow connections
    pool_timeout=30,       # Timeout for getting connection from pool
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_pre_ping=True,   # Test connections before use

    # Performance settings
    echo=False,           # Set to True for SQL query logging in development
    future=True,          # Use SQLAlchemy 2.0 style

    # Connection settings
    connect_args={
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
    }
)

# Session factory with better error handling
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent detached instance errors
)

# Thread-safe scoped session for web applications
ScopedSession = scoped_session(SessionLocal)

Base = declarative_base()

# Event listeners for connection management
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    """Log successful database connections"""
    logger.info("Database connection established")

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    """Handle connection checkout from pool"""
    logger.debug("Database connection checked out from pool")

@event.listens_for(engine, "checkin")
def checkin(dbapi_connection, connection_record):
    """Handle connection checkin to pool"""
    logger.debug("Database connection returned to pool")

@event.listens_for(engine, "close")
def close(dbapi_connection, connection_record):
    """Log connection closures"""
    logger.debug("Database connection closed")

def get_db():
    """
    Dependency injection untuk FastAPI-style database sessions.
    Mengembalikan database session yang akan otomatis ditutup.
    """
    db = ScopedSession()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables and indexes.
    Call this once during application startup.
    """
    try:
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def health_check():
    """
    Perform database health check
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False