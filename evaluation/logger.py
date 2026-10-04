import logging
import sys

# Contoh: 2026-10-04 10:30:00,123 | INFO     | evaluation.baseline.service | Mengukur B1
# levelname dilebarkan 8 karakter supaya kolom pesan sejajar antar-level
TEXT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logger(name: str) -> logging.Logger:
    """Membuat logger berformat teks untuk alat evaluasi.

    Args:
        name: Nama logger, biasanya `__name__`.

    Returns:
        Logger yang siap dipakai.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(TEXT_FORMAT))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
