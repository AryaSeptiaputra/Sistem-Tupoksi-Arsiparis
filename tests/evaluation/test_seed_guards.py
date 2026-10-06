from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from evaluation.config import eval_settings
from evaluation.db import build_engine
from evaluation.errors import SeedGuardError
from evaluation.seed.guards import (
    to_database_key,
    validate_seed_storage_root,
    validate_seed_target,
    validate_target_state,
)
from evaluation.seed.repository import SeedTargetRepository

D1_RO = "mysql+pymysql://eval_ro:ro@localhost/tupoksi_d1"
D1_WRITE = "mysql+pymysql://root:rahasia@127.0.0.1:3306/tupoksi_d1"
APP = "mysql+pymysql://app:app@localhost/arsiparis_smk7"


def test_target_d1_dengan_user_lain_diterima() -> None:
    validate_seed_target(D1_WRITE, D1_RO, APP)


@pytest.mark.parametrize(
    "seed_url",
    [
        "mysql+pymysql://root:x@localhost/arsiparis_smk7",
        "mysql+pymysql://root:x@127.0.0.1:3306/ARSIPARIS_SMK7",
        "mysql+pymysql://root:x@192.168.1.10/arsiparis_smk7",
    ],
)
def test_target_database_aplikasi_ditolak(seed_url: str) -> None:
    with pytest.raises(SeedGuardError, match="database aplikasi"):
        validate_seed_target(seed_url, seed_url, APP)


def test_target_bukan_d1_ditolak() -> None:
    with pytest.raises(SeedGuardError, match="EVAL_OLD_DB_URL"):
        validate_seed_target("mysql+pymysql://root:x@localhost/salinan_lain", D1_RO, APP)


def test_port_berbeda_berarti_server_berbeda() -> None:
    with pytest.raises(SeedGuardError, match="EVAL_OLD_DB_URL"):
        validate_seed_target("mysql+pymysql://root:x@localhost:3307/tupoksi_d1", D1_RO, APP)


@pytest.mark.parametrize(("seed", "old", "app"), [("", D1_RO, APP), (D1_WRITE, "", APP), (D1_WRITE, D1_RO, "")])
def test_url_kosong_menghentikan_seed(seed: str, old: str, app: str) -> None:
    with pytest.raises(SeedGuardError, match="kosong"):
        validate_seed_target(seed, old, app)


def test_pesan_penjaga_tidak_memuat_kata_sandi() -> None:
    with pytest.raises(SeedGuardError) as error:
        validate_seed_target("bukan url://root:rahasia@", D1_RO, APP)

    assert "rahasia" not in str(error.value)


def test_kunci_sqlite_memakai_path(tmp_path: Path) -> None:
    url = f"sqlite:///{tmp_path / 'd1.db'}"

    assert to_database_key(url, "X") == ("sqlite", "", None, str((tmp_path / "d1.db").resolve()))


def test_database_url_aplikasi_dibaca_dari_environment() -> None:
    assert eval_settings.database_url.startswith("mysql+pymysql://test:test@127.0.0.1:9/")


def test_folder_lampiran_terpisah_diterima(tmp_path: Path) -> None:
    root = validate_seed_storage_root(str(tmp_path / "data" / "evaluation" / "storage_d1"), [tmp_path / "storage"])

    assert root == (tmp_path / "data" / "evaluation" / "storage_d1").resolve()


@pytest.mark.parametrize("relative", ["storage", "storage/documents", "."])
def test_folder_lampiran_bersinggungan_dengan_storage_aplikasi_ditolak(tmp_path: Path, relative: str) -> None:
    with pytest.raises(SeedGuardError, match="storage aplikasi"):
        validate_seed_storage_root(str(tmp_path / relative), [tmp_path / "storage"])


def test_folder_lampiran_kosong_ditolak(tmp_path: Path) -> None:
    with pytest.raises(SeedGuardError, match="wajib diisi"):
        validate_seed_storage_root("  ", [tmp_path / "storage"])


def test_d1_kosong_lolos_penjaga_isi(empty_d1) -> None:
    repository = SeedTargetRepository(build_engine(empty_d1.url, read_only=True))

    counts = repository.count_archive_rows()
    references = repository.fetch_references()
    validate_target_state(counts, repository.has_marked_rows(), references)

    assert set(counts.values()) == {0}
    assert "teacher_rank" not in {row["category"] for row in references}


def test_d1_berisi_arsip_ditolak(old_db) -> None:
    repository = SeedTargetRepository(build_engine(old_db.url, read_only=True))

    with pytest.raises(SeedGuardError) as error:
        validate_target_state(repository.count_archive_rows(), repository.has_marked_rows(),
                              repository.fetch_references())

    message = str(error.value)
    assert "incoming_letter berisi 3 baris" in message
    assert "storage_location berisi 1 baris" in message


@pytest.mark.parametrize(
    "statement",
    [
        "INSERT INTO classification (code, name, retention_active_period, retention_inactive_period, final_action) "
        "VALUES ('DMY-D11', 'x', 1, 1, 'destroy')",
        "INSERT INTO teacher (identity_number, full_name, gender, employment_status, status) "
        "VALUES ('990001010000000001', 'Pegawai Dummy 001', 'L', 'PNS', 'aktif')",
        "INSERT INTO classification (code, name, retention_active_period, retention_inactive_period, final_action) "
        "VALUES ('X-1', 'Klasifikasi ANOMALI-B4-2', 1, 1, 'destroy')",
    ],
)
def test_baris_berpenanda_terdeteksi(empty_d1, statement: str) -> None:
    writer = create_engine(empty_d1.url)
    with writer.begin() as conn:
        conn.execute(text(statement))
    writer.dispose()
    repository = SeedTargetRepository(build_engine(empty_d1.url, read_only=True))

    assert repository.has_marked_rows() is True
    with pytest.raises(SeedGuardError, match="berpenanda"):
        validate_target_state(repository.count_archive_rows(), True, repository.fetch_references())


def test_kategori_wajib_kosong_ditolak(empty_d1) -> None:
    writer = create_engine(empty_d1.url)
    with writer.begin() as conn:
        conn.execute(text("DELETE FROM master_reference WHERE category IN ('emp_doc_type', 'finance_category')"))
    writer.dispose()
    repository = SeedTargetRepository(build_engine(empty_d1.url, read_only=True))

    with pytest.raises(SeedGuardError) as error:
        validate_target_state(repository.count_archive_rows(), False, repository.fetch_references())

    assert "finance_category kosong" in str(error.value)
    assert "emp_doc_type kosong" in str(error.value)
