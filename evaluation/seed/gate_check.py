import csv
import json
from collections import Counter
from pathlib import Path

from evaluation.baseline.service import B4_ITEMS
from evaluation.errors import OutputError
from evaluation.logger import setup_logger
from evaluation.report import Row
from evaluation.seed.anomalies import EXPECTED_B4_COUNTS
from evaluation.seed.spec import ARCHIVE_TABLES, CLASSIFIED_TABLES

logger = setup_logger(__name__)

BASELINE_FILES = ("b2_disposal_check", "b3_scheduler_lama", "b4_anomali", "b5_lampiran")
SCHEDULER_TABLES = ("incoming_letter", "outgoing_letter", "finance_archive")


def load_baseline_output(directory: Path) -> tuple[dict[str, list[dict[str, str]]], Row]:
    """Membaca CSV B2–B5 dan `meta.json` hasil `run_baseline` satu putaran.

    Args:
        directory: Folder `outputs/evaluation/<tanggal>/dummy/`.

    Returns:
        Baris CSV per nama berkas dan isi `meta.json`.

    Raises:
        OutputError: Kalau ada berkas yang tidak ada atau tidak bisa dibaca.
    """
    try:
        tables = {}
        for name in BASELINE_FILES:
            with (directory / f"{name}.csv").open(encoding="utf-8", newline="") as handle:
                tables[name] = list(csv.DictReader(handle))
        meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        logger.error(f"Keluaran baseline di {directory} tidak bisa dibaca: {e}", exc_info=True)
        raise OutputError(f"Keluaran baseline di {directory} tidak lengkap atau rusak") from e
    return tables, meta


def to_check(code: str, value: object, target: str, passed: bool) -> Row:
    """Membentuk satu baris hasil pemeriksaan syarat data uji."""
    return {"syarat": code, "nilai": value, "target": target, "lulus": passed}


class SeedGateChecker:
    """Menilai SY2–SY5 dari keluaran `run_baseline` di D1 yang sudah di-seed (Gate 1, rancangan 003)."""

    def __init__(self, seed_storage_root: Path, anomalies: bool, reference_year: int) -> None:
        self._seed_storage_root = seed_storage_root.resolve()
        self._anomalies = anomalies
        self._reference_year = reference_year

    def _check_usage(self, meta: Row) -> list[Row]:
        tanggal_uji = str(meta.get("tanggal_uji", ""))
        storage_root = Path(str(meta.get("storage_root", ""))).resolve()
        return [
            to_check("Syarat pakai: sumber", meta.get("sumber"), "dummy", meta.get("sumber") == "dummy"),
            to_check("Syarat pakai: tahun tanggal_uji", tanggal_uji, f"tahun {self._reference_year}",
                     tanggal_uji[:4] == str(self._reference_year)),
            to_check("Syarat pakai: EVAL_STORAGE_ROOT = folder seed", "sama" if storage_root == self._seed_storage_root
                     else "berbeda", "sama", storage_root == self._seed_storage_root),
        ]

    def _check_sy2(self, rows: list[dict[str, str]]) -> list[Row]:
        candidates = Counter(row["table_source"] for row in rows)
        checks = [to_check(f"SY2 |L| {table}", candidates[table], "> 0", candidates[table] > 0)
                  for table in CLASSIFIED_TABLES]
        checks.append(to_check("SY2 L ijazah", candidates["diploma"], "> 0", candidates["diploma"] > 0))
        return checks

    def _check_sy3(self, rows: list[dict[str, str]]) -> list[Row]:
        changed = Counter(row["tabel"] for row in rows)
        return [to_check(f"SY3 B3 {table}", changed[table], "> 0", changed[table] > 0) for table in SCHEDULER_TABLES]

    def _check_sy4(self, rows: list[dict[str, str]]) -> list[Row]:
        found = Counter(row["butir"] for row in rows)
        expected = EXPECTED_B4_COUNTS if self._anomalies else {item: 0 for item in B4_ITEMS}
        return [to_check(f"SY4 B4 {item}", found[item], str(expected[item]), found[item] == expected[item])
                for item in B4_ITEMS]

    def _check_sy5(self, rows: list[dict[str, str]]) -> list[Row]:
        present = Counter(row["tabel"] for row in rows if row["ada"] == "True")
        missing = Counter(row["tabel"] for row in rows if row["ada"] == "False")
        return [to_check(f"SY5 B5 {table}", f"ada {present[table]}, hilang {missing[table]}", "keduanya > 0",
                         present[table] > 0 and missing[table] > 0) for table in ARCHIVE_TABLES]

    def check(self, baseline_dir: Path) -> list[Row]:
        """Menilai syarat pakai, SY2, SY3, SY4, dan SY5 dari satu folder hasil baseline.

        Args:
            baseline_dir: Folder `outputs/evaluation/<tanggal>/dummy/` dari `run_baseline`.

        Returns:
            Baris `{syarat, nilai, target, lulus}`.

        Raises:
            OutputError: Kalau keluaran baseline tidak lengkap.
        """
        tables, meta = load_baseline_output(baseline_dir)
        checks = self._check_usage(meta)
        checks += self._check_sy2(tables["b2_disposal_check"])
        checks += self._check_sy3(tables["b3_scheduler_lama"])
        checks += self._check_sy4(tables["b4_anomali"])
        checks += self._check_sy5(tables["b5_lampiran"])
        return checks
