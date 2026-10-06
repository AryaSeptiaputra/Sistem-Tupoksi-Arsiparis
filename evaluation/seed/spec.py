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


# ---------------------------------------------------------------------
# DS2 · Parameter bawaan
# ---------------------------------------------------------------------
DEFAULT_SEED = 20261005
DEFAULT_REFERENCE_YEAR = 2026
# Rentang tahun dokumen isian: Y₀−10 … Y₀ (11 tahun)
YEAR_SPAN = 11


# ---------------------------------------------------------------------
# DS3 · Klasifikasi dummy, preset volume, sebaran
# ---------------------------------------------------------------------
@dataclass(frozen=True)
class DummyClassification:
    """Klasifikasi dummy DS3; bukan kode JRA dan tidak boleh dipakai sebagai acuan retensi nyata."""

    code: str
    active_years: int
    inactive_years: int
    final_action: str

    @property
    def name(self) -> str:
        """Nama berpenanda DUMMY, unik, maksimal 50 karakter."""
        return f"DUMMY {self.final_action} {self.active_years}+{self.inactive_years} ({self.code})"


DUMMY_CLASSIFICATIONS = (
    DummyClassification("DMY-D11", 1, 1, "destroy"),
    DummyClassification("DMY-D23", 2, 3, "destroy"),
    DummyClassification("DMY-D55", 5, 5, "destroy"),
    DummyClassification("DMY-D10", 1, 0, "destroy"),
    DummyClassification("DMY-DXX", 10, 10, "destroy"),
    DummyClassification("DMY-P55", 5, 5, "permanent"),
    DummyClassification("DMY-A25", 2, 5, "assess"),
)

# Jenis arsip lama yang memakai klasifikasi; ijazah lama tidak punya klasifikasi dan status
CLASSIFIED_TABLES = ("incoming_letter", "outgoing_letter", "finance_archive", "employee_archive")
ARCHIVE_TABLES = ("incoming_letter", "outgoing_letter", "diploma", "finance_archive", "employee_archive")
ARCHIVE_STATUSES = ("active", "inactive", "destroyed", "permanent")


@dataclass(frozen=True)
class Preset:
    """Volume isian per tahun (DS3); baris cakupan ditambahkan di atasnya."""

    incoming_per_year: int
    outgoing_per_year: int
    diplomas_per_cohort: int
    finance_per_year: int
    employees: int
    documents_per_employee: int


PRESETS = {
    "penuh": Preset(800, 500, 450, 150, 120, 10),
    "kecil": Preset(80, 50, 45, 15, 12, 10),
}

STATUS_WEIGHTS = (("active", 0.60), ("inactive", 0.25), ("destroyed", 0.10), ("permanent", 0.05))
REFERENCE_FORM_WEIGHTS = (("code", 0.70), ("name", 0.20), ("variant", 0.10))
GENDER_WEIGHTS = (("L", 0.40), ("P", 0.40), ("Laki-laki", 0.10), ("Perempuan", 0.10))
RANK_FILLED_SHARE = 0.70
PERIOD_MONTH_NULL_SHARE = 0.20
AMOUNT_NULL_SHARE = 0.10
AMOUNT_RANGE = (100_000, 500_000_000)
AMOUNT_STEP = 1_000
DOCUMENT_YEAR_NULL_SHARE = 0.05
DIPLOMA_COLLECTED_SHARE = 0.70
# collected_at: tahun lulus sampai tahun lulus + 3
DIPLOMA_COLLECT_MAX_DELAY = 3
OUTGOING_APPROVAL_STATUSES = ("draft", "pending", "approved", "rejected")
DECREE_SHARE = 0.10
LOCATION_COUNT = 20
INSTITUTION_COUNT = 30

# Panjang kolom referensi di skema lama (app/models); nilai lebih panjang memakai bentuk code
REFERENCE_COLUMN_LENGTHS = {
    "school_major": 100,
    "teacher_emp_status": 50,
    "teacher_rank": 100,
    "teacher_active_status": 50,
    "finance_category": 50,
    "emp_doc_type": 50,
}


# ---------------------------------------------------------------------
# DS5 · Lampiran
# ---------------------------------------------------------------------
ATTACHMENT_SHARE = 0.40
ATTACHMENT_MISSING_SHARE = 0.10
# Subfolder per route lama (app/routes/*: handle_file_upload)
ATTACHMENT_SUBFOLDERS = {
    "incoming_letter": "incoming_letters",
    "outgoing_letter": "outgoing_letters",
    "diploma": "diplomas",
    "finance_archive": "finance_archives",
    "employee_archive": "employee_archives",
}


# ---------------------------------------------------------------------
# DS7 · Penanda
# ---------------------------------------------------------------------
# Hash argon2 (atas prehash SHA-256, sama dengan app/utils/hash.py) dari sandi acak yang
# langsung dibuang; akun seed tidak bisa dipakai login. Bukan rahasia.
SEED_PASSWORD_HASH = "$argon2id$v=19$m=65536,t=3,p=4$4Nz7H4MQwlgLoZSyNkboHQ$A9dwovswQ9yaznlP2SrHW6kqY0EDNKxIsoUowKwAHGQ"
# Awalan nomor induk: 9900 = tahun 99 bulan 00, bukan NIP sah
IDENTITY_PREFIX = "9900"


def format_text(label: str) -> str:
    """Teks utama berpenanda, misalnya `DUMMY Surat masuk 2020-0001`."""
    return f"DUMMY {label}"


def format_letter_number(kind: str, year: int, number: int) -> str:
    """Nomor surat dummy, misalnya `DMY/IN/2020/0001` atau `DMY/OUT/2020/0001`."""
    return f"DMY/{kind}/{year}/{number:04d}"


def format_diploma_number(year: int, number: int) -> str:
    """Nomor ijazah dummy, misalnya `DMY-IJZ-2020-0001`."""
    return f"DMY-IJZ-{year}-{number:04d}"


def format_student_name(year: int, number: int) -> str:
    """Nama siswa dummy, misalnya `Siswa Dummy 2020-0001`."""
    return f"Siswa Dummy {year}-{number:04d}"


def format_employee_name(number: int) -> str:
    """Nama pegawai dummy, misalnya `Pegawai Dummy 001`."""
    return f"Pegawai Dummy {number:03d}"


def format_address(number: int) -> str:
    """Alamat dummy, misalnya `Alamat Dummy 001`."""
    return f"Alamat Dummy {number:03d}"


def format_identity_number(number: int) -> str:
    """Nomor induk 18 digit berawalan 9900, misalnya `990000000000000001`."""
    return f"{IDENTITY_PREFIX}{number:014d}"


def format_location_name(number: int) -> str:
    """Nama lokasi simpan dummy, misalnya `DUMMY Lemari 01`."""
    return f"DUMMY Lemari {number:02d}"
