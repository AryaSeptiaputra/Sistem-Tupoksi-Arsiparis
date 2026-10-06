"""Mengisi salinan D1 dengan seed data uji Dev-A (rancangan 003, DS1–DS7).

Jalankan dari root project, hanya ke D1 yang baru di-restore:
    python -m scripts.evaluation.seed_d1 --skala penuh --anomali

Kode keluar: 0 semua syarat ringkasan lulus, 2 ada syarat gagal, 1 error (tidak ada yang ditulis,
kecuali error lampiran setelah commit: restore D1 dan kosongkan folder lampiran, lalu ulang).
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from evaluation.config import eval_settings
from evaluation.errors import EvaluationError
from evaluation.factory import build_seed_service
from evaluation.logger import setup_logger
from evaluation.report import format_table
from evaluation.seed.plan import SeedParams
from evaluation.seed.spec import DEFAULT_REFERENCE_YEAR, DEFAULT_SEED, PRESETS

logger = setup_logger(__name__)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Membaca argumen terminal.

    Args:
        argv: Argumen tanpa nama program; `None` berarti `sys.argv`.

    Returns:
        Argumen yang sudah divalidasi argparse.
    """
    parser = argparse.ArgumentParser(description="Seed data uji Dev-A ke D1 (hanya menambah baris).")
    parser.add_argument("--skala", choices=sorted(PRESETS), required=True, help="penuh untuk Gate 1")
    parser.add_argument("--anomali", action="store_true", help="Tambah baris anomali B4 (DS6)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help=f"default {DEFAULT_SEED}")
    parser.add_argument("--tahun-acuan", type=int, default=DEFAULT_REFERENCE_YEAR,
                        help=f"Y₀, default {DEFAULT_REFERENCE_YEAR}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Titik masuk `seed_d1`.

    Args:
        argv: Argumen tanpa nama program; `None` berarti `sys.argv`.

    Returns:
        Kode keluar: 0 lulus, 2 ada syarat gagal, 1 error.
    """
    args = parse_args(argv)
    params = SeedParams(scale=args.skala, anomalies=args.anomali, seed=args.seed, reference_year=args.tahun_acuan)
    run_date = date.today()
    try:
        service = build_seed_service(
            seed_db_url=eval_settings.eval_seed_db_url,
            old_db_url=eval_settings.eval_old_db_url,
            app_db_url=eval_settings.database_url,
            seed_storage_root=eval_settings.eval_seed_storage_root,
            output_root=Path(eval_settings.eval_output_dir),
            run_date=run_date,
        )
        summary = service.run(params)
    except EvaluationError as e:
        logger.error(f"Seed gagal: {e}", exc_info=True)
        return 1
    except Exception as e:
        logger.error(f"Seed gagal karena error tak terduga: {type(e).__name__}", exc_info=True)
        return 1

    print(format_table(summary))
    print(f"\nRingkasan tersimpan di {Path(eval_settings.eval_output_dir) / run_date.isoformat() / 'dummy'}")
    print(f"Sebelum run_baseline: EVAL_STORAGE_ROOT={eval_settings.eval_seed_storage_root}; "
          f"tanggal_uji harus di tahun {params.reference_year}.")
    return 0 if all(row["lulus"] for row in summary) else 2


if __name__ == "__main__":
    sys.exit(main())
