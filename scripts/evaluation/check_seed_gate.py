"""Memeriksa SY2–SY5 dari keluaran run_baseline di D1 yang sudah di-seed (Gate 1, rancangan 003).

Jalankan dari root project setelah run_baseline:
    python -m scripts.evaluation.check_seed_gate --hasil outputs/evaluation/2026-10-06/dummy --anomali

Kode keluar: 0 semua lulus, 2 ada syarat gagal, 1 error.
"""

import argparse
import sys
from pathlib import Path

from evaluation.config import eval_settings
from evaluation.errors import EvaluationError
from evaluation.factory import build_seed_gate_checker
from evaluation.logger import setup_logger
from evaluation.report import format_table
from evaluation.seed.spec import DEFAULT_REFERENCE_YEAR

logger = setup_logger(__name__)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Membaca argumen terminal.

    Args:
        argv: Argumen tanpa nama program; `None` berarti `sys.argv`.

    Returns:
        Argumen yang sudah divalidasi argparse.
    """
    parser = argparse.ArgumentParser(description="Pemeriksa SY2–SY5 untuk Gate 1.")
    parser.add_argument("--hasil", type=Path, required=True, help="Folder outputs/evaluation/<tanggal>/dummy")
    parser.add_argument("--anomali", action="store_true", help="Seed dijalankan dengan --anomali")
    parser.add_argument("--tahun-acuan", type=int, default=DEFAULT_REFERENCE_YEAR,
                        help=f"Y₀ seed, default {DEFAULT_REFERENCE_YEAR}")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Titik masuk `check_seed_gate`.

    Args:
        argv: Argumen tanpa nama program; `None` berarti `sys.argv`.

    Returns:
        Kode keluar: 0 lulus, 2 ada syarat gagal, 1 error.
    """
    args = parse_args(argv)
    try:
        checker = build_seed_gate_checker(eval_settings.eval_seed_storage_root, args.anomali, args.tahun_acuan)
        checks = checker.check(args.hasil)
    except EvaluationError as e:
        logger.error(f"Pemeriksaan gagal: {e}", exc_info=True)
        return 1
    except Exception as e:
        logger.error(f"Pemeriksaan gagal karena error tak terduga: {type(e).__name__}", exc_info=True)
        return 1

    print(format_table(checks))
    passed = all(row["lulus"] for row in checks)
    print("\nSY2–SY5: LULUS" if passed else "\nSY2–SY5: GAGAL (baseline belum sah untuk Gate 1)")
    return 0 if passed else 2


if __name__ == "__main__":
    sys.exit(main())
