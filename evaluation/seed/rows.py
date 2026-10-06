import random
from dataclasses import dataclass, field
from datetime import date, datetime, time

from evaluation.seed.spec import (
    AMOUNT_NULL_SHARE,
    AMOUNT_RANGE,
    AMOUNT_STEP,
    DECREE_SHARE,
    DIPLOMA_COLLECT_MAX_DELAY,
    DUMMY_CLASSIFICATIONS,
    GENDER_WEIGHTS,
    INSTITUTION_COUNT,
    LOCATION_COUNT,
    OUTGOING_APPROVAL_STATUSES,
    PERIOD_MONTH_NULL_SHARE,
    RANK_FILLED_SHARE,
    REFERENCE_COLUMN_LENGTHS,
    REFERENCE_FORM_WEIGHTS,
    SEED_PASSWORD_HASH,
    YEAR_SPAN,
    format_address,
    format_diploma_number,
    format_employee_name,
    format_identity_number,
    format_letter_number,
    format_location_name,
    format_student_name,
    format_text,
)

# Jam yang dipakai untuk semua created_at/updated_at seed (DS2: tanpa NOW())
SEED_CLOCK = time(8, 0)


@dataclass(frozen=True)
class Ref:
    """Rujukan simbolik ke baris seed lain; id-nya ditetapkan saat plan dirakit (langkah 3)."""

    table: str
    key: str | int


@dataclass
class SeedRow:
    """Satu baris yang akan ditambahkan ke tabel lama, beserta asal-usulnya di DS3/DS4/DS6."""

    table: str
    values: dict[str, object]
    tag: str
    key: str | int | None = None
    meta: dict[str, object] = field(default_factory=dict)


def choose_weighted(rng: random.Random, weights: tuple[tuple[str, float], ...]) -> str:
    """Memilih satu nilai sesuai bobot memakai `rng.random()` (stabil antar versi Python).

    Args:
        rng: Generator acak seed.
        weights: Pasangan (nilai, bobot); total bobot tidak harus 1.

    Returns:
        Nilai terpilih.
    """
    point = rng.random() * sum(weight for _, weight in weights)
    for value, weight in weights:
        point -= weight
        if point < 0:
            return value
    return weights[-1][0]


def to_datetime(day: date) -> datetime:
    """Mengubah tanggal menjadi jejak waktu seed pada jam tetap."""
    return datetime.combine(day, SEED_CLOCK)


class RowFactory:
    """Membentuk baris seed berpenanda DS7 dari satu generator acak (DS2)."""

    def __init__(self, rng: random.Random, references: dict[str, list[tuple[str, str]]], reference_year: int) -> None:
        self._rng = rng
        self._references = references
        self._y0 = reference_year
        self._counters: dict[tuple[str, int], int] = {}
        self._setup_time = to_datetime(date(reference_year - YEAR_SPAN + 1, 1, 2))

    @property
    def has_rank_references(self) -> bool:
        """Menjawab apakah D1 punya kategori `teacher_rank` (opsional, DS1)."""
        return bool(self._references.get("teacher_rank"))

    def _next_number(self, scope: str, year: int) -> int:
        number = self._counters.get((scope, year), 0) + 1
        self._counters[(scope, year)] = number
        return number

    def _to_variant(self, value: str, limit: int) -> str:
        transforms = (str.lower, str.upper, lambda text: f" {text}", lambda text: f"{text} ")
        start = self._rng.randrange(len(transforms))
        for offset in range(len(transforms)):
            candidate = transforms[(start + offset) % len(transforms)](value)
            if candidate != value and len(candidate) <= limit:
                return candidate
        return value

    def pick_reference(self, category: str, form: str | None = None) -> str:
        """Memilih nilai referensi dari master_reference D1 dalam bentuk code, name, atau varian.

        Varian hanya beda huruf besar/kecil atau spasi di tepi, jadi tetap cocok menurut aturan B4.
        Nilai yang lebih panjang dari kolom lama diganti bentuk code.

        Args:
            category: Kategori master_reference.
            form: `code`, `name`, atau `variant`; `None` berarti diundi sesuai DS3.

        Returns:
            Nilai string untuk kolom referensi lama.
        """
        code, name = self._rng.choice(self._references[category])
        chosen = form or choose_weighted(self._rng, REFERENCE_FORM_WEIGHTS)
        limit = REFERENCE_COLUMN_LENGTHS[category]
        if chosen == "name" and len(name) <= limit:
            return name
        if chosen == "variant":
            return self._to_variant(code, limit)
        return code

    def build_classification_rows(self) -> list[SeedRow]:
        """Membentuk tujuh klasifikasi dummy DS3."""
        return [
            SeedRow("classification", {
                "code": item.code, "name": item.name, "description": format_text("bukan kode JRA"),
                "retention_active_period": item.active_years, "retention_inactive_period": item.inactive_years,
                "final_action": item.final_action, "created_at": self._setup_time, "updated_at": self._setup_time,
            }, tag="DS3-klasifikasi", key=item.code)
            for item in DUMMY_CLASSIFICATIONS
        ]

    def build_location_rows(self) -> list[SeedRow]:
        """Membentuk lokasi simpan dummy."""
        return [
            SeedRow("storage_location", {
                "name": format_location_name(number), "description": format_text("lokasi simpan"),
                "created_at": self._setup_time, "updated_at": self._setup_time,
            }, tag="DS3-lokasi", key=number)
            for number in range(1, LOCATION_COUNT + 1)
        ]

    def build_employee_row(self, number: int, form: str | None = None) -> SeedRow:
        """Membentuk satu pegawai dummy; `form` memaksa bentuk referensi (cakupan C7)."""
        rank = None
        if self.has_rank_references and (form is not None or self._rng.random() < RANK_FILLED_SHARE):
            rank = self.pick_reference("teacher_rank", form)
        return SeedRow("teacher", {
            "identity_number": format_identity_number(number), "full_name": format_employee_name(number),
            "gender": choose_weighted(self._rng, GENDER_WEIGHTS),
            "employment_status": self.pick_reference("teacher_emp_status", form),
            "rank": rank, "status": self.pick_reference("teacher_active_status", form),
            "address": format_address(number), "created_at": self._setup_time, "updated_at": self._setup_time,
        }, tag="DS3-pegawai", key=number)

    def build_user_row(self, teacher_key: int, role: str, status: str) -> SeedRow:
        """Membentuk akun seed yang tidak bisa dipakai login (DS7)."""
        return SeedRow("user", {
            "teacher_id": Ref("teacher", teacher_key), "password": SEED_PASSWORD_HASH, "role": role,
            "status": status, "created_at": self._setup_time, "updated_at": self._setup_time,
        }, tag="C8", key=teacher_key)

    def _location(self) -> Ref:
        return Ref("storage_location", self._rng.randint(1, LOCATION_COUNT))

    def _institution(self) -> str:
        return format_text(f"Instansi {self._rng.randint(1, INSTITUTION_COUNT):02d}")

    def build_incoming_row(self, letter_date: date, received_date: date, classification: str, status: str,
                           tag: str) -> SeedRow:
        """Membentuk surat masuk; tahun dokumen = tahun `letter_date`."""
        number = self._next_number("incoming_letter", letter_date.year)
        stamp = to_datetime(received_date)
        return SeedRow("incoming_letter", {
            "number": format_letter_number("IN", letter_date.year, number),
            "letter_date": to_datetime(letter_date), "received_date": stamp, "sender": self._institution(),
            "subject": format_text(f"Surat masuk {letter_date.year}-{number:04d}"),
            "attachment_path": None, "classification_id": Ref("classification", classification),
            "storage_location_id": self._location(), "archive_status": status,
            "created_at": stamp, "updated_at": stamp,
        }, tag=tag)

    def build_outgoing_row(self, letter_date: date, sent_date: date, classification: str, status: str,
                           tag: str) -> SeedRow:
        """Membentuk surat keluar; nomor unik per tahun sehingga tidak ada pola B4-1."""
        number = self._next_number("outgoing_letter", letter_date.year)
        stamp = to_datetime(sent_date)
        return SeedRow("outgoing_letter", {
            "number": format_letter_number("OUT", letter_date.year, number),
            "letter_date": to_datetime(letter_date), "sent_date": stamp, "destination": self._institution(),
            "subject": format_text(f"Surat keluar {letter_date.year}-{number:04d}"),
            "is_decree": self._rng.random() < DECREE_SHARE, "attachment_path": None,
            "archive_status": status, "approval_status": self._rng.choice(OUTGOING_APPROVAL_STATUSES),
            "classification_id": Ref("classification", classification),
            "storage_location_id": self._location(), "created_at": stamp, "updated_at": stamp,
        }, tag=tag)

    def build_finance_row(self, fiscal_year: int, classification: str, status: str, tag: str,
                          category_form: str | None = None) -> SeedRow:
        """Membentuk arsip keuangan; tahun dokumen = `fiscal_year`."""
        number = self._next_number("finance_archive", fiscal_year)
        month = None if self._rng.random() < PERIOD_MONTH_NULL_SHARE else self._rng.randint(1, 12)
        amount = None
        if self._rng.random() >= AMOUNT_NULL_SHARE:
            amount = self._rng.randrange(AMOUNT_RANGE[0], AMOUNT_RANGE[1] + 1, AMOUNT_STEP)
        stamp = to_datetime(date(fiscal_year, month or 6, self._rng.randint(1, 28)))
        return SeedRow("finance_archive", {
            "title": format_text(f"Arsip keuangan {fiscal_year}-{number:04d}"), "fiscal_year": fiscal_year,
            "period_month": month, "category": self.pick_reference("finance_category", category_form),
            "amount": amount, "description": None, "attachment_path": None,
            "classification_id": Ref("classification", classification),
            "storage_location_id": self._location(), "archive_status": status,
            "created_at": stamp, "updated_at": stamp,
        }, tag=tag)

    def build_employee_document_row(self, owner: int, document_year: int | None, created_year: int,
                                    classification: str, status: str, tag: str,
                                    type_form: str | None = None) -> SeedRow:
        """Membentuk dokumen pegawai; `document_year` kosong memakai `created_at` sebagai tahun lama."""
        number = self._next_number("employee_archive", created_year)
        stamp = to_datetime(date(created_year, self._rng.randint(1, 12), self._rng.randint(1, 28)))
        return SeedRow("employee_archive", {
            "document_name": format_text(f"Dokumen pegawai {created_year}-{number:04d}"),
            "document_type": self.pick_reference("emp_doc_type", type_form), "archive_status": status,
            "document_year": document_year, "description": None, "attachment_path": None,
            "owner_id": Ref("teacher", owner), "classification_id": Ref("classification", classification),
            "storage_location_id": self._location(), "created_at": stamp, "updated_at": stamp,
        }, tag=tag)

    def build_diploma_row(self, graduation_year: int, collected: bool, tag: str,
                          major_form: str | None = None) -> SeedRow:
        """Membentuk ijazah angkatan lulus `graduation_year` (tahun ajaran `g−1/g`).

        `collected_at` jatuh di tahun lulus sampai +3 tahun, tidak melewati tahun acuan.
        """
        number = self._next_number("diploma", graduation_year)
        collected_at = None
        if collected:
            delay = self._rng.randint(0, min(DIPLOMA_COLLECT_MAX_DELAY, self._y0 - graduation_year))
            month = self._rng.randint(7, 12) if delay == 0 else self._rng.randint(1, 12)
            collected_at = to_datetime(date(graduation_year + delay, month, self._rng.randint(1, 28)))
        stamp = to_datetime(date(graduation_year, 6, 1))
        return SeedRow("diploma", {
            "number": format_diploma_number(graduation_year, number),
            "student_name": format_student_name(graduation_year, number),
            "major": self.pick_reference("school_major", major_form),
            "academic_year": f"{graduation_year - 1}/{graduation_year}", "is_collected": collected,
            "collected_at": collected_at, "attachment_path": None, "storage_location_id": self._location(),
            "created_at": stamp, "updated_at": collected_at or stamp,
        }, tag=tag)

