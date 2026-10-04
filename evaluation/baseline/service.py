from datetime import date, datetime
from pathlib import Path

from evaluation.baseline.legacy_runner import LegacyCodeRunner
from evaluation.baseline.old_repository import OldDatabaseRepository, has_file
from evaluation.baseline.rules import is_academic_year_valid, is_gender_mappable, strip_storage_prefix
from evaluation.logger import setup_logger
from evaluation.report import ResultWriter, Row

logger = setup_logger(__name__)

# Urutan butir B4 di laporan (002a)
B4_ITEMS = (
    "nomor_surat_keluar_ganda",
    "status_di_luar_domain",
    "tahun_ajaran_tidak_berformat",
    "gender_tidak_terpetakan",
    "referensi_tidak_cocok",
    "ijazah_diambil_tanpa_tanggal",
    "dokumen_pegawai_tanpa_klasifikasi",
)
LEGACY_DIPLOMA_SOURCE = "diploma"


def to_finding(item: str, table_name: str, column_name: str, row: Row, value_key: str | None) -> Row:
    """Membentuk satu baris temuan B4 dengan kolom yang seragam.

    Args:
        item: Nama butir B4.
        table_name: Tabel lama asal baris.
        column_name: Kolom yang bermasalah.
        row: Baris hasil repository; wajib punya `id`.
        value_key: Kunci nilai di `row`, atau `None` kalau nilainya kosong.

    Returns:
        Baris `{butir, tabel, id, kolom, nilai}`.
    """
    return {
        "butir": item,
        "tabel": table_name,
        "id": row["id"],
        "kolom": column_name,
        "nilai": row.get(value_key) if value_key else None,
    }


class BaselineService:
    """Mengukur baseline B1–B6 di database lama dan menyimpan hasilnya (Gate 1)."""

    def __init__(
        self,
        repository: OldDatabaseRepository,
        legacy_runner: LegacyCodeRunner,
        writer: ResultWriter,
        storage_root: Path,
        old_db_label: str,
    ) -> None:
        self._repository = repository
        self._legacy_runner = legacy_runner
        self._writer = writer
        self._storage_root = storage_root
        self._old_db_label = old_db_label

    def _measure_counts(self) -> list[Row]:
        counts = self._repository.count_rows()
        self._writer.save_table("b1_jumlah_tabel", counts, {"tabel"})
        self._writer.save_table("b1_jumlah_status", self._repository.count_by_status(), {"tabel", "archive_status"})
        return [{"bagian": "B1", "ukuran": f"baris {row['tabel']}", "nilai": row["jumlah"]} for row in counts]

    def _collect_findings(self) -> list[Row]:
        findings = [
            to_finding("nomor_surat_keluar_ganda", "outgoing_letter", "number", row, "number")
            for row in self._repository.fetch_duplicate_outgoing_numbers()
        ]
        findings += [
            to_finding("status_di_luar_domain", str(row["tabel"]), str(row["kolom"]), row, "nilai")
            for row in self._repository.fetch_out_of_domain_statuses()
        ]
        findings += [
            to_finding("tahun_ajaran_tidak_berformat", "diploma", "academic_year", row, "academic_year")
            for row in self._repository.fetch_academic_years()
            if not is_academic_year_valid(row["academic_year"])
        ]
        findings += [
            to_finding("gender_tidak_terpetakan", "teacher", "gender", row, "gender")
            for row in self._repository.fetch_gender_values()
            if not is_gender_mappable(row["gender"])
        ]
        findings += [
            {**to_finding("referensi_tidak_cocok", str(row["tabel"]), str(row["kolom"]), row, "nilai"),
             "kategori": row["kategori"]}
            for row in self._repository.fetch_unmatched_references()
        ]
        findings += [
            to_finding("ijazah_diambil_tanpa_tanggal", "diploma", "collected_at", row, None)
            for row in self._repository.fetch_collected_without_date()
        ]
        findings += [
            to_finding("dokumen_pegawai_tanpa_klasifikasi", "employee_archive", "classification_id", row, None)
            for row in self._repository.fetch_employee_docs_without_classification()
        ]
        return findings

    def _measure_anomalies(self) -> list[Row]:
        findings = self._collect_findings()
        self._writer.save_table("b4_anomali", findings, {"butir", "tabel", "kolom", "kategori"})
        return [
            {"bagian": "B4", "ukuran": item, "nilai": sum(1 for row in findings if row["butir"] == item)}
            for item in B4_ITEMS
        ]

    def _measure_attachments(self) -> list[Row]:
        rows = []
        for row in self._repository.fetch_attachment_paths():
            new_path = strip_storage_prefix(str(row["path"]))
            rows.append({**row, "path_baru": new_path, "ada": has_file(self._storage_root, new_path)})
        self._writer.save_table("b5_lampiran", rows, {"tabel"})
        present = sum(1 for row in rows if row["ada"])
        return [
            {"bagian": "B5", "ukuran": "lampiran ada", "nilai": present},
            {"bagian": "B5", "ukuran": "lampiran hilang", "nilai": len(rows) - present},
        ]

    def _measure_legacy(self, tanggal_uji: date, repeat: int) -> list[Row]:
        expired = [
            {**row, "masuk_l": row.get("table_source") != LEGACY_DIPLOMA_SOURCE}
            for row in self._legacy_runner.run_disposal_check(tanggal_uji)
        ]
        self._writer.save_table("b2_disposal_check", expired, {"type", "table_source"})
        scheduler_changes = self._legacy_runner.preview_scheduler(tanggal_uji)
        self._writer.save_table("b3_scheduler_lama", scheduler_changes, {"tabel", "status_lama", "status_baru"})
        timings = self._legacy_runner.time_calls(tanggal_uji, repeat)
        self._writer.save_table("b6_waktu", timings, {"modul", "fungsi"})

        candidates = sum(1 for row in expired if row["masuk_l"])
        return [
            {"bagian": "B2", "ukuran": "|L| (tanpa ijazah)", "nilai": candidates},
            {"bagian": "B2", "ukuran": "kandidat ijazah lama", "nilai": len(expired) - candidates},
            {"bagian": "B3", "ukuran": "akan diubah scheduler lama", "nilai": len(scheduler_changes)},
            *({"bagian": "B6", "ukuran": f"median ms {row['modul']}", "nilai": row["median_ms"]} for row in timings),
        ]

    def measure(self, tanggal_uji: date, repeat: int) -> list[Row]:
        """Mengukur B1–B6 lalu menyimpan semua tabel, ringkasan, dan `meta.json`.

        Args:
            tanggal_uji: Tanggal yang dipakai sebagai "hari ini" untuk B2, B3, dan B6.
            repeat: Jumlah pengulangan pengukuran waktu B6.

        Returns:
            Ringkasan angka `{bagian, ukuran, nilai}`.

        Raises:
            DatabaseAccessError: Kalau database lama tidak bisa dibaca.
            LegacyCodeError: Kalau kode lama gagal dijalankan.
            OutputError: Kalau hasil tidak bisa disimpan.
        """
        started_at = datetime.now()
        logger.info(f"Mengukur baseline pada tanggal_uji {tanggal_uji.isoformat()}")
        summary = self._measure_counts()
        summary += self._measure_anomalies()
        summary += self._measure_attachments()
        summary += self._measure_legacy(tanggal_uji, repeat)
        self._writer.save_table("ringkasan", summary, {"bagian", "ukuran"})
        self._writer.save_meta({
            "tanggal_uji": tanggal_uji,
            "db_lama": self._old_db_label,
            "storage_root": str(self._storage_root),
            "ulang_b6": repeat,
            "mulai": started_at.isoformat(timespec="seconds"),
            "selesai": datetime.now().isoformat(timespec="seconds"),
        })
        logger.info(f"Baseline tersimpan di {self._writer.directory}")
        return summary
