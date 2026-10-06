from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from evaluation.db import build_engine
from evaluation.errors import DatabaseAccessError
from evaluation.hashing import hash_table_rows, to_hashable_value


def _make_db(path: Path, rows: list[tuple[int, str, str]]) -> str:
    url = f"sqlite:///{path}"
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE contoh (id INTEGER PRIMARY KEY, nama TEXT, tanggal DATE)"))
        conn.execute(text("CREATE TABLE kosong (id INTEGER PRIMARY KEY)"))
        for row in rows:
            conn.execute(text("INSERT INTO contoh (id, nama, tanggal) VALUES (:id, :nama, :tanggal)"),
                         {"id": row[0], "nama": row[1], "tanggal": row[2]})
    engine.dispose()
    return url


ROWS = [(1, "a", "2026-01-01"), (2, "b", "2026-01-02"), (3, None, None)]


def test_hash_tidak_bergantung_urutan_insert(tmp_path: Path) -> None:
    first = build_engine(_make_db(tmp_path / "satu.db", ROWS), read_only=True)
    second = build_engine(_make_db(tmp_path / "dua.db", list(reversed(ROWS))), read_only=True)

    assert hash_table_rows(first, ["contoh", "kosong"]) == hash_table_rows(second, ["contoh", "kosong"])


def test_hash_berubah_kalau_satu_nilai_berubah(tmp_path: Path) -> None:
    changed = [(1, "a", "2026-01-01"), (2, "B", "2026-01-02"), (3, None, None)]
    first = build_engine(_make_db(tmp_path / "satu.db", ROWS), read_only=True)
    second = build_engine(_make_db(tmp_path / "dua.db", changed), read_only=True)

    assert hash_table_rows(first, ["contoh"]) != hash_table_rows(second, ["contoh"])


def test_hash_membedakan_null_dan_teks_kosong(tmp_path: Path) -> None:
    first = build_engine(_make_db(tmp_path / "satu.db", [(1, None, None)]), read_only=True)
    second = build_engine(_make_db(tmp_path / "dua.db", [(1, "", None)]), read_only=True)

    assert hash_table_rows(first, ["contoh"]) != hash_table_rows(second, ["contoh"])


def test_tabel_tidak_ada_menjadi_error(tmp_path: Path) -> None:
    engine = build_engine(_make_db(tmp_path / "satu.db", ROWS), read_only=True)

    with pytest.raises(DatabaseAccessError):
        hash_table_rows(engine, ["tidak_ada"])


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, 1),
        (datetime(2026, 1, 2, 3, 4, 5), "2026-01-02T03:04:05"),
        (date(2026, 1, 2), "2026-01-02"),
        (Decimal("1000.50"), "1000.50"),
        (b"\x01\xff", "01ff"),
        (None, None),
        (7, 7),
    ],
)
def test_nilai_dinormalisasi(value: object, expected: object) -> None:
    assert to_hashable_value(value) == expected


def test_hash_skema_lama_d1(empty_d1) -> None:
    engine = build_engine(empty_d1.url, read_only=True)

    hashes = hash_table_rows(engine, ["user", "teacher", "log", "master_reference"])

    assert set(hashes) == {"user", "teacher", "log", "master_reference"}
    assert hashes == hash_table_rows(engine, ["user", "teacher", "log", "master_reference"])
