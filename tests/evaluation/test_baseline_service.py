import csv
import json
from datetime import date
from pathlib import Path

import pytest

from evaluation.factory import build_baseline_service
from scripts.evaluation import run_baseline


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _summary(rows: list[dict]) -> dict[tuple[str, str], object]:
    return {(row["bagian"], row["ukuran"]): row["nilai"] for row in rows}


def test_baseline_mengukur_b1_sampai_b6_dan_menyimpan_hasil(old_db, tmp_path: Path) -> None:
    service = build_baseline_service(old_db.url, old_db.storage_root, tmp_path / "out", date(2026, 10, 5), "dummy")

    summary = _summary(service.measure(date(2026, 10, 4), repeat=1))

    assert summary[("B1", "baris incoming_letter")] == 3
    assert [summary[("B4", item)] for item in (
        "nomor_surat_keluar_ganda", "status_di_luar_domain", "tahun_ajaran_tidak_berformat",
        "gender_tidak_terpetakan", "referensi_tidak_cocok", "ijazah_diambil_tanpa_tanggal",
        "dokumen_pegawai_tanpa_klasifikasi",
    )] == [2, 2, 1, 1, 1, 1, 1]
    assert summary[("B5", "lampiran ada")] == 1
    assert summary[("B5", "lampiran hilang")] == 1
    assert summary[("B2", "|L| (tanpa ijazah)")] == 5
    assert summary[("B2", "kandidat ijazah lama")] == 2
    assert summary[("B3", "akan diubah scheduler lama")] == 6

    folder = tmp_path / "out" / "2026-10-05" / "dummy"
    assert sorted(path.name for path in folder.iterdir()) == [
        "b1_jumlah_status.csv", "b1_jumlah_tabel.csv", "b2_disposal_check.csv", "b3_scheduler_lama.csv",
        "b4_anomali.csv", "b5_lampiran.csv", "b6_waktu.csv", "meta.json", "ringkasan.csv",
    ]
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    assert meta["tanggal_uji"] == "2026-10-04"
    assert meta["sumber"] == "dummy"


def test_baseline_nyata_tidak_menyimpan_nilai_teks(old_db, tmp_path: Path) -> None:
    service = build_baseline_service(old_db.url, old_db.storage_root, tmp_path / "out", date(2026, 10, 5), "nyata")
    service.measure(date(2026, 10, 4), repeat=1)

    folder = tmp_path / "out" / "2026-10-05" / "nyata"
    anomalies = _read_csv(folder / "b4_anomali.csv")
    expired = _read_csv(folder / "b2_disposal_check.csv")
    attachments = _read_csv(folder / "b5_lampiran.csv")

    assert set(anomalies[0]) == {"butir", "tabel", "id", "kolom", "kategori"}
    assert "title" not in expired[0] and "number" not in expired[0]
    assert set(attachments[0]) == {"tabel", "id", "ada"}


def test_titik_masuk_mencetak_ringkasan(old_db, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                        capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(run_baseline.eval_settings, "eval_old_db_url", old_db.url)
    monkeypatch.setattr(run_baseline.eval_settings, "eval_storage_root", str(old_db.storage_root))
    monkeypatch.setattr(run_baseline.eval_settings, "eval_output_dir", str(tmp_path / "out"))

    exit_code = run_baseline.main(["--tanggal-uji", "2026-10-04", "--sumber", "dummy", "--ulang", "1"])

    assert exit_code == 0
    assert "|L| (tanpa ijazah)" in capsys.readouterr().out


def test_titik_masuk_gagal_tanpa_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(run_baseline.eval_settings, "eval_old_db_url", "")

    assert run_baseline.main(["--tanggal-uji", "2026-10-04", "--sumber", "dummy"]) == 1
