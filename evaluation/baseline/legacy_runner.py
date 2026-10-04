import contextlib
import importlib
import io
import os
import statistics
import sys
import time as timer
from collections.abc import Callable, Iterator
from datetime import date, datetime, time
from types import ModuleType

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from evaluation.errors import LegacyCodeError
from evaluation.logger import setup_logger
from evaluation.report import Row

logger = setup_logger(__name__)

# Jam yang dipakai saat waktu kode lama dipatok: sama dengan jadwal scheduler lama 00:01
LEGACY_RUN_TIME = time(0, 1)

# Nilai pengisi agar `Settings()` lama bisa dibuat; alat evaluasi tidak memakai JWT
JWT_PLACEHOLDER = "evaluasi-tidak-memakai-jwt"

# Pesan yang dicetak scheduler lama saat ia menelan exception
LEGACY_SCHEDULER_ERROR_MARK = "ERROR pada Retention Scheduler"

# (modul, nama modul service lama, fungsi get_all) untuk B6
LEGACY_GET_ALL = (
    ("incoming_letter", "app.services.incoming_letter", "get_all_incoming_letters"),
    ("outgoing_letter", "app.services.outgoing_letter", "get_all_outgoing_letters"),
    ("diploma", "app.services.diploma", "get_all_diplomas"),
    ("finance_archive", "app.services.finance_archive", "get_all_finance_archives"),
    ("employee_archive", "app.services.employee_archive", "get_all_employee_archives"),
    ("classification", "app.services.classification", "get_all_classifications"),
    ("storage_location", "app.services.storage_location", "get_all_storage_locations"),
    ("teacher", "app.services.teacher", "get_all_teachers"),
    ("user", "app.services.user", "get_all_users"),
    ("log", "app.services.log", "get_all_logs"),
)


def build_frozen_datetime(moment: datetime) -> type[datetime]:
    """Membuat pengganti class `datetime` yang `now()`-nya selalu `moment`.

    Args:
        moment: Waktu yang dipatok.

    Returns:
        Subclass `datetime` untuk dipasang di modul lama.
    """

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz: object = None) -> datetime:
            return moment

    return FrozenDatetime


@contextlib.contextmanager
def replace_attribute(module: ModuleType, name: str, value: object) -> Iterator[None]:
    """Mengganti atribut modul sementara, lalu mengembalikannya.

    Args:
        module: Modul yang atributnya diganti.
        name: Nama atribut.
        value: Nilai pengganti.

    Yields:
        Tidak ada; atribut asli dipulihkan saat keluar.
    """
    original = getattr(module, name)
    setattr(module, name, value)
    try:
        yield
    finally:
        setattr(module, name, original)


class _RecordingSession(Session):
    """Session yang mencatat perubahan saat `commit()` lalu membatalkannya."""

    def __init__(self, *args: object, recorder: list[Row], **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._recorder = recorder

    def commit(self) -> None:
        for obj in self.dirty:
            history = inspect(obj).attrs.archive_status.history
            self._recorder.append({
                "tabel": obj.__tablename__,
                "id": obj.id,
                "status_lama": history.deleted[0] if history.deleted else None,
                "status_baru": obj.archive_status,
            })
        self.rollback()


class LegacyCodeRunner:
    """Menjalankan fungsi aplikasi lama apa adanya terhadap salinan database lama (D1)."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def _import_legacy(self, module_name: str) -> ModuleType:
        if "app" not in sys.modules:
            # `app/__init__.py` membuat `Settings()` dari environment; diarahkan ke D1, bukan `.env`
            os.environ["DATABASE_URL"] = self._engine.url.render_as_string(hide_password=False)
            os.environ.setdefault("JWT_SECRET_KEY", JWT_PLACEHOLDER)
        try:
            return importlib.import_module(module_name)
        except (ImportError, ValueError) as e:
            logger.error(f"Gagal meng-import kode lama {module_name}: {type(e).__name__}", exc_info=True)
            raise LegacyCodeError(f"Kode lama {module_name} tidak bisa di-import") from e

    def _frozen_at(self, tanggal_uji: date) -> type[datetime]:
        return build_frozen_datetime(datetime.combine(tanggal_uji, LEGACY_RUN_TIME))

    def run_disposal_check(self, tanggal_uji: date) -> list[Row]:
        """Menjalankan `get_expired_archives` lama pada `tanggal_uji` (B2).

        Args:
            tanggal_uji: Tanggal yang dipatok sebagai "hari ini" untuk kode lama.

        Returns:
            Baris hasil `/disposal/check` lama apa adanya, termasuk ijazah.

        Raises:
            LegacyCodeError: Kalau kode lama gagal di-import atau gagal dijalankan.
        """
        disposal = self._import_legacy("app.services.disposal")
        try:
            with Session(self._engine) as session, replace_attribute(
                disposal, "datetime", self._frozen_at(tanggal_uji)
            ):
                return list(disposal.get_expired_archives(session))
        except SQLAlchemyError as e:
            logger.error(f"get_expired_archives lama gagal: {type(e).__name__}", exc_info=True)
            raise LegacyCodeError("get_expired_archives lama gagal dijalankan") from e

    def preview_scheduler(self, tanggal_uji: date) -> list[Row]:
        """Mencatat arsip yang akan diubah scheduler lama pada `tanggal_uji`, tanpa menulis (B3).

        `SessionLocal` modul lama diganti session yang `commit()`-nya hanya mencatat
        perubahan lalu rollback; koneksi juga hanya-baca.

        Args:
            tanggal_uji: Tanggal yang dipatok sebagai "hari ini" untuk kode lama.

        Returns:
            Baris `{tabel, id, status_lama, status_baru}`.

        Raises:
            LegacyCodeError: Kalau kode lama gagal di-import atau mencetak error.
        """
        scheduler = self._import_legacy("app.services.retention_scheduler")
        records: list[Row] = []
        recording_factory = sessionmaker(
            bind=self._engine, class_=_RecordingSession, autoflush=False, recorder=records
        )
        printed = io.StringIO()
        with replace_attribute(scheduler, "SessionLocal", recording_factory), replace_attribute(
            scheduler, "datetime", self._frozen_at(tanggal_uji)
        ), contextlib.redirect_stdout(printed):
            scheduler.check_and_deactivate_archives()

        output = printed.getvalue()
        logger.debug(f"Keluaran scheduler lama: {output.strip()}")
        if LEGACY_SCHEDULER_ERROR_MARK in output:
            raise LegacyCodeError("Scheduler lama menelan error; lihat log DEBUG untuk keluarannya")
        return sorted(records, key=lambda row: (str(row["tabel"]), int(row["id"])))

    def _build_timing_targets(self, disposal: ModuleType) -> list[tuple[str, str, Callable[[Session], int]]]:
        def count_expired(session: Session) -> int:
            return len(disposal.get_expired_archives(session))

        targets: list[tuple[str, str, Callable[[Session], int]]] = [
            ("disposal", "get_expired_archives", count_expired)
        ]
        for module_label, module_name, function_name in LEGACY_GET_ALL:
            get_all = getattr(self._import_legacy(module_name), function_name)

            def count_as_dicts(session: Session, fn: Callable[..., list[object]] = get_all) -> int:
                return len([item.to_dict() for item in fn(session, None)])

            targets.append((module_label, function_name, count_as_dicts))
        return targets

    def _measure(self, call: Callable[[Session], int], repeat: int) -> tuple[float, float, int]:
        durations: list[float] = []
        count = 0
        for _ in range(repeat):
            with Session(self._engine) as session:
                start = timer.perf_counter()
                count = call(session)
                durations.append((timer.perf_counter() - start) * 1000)
        return round(statistics.median(durations), 2), round(min(durations), 2), count

    def time_calls(self, tanggal_uji: date, repeat: int) -> list[Row]:
        """Mengukur waktu `/disposal/check` lama dan get_all per modul (B6, informasi).

        Fungsi service lama dipanggil tanpa pagination, lalu `to_dict()` per baris seperti route.
        Setiap pengulangan memakai session baru supaya tidak ada cache identity map.

        Args:
            tanggal_uji: Tanggal yang dipatok untuk `/disposal/check`.
            repeat: Jumlah pengulangan per fungsi; median dan minimum dilaporkan.

        Returns:
            Baris `{modul, fungsi, median_ms, min_ms, jumlah_baris}`.

        Raises:
            LegacyCodeError: Kalau kode lama gagal di-import atau gagal dijalankan.
        """
        disposal = self._import_legacy("app.services.disposal")
        targets = self._build_timing_targets(disposal)
        rows: list[Row] = []
        try:
            with replace_attribute(disposal, "datetime", self._frozen_at(tanggal_uji)):
                for module_label, function_name, call in targets:
                    median_ms, min_ms, count = self._measure(call, repeat)
                    rows.append({"modul": module_label, "fungsi": function_name, "median_ms": median_ms,
                                 "min_ms": min_ms, "jumlah_baris": count})
        except SQLAlchemyError as e:
            logger.error(f"Pengukuran waktu kode lama gagal: {type(e).__name__}", exc_info=True)
            raise LegacyCodeError("Pengukuran waktu kode lama gagal") from e
        return rows
