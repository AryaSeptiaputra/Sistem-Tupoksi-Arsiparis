from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.core.config import settings

"""
Database configuration and session management.

This module initializes the SQLAlchemy engine and session factory used
for all database interactions within the application. It serves as the
central point for database connectivity.

OPTIMIZATION NOTES:
- pool_size: 20 (default 5) - jumlah connection yg di-maintain
- max_overflow: 10 - additional connections yg bisa dibuat jika diperlukan
- pool_pre_ping: True - test connection sebelum menggunakan
- pool_recycle: 3600 - recycle connection setiap 1 jam (MySQL default timeout)
- echo: False - set True hanya untuk debugging SQL
"""

# Determine pool configuration based on environment
DATABASE_URL = settings.DATABASE_URL
IS_SQLITE = 'sqlite' in DATABASE_URL

# Use NullPool untuk SQLite, QueuePool untuk MySQL
pool_class = NullPool if IS_SQLITE else QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=pool_class,
    pool_size=20,                    # Maintain 20 connections
    max_overflow=10,                 # Allow up to 10 additional connections
    pool_pre_ping=True,              # Check connection health before use
    pool_recycle=3600,               # Recycle connections after 1 hour
    echo=False,                      # Set to True for SQL logging in development
    connect_args={
        'charset': 'utf8mb4',        # For MySQL: support emoji dan special chars
        'connect_timeout': 10,       # Connection timeout 10 detik
        'read_timeout': 30,          # Query timeout 30 detik
    } if not IS_SQLITE else {}
)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=True  # Expired objects after commit untuk free memory
)

Base = declarative_base()