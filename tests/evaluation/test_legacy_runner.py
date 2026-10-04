from datetime import date

import pytest
from sqlalchemy import create_engine, text

from evaluation.baseline.legacy_runner import LegacyCodeRunner
from evaluation.db import build_engine
from evaluation.errors import LegacyCodeError


@pytest.fixture
def runner(old_db) -> LegacyCodeRunner:
    return LegacyCodeRunner(build_engine(old_db.url, read_only=True))


@pytest.fixture(autouse=True)
def create_app_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    import app

    def fail_create_app() -> None:
        raise AssertionError("create_app() tidak boleh dipanggil oleh alat evaluasi")

    monkeypatch.setattr(app, "create_app", fail_create_app)


def _keys(rows: list[dict]) -> set[tuple[str, int]]:
    return {(row["table_source"], row["id"]) for row in rows}


def test_b2_mengikuti_rumus_lama_pada_tanggal_2026(runner: LegacyCodeRunner) -> None:
    rows = runner.run_disposal_check(date(2026, 10, 4))

    assert _keys(rows) == {
        ("incoming_letter", 1), ("incoming_letter", 3), ("outgoing_letter", 1),
        ("finance_archive", 1), ("employee_archive", 1), ("diploma", 1), ("diploma", 3),
    }


def test_b2_berubah_mengikuti_tanggal_uji(runner: LegacyCodeRunner) -> None:
    # 2015 + (1 + 1) = 2017; kode lama memakai "tahun ini > tahun kedaluwarsa", jadi 2017 belum masuk
    assert runner.run_disposal_check(date(2017, 6, 1)) == []
    assert _keys(runner.run_disposal_check(date(2018, 1, 1))) == {
        ("incoming_letter", 1), ("incoming_letter", 3), ("outgoing_letter", 1),
        ("finance_archive", 1), ("employee_archive", 1),
    }


def test_b3_mencatat_perubahan_tanpa_menulis(runner: LegacyCodeRunner, old_db) -> None:
    def statuses() -> list[tuple]:
        engine = create_engine(old_db.url)
        with engine.connect() as conn:
            rows = conn.execute(text(
                "SELECT 'incoming_letter', id, archive_status FROM incoming_letter "
                "UNION ALL SELECT 'outgoing_letter', id, archive_status FROM outgoing_letter "
                "UNION ALL SELECT 'finance_archive', id, archive_status FROM finance_archive ORDER BY 1, 2"
            )).all()
        engine.dispose()
        return [tuple(row) for row in rows]

    before = statuses()
    changes = runner.preview_scheduler(date(2026, 10, 4))

    assert {(row["tabel"], row["id"]) for row in changes} == {
        ("finance_archive", 1), ("finance_archive", 2), ("incoming_letter", 1), ("incoming_letter", 2),
        ("outgoing_letter", 1), ("outgoing_letter", 2),
    }
    assert all(row["status_lama"] == "active" and row["status_baru"] == "inactive" for row in changes)
    assert statuses() == before


def test_b3_mengikuti_tanggal_uji(runner: LegacyCodeRunner) -> None:
    changes = runner.preview_scheduler(date(2017, 6, 1))

    assert {(row["tabel"], row["id"]) for row in changes} == {
        ("finance_archive", 1), ("incoming_letter", 1), ("outgoing_letter", 1),
    }


def test_b3_error_yang_ditelan_kode_lama_menjadi_error(old_db) -> None:
    runner = LegacyCodeRunner(create_engine("sqlite:///" + str(old_db.storage_root / "tidak_ada" / "x.db")))

    with pytest.raises(LegacyCodeError):
        runner.preview_scheduler(date(2026, 10, 4))


def test_b6_mengukur_semua_modul(runner: LegacyCodeRunner) -> None:
    rows = runner.time_calls(date(2026, 10, 4), repeat=2)

    counts = {row["modul"]: row["jumlah_baris"] for row in rows}
    assert counts == {
        "disposal": 7, "incoming_letter": 3, "outgoing_letter": 2, "diploma": 3, "finance_archive": 2,
        "employee_archive": 2, "classification": 3, "storage_location": 1, "teacher": 2, "user": 2, "log": 1,
    }
    assert all(row["min_ms"] <= row["median_ms"] for row in rows)


def test_waktu_modul_lama_dipulihkan_setelah_jalan(runner: LegacyCodeRunner) -> None:
    from datetime import datetime

    import app.services.disposal as disposal

    runner.run_disposal_check(date(2017, 6, 1))

    assert disposal.datetime is datetime
