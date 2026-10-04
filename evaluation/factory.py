from datetime import date
from pathlib import Path

from evaluation.baseline.legacy_runner import LegacyCodeRunner
from evaluation.baseline.old_repository import OldDatabaseRepository
from evaluation.baseline.service import BaselineService
from evaluation.db import build_engine, to_safe_url
from evaluation.report import ResultWriter


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
