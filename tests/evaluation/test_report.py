import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from evaluation.report import ResultWriter, format_table, to_safe_rows


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_folder_hasil_mengikuti_tanggal_jalan_dan_sumber(tmp_path: Path) -> None:
    writer = ResultWriter(tmp_path, date(2026, 10, 4), "dummy")

    path = writer.save_table("b1", [{"tabel": "diploma", "jumlah": 3}])

    assert path == tmp_path / "2026-10-04" / "dummy" / "b1.csv"
    assert _read_csv(path) == [{"tabel": "diploma", "jumlah": "3"}]


def test_sumber_selain_dummy_dan_nyata_ditolak(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        ResultWriter(tmp_path, date(2026, 10, 4), "campuran")


def test_mode_nyata_hanya_menyimpan_angka_id_dan_label(tmp_path: Path) -> None:
    rows = [
        {"butir": "gender", "tabel": "teacher", "id": 2, "nilai": "X", "nama": "Pegawai", "jumlah": Decimal("1")},
        {"butir": "gender", "tabel": "teacher", "id": 3, "nilai": None, "nama": "Lain", "jumlah": 2},
    ]
    writer = ResultWriter(tmp_path, date(2026, 10, 4), "nyata")

    stored = _read_csv(writer.save_table("b4", rows, label_columns={"butir", "tabel"}))

    assert list(stored[0]) == ["butir", "tabel", "id", "jumlah"]
    assert stored[1] == {"butir": "gender", "tabel": "teacher", "id": "3", "jumlah": "2"}


def test_mode_dummy_menyimpan_semua_kolom(tmp_path: Path) -> None:
    writer = ResultWriter(tmp_path, date(2026, 10, 4), "dummy")

    stored = _read_csv(writer.save_table("b4", [{"id": 2, "nilai": "X", "nama": "Pegawai"}]))

    assert stored == [{"id": "2", "nilai": "X", "nama": "Pegawai"}]


def test_kolom_teks_berisi_angka_tetap_dibuang_di_mode_nyata() -> None:
    rows = [{"id": 1, "identity_number": "198001012005011001"}]

    assert to_safe_rows(rows) == [{"id": 1}]


def test_meta_mencatat_sumber(tmp_path: Path) -> None:
    writer = ResultWriter(tmp_path, date(2026, 10, 4), "dummy")

    path = writer.save_meta({"tanggal_uji": date(2026, 10, 4), "db_lama": "mysql+pymysql://u:***@h/db"})

    assert json.loads(path.read_text(encoding="utf-8")) == {
        "tanggal_uji": "2026-10-04",
        "db_lama": "mysql+pymysql://u:***@h/db",
        "sumber": "dummy",
    }


def test_tabel_kosong_tetap_menjadi_berkas(tmp_path: Path) -> None:
    writer = ResultWriter(tmp_path, date(2026, 10, 4), "dummy")

    assert writer.save_table("kosong", []).read_text(encoding="utf-8") == ""


def test_format_table_rata_kiri() -> None:
    text = format_table([{"ukuran": "B1 tabel", "nilai": 12}, {"ukuran": "B2 |L|", "nilai": 5}])

    assert text.splitlines() == [
        "ukuran    nilai",
        "--------  -----",
        "B1 tabel  12   ",
        "B2 |L|    5    ",
    ]
    assert format_table([]) == "(kosong)"
