from datetime import date

from evaluation.seed.rows import RowFactory, SeedRow
from evaluation.seed.spec import CLASSIFIED_TABLES, DUMMY_CLASSIFICATIONS, YEAR_SPAN, DummyClassification

REFERENCE_FORMS = ("code", "name", "variant")
# C8: (pegawai pemilik akun, role, status); admin aktif = akun lama yang sudah ada di D1
SEED_USERS = ((1, "admin", "inactive"), (2, "teacher", "active"), (3, "teacher", "inactive"), (4, "headmaster", "active"))
DESTROY_CODES = tuple(item.code for item in DUMMY_CLASSIFICATIONS if item.final_action == "destroy" and item.code != "DMY-DXX")
KEEP_CODES = tuple(item.code for item in DUMMY_CLASSIFICATIONS if item.final_action in ("permanent", "assess"))
CLASSIFICATIONS = {item.code: item for item in DUMMY_CLASSIFICATIONS}
# Jumlah minimum baris per sel cakupan (003a DS3)
C2_ROWS = 3
C3_ROWS = 5
C6_ROWS = 5


def build_archive_row(factory: RowFactory, table: str, year: int, classification: str, status: str, tag: str,
                      owner: int, month: int = 7, day: int = 1) -> SeedRow:
    """Membentuk satu arsip ber-klasifikasi dengan tahun dokumen `year`.

    Args:
        factory: Pembentuk baris.
        table: Salah satu `CLASSIFIED_TABLES`.
        year: Tahun dokumen (letter_date.year, fiscal_year, atau document_year).
        classification: Kode klasifikasi dummy.
        status: archive_status.
        tag: Asal baris (DS4-*, C1, ...).
        owner: Nomor pegawai pemilik untuk dokumen pegawai.
        month: Bulan tanggal surat.
        day: Hari tanggal surat.

    Returns:
        Baris seed. Tanggal terima/kirim surat 2 hari setelah tanggal surat, di tahun yang sama.
    """
    letter_date = date(year, month, day)
    if table == "incoming_letter":
        return factory.build_incoming_row(letter_date, date(year, month, day + 2), classification, status, tag)
    if table == "outgoing_letter":
        return factory.build_outgoing_row(letter_date, date(year, month, day + 2), classification, status, tag)
    if table == "finance_archive":
        return factory.build_finance_row(year, classification, status, tag)
    return factory.build_employee_document_row(owner, year, year, classification, status, tag)


def to_boundary_years(item: DummyClassification, reference_year: int) -> tuple[tuple[str, int, str], ...]:
    """Menghitung empat baris batas DS4 untuk satu klasifikasi.

    Args:
        item: Klasifikasi dummy (a = masa aktif, i = masa inaktif).
        reference_year: Tahun acuan Y₀.

    Returns:
        (tag, tahun dokumen, status): akhir_batas Y₀−(a+i) dan akhir_lewat Y₀−(a+i)−1 berstatus
        inactive; aktif_batas Y₀−a dan aktif_lewat Y₀−a−1 berstatus active.
    """
    total = item.active_years + item.inactive_years
    return (
        ("DS4-akhir-batas", reference_year - total, "inactive"),
        ("DS4-akhir-lewat", reference_year - total - 1, "inactive"),
        ("DS4-aktif-batas", reference_year - item.active_years, "active"),
        ("DS4-aktif-lewat", reference_year - item.active_years - 1, "active"),
    )


def build_people_rows(factory: RowFactory, employee_count: int) -> list[SeedRow]:
    """Membentuk pegawai dan akun seed (C7 untuk referensi pegawai, C8 untuk akun).

    Pegawai 1–3 memakai bentuk referensi code, name, dan varian; sisanya diundi.

    Args:
        factory: Pembentuk baris.
        employee_count: Jumlah pegawai preset (minimal 4).

    Returns:
        Baris `teacher` lalu baris `user`.
    """
    employees = [
        factory.build_employee_row(number, REFERENCE_FORMS[number - 1] if number <= len(REFERENCE_FORMS) else None)
        for number in range(1, employee_count + 1)
    ]
    users = [factory.build_user_row(owner, role, status) for owner, role, status in SEED_USERS]
    return employees + users


def build_boundary_rows(factory: RowFactory, reference_year: int, owners: list[int]) -> list[SeedRow]:
    """Membentuk baris batas retensi DS4 untuk tiap jenis ber-klasifikasi × tiap klasifikasi.

    Args:
        factory: Pembentuk baris.
        reference_year: Tahun acuan Y₀.
        owners: Nomor pegawai pemilik dokumen pegawai, dipakai bergiliran.

    Returns:
        4 baris per (jenis, klasifikasi).
    """
    rows: list[SeedRow] = []
    for table in CLASSIFIED_TABLES:
        for item in DUMMY_CLASSIFICATIONS:
            for tag, year, status in to_boundary_years(item, reference_year):
                row = build_archive_row(factory, table, year, item.code, status, tag, owners[len(rows) % len(owners)])
                row.meta.update({"classification": item.code, "doc_year": year})
                rows.append(row)
    return rows


def _build_status_cells(factory: RowFactory, reference_year: int, owners: list[int]) -> list[SeedRow]:
    rows: list[SeedRow] = []
    for table in CLASSIFIED_TABLES:
        for item in DUMMY_CLASSIFICATIONS:
            rows.append(build_archive_row(factory, table, reference_year, item.code, "active", "C1",
                                          owners[len(rows) % len(owners)], month=3))
            rows.append(build_archive_row(factory, table, reference_year - item.active_years - 1, item.code,
                                          "inactive", "C1", owners[len(rows) % len(owners)], month=3))
        for k in range(C2_ROWS):
            destroy = CLASSIFICATIONS[DESTROY_CODES[k % len(DESTROY_CODES)]]
            year = reference_year - destroy.active_years - destroy.inactive_years - 1 - k
            rows.append(build_archive_row(factory, table, year, destroy.code, "destroyed", "C2",
                                          owners[len(rows) % len(owners)], month=5))
            keep = KEEP_CODES[k % len(KEEP_CODES)]
            rows.append(build_archive_row(factory, table, reference_year - 6 - k, keep, "permanent", "C2",
                                          owners[len(rows) % len(owners)], month=5))
    return rows


def _build_cross_year_letters(factory: RowFactory, reference_year: int) -> list[SeedRow]:
    rows: list[SeedRow] = []
    for k in range(C3_ROWS):
        year = reference_year - 3 - k
        code = DESTROY_CODES[k % len(DESTROY_CODES)]
        rows.append(factory.build_incoming_row(date(year, 12, 20 + k), date(year + 1, 1, 3 + k), code, "active", "C3"))
        rows.append(factory.build_outgoing_row(date(year, 12, 20 + k), date(year + 1, 1, 5 + k), code, "active", "C3"))
    return rows


def _build_month_edges(factory: RowFactory, reference_year: int) -> list[SeedRow]:
    rows: list[SeedRow] = []
    for item in DUMMY_CLASSIFICATIONS:
        year = reference_year - item.active_years
        for month in (1, 12):
            day = date(year, month, 15)
            rows.append(factory.build_incoming_row(day, day, item.code, "active", "C4"))
            rows.append(factory.build_outgoing_row(day, day, item.code, "active", "C4"))
    return rows


def _build_diploma_cells(factory: RowFactory, reference_year: int) -> list[SeedRow]:
    rows: list[SeedRow] = []
    for graduation_year in range(reference_year - YEAR_SPAN + 1, reference_year + 1):
        rows.append(factory.build_diploma_row(graduation_year, True, "C5"))
        rows.append(factory.build_diploma_row(graduation_year, False, "C5"))
    return rows


def _build_reference_forms(factory: RowFactory, reference_year: int, owners: list[int]) -> list[SeedRow]:
    rows: list[SeedRow] = []
    for k, form in enumerate(REFERENCE_FORMS):
        rows.append(factory.build_finance_row(reference_year - 1, DESTROY_CODES[0], "active", "C7", category_form=form))
        rows.append(factory.build_employee_document_row(owners[k % len(owners)], reference_year - 1, reference_year - 1,
                                                        DESTROY_CODES[0], "active", "C7", type_form=form))
        rows.append(factory.build_diploma_row(reference_year - 1, False, "C7", major_form=form))
    return rows


def build_coverage_rows(factory: RowFactory, reference_year: int, owners: list[int]) -> list[SeedRow]:
    """Membentuk baris cakupan wajib C1–C7 untuk arsip (C7 pegawai dan C8 ada di `build_people_rows`).

    Args:
        factory: Pembentuk baris.
        reference_year: Tahun acuan Y₀.
        owners: Nomor pegawai pemilik dokumen pegawai, dipakai bergiliran.

    Returns:
        Baris cakupan, berurutan C1/C2 → C3 → C4 → C5 → C6 → C7.
    """
    rows = _build_status_cells(factory, reference_year, owners)
    rows += _build_cross_year_letters(factory, reference_year)
    rows += _build_month_edges(factory, reference_year)
    rows += _build_diploma_cells(factory, reference_year)
    rows += [
        factory.build_employee_document_row(owners[k % len(owners)], None, reference_year - 9 + 2 * k,
                                            DESTROY_CODES[k % len(DESTROY_CODES)], "active", "C6")
        for k in range(C6_ROWS)
    ]
    rows += _build_reference_forms(factory, reference_year, owners)
    return rows
