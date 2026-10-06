from dataclasses import dataclass

# Tabel yang wajib kosong sebelum seed (003a DS1)
SEED_EMPTY_TABLES = (
    "incoming_letter",
    "outgoing_letter",
    "diploma",
    "finance_archive",
    "employee_archive",
    "storage_location",
)

# Kategori master_reference yang wajib ada; teacher_rank opsional (rank NULL semua bila kosong)
REQUIRED_REFERENCE_CATEGORIES = (
    "school_major",
    "teacher_emp_status",
    "teacher_active_status",
    "finance_category",
    "emp_doc_type",
)
OPTIONAL_REFERENCE_CATEGORIES = ("teacher_rank",)


@dataclass(frozen=True)
class MarkerPattern:
    """Pola LIKE yang mengenali baris seed (003a DS7) atau baris anomali (DS6) di satu kolom."""

    table: str
    column: str
    pattern: str


# Pola penanda DS7 dan tag anomali DS6; dipakai penjaga "sudah ada baris berpenanda"
MARKER_PATTERNS = (
    MarkerPattern("classification", "code", "DMY-%"),
    MarkerPattern("storage_location", "name", "DUMMY %"),
    MarkerPattern("teacher", "full_name", "Pegawai Dummy %"),
    MarkerPattern("teacher", "identity_number", "9900%"),
    MarkerPattern("incoming_letter", "number", "DMY/IN/%"),
    MarkerPattern("incoming_letter", "subject", "DUMMY %"),
    MarkerPattern("outgoing_letter", "number", "DMY/OUT/%"),
    MarkerPattern("outgoing_letter", "subject", "DUMMY %"),
    MarkerPattern("diploma", "number", "DMY-IJZ-%"),
    MarkerPattern("diploma", "student_name", "Siswa Dummy %"),
    MarkerPattern("finance_archive", "title", "DUMMY %"),
    MarkerPattern("employee_archive", "document_name", "DUMMY %"),
    MarkerPattern("classification", "name", "%ANOMALI-%"),
    MarkerPattern("teacher", "full_name", "%ANOMALI-%"),
)
