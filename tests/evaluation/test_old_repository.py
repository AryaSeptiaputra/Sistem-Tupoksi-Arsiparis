from pathlib import Path

import pytest

from evaluation.baseline.old_repository import OldDatabaseRepository, has_file
from evaluation.baseline.rules import (
    is_academic_year_valid,
    is_gender_mappable,
    is_reference_match,
    strip_storage_prefix,
)
from evaluation.db import build_engine


@pytest.fixture
def repository(old_db) -> OldDatabaseRepository:
    return OldDatabaseRepository(build_engine(old_db.url, read_only=True))


def test_b1_jumlah_baris_per_tabel(repository: OldDatabaseRepository) -> None:
    counts = {row["tabel"]: row["jumlah"] for row in repository.count_rows()}

    assert counts == {
        "user": 2, "teacher": 2, "log": 1, "backup": 0, "master_reference": 6, "classification": 3,
        "storage_location": 1, "incoming_letter": 3, "outgoing_letter": 2, "diploma": 3,
        "finance_archive": 2, "employee_archive": 2,
    }


def test_b1_jumlah_per_status(repository: OldDatabaseRepository) -> None:
    rows = {(row["tabel"], row["archive_status"]): row["jumlah"] for row in repository.count_by_status()}

    assert rows == {
        ("incoming_letter", "Aktif"): 1, ("incoming_letter", "active"): 2,
        ("outgoing_letter", "active"): 2, ("finance_archive", "active"): 2, ("employee_archive", "active"): 2,
    }


def test_b4_nomor_surat_keluar_ganda(repository: OldDatabaseRepository) -> None:
    assert repository.fetch_duplicate_outgoing_numbers() == [
        {"id": 1, "number": "OUT-1"},
        {"id": 2, "number": "OUT-1"},
    ]


def test_b4_status_di_luar_domain(repository: OldDatabaseRepository) -> None:
    assert repository.fetch_out_of_domain_statuses() == [
        {"tabel": "incoming_letter", "id": 3, "kolom": "archive_status", "nilai": "Aktif"},
        {"tabel": "classification", "id": 3, "kolom": "final_action", "nilai": "musnah"},
    ]


def test_b4_tahun_ajaran_dan_gender(repository: OldDatabaseRepository) -> None:
    invalid_years = [row["id"] for row in repository.fetch_academic_years()
                     if not is_academic_year_valid(row["academic_year"])]
    unmappable = [row["id"] for row in repository.fetch_gender_values() if not is_gender_mappable(row["gender"])]

    assert invalid_years == [2]
    assert unmappable == [2]


def test_b4_referensi_tidak_cocok(repository: OldDatabaseRepository) -> None:
    assert repository.fetch_unmatched_references() == [
        {"tabel": "finance_archive", "id": 2, "kolom": "category", "kategori": "finance_category", "nilai": "dana_x"},
    ]


def test_b4_ijazah_dan_dokumen_pegawai(repository: OldDatabaseRepository) -> None:
    assert repository.fetch_collected_without_date() == [{"id": 3}]
    assert repository.fetch_employee_docs_without_classification() == [{"id": 2}]


def test_b5_membedakan_file_ada_dan_hilang(repository: OldDatabaseRepository, old_db) -> None:
    paths = repository.fetch_attachment_paths()
    found = {(row["tabel"], row["id"]): has_file(old_db.storage_root, strip_storage_prefix(row["path"]))
             for row in paths}

    assert found == {("incoming_letter", 1): True, ("incoming_letter", 2): False}


def test_has_file_tidak_keluar_dari_storage(tmp_path: Path) -> None:
    (tmp_path / "rahasia.txt").write_text("x", encoding="utf-8")
    root = tmp_path / "storage"
    root.mkdir()

    assert has_file(root, "../rahasia.txt") is False


@pytest.mark.parametrize(
    ("value", "expected"),
    [("2019/2020", True), ("2019-2020", False), ("19/20", False), (None, False), (" 2019/2020", False)],
)
def test_format_tahun_ajaran(value: str | None, expected: bool) -> None:
    assert is_academic_year_valid(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("L", True), ("laki-laki", True), (" Perempuan ", True), ("p", True), ("X", False), (None, False), ("", False)],
)
def test_gender_bisa_dipetakan(value: str | None, expected: bool) -> None:
    assert is_gender_mappable(value) is expected


def test_pencocokan_referensi_memakai_code_atau_name() -> None:
    references = [("TKJ", "Teknik Komputer")]

    assert is_reference_match(" tkj", references)
    assert is_reference_match("teknik komputer", references)
    assert not is_reference_match("TKR", references)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("storage/documents/a.pdf", "documents/a.pdf"),
        ("/storage/documents/a.pdf", "documents/a.pdf"),
        ("storage\\documents\\a.pdf", "documents/a.pdf"),
        ("documents/a.pdf", "documents/a.pdf"),
    ],
)
def test_awalan_storage_dibuang(path: str, expected: str) -> None:
    assert strip_storage_prefix(path) == expected
