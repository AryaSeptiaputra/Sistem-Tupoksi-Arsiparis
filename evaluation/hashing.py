import hashlib
import json
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import MetaData, Select, Table, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import NoSuchTableError, SQLAlchemyError

from evaluation.errors import DatabaseAccessError
from evaluation.logger import setup_logger

logger = setup_logger(__name__)


def to_hashable_value(value: object) -> object:
    """Mengubah satu nilai kolom menjadi bentuk JSON yang sama di setiap jalan.

    Args:
        value: Nilai dari database.

    Returns:
        Nilai yang bisa di-serialisasi JSON tanpa kehilangan pembeda: tanggal dan waktu
        sebagai ISO 8601, desimal sebagai teks, bool sebagai 0/1, bytes sebagai hex.
    """
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes(value).hex()
    return value


def _ordered_select(table: Table, id_limit: int | None) -> tuple[Select, list[str]]:
    columns = sorted(table.columns, key=lambda col: col.name)
    order = list(table.primary_key.columns) or columns
    statement = select(*columns).order_by(*order)
    if id_limit is not None:
        statement = statement.where(table.c.id <= id_limit)
    return statement, [col.name for col in columns]


def hash_table_rows(engine: Engine, tables: list[str], id_limits: dict[str, int] | None = None) -> dict[str, str]:
    """Menghitung hash SHA-256 berurutan atas semua baris setiap tabel.

    Baris diurutkan menurut primary key dan kolom diurutkan menurut nama, sehingga
    urutan insert dan urutan kolom fisik tidak memengaruhi hasil.

    Args:
        engine: Engine database yang dibaca.
        tables: Nama tabel yang di-hash.
        id_limits: Kalau diisi, hanya baris dengan `id` ≤ batas per tabel yang di-hash
            (baris yang sudah ada sebelum seed, SY8). Tabel tanpa batas di-hash seluruhnya.

    Returns:
        Hash hex per nama tabel.

    Raises:
        DatabaseAccessError: Kalau tabel tidak ada atau query gagal.
    """
    metadata = MetaData()
    hashes: dict[str, str] = {}
    try:
        with engine.connect() as conn:
            for name in tables:
                statement, column_names = _ordered_select(
                    Table(name, metadata, autoload_with=conn), (id_limits or {}).get(name))
                digest = hashlib.sha256(json.dumps(column_names).encode("utf-8"))
                for row in conn.execute(statement):
                    line = json.dumps([to_hashable_value(value) for value in row], ensure_ascii=False)
                    digest.update(b"\n" + line.encode("utf-8"))
                hashes[name] = digest.hexdigest()
    except NoSuchTableError as e:
        logger.error(f"Tabel untuk hash tidak ada: {e}", exc_info=True)
        raise DatabaseAccessError(f"Tabel tidak ada: {e}") from e
    except SQLAlchemyError as e:
        logger.error(f"Hash baris gagal: {type(e).__name__}", exc_info=True)
        raise DatabaseAccessError(f"Hash baris gagal: {type(e).__name__}") from e
    return hashes
