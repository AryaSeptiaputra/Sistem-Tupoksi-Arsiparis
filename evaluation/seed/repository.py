from sqlalchemy import MetaData, Select, String, Table, false, func, or_, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import InvalidRequestError, SQLAlchemyError

from evaluation.baseline.old_repository import OLD_TABLES
from evaluation.errors import DatabaseAccessError
from evaluation.logger import setup_logger
from evaluation.report import Row
from evaluation.seed.plan import TABLE_ORDER, SeedPlan
from evaluation.seed.spec import MARKER_PATTERNS, SEED_EMPTY_TABLES, SEED_PASSWORD_HASH

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

    def count_rows(self) -> dict[str, int]:
        """Menghitung baris ke-12 tabel lama.

        Returns:
            Jumlah baris per nama tabel.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap atau query gagal.
        """
        return {
            name: int(self._fetch(select(func.count().label("jumlah")).select_from(self._table(name)))[0]["jumlah"])
            for name in OLD_TABLES
        }

    def fetch_max_ids(self) -> dict[str, int]:
        """Mengambil id terbesar setiap tabel lama (0 kalau kosong).

        Returns:
            id terbesar per nama tabel.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap atau query gagal.
        """
        max_ids: dict[str, int] = {}
        for name in OLD_TABLES:
            table = self._table(name)
            rows = self._fetch(select(func.max(table.c.id).label("maks")))
            max_ids[name] = int(rows[0]["maks"] or 0)
        return max_ids

    def fetch_column_lengths(self) -> dict[tuple[str, str], int]:
        """Mengambil panjang maksimal kolom teks di tabel yang ditulis seed.

        Returns:
            Panjang per (tabel, kolom) untuk kolom bertipe string berpanjang tetap.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap.
        """
        return {
            (name, column.name): int(column.type.length)
            for name in TABLE_ORDER
            for column in self._table(name).columns
            if isinstance(column.type, String) and column.type.length
        }

    def fetch_column_names(self) -> dict[str, set[str]]:
        """Mengambil nama kolom setiap tabel yang ditulis seed.

        Returns:
            Himpunan nama kolom per tabel.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap.
        """
        return {name: {column.name for column in self._table(name).columns} for name in TABLE_ORDER}

    def save_plan(self, plan: SeedPlan) -> dict[str, int]:
        """Menambahkan semua baris plan dalam satu transaksi (003a DS1).

        Kalau satu insert gagal, seluruh transaksi dibatalkan dan tidak ada baris yang tertinggal.

        Args:
            plan: Plan seed; id dan FK sudah berupa angka.

        Returns:
            Jumlah baris yang ditambahkan per tabel.

        Raises:
            DatabaseAccessError: Kalau insert gagal; transaksi sudah di-rollback.
        """
        inserted: dict[str, int] = {}
        tables = {name: self._table(name) for name in TABLE_ORDER}
        try:
            with self._engine.begin() as conn:
                for name in TABLE_ORDER:
                    rows = plan.rows_for(name)
                    if rows:
                        conn.execute(tables[name].insert(), rows)
                    inserted[name] = len(rows)
        except SQLAlchemyError as e:
            logger.error(f"Seed gagal dan di-rollback: {type(e).__name__}", exc_info=True)
            raise DatabaseAccessError(f"Seed gagal dan di-rollback: {type(e).__name__}") from e
        return inserted

    def count_marked_rows(self) -> dict[str, int]:
        """Menghitung baris berpenanda DUMMY/ANOMALI- per tabel (SY8).

        Akun seed dikenali dari hash sandi konstanta DS7, karena tabel `user` tidak punya kolom teks.

        Returns:
            Jumlah baris berpenanda untuk setiap tabel yang ditulis seed.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap atau query gagal.
        """
        counts: dict[str, int] = {}
        for name in TABLE_ORDER:
            table = self._table(name)
            conditions = [table.c[m.column].like(m.pattern) for m in MARKER_PATTERNS if m.table == name]
            if name == "user":
                conditions.append(table.c.password == SEED_PASSWORD_HASH)
            condition = or_(*conditions) if conditions else false()
            rows = self._fetch(select(func.count().label("jumlah")).select_from(table).where(condition))
            counts[name] = int(rows[0]["jumlah"])
        return counts

    def fetch_rows_after(self, name: str, columns: list[str], min_id: int) -> list[Row]:
        """Mengambil kolom tertentu dari baris dengan `id` > `min_id` (baris seed).

        Args:
            name: Nama tabel lama.
            columns: Kolom yang diambil; `id` selalu ikut.
            min_id: id terbesar sebelum seed.

        Returns:
            Baris urut per id.

        Raises:
            DatabaseAccessError: Kalau skema lama tidak lengkap atau query gagal.
        """
        table = self._table(name)
        selected = [table.c.id] + [table.c[column] for column in columns if column != "id"]
        return self._fetch(select(*selected).where(table.c.id > min_id).order_by(table.c.id))
