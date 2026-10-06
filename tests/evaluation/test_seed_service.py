from datetime import date
from pathlib import Path

import pytest

from evaluation.baseline.old_repository import OLD_TABLES
from evaluation.db import build_engine
from evaluation.errors import SeedGuardError
from evaluation.factory import build_baseline_service, build_seed_gate_checker, build_seed_service
from evaluation.hashing import hash_table_rows
from evaluation.seed.plan import SeedParams
from scripts.evaluation import check_seed_gate, seed_d1

RUN_DATE = date(2026, 10, 6)
TANGGAL_UJI = date(2026, 10, 6)
APP_URL = "mysql+pymysql://test:test@127.0.0.1:9/tidak_ada"


@pytest.fixture(autouse=True)
def create_app_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    import app

    def fail_create_app() -> None:
        raise AssertionError("create_app() tidak boleh dipanggil oleh seed atau baseline")

    monkeypatch.setattr(app, "create_app", fail_create_app)


def _seed(d1, output: Path, params: SeedParams) -> list[dict]:
    service = build_seed_service(d1.url, d1.url, APP_URL, str(d1.storage_root), output, RUN_DATE)
    return service.run(params)


def _baseline(d1, output: Path) -> Path:
    service = build_baseline_service(d1.url, d1.storage_root, output, RUN_DATE, "dummy")
    service.measure(TANGGAL_UJI, repeat=1)
    return output / RUN_DATE.isoformat() / "dummy"


def _failed(rows: list[dict]) -> list[str]:
    return [row["syarat"] for row in rows if not row["lulus"]]


def test_sy7_parameter_sama_hash_identik_seed_berbeda_hash_berbeda(make_empty_d1, tmp_path: Path) -> None:
    first, second, third = make_empty_d1("satu"), make_empty_d1("dua"), make_empty_d1("tiga")
    _seed(first, tmp_path / "out1", SeedParams(scale="kecil", anomalies=True))
    _seed(second, tmp_path / "out2", SeedParams(scale="kecil", anomalies=True))
    _seed(third, tmp_path / "out3", SeedParams(scale="kecil", anomalies=True, seed=7))

    hashes = [hash_table_rows(build_engine(d1.url, read_only=True), list(OLD_TABLES)) for d1 in (first, second, third)]

    assert hashes[0] == hashes[1]
    assert hashes[0] != hashes[2]
    files = [sorted(path.relative_to(d1.storage_root) for path in d1.storage_root.rglob("*.txt"))
             for d1 in (first, second)]
    assert files[0] == files[1]


@pytest.mark.parametrize("anomalies", [True, False])
def test_seed_lalu_baseline_kode_lama_memenuhi_sy1_sampai_sy9(empty_d1, tmp_path: Path, anomalies: bool) -> None:
    summary = _seed(empty_d1, tmp_path / "out", SeedParams(scale="kecil", anomalies=anomalies))
    baseline_dir = _baseline(empty_d1, tmp_path / "out")

    checks = build_seed_gate_checker(str(empty_d1.storage_root), anomalies, 2026).check(baseline_dir)

    assert _failed(summary) == []
    assert _failed(checks) == []
    b4 = {row["syarat"]: row["nilai"] for row in checks if row["syarat"].startswith("SY4")}
    assert sum(b4.values()) == (10 if anomalies else 0)
    assert (baseline_dir / "seed_ringkasan.csv").exists() and (baseline_dir / "seed_meta.json").exists()
    assert (baseline_dir / "meta.json").exists()


def test_pemeriksa_menangkap_storage_root_salah_dan_target_b4_salah(empty_d1, tmp_path: Path) -> None:
    _seed(empty_d1, tmp_path / "out", SeedParams(scale="kecil", anomalies=True))
    service = build_baseline_service(empty_d1.url, tmp_path / "storage-lain", tmp_path / "out", RUN_DATE, "dummy")
    service.measure(TANGGAL_UJI, repeat=1)
    baseline_dir = tmp_path / "out" / RUN_DATE.isoformat() / "dummy"

    failed = _failed(build_seed_gate_checker(str(empty_d1.storage_root), False, 2026).check(baseline_dir))

    assert "Syarat pakai: EVAL_STORAGE_ROOT = folder seed" in failed
    assert all(f"SY5 B5 {table}" in failed for table in ("incoming_letter", "diploma"))
    assert "SY4 B4 gender_tidak_terpetakan" in failed


def test_pemeriksa_menolak_tahun_tanggal_uji_berbeda(empty_d1, tmp_path: Path) -> None:
    _seed(empty_d1, tmp_path / "out", SeedParams(scale="kecil"))
    baseline_dir = _baseline(empty_d1, tmp_path / "out")

    failed = _failed(build_seed_gate_checker(str(empty_d1.storage_root), False, 2027).check(baseline_dir))

    assert failed == ["Syarat pakai: tahun tanggal_uji"]


def test_target_database_aplikasi_ditolak_sebelum_engine_dibuat(empty_d1, tmp_path: Path) -> None:
    with pytest.raises(SeedGuardError, match="database aplikasi"):
        build_seed_service(empty_d1.url, empty_d1.url, empty_d1.url, str(empty_d1.storage_root), tmp_path, RUN_DATE)


def _use_settings(monkeypatch: pytest.MonkeyPatch, d1, output: Path) -> None:
    from evaluation.config import eval_settings

    for name, value in {"eval_seed_db_url": d1.url, "eval_old_db_url": d1.url, "database_url": APP_URL,
                        "eval_seed_storage_root": str(d1.storage_root), "eval_output_dir": str(output),
                        "eval_storage_root": str(d1.storage_root)}.items():
        monkeypatch.setattr(eval_settings, name, value)


def test_titik_masuk_seed_dan_pemeriksa(empty_d1, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                        capsys: pytest.CaptureFixture[str]) -> None:
    _use_settings(monkeypatch, empty_d1, tmp_path / "out")

    assert seed_d1.main(["--skala", "kecil", "--anomali"]) == 0
    assert "SY6 baris batas DS4" in capsys.readouterr().out
    assert seed_d1.main(["--skala", "kecil", "--anomali"]) == 1

    baseline_dir = _baseline(empty_d1, tmp_path / "out")
    assert check_seed_gate.main(["--hasil", str(baseline_dir), "--anomali"]) == 0
    assert "SY2–SY5: LULUS" in capsys.readouterr().out
    assert check_seed_gate.main(["--hasil", str(baseline_dir)]) == 2
    assert check_seed_gate.main(["--hasil", str(tmp_path / "tidak-ada")]) == 1


def test_titik_masuk_seed_menolak_folder_storage_kosong(empty_d1, tmp_path: Path,
                                                        monkeypatch: pytest.MonkeyPatch) -> None:
    _use_settings(monkeypatch, empty_d1, tmp_path / "out")
    from evaluation.config import eval_settings

    monkeypatch.setattr(eval_settings, "eval_seed_storage_root", "")

    assert seed_d1.main(["--skala", "kecil"]) == 1
