"""Engine SQLAlchemy, pabrik session, dan `Base` model untuk seluruh aplikasi."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
IS_SQLITE = 'sqlite' in DATABASE_URL

# SQLite (dipakai test) memakai NullPool, yang menolak argumen pool_size dan
# max_overflow; argumen pool hanya dikirim untuk MySQL.
if IS_SQLITE:
    engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)
else:
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=10,
        # Cek koneksi sebelum dipakai supaya koneksi yang diputus MySQL tidak dipakai ulang
        pool_pre_ping=True,
        # 3600 detik, di bawah wait_timeout default MySQL
        pool_recycle=3600,
        echo=False,
        connect_args={
            # utf8mb4 agar emoji dan karakter 4 byte tersimpan utuh
            'charset': 'utf8mb4',
            'connect_timeout': 10,
            'read_timeout': 30,
        }
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=True
)

Base = declarative_base()
