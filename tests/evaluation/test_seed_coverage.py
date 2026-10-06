import random
import re
from collections import Counter
from datetime import datetime

import pytest

from evaluation.baseline.rules import (
    APPROVAL_STATUS_DOMAIN,
    ARCHIVE_STATUS_DOMAIN,
    FINAL_ACTION_DOMAIN,
    REFERENCE_COLUMNS,
    is_academic_year_valid,
    is_gender_mappable,
    is_reference_match,
)
from evaluation.seed.coverage import (
    SEED_USERS,
    build_boundary_rows,
    build_coverage_rows,
    build_people_rows,
    to_boundary_years,
)
from evaluation.seed.rows import Ref, RowFactory, SeedRow
from evaluation.seed.spec import CLASSIFIED_TABLES, DUMMY_CLASSIFICATIONS, REFERENCE_COLUMN_LENGTHS

Y0 = 2026
REFERENCES = {
    "school_major": [("TKJ", "Teknik Komputer dan Jaringan"), ("RPL", "Rekayasa Perangkat Lunak")],
    "teacher_emp_status": [("PNS", "Pegawai Negeri Sipil"), ("honorer", "Honorer")],
    "teacher_active_status": [("aktif", "Aktif")],
    "teacher_rank": [("III/a", "Penata Muda")],
    "finance_category": [("bos_reguler", "BOS Reguler"), ("komite", "Dana Komite")],
    "emp_doc_type": [("sk", "Surat Keputusan")],
}
CLASSIFICATIONS = {item.code: item for item in DUMMY_CLASSIFICATIONS}
YEAR_COLUMNS = {"incoming_letter": "letter_date", "outgoing_letter": "letter_date",
                "finance_archive": "fiscal_year", "employee_archive": "document_year"}


def _build(seed: int = 20261005, references: dict | None = None) -> list[SeedRow]:
    factory = RowFactory(random.Random(seed), references or REFERENCES, Y0)
    owners = list(range(1, 13))
    rows = factory.build_classification_rows() + factory.build_location_rows() + build_people_rows(factory, 12)
    return rows + build_boundary_rows(factory, Y0, owners) + build_coverage_rows(factory, Y0, owners)


def _doc_year(row: SeedRow) -> int | None:
    value = row.values[YEAR_COLUMNS[row.table]]
    return value.year if isinstance(value, datetime) else value


def _of(rows: list[SeedRow], table: str, tag: str | None = None) -> list[SeedRow]:
    return [row for row in rows if row.table == table and (tag is None or row.tag == tag)]


@pytest.fixture(scope="module")
def rows() -> list[SeedRow]:
    return _build()


def test_sy6_empat_baris_batas_per_jenis_dan_klasifikasi(rows: list[SeedRow]) -> None:
    for table in CLASSIFIED_TABLES:
        for item in DUMMY_CLASSIFICATIONS:
            boundary = {(row.tag, _doc_year(row), row.values["archive_status"])
                        for row in _of(rows, table) if row.tag.startswith("DS4")
                        and row.values["classification_id"] == Ref("classification", item.code)}
            assert boundary == set(to_boundary_years(item, Y0)), (table, item.code)


def test_baris_batas_dmy_dxx_lebih_tua_dari_rentang_isian() -> None:
    years = {tag: year for tag, year, _ in to_boundary_years(CLASSIFICATIONS["DMY-DXX"], Y0)}

    assert years == {"DS4-akhir-batas": 2006, "DS4-akhir-lewat": 2005,
                     "DS4-aktif-batas": 2016, "DS4-aktif-lewat": 2015}


def test_baris_batas_memisahkan_rumus_lama(rows: list[SeedRow]) -> None:
    # Rumus lama /disposal/check: tahun ini > x + a + i, hanya final_action destroy
    for table in CLASSIFIED_TABLES:
        for row in _of(rows, table):
            if not row.tag.startswith("DS4-akhir"):
                continue
            item = CLASSIFICATIONS[row.values["classification_id"].key]
            in_old_l = Y0 > _doc_year(row) + item.active_years + item.inactive_years
            assert in_old_l is (row.tag == "DS4-akhir-lewat")


def test_c1_dan_c2_setiap_status(rows: list[SeedRow]) -> None:
    for table in CLASSIFIED_TABLES:
        cells = Counter((row.values["classification_id"].key, row.values["archive_status"])
                        for row in _of(rows, table, "C1"))
        assert all(cells[(code, status)] >= 1 for code in CLASSIFICATIONS for status in ("active", "inactive"))
        statuses = Counter(row.values["archive_status"] for row in _of(rows, table, "C2"))
        assert statuses["destroyed"] >= 3 and statuses["permanent"] >= 3


def test_c2_destroyed_dan_permanent_sesuai_aturan(rows: list[SeedRow]) -> None:
    for row in rows:
        status = row.values.get("archive_status")
        if row.table not in CLASSIFIED_TABLES or status not in ("destroyed", "permanent"):
            continue
        item = CLASSIFICATIONS[row.values["classification_id"].key]
        if status == "destroyed":
            assert item.final_action == "destroy"
            assert Y0 > _doc_year(row) + item.active_years + item.inactive_years
            assert row.values["attachment_path"] is None
        else:
            assert item.final_action in ("permanent", "assess")


def test_c3_tanggal_lintas_tahun(rows: list[SeedRow]) -> None:
    incoming = [row for row in _of(rows, "incoming_letter", "C3")
                if row.values["letter_date"].month == 12 and row.values["received_date"].month == 1
                and row.values["received_date"].year == row.values["letter_date"].year + 1]
    outgoing = [row for row in _of(rows, "outgoing_letter", "C3")
                if row.values["sent_date"].year != row.values["letter_date"].year]

    assert len(incoming) >= 5 and len(outgoing) >= 5


def test_c4_januari_dan_desember_di_tahun_y0_kurang_a(rows: list[SeedRow]) -> None:
    for table in ("incoming_letter", "outgoing_letter"):
        cells = {(row.values["classification_id"].key, row.values["letter_date"].month)
                 for row in _of(rows, table, "C4")
                 if row.values["letter_date"].year == Y0 - CLASSIFICATIONS[row.values["classification_id"].key].active_years
                 and row.values["archive_status"] == "active"}
        assert cells == {(code, month) for code in CLASSIFICATIONS for month in (1, 12)}


def test_c5_ijazah_per_angkatan(rows: list[SeedRow]) -> None:
    diplomas = _of(rows, "diploma")
    by_year: dict[int, set[bool]] = {}
    for row in diplomas:
        by_year.setdefault(int(row.values["academic_year"][-4:]), set()).add(row.values["is_collected"])

    assert all(by_year[year] == {True, False} for year in range(Y0 - 10, Y0 + 1))
    old_collected = [row for row in diplomas
                     if row.values["is_collected"] and int(row.values["academic_year"][:4]) < Y0 - 5]
    assert len(old_collected) >= 5
    assert all(row.values["collected_at"] is not None for row in diplomas if row.values["is_collected"])
    assert all(row.values["collected_at"].year <= Y0 for row in diplomas if row.values["is_collected"])


def test_c6_dokumen_pegawai_tanpa_tahun(rows: list[SeedRow]) -> None:
    documents = [row for row in _of(rows, "employee_archive", "C6") if row.values["document_year"] is None]

    assert len(documents) >= 5
    assert len({row.values["created_at"].year for row in documents}) >= 3


def test_c7_tiap_kategori_punya_bentuk_code_name_varian(rows: list[SeedRow]) -> None:
    for spec in REFERENCE_COLUMNS:
        values = [row.values[spec.column] for row in rows if row.table == spec.table and row.values.get(spec.column)]
        codes = {code for code, _ in REFERENCES[spec.category]}
        names = {name for _, name in REFERENCES[spec.category]}
        assert any(value in codes for value in values), spec
        assert any(value in names for value in values), spec
        assert any(value not in codes and value not in names for value in values), spec


def test_c8_akun_seed(rows: list[SeedRow]) -> None:
    users = {(row.values["role"], row.values["status"]) for row in rows if row.table == "user"}

    assert users == {(role, status) for _, role, status in SEED_USERS}


def test_tidak_ada_pola_b4(rows: list[SeedRow]) -> None:
    outgoing_numbers = Counter(row.values["number"] for row in _of(rows, "outgoing_letter"))
    assert max(outgoing_numbers.values()) == 1
    for row in rows:
        if "archive_status" in row.values:
            assert row.values["archive_status"] in ARCHIVE_STATUS_DOMAIN
        if row.table == "classification":
            assert row.values["final_action"] in FINAL_ACTION_DOMAIN
        if row.table == "outgoing_letter":
            assert row.values["approval_status"] in APPROVAL_STATUS_DOMAIN
        if row.table == "diploma":
            assert is_academic_year_valid(row.values["academic_year"])
            assert not (row.values["is_collected"] and row.values["collected_at"] is None)
        if row.table == "teacher":
            assert is_gender_mappable(row.values["gender"])
        if row.table == "employee_archive":
            assert row.values["classification_id"] is not None
    for spec in REFERENCE_COLUMNS:
        for row in rows:
            value = row.values.get(spec.column) if row.table == spec.table else None
            if value is not None:
                assert is_reference_match(value, REFERENCES[spec.category]), (spec, value)


def test_penanda_ds7(rows: list[SeedRow]) -> None:
    patterns = {
        "classification": ("code", r"DMY-"), "storage_location": ("name", r"DUMMY "),
        "incoming_letter": ("number", r"DMY/IN/\d{4}/\d{4}$"), "outgoing_letter": ("number", r"DMY/OUT/\d{4}/\d{4}$"),
        "diploma": ("number", r"DMY-IJZ-\d{4}-\d{4}$"), "finance_archive": ("title", r"DUMMY "),
        "employee_archive": ("document_name", r"DUMMY "), "teacher": ("full_name", r"Pegawai Dummy \d{3}$"),
    }
    for row in rows:
        if row.table in patterns:
            column, pattern = patterns[row.table]
            assert re.match(pattern, str(row.values[column])), (row.table, row.values[column])
    for row in _of(rows, "teacher"):
        assert re.fullmatch(r"9900\d{14}", row.values["identity_number"])
        assert row.values["address"].startswith("Alamat Dummy ")
    for row in _of(rows, "diploma"):
        assert row.values["student_name"].startswith("Siswa Dummy ")
    for table in ("incoming_letter", "outgoing_letter"):
        assert all(row.values["subject"].startswith("DUMMY ") for row in _of(rows, table))


def test_semua_jejak_waktu_diisi_dan_tidak_melewati_tahun_acuan(rows: list[SeedRow]) -> None:
    for row in rows:
        assert isinstance(row.values["created_at"], datetime)
        assert isinstance(row.values["updated_at"], datetime)
        dates = [value for value in row.values.values() if isinstance(value, datetime)]
        assert all(value.year <= Y0 for value in dates)


def test_referensi_tidak_melebihi_panjang_kolom() -> None:
    long_name = "N" * 60
    references = {**REFERENCES, "finance_category": [("kat", long_name)]}
    factory = RowFactory(random.Random(1), references, Y0)

    values = {factory.pick_reference("finance_category", "name") for _ in range(5)}

    assert values == {"kat"}
    assert len(factory.pick_reference("finance_category", "variant")) <= REFERENCE_COLUMN_LENGTHS["finance_category"]


def test_tanpa_teacher_rank_semua_rank_kosong() -> None:
    references = {key: value for key, value in REFERENCES.items() if key != "teacher_rank"}

    rows = _build(references=references)

    assert all(row.values["rank"] is None for row in _of(rows, "teacher"))


def test_deterministik(rows: list[SeedRow]) -> None:
    same = _build()
    other = _build(seed=1)

    assert [(row.table, row.tag, row.values) for row in same] == [(row.table, row.tag, row.values) for row in rows]
    assert [row.values for row in other] != [row.values for row in rows]
