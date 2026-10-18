"""Engine SQLAlchemy, pabrik session, dan `Base` model untuk seluruh aplikasi.

Aplikasi memakai SQLite agar ringan di device lama tanpa server database.
"""

from sqlite3 import Connection as SQLiteConnection

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import ConnectionPoolEntry, NullPool
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL.startswith('sqlite'):
    raise ValueError(
        f"DATABASE_URL harus SQLite, misalnya sqlite:///database/arsip.db; "
        f"didapat skema '{DATABASE_URL.split(':', 1)[0]}'. "
        f"Pindahkan data MySQL lama dengan scripts/migrate_mysql_to_sqlite.py."
    )

# NullPool membuka koneksi baru per session; murah untuk SQLite dan aman lintas thread waitress
engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)

# 5000 milidetik menunggu kunci tulis dilepas sebelum gagal "database is locked"
BUSY_TIMEOUT_MS = 5000


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection: SQLiteConnection, connection_record: ConnectionPoolEntry) -> None:
    # SQLite mengabaikan foreign key kecuali diaktifkan per koneksi.
    # WAL membuat pembacaan tidak terblokir saat ada penulisan dari thread lain.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
    cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=True
)

Base = declarative_base()
