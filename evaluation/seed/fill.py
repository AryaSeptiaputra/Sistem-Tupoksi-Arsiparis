import random
from datetime import date, timedelta

from evaluation.seed.coverage import build_archive_row
from evaluation.seed.rows import RowFactory, SeedRow, choose_weighted
from evaluation.seed.spec import (
    ARCHIVE_TABLES,
    ATTACHMENT_MISSING_SHARE,
    ATTACHMENT_SHARE,
    ATTACHMENT_SUBFOLDERS,
    DIPLOMA_COLLECTED_SHARE,
    DOCUMENT_YEAR_NULL_SHARE,
    DUMMY_CLASSIFICATIONS,
    STATUS_WEIGHTS,
    YEAR_SPAN,
    DummyClassification,
    Preset,
)

# Selisih maksimal tanggal terima/kirim dari tanggal surat (hari)
MAX_RECEIVE_DELAY = 7
MAX_SEND_DELAY = 5


def is_status_allowed(status: str, item: DummyClassification, year: int, reference_year: int) -> bool:
    """Menjawab apakah status sah untuk klasifikasi dan tahun dokumen (003a DS3).

    Args:
        status: archive_status yang diundi.
        item: Klasifikasi baris.
        year: Tahun dokumen.
        reference_year: Tahun acuan Y₀.

    Returns:
        `False` untuk destroyed yang bukan destroy atau belum lewat masa akhir
        (Y₀ > x + a + i), dan untuk permanent yang bukan permanent/assess.
    """
    if status == "destroyed":
        return item.final_action == "destroy" and reference_year > year + item.active_years + item.inactive_years
    if status == "permanent":
        return item.final_action in ("permanent", "assess")
    return True


def draw_status_and_classification(rng: random.Random, year: int,
                                   reference_year: int) -> tuple[str, DummyClassification]:
    """Mengundi status sesuai bobot DS3, lalu klasifikasi secara seragam dari yang sah untuk status itu.

    Kalau tidak ada klasifikasi yang sah (destroyed di tahun yang belum lewat masa akhir
    untuk klasifikasi mana pun), status diundi ulang dari status yang masih punya klasifikasi sah.

    Args:
        rng: Generator acak seed.
        year: Tahun dokumen.
        reference_year: Tahun acuan Y₀.

    Returns:
        (archive_status, klasifikasi) yang sah menurut `is_status_allowed`.
    """
    def allowed_for(status: str) -> list[DummyClassification]:
        return [item for item in DUMMY_CLASSIFICATIONS if is_status_allowed(status, item, year, reference_year)]

    status = choose_weighted(rng, STATUS_WEIGHTS)
    if not allowed_for(status):
        status = choose_weighted(rng, tuple((value, weight) for value, weight in STATUS_WEIGHTS if allowed_for(value)))
    return status, rng.choice(allowed_for(status))


def _random_day(rng: random.Random, year: int) -> date:
    return date(year, 1, 1) + timedelta(days=rng.randrange(365))


def _delayed(rng: random.Random, day: date, max_delay: int, reference_year: int) -> date:
    latest = date(reference_year, 12, 31)
    return min(day + timedelta(days=rng.randint(0, max_delay)), latest)


def _build_letters(factory: RowFactory, rng: random.Random, table: str, per_year: int,
                   reference_year: int) -> list[SeedRow]:
    rows: list[SeedRow] = []
    for year in range(reference_year - YEAR_SPAN + 1, reference_year + 1):
        for _ in range(per_year):
            status, item = draw_status_and_classification(rng, year, reference_year)
            letter_date = _random_day(rng, year)
            if table == "incoming_letter":
                received = _delayed(rng, letter_date, MAX_RECEIVE_DELAY, reference_year)
                rows.append(factory.build_incoming_row(letter_date, received, item.code, status, "isian"))
            else:
                sent = _delayed(rng, letter_date, MAX_SEND_DELAY, reference_year)
                rows.append(factory.build_outgoing_row(letter_date, sent, item.code, status, "isian"))
    return rows


def _build_finance(factory: RowFactory, rng: random.Random, per_year: int, reference_year: int) -> list[SeedRow]:
    rows: list[SeedRow] = []
    for year in range(reference_year - YEAR_SPAN + 1, reference_year + 1):
        for _ in range(per_year):
            status, item = draw_status_and_classification(rng, year, reference_year)
            rows.append(factory.build_finance_row(year, item.code, status, "isian"))
    return rows


def _build_diplomas(factory: RowFactory, rng: random.Random, per_cohort: int, reference_year: int) -> list[SeedRow]:
    return [
        factory.build_diploma_row(year, rng.random() < DIPLOMA_COLLECTED_SHARE, "isian")
        for year in range(reference_year - YEAR_SPAN + 1, reference_year + 1)
        for _ in range(per_cohort)
    ]


def _build_employee_documents(factory: RowFactory, rng: random.Random, preset: Preset,
                              reference_year: int) -> list[SeedRow]:
    drafts: list[tuple[int, int]] = [
        (rng.randint(reference_year - YEAR_SPAN + 1, reference_year), owner)
        for owner in range(1, preset.employees + 1)
        for _ in range(preset.documents_per_employee)
    ]
    rows: list[SeedRow] = []
    for year, owner in sorted(drafts):
        status, item = draw_status_and_classification(rng, year, reference_year)
        if rng.random() < DOCUMENT_YEAR_NULL_SHARE:
            rows.append(factory.build_employee_document_row(owner, None, year, item.code, status, "isian"))
        else:
            rows.append(build_archive_row(factory, "employee_archive", year, item.code, status, "isian", owner))
    return rows


def build_fill_rows(factory: RowFactory, rng: random.Random, preset: Preset, reference_year: int) -> list[SeedRow]:
    """Membentuk baris isian acak sampai volume preset (003a DS3).

    Urutan tetap: per tabel, lalu per tahun, lalu nomor urut (DS2).

    Args:
        factory: Pembentuk baris (berbagi `rng` yang sama).
        rng: Generator acak seed.
        preset: Volume per tahun.
        reference_year: Tahun acuan Y₀.

    Returns:
        Baris isian lima jenis arsip.
    """
    rows = _build_letters(factory, rng, "incoming_letter", preset.incoming_per_year, reference_year)
    rows += _build_letters(factory, rng, "outgoing_letter", preset.outgoing_per_year, reference_year)
    rows += _build_diplomas(factory, rng, preset.diplomas_per_cohort, reference_year)
    rows += _build_finance(factory, rng, preset.finance_per_year, reference_year)
    rows += _build_employee_documents(factory, rng, preset, reference_year)
    return rows


def to_attachment_path(table: str, file_name: str) -> str:
    """Membentuk path lampiran berformat lama, misalnya `storage/documents/diplomas/<hex>.txt` (DS5)."""
    return f"storage/documents/{ATTACHMENT_SUBFOLDERS[table]}/{file_name}.txt"


def assign_attachments(rng: random.Random, rows: list[SeedRow]) -> None:
    """Mengisi `attachment_path` arsip non-destroyed dan menandai berkas yang sengaja hilang (DS5).

    40% baris non-destroyed mendapat path; 10% di antaranya `meta["attachment_missing"]`.
    Setiap jenis dijamin punya minimal satu lampiran ada dan satu hilang.

    Args:
        rng: Generator acak seed.
        rows: Baris seed; diubah di tempat.
    """
    for row in rows:
        if row.table not in ARCHIVE_TABLES or row.values.get("archive_status") == "destroyed":
            continue
        if rng.random() < ATTACHMENT_SHARE:
            row.values["attachment_path"] = to_attachment_path(row.table, f"{rng.getrandbits(128):032x}")
            row.meta["attachment_missing"] = rng.random() < ATTACHMENT_MISSING_SHARE
    for table in ARCHIVE_TABLES:
        with_path = [row for row in rows if row.table == table and row.values.get("attachment_path")]
        if len(with_path) >= 2 and all(row.meta["attachment_missing"] for row in with_path):
            with_path[0].meta["attachment_missing"] = False
        if len(with_path) >= 2 and not any(row.meta["attachment_missing"] for row in with_path):
            with_path[-1].meta["attachment_missing"] = True
