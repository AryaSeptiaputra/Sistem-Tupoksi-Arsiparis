from pathlib import Path

import pytest
from sqlalchemy import text

from evaluation.baseline.old_repository import OLD_TABLES
from evaluation.db import build_engine
from evaluation.errors import DatabaseAccessError, OutputError, SeedGuardError
from evaluation.hashing import hash_table_rows
from evaluation.seed.attachments import AttachmentWriter
from evaluation.seed.guards import validate_plan_columns, validate_target_state
from evaluation.seed.plan import TABLE_ORDER, AttachmentFile, SeedParams, SeedPlan, build_seed_plan
from evaluation.seed.repository import SeedTargetRepository
from evaluation.seed.summary import BeforeSeed, SeedSummary


def _prepare(d1, params: SeedParams) -> tuple[SeedTargetRepository, BeforeSeed, SeedPlan]:
    engine = build_engine(d1.url, read_only=False)
    repository = SeedTargetRepository(engine)
    validate_target_state(repository.count_archive_rows(), repository.has_marked_rows(), repository.fetch_references())
    max_ids = repository.fetch_max_ids()
    before = BeforeSeed(max_ids, repository.count_rows(), hash_table_rows(engine, list(OLD_TABLES), max_ids))
    plan = build_seed_plan(params, repository.fetch_references(), max_ids)
    validate_plan_columns({name: plan.rows_for(name) for name in TABLE_ORDER},
                          repository.fetch_column_names(), repository.fetch_column_lengths())
    return repository, before, plan


def _seed(d1, params: SeedParams) -> tuple[list[dict], SeedPlan, int]:
    repository, before, plan = _prepare(d1, params)
    inserted = repository.save_plan(plan)
    written = AttachmentWriter(d1.storage_root).save(plan.files)
    engine = build_engine(d1.url, read_only=True)
    after = hash_table_rows(engine, list(OLD_TABLES), before.max_ids)
    return SeedSummary(SeedTargetRepository(engine), params).evaluate(before, inserted, after), plan, written


def _failed(summary: list[dict]) -> list[dict]:
    return [row for row in summary if not row["lulus"]]


@pytest.mark.parametrize("anomalies", [False, True])
def test_seed_kecil_lulus_sy1_sy6_sy8_sy9(empty_d1, anomalies: bool) -> None:
    summary, plan, written = _seed(empty_d1, SeedParams(scale="kecil", anomalies=anomalies))

    assert _failed(summary) == []
    assert {row["syarat"].split()[0] for row in summary} == {"SY1", "SY6", "SY8", "SY9"}
    assert written == len(plan.files) > 0


def test_berkas_lampiran_ditulis_di_folder_seed(empty_d1) -> None:
    _, plan, _ = _seed(empty_d1, SeedParams(scale="kecil"))

    first = plan.files[0]
    assert (empty_d1.storage_root / first.relative_path).read_text(encoding="utf-8") == first.content
    assert len(list(empty_d1.storage_root.rglob("*.txt"))) == len(plan.files)


def test_jalan_kedua_ditolak_penjaga(empty_d1) -> None:
    _seed(empty_d1, SeedParams(scale="kecil"))

    with pytest.raises(SeedGuardError, match="berpenanda|berisi"):
        _prepare(empty_d1, SeedParams(scale="kecil"))


def test_gagal_di_tengah_tidak_meninggalkan_baris_maupun_berkas(empty_d1) -> None:
    repository, before, plan = _prepare(empty_d1, SeedParams(scale="kecil"))
    diplomas = [row for row in plan.rows if row.table == "diploma"]
    diplomas[-1].values["number"] = diplomas[0].values["number"]

    with pytest.raises(DatabaseAccessError, match="di-rollback"):
        repository.save_plan(plan)

    assert repository.count_rows() == before.row_counts
    assert not empty_d1.storage_root.exists()


def test_sy8_mendeteksi_baris_lama_yang_berubah(empty_d1) -> None:
    repository, before, plan = _prepare(empty_d1, SeedParams(scale="kecil"))
    inserted = repository.save_plan(plan)
    engine = build_engine(empty_d1.url, read_only=False)
    with engine.begin() as conn:
        conn.execute(text("UPDATE teacher SET full_name = 'Diubah' WHERE id = 1"))

    after = hash_table_rows(engine, list(OLD_TABLES), before.max_ids)
    summary = SeedSummary(repository, SeedParams(scale="kecil")).evaluate(before, inserted, after)

    assert [row["syarat"] for row in _failed(summary)] == ["SY8 hash baris lama"]


def test_sy6_mendeteksi_baris_batas_yang_hilang(empty_d1) -> None:
    repository, before, plan = _prepare(empty_d1, SeedParams(scale="kecil"))
    inserted = repository.save_plan(plan)
    engine = build_engine(empty_d1.url, read_only=False)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM finance_archive WHERE fiscal_year = 2023 AND archive_status = 'inactive' "
                          "AND classification_id = (SELECT id FROM classification WHERE code = 'DMY-D11')"))

    after = hash_table_rows(engine, list(OLD_TABLES), before.max_ids)
    summary = SeedSummary(repository, SeedParams(scale="kecil")).evaluate(before, inserted, after)

    sy6 = next(row for row in summary if row["syarat"].startswith("SY6"))
    assert sy6["lulus"] is False and sy6["nilai"] == "27/28"


def test_plan_ditolak_kalau_tidak_muat_di_kolom_d1() -> None:
    rows = {"teacher": [{"id": 9, "full_name": "x" * 200, "alamat_baru": "y"}]}

    with pytest.raises(SeedGuardError) as error:
        validate_plan_columns(rows, {"teacher": {"id", "full_name"}}, {("teacher", "full_name"): 150})

    message = str(error.value)
    assert "teacher.alamat_baru tidak ada" in message and "butuh 200 karakter" in message
    assert "xxxx" not in message


def test_lampiran_tidak_boleh_keluar_dari_folder_seed(tmp_path: Path) -> None:
    writer = AttachmentWriter(tmp_path / "storage_d1")

    with pytest.raises(OutputError):
        writer.save([AttachmentFile("../luar.txt", "x")])
    assert not (tmp_path / "luar.txt").exists()
