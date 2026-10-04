from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from evaluation.db import build_engine, to_read_only_statement, to_safe_url
from evaluation.errors import DatabaseAccessError


def _make_sqlite_with_table(path: Path) -> str:
    url = f"sqlite:///{path}"
    setup_engine = create_engine(url)
    with setup_engine.begin() as conn:
        conn.execute(text("CREATE TABLE contoh (id INTEGER PRIMARY KEY, nama TEXT)"))
        conn.execute(text("INSERT INTO contoh (nama) VALUES ('awal')"))
    setup_engine.dispose()
    return url


def test_engine_hanya_baca_menolak_insert(tmp_path: Path) -> None:
    engine = build_engine(_make_sqlite_with_table(tmp_path / "lama.db"), read_only=True)

    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM contoh")).scalar_one() == 1
        with pytest.raises(OperationalError):
            conn.execute(text("INSERT INTO contoh (nama) VALUES ('baru')"))


def test_engine_biasa_boleh_menulis(tmp_path: Path) -> None:
    engine = build_engine(_make_sqlite_with_table(tmp_path / "baru.db"), read_only=False)

    with engine.begin() as conn:
        conn.execute(text("INSERT INTO contoh (nama) VALUES ('baru')"))
        assert conn.execute(text("SELECT COUNT(*) FROM contoh")).scalar_one() == 2


def test_url_kosong_ditolak() -> None:
    with pytest.raises(DatabaseAccessError):
        build_engine("", read_only=True)


def test_url_tidak_valid_tidak_membocorkan_kata_sandi() -> None:
    with pytest.raises(DatabaseAccessError) as error:
        build_engine("driver-tidak-ada://user:rahasia123@host/db", read_only=True)

    assert "rahasia123" not in str(error.value)
    assert error.value.__cause__ is None


def test_perintah_hanya_baca_per_dialek() -> None:
    assert to_read_only_statement("mysql") == "SET SESSION TRANSACTION READ ONLY"
    assert to_read_only_statement("sqlite") == "PRAGMA query_only = ON"
    with pytest.raises(DatabaseAccessError):
        to_read_only_statement("postgresql")


def test_url_aman_menyembunyikan_kata_sandi() -> None:
    safe = to_safe_url("mysql+pymysql://user:rahasia123@localhost/arsip")

    assert "rahasia123" not in safe
    assert "user" in safe and "arsip" in safe


def test_pengaman_menolak_engine_selain_sqlite_sementara(tmp_path: Path) -> None:
    with pytest.raises(AssertionError):
        build_engine("mysql+pymysql://user:sandi@localhost/arsip", read_only=True)
    with pytest.raises(AssertionError):
        build_engine("sqlite:////var/tmp/di_luar_folder_test.db", read_only=True)


def test_env_aplikasi_palsu_terpasang() -> None:
    from app.core.config import settings

    assert settings.DATABASE_URL.startswith("mysql+pymysql://test:test@127.0.0.1:9/")
