from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import Engine

from evaluation.baseline.old_repository import OLD_TABLES
from evaluation.hashing import hash_table_rows
from evaluation.logger import setup_logger
from evaluation.report import ResultWriter, Row
from evaluation.seed.attachments import AttachmentWriter
from evaluation.seed.guards import validate_plan_columns, validate_target_state
from evaluation.seed.plan import TABLE_ORDER, SeedParams, SeedPlan, build_seed_plan
from evaluation.seed.repository import SeedTargetRepository
from evaluation.seed.summary import BeforeSeed, SeedSummary

logger = setup_logger(__name__)


class SeedService:
    """Mengisi D1 dengan seed data uji Dev-A lalu menilai SY1, SY6, SY8, SY9 (rancangan 003)."""

    def __init__(
        self,
        engine: Engine,
        repository: SeedTargetRepository,
        attachments: AttachmentWriter,
        writer: ResultWriter,
        target_label: str,
        storage_root: Path,
    ) -> None:
        self._engine = engine
        self._repository = repository
        self._attachments = attachments
        self._writer = writer
        self._target_label = target_label
        self._storage_root = storage_root

    def _check_target(self) -> list[Row]:
        references = self._repository.fetch_references()
        validate_target_state(self._repository.count_archive_rows(), self._repository.has_marked_rows(), references)
        return references

    def _capture_before(self) -> BeforeSeed:
        max_ids = self._repository.fetch_max_ids()
        return BeforeSeed(max_ids, self._repository.count_rows(),
                          hash_table_rows(self._engine, list(OLD_TABLES), max_ids))

    def _build_plan(self, params: SeedParams, references: list[Row], before: BeforeSeed) -> SeedPlan:
        plan = build_seed_plan(params, references, before.max_ids)
        validate_plan_columns({name: plan.rows_for(name) for name in TABLE_ORDER},
                              self._repository.fetch_column_names(), self._repository.fetch_column_lengths())
        return plan

    def _save_results(self, params: SeedParams, summary: list[Row], inserted: dict[str, int], files: int,
                      started_at: datetime) -> None:
        self._writer.save_table("seed_ringkasan", summary, {"syarat", "nilai", "target"})
        self._writer.save_meta({
            "skala": params.scale, "anomali": params.anomalies, "seed": params.seed,
            "tahun_acuan": params.reference_year, "db_target": self._target_label,
            "storage_root": str(self._storage_root), "baris_ditambahkan": inserted, "berkas_lampiran": files,
            "mulai": started_at.isoformat(timespec="seconds"), "selesai": datetime.now().isoformat(timespec="seconds"),
        }, name="seed_meta")

    def run(self, params: SeedParams) -> list[Row]:
        """Menjalankan seed: penjaga → keadaan awal → plan → simpan (1 transaksi) → lampiran → ringkasan.

        Args:
            params: Parameter seed.

        Returns:
            Ringkasan SY1, SY6, SY8, SY9 (`{syarat, nilai, target, lulus}`).

        Raises:
            SeedGuardError: Kalau D1 tidak siap atau plan tidak cocok dengan skema; tidak ada yang ditulis.
            DatabaseAccessError: Kalau D1 tidak bisa dibaca, atau insert gagal (sudah di-rollback).
            OutputError: Kalau lampiran atau ringkasan tidak bisa ditulis (D1 sudah terisi; restore lalu ulang).
        """
        started_at = datetime.now()
        references = self._check_target()
        before = self._capture_before()
        plan = self._build_plan(params, references, before)
        logger.info(f"Menulis {len(plan.rows)} baris seed ke {self._target_label}")
        inserted = self._repository.save_plan(plan)
        files = self._attachments.save(plan.files)
        old_hashes_after = hash_table_rows(self._engine, list(OLD_TABLES), before.max_ids)
        summary = SeedSummary(self._repository, params).evaluate(before, inserted, old_hashes_after)
        self._save_results(params, summary, inserted, files, started_at)
        logger.info(f"Seed selesai: {sum(inserted.values())} baris, {files} berkas lampiran")
        return summary
