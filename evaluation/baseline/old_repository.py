from pathlib import Path

from sqlalchemy import Select, column, func, select, table
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from evaluation.baseline.rules import REFERENCE_COLUMNS, STATUS_COLUMNS, is_blank, is_in_domain, is_reference_match
from evaluation.errors import DatabaseAccessError
from evaluation.logger import setup_logger
from evaluation.report import Row

logger = setup_logger(__name__)

OLD_TABLES = (
    "user",
    "teacher",
    "log",
    "backup",
    "master_reference",
    "classification",
    "storage_location",
    "incoming_letter",
    "outgoing_letter",
    "diploma",
    "finance_archive",
    "employee_archive",
)
ARCHIVE_STATUS_TABLES = ("incoming_letter", "outgoing_letter", "finance_archive", "employee_archive")
ATTACHMENT_TABLES = ("incoming_letter", "outgoing_letter", "diploma", "finance_archive", "employee_archive")


def has_file(storage_root: Path, relative_path: str) -> bool:
    """Menjawab apakah berkas lampiran ada di dalam folder storage.

    Args:
        storage_root: Folder `storage/` lama.
        relative_path: Path relatif ke `storage_root` (awalan `storage/` sudah dibuang).

    Returns:
        `True` kalau berkas ada dan letaknya tidak keluar dari `storage_root`.
    """
    root = storage_root.resolve()
    target = (root / relative_path).resolve()
    return root in target.parents and target.is_file()


class OldDatabaseRepository:
    """Akses hanya-baca ke salinan database lama (D1)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def _fetch(self, statement: Select) -> list[Row]:
        try:
            with self._engine.connect() as conn:
                return [dict(row) for row in conn.execute(statement).mappings()]
        except SQLAlchemyError as e:
            logger.error(f"Query ke database lama gagal: {type(e).__name__}", exc_info=True)
            raise DatabaseAccessError(f"Query ke database lama gagal: {type(e).__name__}") from e

    def count_rows(self) -> list[Row]:
        """Menghitung baris setiap tabel lama (B1).

        Returns:
            Baris `{tabel, jumlah}` untuk 12 tabel lama.

        Raises:
            DatabaseAccessError: Kalau query gagal, misalnya tabel tidak ada.
        """
        rows: list[Row] = []
        for name in OLD_TABLES:
            result = self._fetch(select(func.count().label("jumlah")).select_from(table(name)))
            rows.append({"tabel": name, "jumlah": result[0]["jumlah"]})
        return rows

    def count_by_status(self) -> list[Row]:
        """Menghitung baris per `archive_status` di empat tabel arsip yang punya kolom itu (B1).

        Returns:
            Baris `{tabel, archive_status, jumlah}`, urut per status.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        rows: list[Row] = []
        for name in ARCHIVE_STATUS_TABLES:
            status = column("archive_status")
            statement = (
                select(status, func.count().label("jumlah"))
                .select_from(table(name, status))
                .group_by(status)
                .order_by(status)
            )
            rows.extend({"tabel": name, **row} for row in self._fetch(statement))
        return rows

    def fetch_duplicate_outgoing_numbers(self) -> list[Row]:
        """Mengambil surat keluar yang nomornya dipakai lebih dari satu baris (B4).

        Returns:
            Baris `{id, number}` untuk setiap surat yang nomornya ganda, urut per nomor lalu id.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        letters = table("outgoing_letter", column("id"), column("number"))
        duplicated = (
            select(letters.c.number).group_by(letters.c.number).having(func.count() > 1).scalar_subquery()
        )
        statement = (
            select(letters.c.id, letters.c.number)
            .where(letters.c.number.in_(duplicated))
            .order_by(letters.c.number, letters.c.id)
        )
        return self._fetch(statement)

    def fetch_out_of_domain_statuses(self) -> list[Row]:
        """Mengambil nilai status, final_action, dan approval_status di luar domain 001a (B4).

        Returns:
            Baris `{tabel, id, kolom, nilai}`; perbandingan persis, tanpa normalisasi.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        rows: list[Row] = []
        for spec in STATUS_COLUMNS:
            source = table(spec.table, column("id"), column(spec.column))
            statement = select(source.c.id, source.c[spec.column].label("nilai")).order_by(source.c.id)
            rows.extend(
                {"tabel": spec.table, "id": row["id"], "kolom": spec.column, "nilai": row["nilai"]}
                for row in self._fetch(statement)
                if not is_in_domain(row["nilai"], spec.domain)
            )
        return rows

    def fetch_academic_years(self) -> list[Row]:
        """Mengambil semua `diploma.academic_year` (B4).

        Returns:
            Baris `{id, academic_year}`, urut per id.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        diplomas = table("diploma", column("id"), column("academic_year"))
        return self._fetch(select(diplomas.c.id, diplomas.c.academic_year).order_by(diplomas.c.id))

    def fetch_gender_values(self) -> list[Row]:
        """Mengambil semua `teacher.gender` (B4).

        Returns:
            Baris `{id, gender}`, urut per id.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        teachers = table("teacher", column("id"), column("gender"))
        return self._fetch(select(teachers.c.id, teachers.c.gender).order_by(teachers.c.id))

    def _fetch_references(self, category: str) -> list[tuple[str, str]]:
        references = table("master_reference", column("category"), column("code"), column("name"))
        statement = select(references.c.code, references.c.name).where(references.c.category == category)
        return [(row["code"] or "", row["name"] or "") for row in self._fetch(statement)]

    def fetch_unmatched_references(self) -> list[Row]:
        """Mengambil nilai string referensi yang tidak cocok dengan `master_reference` (B4).

        Kolom yang boleh kosong (`teacher.rank`) dilewati kalau nilainya kosong.

        Returns:
            Baris `{tabel, id, kolom, kategori, nilai}`, urut per kolom lalu id.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        rows: list[Row] = []
        for spec in REFERENCE_COLUMNS:
            references = self._fetch_references(spec.category)
            source = table(spec.table, column("id"), column(spec.column))
            statement = select(source.c.id, source.c[spec.column].label("nilai")).order_by(source.c.id)
            for row in self._fetch(statement):
                value = row["nilai"]
                if spec.nullable and is_blank(value):
                    continue
                if value is None or not is_reference_match(value, references):
                    rows.append(
                        {"tabel": spec.table, "id": row["id"], "kolom": spec.column, "kategori": spec.category, "nilai": value}
                    )
        return rows

    def fetch_collected_without_date(self) -> list[Row]:
        """Mengambil ijazah yang tercatat sudah diambil tetapi tanpa tanggal (B4).

        Returns:
            Baris `{id}`, urut per id.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        diplomas = table("diploma", column("id"), column("is_collected"), column("collected_at"))
        statement = (
            select(diplomas.c.id)
            .where(diplomas.c.is_collected.is_(True), diplomas.c.collected_at.is_(None))
            .order_by(diplomas.c.id)
        )
        return self._fetch(statement)

    def fetch_employee_docs_without_classification(self) -> list[Row]:
        """Mengambil dokumen pegawai tanpa klasifikasi (B4).

        Returns:
            Baris `{id}`, urut per id.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        documents = table("employee_archive", column("id"), column("classification_id"))
        statement = select(documents.c.id).where(documents.c.classification_id.is_(None)).order_by(documents.c.id)
        return self._fetch(statement)

    def fetch_attachment_paths(self) -> list[Row]:
        """Mengambil path lampiran yang terisi di lima tabel arsip lama (B5).

        Returns:
            Baris `{tabel, id, path}`, urut per tabel lalu id.

        Raises:
            DatabaseAccessError: Kalau query gagal.
        """
        rows: list[Row] = []
        for name in ATTACHMENT_TABLES:
            source = table(name, column("id"), column("attachment_path"))
            statement = (
                select(source.c.id, source.c.attachment_path.label("path"))
                .where(source.c.attachment_path.is_not(None), source.c.attachment_path != "")
                .order_by(source.c.id)
            )
            rows.extend({"tabel": name, **row} for row in self._fetch(statement))
        return rows
