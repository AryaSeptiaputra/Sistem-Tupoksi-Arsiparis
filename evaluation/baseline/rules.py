import re
from dataclasses import dataclass

# Domain tetap dari 001a K3/K4 (CHECK di skema baru)
ARCHIVE_STATUS_DOMAIN = frozenset({"active", "inactive", "destroyed", "permanent"})
FINAL_ACTION_DOMAIN = frozenset({"destroy", "permanent", "assess"})
APPROVAL_STATUS_DOMAIN = frozenset({"draft", "pending", "approved", "rejected"})

# Tahun ajaran empat digit, garis miring, empat digit. Contoh sah: "2019/2020"
ACADEMIC_YEAR_PATTERN = re.compile(r"^\d{4}/\d{4}$")

# Nilai gender lama yang bisa dipetakan (001a K7 langkah 3), dibandingkan setelah trim dan huruf kecil
GENDER_MAP = {"l": "L", "laki-laki": "L", "p": "P", "perempuan": "P"}

STORAGE_PREFIX = "storage/"


@dataclass(frozen=True)
class StatusColumn:
    """Kolom status lama yang nilainya harus masuk domain tetap."""

    table: str
    column: str
    domain: frozenset[str]


@dataclass(frozen=True)
class ReferenceColumn:
    """Kolom string lama yang akan menjadi FK ke tabel lookup (001a K3)."""

    table: str
    column: str
    category: str
    nullable: bool


STATUS_COLUMNS = (
    StatusColumn("incoming_letter", "archive_status", ARCHIVE_STATUS_DOMAIN),
    StatusColumn("outgoing_letter", "archive_status", ARCHIVE_STATUS_DOMAIN),
    StatusColumn("finance_archive", "archive_status", ARCHIVE_STATUS_DOMAIN),
    StatusColumn("employee_archive", "archive_status", ARCHIVE_STATUS_DOMAIN),
    StatusColumn("classification", "final_action", FINAL_ACTION_DOMAIN),
    StatusColumn("outgoing_letter", "approval_status", APPROVAL_STATUS_DOMAIN),
)

REFERENCE_COLUMNS = (
    ReferenceColumn("diploma", "major", "school_major", nullable=False),
    ReferenceColumn("teacher", "employment_status", "teacher_emp_status", nullable=False),
    ReferenceColumn("teacher", "rank", "teacher_rank", nullable=True),
    ReferenceColumn("teacher", "status", "teacher_active_status", nullable=False),
    ReferenceColumn("finance_archive", "category", "finance_category", nullable=False),
    ReferenceColumn("employee_archive", "document_type", "emp_doc_type", nullable=False),
)


def is_in_domain(value: str | None, domain: frozenset[str]) -> bool:
    """Menjawab apakah nilai status persis sama dengan salah satu nilai domain.

    Args:
        value: Nilai di database lama.
        domain: Nilai yang sah.

    Returns:
        `True` kalau nilainya ada di domain, tanpa normalisasi huruf atau spasi.
    """
    return value in domain


def is_academic_year_valid(value: str | None) -> bool:
    """Menjawab apakah tahun ajaran berformat `YYYY/YYYY`.

    Args:
        value: Nilai `diploma.academic_year` lama.

    Returns:
        `True` kalau formatnya sah.
    """
    return value is not None and ACADEMIC_YEAR_PATTERN.match(value) is not None


def is_gender_mappable(value: str | None) -> bool:
    """Menjawab apakah nilai gender lama bisa dipetakan ke `L` atau `P`.

    Args:
        value: Nilai `teacher.gender` lama.

    Returns:
        `True` untuk L, Laki-laki, P, atau Perempuan (setelah trim, tanpa membedakan huruf besar).
    """
    return value is not None and value.strip().lower() in GENDER_MAP


def is_blank(value: str | None) -> bool:
    """Menjawab apakah nilai kosong atau hanya berisi spasi.

    Args:
        value: Nilai teks.

    Returns:
        `True` kalau `None` atau kosong setelah trim.
    """
    return value is None or not value.strip()


def is_reference_match(value: str, references: list[tuple[str, str]]) -> bool:
    """Menjawab apakah nilai cocok dengan `code` atau `name` salah satu referensi (001a K7 langkah 3).

    Args:
        value: Nilai string lama.
        references: Pasangan (code, name) dari `master_reference` satu kategori.

    Returns:
        `True` kalau cocok setelah trim, tanpa membedakan huruf besar.
    """
    target = value.strip().casefold()
    return any(target in (code.strip().casefold(), name.strip().casefold()) for code, name in references)


def strip_storage_prefix(path: str) -> str:
    """Mengubah path lampiran lama menjadi path relatif ke folder `storage/` (001a K6).

    Args:
        path: Path lama, misalnya `storage/documents/diplomas/a.pdf`.

    Returns:
        Path tanpa awalan, misalnya `documents/diplomas/a.pdf`.
    """
    normalized = path.strip().replace("\\", "/").lstrip("/")
    if normalized.startswith(STORAGE_PREFIX):
        return normalized[len(STORAGE_PREFIX):]
    return normalized
