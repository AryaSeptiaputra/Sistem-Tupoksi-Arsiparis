"""Mengukur baseline B1–B6 di salinan database lama (Gate 1 rencana evaluasi).

Jalankan dari root project:
    python -m scripts.evaluation.run_baseline --tanggal-uji 2026-10-04 --sumber dummy
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from evaluation.config import eval_settings
from evaluation.errors import EvaluationError
from evaluation.factory import build_baseline_service
from evaluation.logger import setup_logger
from evaluation.report import SOURCES, format_table

logger = setup_logger(__name__)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Membaca argumen terminal.

    Args:
        argv: Argumen tanpa nama program; `None` berarti `sys.argv`.

    Returns:
        Argumen yang sudah divalidasi argparse.
    """
    parser = argparse.ArgumentParser(description="Baseline B1–B6 di database lama (hanya dibaca).")
    parser.add_argument("--tanggal-uji", type=date.fromisoformat, required=True, help="YYYY-MM-DD")
    parser.add_argument("--sumber", choices=SOURCES, required=True, help="dummy atau nyata")
    parser.add_argument("--ulang", type=int, default=5, help="Pengulangan pengukuran waktu B6 (default 5)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Titik masuk `run_baseline`.

    Args:
        argv: Argumen tanpa nama program; `None` berarti `sys.argv`.

    Returns:
        Kode keluar: 0 berhasil, 1 gagal.
    """
    args = parse_args(argv)
    run_date = date.today()
    output_root = Path(eval_settings.eval_output_dir)
    try:
        service = build_baseline_service(
            old_db_url=eval_settings.eval_old_db_url,
            storage_root=Path(eval_settings.eval_storage_root),
            output_root=output_root,
            run_date=run_date,
            source=args.sumber,
        )
        summary = service.measure(args.tanggal_uji, max(1, args.ulang))
    except EvaluationError as e:
        logger.error(f"Baseline gagal: {e}", exc_info=True)
        return 1
    except Exception as e:
        logger.error(f"Baseline gagal karena error tak terduga: {type(e).__name__}", exc_info=True)
        return 1

    print(format_table(summary))
    print(f"\nHasil tersimpan di {output_root / run_date.isoformat() / args.sumber}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
