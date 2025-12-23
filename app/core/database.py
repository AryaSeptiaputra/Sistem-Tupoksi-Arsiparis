from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

"""
Database configuration and session management.

This module initializes the SQLAlchemy engine and session factory used
for all database interactions within the application. It serves as the
central point for database connectivity.
"""

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Check connection health before use
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set to True for SQL logging in development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()