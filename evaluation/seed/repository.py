from sqlalchemy import MetaData, Select, Table, func, or_, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import InvalidRequestError, SQLAlchemyError

from evaluation.baseline.old_repository import OLD_TABLES
from evaluation.errors import DatabaseAccessError
from evaluation.logger import setup_logger
from evaluation.report import Row
from evaluation.seed.spec import MARKER_PATTERNS, SEED_EMPTY_TABLES

logger = setup_logger(__name__)


class SeedTargetRepository:
    """Akses ke D1 untuk seed: membaca keadaan sebelum seed (langkah 1) dan menulis (langkah 4)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._tables: dict[str, Table] = {}

    def _table(self, name: str) -> Table:
        if not self._tables:
            metadata = MetaData()
            try:
                metadata.reflect(bind=self._engine, only=list(OLD_TABLES))
            except InvalidRequestError as e:
                logger.error(f"Skema lama di D1 tidak lengkap: {e}", exc_info=True)
                raise DatabaseAccessError(f"Skema lama di D1 tidak lengkap: {e}") from e
            except SQLAlchemyError as e:
                logger.error(f"Membaca skema D1 gagal: {type(e).__name__}", exc_info=True)
                raise DatabaseAccessError(f"Membaca skema D1 gagal: {type(e).__name__}") from e
            self._tables = dict(metadata.tables)
        return self._tables[name]

    def _fetch(self, statement: Select) -> list[Row]:
        try:
            with self._engine.connect() as conn:
                return [dict(row) for row in conn.execute(statement).mappings()]
        except SQLAlchemyError as e:
            logger.error(f"Query ke D1 gagal: {type(e).__name__}", exc_info=True)
            raise DatabaseAccessError(f"Query ke D1 gagal: {type(e).__name__}") from e

    def count_archive_rows(self) -> dict[str, int]:
        """Menghitung baris lima tabel arsip dan `storage_location`.

        Returns:
            Jumlah baris per nama tabel.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap atau query gagal.
        """
        counts: dict[str, int] = {}
        for name in SEED_EMPTY_TABLES:
            rows = self._fetch(select(func.count().label("jumlah")).select_from(self._table(name)))
            counts[name] = int(rows[0]["jumlah"])
        return counts

    def has_marked_rows(self) -> bool:
        """Menjawab apakah sudah ada baris berpenanda seed (DS7) atau anomali (DS6).

        Returns:
            `True` kalau ada satu saja baris yang cocok dengan pola penanda.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap atau query gagal.
        """
        tables = sorted({marker.table for marker in MARKER_PATTERNS})
        for name in tables:
            table = self._table(name)
            conditions = [table.c[m.column].like(m.pattern) for m in MARKER_PATTERNS if m.table == name]
            rows = self._fetch(select(func.count().label("jumlah")).select_from(table).where(or_(*conditions)))
            if int(rows[0]["jumlah"]) > 0:
                return True
        return False

    def fetch_references(self) -> list[Row]:
        """Mengambil semua baris `master_reference`.

        Returns:
            Baris `{id, category, code, name}`, urut per id.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap atau query gagal.
        """
        table = self._table("master_reference")
        statement = select(table.c.id, table.c.category, table.c.code, table.c.name).order_by(table.c.id)
        return self._fetch(statement)
