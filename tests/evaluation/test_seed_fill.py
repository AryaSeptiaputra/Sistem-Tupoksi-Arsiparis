import re
from collections import Counter
from datetime import datetime

import pytest

from evaluation.baseline.rules import (
    APPROVAL_STATUS_DOMAIN,
    ARCHIVE_STATUS_DOMAIN,
    FINAL_ACTION_DOMAIN,
    REFERENCE_COLUMNS,
    is_academic_year_valid,
    is_gender_mappable,
    is_reference_match,
)
from evaluation.seed.anomalies import B4_VALUES, EXPECTED_B4_COUNTS
from evaluation.seed.plan import TABLE_ORDER, SeedParams, SeedPlan, build_seed_plan, to_reference_map
from evaluation.seed.rows import Ref, SeedRow
from evaluation.seed.spec import ARCHIVE_TABLES, DUMMY_CLASSIFICATIONS, PRESETS

Y0 = 2026
REFERENCES = [
    {"id": 1, "category": "school_major", "code": "TKJ", "name": "Teknik Komputer dan Jaringan"},
    {"id": 2, "category": "school_major", "code": "RPL", "name": "Rekayasa Perangkat Lunak"},
    {"id": 3, "category": "teacher_emp_status", "code": "PNS", "name": "Pegawai Negeri Sipil"},
    {"id": 4, "category": "teacher_active_status", "code": "aktif", "name": "Aktif"},
    {"id": 5, "category": "teacher_rank", "code": "III/a", "name": "Penata Muda"},
    {"id": 6, "category": "finance_category", "code": "bos_reguler", "name": "BOS Reguler"},
    {"id": 7, "category": "emp_doc_type", "code": "sk", "name": "Surat Keputusan"},
    {"id": 8, "category": "archive_status", "code": "active", "name": "Aktif"},
]
MAX_IDS = {"user": 1, "teacher": 1, "log": 203}
CLASSIFICATIONS = {item.code: item for item in DUMMY_CLASSIFICATIONS}
FILL_VOLUME = {"incoming_letter": "incoming_per_year", "outgoing_letter": "outgoing_per_year",
               "diploma": "diplomas_per_cohort", "finance_archive": "finance_per_year"}


def count_b4(plan: SeedPlan) -> Counter:
    """Menghitung temuan B4 di plan memakai aturan pembanding yang sama dengan baseline."""
    found: Counter = Counter()
    numbers = Counter(row["number"] for row in plan.rows_for("outgoing_letter"))
    found["nomor_surat_keluar_ganda"] = sum(count for count in numbers.values() if count > 1)
    for table in ("incoming_letter", "outgoing_letter", "finance_archive", "employee_archive"):
        found["status_di_luar_domain"] += sum(row["archive_status"] not in ARCHIVE_STATUS_DOMAIN
                                              for row in plan.rows_for(table))
    found["status_di_luar_domain"] += sum(row["final_action"] not in FINAL_ACTION_DOMAIN
                                          for row in plan.rows_for("classification"))
    found["status_di_luar_domain"] += sum(row["approval_status"] not in APPROVAL_STATUS_DOMAIN
                                          for row in plan.rows_for("outgoing_letter"))
    diplomas = plan.rows_for("diploma")
    found["tahun_ajaran_tidak_berformat"] = sum(not is_academic_year_valid(row["academic_year"]) for row in diplomas)
    found["ijazah_diambil_tanpa_tanggal"] = sum(row["is_collected"] and row["collected_at"] is None for row in diplomas)
    found["gender_tidak_terpetakan"] = sum(not is_gender_mappable(row["gender"]) for row in plan.rows_for("teacher"))
    found["dokumen_pegawai_tanpa_klasifikasi"] = sum(row["classification_id"] is None
                                                     for row in plan.rows_for("employee_archive"))
    references = to_reference_map(REFERENCES)
    for spec in REFERENCE_COLUMNS:
        found["referensi_tidak_cocok"] += sum(
            row[spec.column] is not None and not is_reference_match(row[spec.column], references[spec.category])
            for row in plan.rows_for(spec.table)
        )
    return found


@pytest.fixture(scope="module")
def full_plan() -> SeedPlan:
    return build_seed_plan(SeedParams(scale="penuh"), REFERENCES, MAX_IDS)


@pytest.fixture(scope="module")
def small_plan() -> SeedPlan:
    return build_seed_plan(SeedParams(scale="kecil"), REFERENCES, MAX_IDS)


@pytest.mark.parametrize("scale", ["penuh", "kecil"])
def test_volume_isian_sesuai_preset(scale: str, full_plan: SeedPlan, small_plan: SeedPlan) -> None:
    plan = full_plan if scale == "penuh" else small_plan
    preset = PRESETS[scale]
    fill = Counter(row.table for row in plan.rows if row.tag == "isian")

    for table, attribute in FILL_VOLUME.items():
        assert fill[table] == getattr(preset, attribute) * 11
        assert len(plan.rows_for(table)) > fill[table]
    assert fill["employee_archive"] == preset.employees * preset.documents_per_employee
    assert len([row for row in plan.rows if row.table == "teacher"]) == preset.employees


def test_total_arsip_penuh_dan_kecil(full_plan: SeedPlan, small_plan: SeedPlan) -> None:
    def total(plan: SeedPlan) -> int:
        return sum(len(plan.rows_for(table)) for table in ARCHIVE_TABLES)

    assert 22_000 <= total(full_plan) <= 22_600
    assert 2_200 <= total(small_plan) <= 2_700


def test_sebaran_status_isian(full_plan: SeedPlan) -> None:
    statuses = Counter(row.values["archive_status"] for row in full_plan.rows
                       if row.tag == "isian" and "archive_status" in row.values)
    total = sum(statuses.values())
    shares = {status: count / total for status, count in statuses.items()}

    # Target DS3 60/25/10/5; destroyed lebih rendah karena tahun dokumen terbaru belum lewat masa akhir
    assert 0.58 <= shares["active"] <= 0.64
    assert 0.23 <= shares["inactive"] <= 0.27
    assert 0.07 <= shares["destroyed"] <= 0.10
    assert 0.045 <= shares["permanent"] <= 0.06


def test_klasifikasi_isian_seragam(full_plan: SeedPlan) -> None:
    codes = Counter(row.values["classification_id"] for row in full_plan.rows
                    if row.tag == "isian" and "classification_id" in row.values)
    total = sum(codes.values())

    assert len(codes) == 7
    # Seragam di antara klasifikasi yang sah untuk status terundi; selisih dari 1/7 tetap kecil
    assert all(abs(count / total - 1 / 7) < 0.025 for count in codes.values())


def test_destroyed_dan_permanent_sah(full_plan: SeedPlan) -> None:
    codes_by_id = {row["id"]: row["code"] for row in full_plan.rows_for("classification")}
    for row in full_plan.rows:
        status = row.values.get("archive_status")
        if row.table == "diploma" or status not in ("destroyed", "permanent"):
            continue
        item = CLASSIFICATIONS[codes_by_id[row.values["classification_id"]]]
        year = row.values.get("fiscal_year") or row.values.get("document_year") or (
            row.values["letter_date"].year if "letter_date" in row.values else row.values["created_at"].year)
        if status == "destroyed":
            assert item.final_action == "destroy" and Y0 > year + item.active_years + item.inactive_years
        else:
            assert item.final_action in ("permanent", "assess")


def test_sebaran_kolom_lain(full_plan: SeedPlan) -> None:
    fill = [row.values for row in full_plan.rows if row.tag == "isian"]
    finance = [row for row in fill if "fiscal_year" in row]
    documents = [row for row in fill if "document_name" in row]
    diplomas = [row for row in fill if "academic_year" in row]
    genders = Counter(row["gender"] for row in full_plan.rows_for("teacher"))

    assert 0.15 <= sum(row["period_month"] is None for row in finance) / len(finance) <= 0.25
    assert 0.06 <= sum(row["amount"] is None for row in finance) / len(finance) <= 0.14
    assert all(row["amount"] % 1000 == 0 and 100_000 <= row["amount"] <= 500_000_000
               for row in finance if row["amount"] is not None)
    assert 0.02 <= sum(row["document_year"] is None for row in documents) / len(documents) <= 0.09
    assert 0.67 <= sum(row["is_collected"] for row in diplomas) / len(diplomas) <= 0.73
    assert set(genders) == {"L", "P", "Laki-laki", "Perempuan"}


def test_lampiran_ds5(full_plan: SeedPlan, small_plan: SeedPlan) -> None:
    for plan in (full_plan, small_plan):
        for table in ARCHIVE_TABLES:
            rows = [row for row in plan.rows if row.table == table]
            with_path = [row for row in rows if row.values["attachment_path"]]
            missing = [row for row in with_path if row.meta["attachment_missing"]]
            assert with_path and missing and len(missing) < len(with_path), table
            assert all(row.values["attachment_path"] is None for row in rows
                       if row.values.get("archive_status") == "destroyed")
            assert all(re.fullmatch(rf"storage/documents/[a-z_]+/[0-9a-f]{{32}}\.txt", row.values["attachment_path"])
                       for row in with_path)

    candidates = [row for row in full_plan.rows if row.table in ARCHIVE_TABLES
                  and row.values.get("archive_status") != "destroyed"]
    pathed = [row for row in candidates if row.values["attachment_path"]]
    assert 0.37 <= len(pathed) / len(candidates) <= 0.43
    assert 0.07 <= sum(row.meta["attachment_missing"] for row in pathed) / len(pathed) <= 0.13


def test_berkas_lampiran_hanya_untuk_yang_tidak_hilang(small_plan: SeedPlan) -> None:
    present = [row for row in small_plan.rows if row.values.get("attachment_path")
               and not row.meta["attachment_missing"]]

    assert len(small_plan.files) == len(present)
    first = small_plan.files[0]
    assert first.relative_path.startswith("documents/") and not first.relative_path.startswith("storage/")
    assert re.fullmatch(r"DUMMY lampiran [a-z_]+ \d+\n", first.content)


def test_id_berurutan_setelah_id_lama_dan_fk_terselesaikan(small_plan: SeedPlan) -> None:
    for table in TABLE_ORDER:
        ids = [row["id"] for row in small_plan.rows_for(table)]
        assert ids == list(range(MAX_IDS.get(table, 0) + 1, MAX_IDS.get(table, 0) + 1 + len(ids)))
    plan_ids = {table: {row["id"] for row in small_plan.rows_for(table)} for table in TABLE_ORDER}
    foreign = {"classification_id": "classification", "storage_location_id": "storage_location",
               "owner_id": "teacher", "teacher_id": "teacher"}
    for row in small_plan.rows:
        assert not any(isinstance(value, Ref) for value in row.values.values())
        for column, table in foreign.items():
            if row.values.get(column) is not None:
                assert row.values[column] in plan_ids[table], (row.table, column)


def test_tanpa_anomali_tidak_ada_pola_b4(full_plan: SeedPlan) -> None:
    assert sum(count_b4(full_plan).values()) == 0


def test_tanggal_tidak_melewati_tahun_acuan(full_plan: SeedPlan) -> None:
    for row in full_plan.rows:
        assert all(value.year <= Y0 for value in row.values.values() if hasattr(value, "year"))


def test_plan_deterministik(small_plan: SeedPlan) -> None:
    same = build_seed_plan(SeedParams(scale="kecil"), REFERENCES, MAX_IDS)
    other = build_seed_plan(SeedParams(scale="kecil", seed=7), REFERENCES, MAX_IDS)

    assert [row.values for row in same.rows] == [row.values for row in small_plan.rows]
    assert same.files == small_plan.files
    assert [row.values for row in other.rows] != [row.values for row in small_plan.rows]


def test_preset_tidak_dikenal_ditolak() -> None:
    with pytest.raises(KeyError):
        build_seed_plan(SeedParams(scale="sedang"), REFERENCES, MAX_IDS)


# --- DS6 · anomali B4 (opsi --anomali) ---


@pytest.fixture(scope="module")
def plans() -> tuple[SeedPlan, SeedPlan]:
    return (build_seed_plan(SeedParams(scale="kecil"), REFERENCES, MAX_IDS),
            build_seed_plan(SeedParams(scale="kecil", anomalies=True), REFERENCES, MAX_IDS))


def _anomalies(plan: SeedPlan) -> list[SeedRow]:
    return [row for row in plan.rows if row.tag.startswith("DS6-")]


def test_b4_tepat_sesuai_target_sy4(plans: tuple[SeedPlan, SeedPlan]) -> None:
    without, with_anomalies = plans

    assert sum(count_b4(without).values()) == 0
    assert {item: count for item, count in count_b4(with_anomalies).items() if count} == EXPECTED_B4_COUNTS


def test_sepuluh_baris_anomali_dengan_nilai_ds6(plans: tuple[SeedPlan, SeedPlan]) -> None:
    rows = {row.tag: row.values for row in _anomalies(plans[1])}

    assert len(_anomalies(plans[1])) == 10
    assert rows["DS6-ANOMALI-B4-2A"]["archive_status"] == B4_VALUES["archive_status"]
    assert rows["DS6-ANOMALI-B4-2B"]["final_action"] == B4_VALUES["final_action"]
    assert rows["DS6-ANOMALI-B4-2C"]["approval_status"] == B4_VALUES["approval_status"]
    assert rows["DS6-ANOMALI-B4-3"]["academic_year"] == B4_VALUES["tahun_ajaran"]
    assert rows["DS6-ANOMALI-B4-4"]["gender"] == B4_VALUES["gender"]
    assert rows["DS6-ANOMALI-B4-5"]["category"] == B4_VALUES["kategori_keuangan"]
    duplicates = [row.values for row in _anomalies(plans[1]) if row.tag == "DS6-ANOMALI-B4-1"]
    assert [row["number"] for row in duplicates] == [B4_VALUES["nomor_surat_keluar"]] * 2


def test_induk_dmy_p55_dan_pegawai_seed(plans: tuple[SeedPlan, SeedPlan]) -> None:
    plan = plans[1]
    p55 = next(row["id"] for row in plan.rows_for("classification") if row["code"] == "DMY-P55")
    first_employee = plan.rows_for("teacher")[0]["id"]

    for row in _anomalies(plan):
        if row.values.get("classification_id") is not None and row.table != "classification":
            assert row.values["classification_id"] == p55
    document = next(row.values for row in _anomalies(plan) if row.tag == "DS6-ANOMALI-B4-7")
    assert document["owner_id"] == first_employee and document["classification_id"] is None


def test_penanda_ds7_dengan_tag_anomali(plans: tuple[SeedPlan, SeedPlan]) -> None:
    for row in _anomalies(plans[1]):
        tag = row.tag.removeprefix("DS6-")
        text = " ".join(str(value) for value in row.values.values() if isinstance(value, str))
        assert tag in text
        assert "DUMMY" in text or "Dummy" in text
        assert all(value == datetime(Y0, 7, 1, 8, 0) for column, value in row.values.items()
                   if column in ("created_at", "updated_at", "letter_date"))
    employee = next(row.values for row in _anomalies(plans[1]) if row.tag == "DS6-ANOMALI-B4-4")
    assert employee["identity_number"].startswith("9900") and "Pegawai Dummy" in employee["full_name"]


def test_anomali_tidak_mengubah_baris_lain(plans: tuple[SeedPlan, SeedPlan]) -> None:
    without, with_anomalies = plans
    others = [row.values for row in with_anomalies.rows if not row.tag.startswith("DS6-")]

    assert others == [row.values for row in without.rows]
    assert with_anomalies.files == without.files
