from datetime import date
from pathlib import Path

from evaluation.baseline.legacy_runner import LegacyCodeRunner
from evaluation.baseline.old_repository import OldDatabaseRepository
from evaluation.baseline.service import BaselineService
from evaluation.db import build_engine, to_safe_url
from evaluation.report import ResultWriter
from evaluation.seed.attachments import AttachmentWriter
from evaluation.seed.gate_check import SeedGateChecker
from evaluation.seed.guards import validate_seed_storage_root, validate_seed_target
from evaluation.seed.repository import SeedTargetRepository
from evaluation.seed.service import SeedService


# Folder storage aplikasi lama (app/utils/file_helper.py) yang tidak boleh disentuh seed
PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_STORAGE_DIRS = [PROJECT_ROOT / "storage", PROJECT_ROOT / "app" / "static" / "storage"]


def build_baseline_service(
    old_db_url: str,
    storage_root: Path,
    output_root: Path,
    run_date: date,
    source: str,
) -> BaselineService:
    """Membuat `BaselineService` dengan satu engine hanya-baca ke database lama.

    Args:
        old_db_url: URL salinan database lama (D1).
        storage_root: Folder `storage/` lama untuk pemeriksaan lampiran.
        output_root: Folder induk hasil evaluasi.
        run_date: Tanggal jalan, menjadi nama folder hasil.
        source: `dummy` atau `nyata`.

    Returns:
        `BaselineService` yang siap dipakai.

    Raises:
        DatabaseAccessError: Kalau URL kosong atau tidak valid.
        ValueError: Kalau `source` bukan `dummy` atau `nyata`.
    """
    engine = build_engine(old_db_url, read_only=True)
    return BaselineService(
        repository=OldDatabaseRepository(engine),
        legacy_runner=LegacyCodeRunner(engine),
        writer=ResultWriter(output_root, run_date, source),
        storage_root=storage_root,
        old_db_label=to_safe_url(old_db_url),
    )



def build_seed_service(
    seed_db_url: str,
    old_db_url: str,
    app_db_url: str,
    seed_storage_root: str,
    output_root: Path,
    run_date: date,
) -> SeedService:
    """Membuat `SeedService` setelah penjaga target dan folder lampiran lulus (003a DS1).

    Args:
        seed_db_url: `EVAL_SEED_DB_URL` (user yang boleh INSERT di D1).
        old_db_url: `EVAL_OLD_DB_URL` (D1 yang dibaca baseline).
        app_db_url: `DATABASE_URL` aplikasi, hanya untuk dibandingkan.
        seed_storage_root: `EVAL_SEED_STORAGE_ROOT`.
        output_root: Folder induk hasil evaluasi.
        run_date: Tanggal jalan, menjadi nama folder hasil.

    Returns:
        `SeedService` yang siap dipakai.

    Raises:
        SeedGuardError: Kalau target bukan D1, sama dengan DB aplikasi, atau folder lampiran tidak sah.
        DatabaseAccessError: Kalau URL tidak valid.
    """
    validate_seed_target(seed_db_url, old_db_url, app_db_url)
    storage_root = validate_seed_storage_root(seed_storage_root, APP_STORAGE_DIRS)
    engine = build_engine(seed_db_url, read_only=False)
    return SeedService(
        engine=engine,
        repository=SeedTargetRepository(engine),
        attachments=AttachmentWriter(storage_root),
        writer=ResultWriter(output_root, run_date, "dummy"),
        target_label=to_safe_url(seed_db_url),
        storage_root=storage_root,
    )


def build_seed_gate_checker(seed_storage_root: str, anomalies: bool, reference_year: int) -> SeedGateChecker:
    """Membuat pemeriksa SY2–SY5 untuk keluaran baseline (Gate 1).

    Args:
        seed_storage_root: `EVAL_SEED_STORAGE_ROOT` yang dipakai saat seed.
        anomalies: Apakah seed dijalankan dengan `--anomali`.
        reference_year: Tahun acuan Y₀ seed.

    Returns:
        `SeedGateChecker` yang siap dipakai.

    Raises:
        SeedGuardError: Kalau folder lampiran kosong atau bersinggungan dengan storage aplikasi.
    """
    return SeedGateChecker(validate_seed_storage_root(seed_storage_root, APP_STORAGE_DIRS), anomalies, reference_year)
