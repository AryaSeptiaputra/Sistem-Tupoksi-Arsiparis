import logging
import os
import sys

from pythonjsonlogger.json import JsonFormatter

from app.core.config import settings

# Logger induk; semua logger modul (`app.routes.auth`, `app.services.backup`, ...)
# meneruskan catatannya ke sini, jadi handler cukup dipasang sekali.
PACKAGE_LOGGER = "app"

# Contoh: 2026-10-18 10:30:00,123 | INFO     | app.services.backup | Backup selesai
# levelname dilebarkan 8 karakter supaya kolom pesan sejajar antar-level
TEXT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

# Field yang sama dengan TEXT_FORMAT, dikeluarkan sebagai JSON satu baris per log
JSON_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def _build_formatter() -> logging.Formatter:
    if settings.LOG_FORMAT == "json":
        return JsonFormatter(JSON_FORMAT)
    return logging.Formatter(TEXT_FORMAT)


def _build_handlers() -> list[logging.Handler]:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if settings.LOG_FILE_PATH:
        os.makedirs(os.path.dirname(settings.LOG_FILE_PATH) or ".", exist_ok=True)
        handlers.append(logging.FileHandler(settings.LOG_FILE_PATH, encoding="utf-8"))
    return handlers


def setup_logger(name: str) -> logging.Logger:
    """Mengambil logger modul dengan format sesuai `LOG_FORMAT`.

    Handler stdout, ditambah file bila `LOG_FILE_PATH` diisi, dipasang sekali
    di logger induk `app`.

    Args:
        name: Nama logger, biasanya `__name__`.

    Returns:
        Logger yang siap dipakai.
    """
    package_logger = logging.getLogger(PACKAGE_LOGGER)
    if not package_logger.handlers:
        formatter = _build_formatter()
        for handler in _build_handlers():
            handler.setFormatter(formatter)
            package_logger.addHandler(handler)
        package_logger.setLevel(logging.INFO)
    return logging.getLogger(name)
