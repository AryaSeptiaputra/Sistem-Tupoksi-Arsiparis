from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.exc import ArgumentError
from sqlalchemy.pool import ConnectionPoolEntry, NullPool

from evaluation.errors import DatabaseAccessError

READ_ONLY_STATEMENTS = {
    "mysql": "SET SESSION TRANSACTION READ ONLY",
    "sqlite": "PRAGMA query_only = ON",
}


def to_read_only_statement(dialect_name: str) -> str:
    """Memilih perintah yang membuat satu koneksi hanya bisa membaca.

    Args:
        dialect_name: Nama dialek SQLAlchemy, misalnya `mysql` atau `sqlite`.

    Returns:
        Perintah SQL yang dijalankan setiap koneksi dibuka.

    Raises:
        DatabaseAccessError: Kalau dialeknya tidak didukung.
    """
    if dialect_name not in READ_ONLY_STATEMENTS:
        raise DatabaseAccessError(f"Mode hanya-baca belum didukung untuk dialek {dialect_name}")
    return READ_ONLY_STATEMENTS[dialect_name]


def to_safe_url(url: str) -> str:
    """Menampilkan URL database tanpa kata sandi.

    Args:
        url: URL SQLAlchemy.

    Returns:
        URL dengan kata sandi diganti `***`, atau `(tidak valid)` kalau tidak bisa dibaca.
    """
    try:
        return make_url(url).render_as_string(hide_password=True)
    except ArgumentError:
        return "(tidak valid)"


def build_engine(url: str, read_only: bool) -> Engine:
    """Membuat engine untuk database evaluasi.

    Args:
        url: URL SQLAlchemy database tujuan.
        read_only: Kalau `True`, setiap koneksi langsung dijadikan hanya-baca.

    Returns:
        Engine tanpa pool, supaya setiap koneksi baru melewati pengaturan hanya-baca.

    Raises:
        DatabaseAccessError: Kalau URL kosong, tidak valid, driver tidak ada,
            atau dialek tidak mendukung mode hanya-baca.
    """
    if not url:
        raise DatabaseAccessError("URL database kosong; isi setting EVAL_* yang sesuai di .env")
    try:
        engine = create_engine(url, poolclass=NullPool)
    except ArgumentError:
        # Pesan asli SQLAlchemy memuat URL lengkap beserta kata sandinya, jadi tidak dirantai.
        raise DatabaseAccessError(f"URL database tidak valid atau driver tidak ada: {to_safe_url(url)}") from None

    if read_only:
        statement = to_read_only_statement(engine.dialect.name)

        @event.listens_for(engine, "connect")
        def _set_read_only(dbapi_connection: DBAPIConnection, connection_record: ConnectionPoolEntry) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute(statement)
            cursor.close()

    return engine
