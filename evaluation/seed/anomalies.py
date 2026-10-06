from datetime import date

from evaluation.seed.rows import RowFactory, SeedRow, to_datetime
from evaluation.seed.spec import format_text

# Nilai pelanggar B4, sama dengan scripts/evaluation/b4_anomali_dev_a.sql (003a DS6); diisi agent atas permintaan Arya
B4_VALUES = {
    "nomor_surat_keluar": "ANOMALI-421.2/045/SMKN7/2026",
    "archive_status": "Aktif",
    "final_action": "Musnah",
    "approval_status": "Disetujui",
    "tahun_ajaran": "2019/20",
    "gender": "Pria",
    "kategori_keuangan": "ANOMALI-Dana BOSS",
}
# Induk baris anomali: klasifikasi seed permanent (tidak masuk L atau B3) dan pegawai seed nomor 1
PARENT_CLASSIFICATION = "DMY-P55"
PARENT_EMPLOYEE = 1
ANOMALY_CLASSIFICATION_CODE = "DMY-ANM2B"
# Hasil run_baseline yang diharapkan per butir B4 dengan --anomali (jawaban Arya 2026-10-06)
EXPECTED_B4_COUNTS = {
    "nomor_surat_keluar_ganda": 2,
    "status_di_luar_domain": 3,
    "tahun_ajaran_tidak_berformat": 1,
    "gender_tidak_terpetakan": 1,
    "referensi_tidak_cocok": 1,
    "ijazah_diambil_tanpa_tanggal": 1,
    "dokumen_pegawai_tanpa_klasifikasi": 1,
}


def _tagged(row: SeedRow, tag: str, column: str, label: str) -> SeedRow:
    row.tag = f"DS6-{tag}"
    row.values[column] = format_text(f"{tag} {label}")
    return row


def _build_letters(factory: RowFactory, day: date) -> list[SeedRow]:
    duplicates = []
    for part in (1, 2):
        row = factory.build_outgoing_row(day, day, PARENT_CLASSIFICATION, "active", "")
        row.values.update({"number": B4_VALUES["nomor_surat_keluar"], "approval_status": "pending"})
        duplicates.append(_tagged(row, "ANOMALI-B4-1", "subject", f"nomor ganda ({part} dari 2)"))
    incoming = factory.build_incoming_row(day, day, PARENT_CLASSIFICATION, B4_VALUES["archive_status"], "")
    approval = factory.build_outgoing_row(day, day, PARENT_CLASSIFICATION, "active", "")
    approval.values["approval_status"] = B4_VALUES["approval_status"]
    return duplicates + [
        _tagged(incoming, "ANOMALI-B4-2A", "subject", "archive_status di luar domain"),
        _tagged(approval, "ANOMALI-B4-2C", "subject", "approval_status di luar domain"),
    ]


def _build_classification(day: date) -> SeedRow:
    stamp = to_datetime(day)
    return SeedRow("classification", {
        "code": ANOMALY_CLASSIFICATION_CODE, "name": format_text("ANOMALI-B4-2B final_action"),
        "description": format_text("baris anomali B4-2B"), "retention_active_period": 1,
        "retention_inactive_period": 1, "final_action": B4_VALUES["final_action"],
        "created_at": stamp, "updated_at": stamp,
    }, tag="DS6-ANOMALI-B4-2B", key=ANOMALY_CLASSIFICATION_CODE)


def _build_people_and_records(factory: RowFactory, day: date, reference_year: int, employee_number: int) -> list[SeedRow]:
    academic = factory.build_diploma_row(reference_year, False, "DS6-ANOMALI-B4-3")
    academic.values["academic_year"] = B4_VALUES["tahun_ajaran"]
    academic.values["student_name"] += " ANOMALI-B4-3"

    collected = factory.build_diploma_row(reference_year, False, "DS6-ANOMALI-B4-6")
    collected.values.update({"is_collected": True, "collected_at": None})
    collected.values["student_name"] += " ANOMALI-B4-6"

    employee = factory.build_employee_row(employee_number)
    employee.tag = "DS6-ANOMALI-B4-4"
    employee.values["gender"] = B4_VALUES["gender"]
    employee.values["full_name"] += " ANOMALI-B4-4"

    finance = factory.build_finance_row(reference_year, PARENT_CLASSIFICATION, "active", "")
    finance.values["category"] = B4_VALUES["kategori_keuangan"]

    document = factory.build_employee_document_row(PARENT_EMPLOYEE, reference_year, reference_year,
                                                   PARENT_CLASSIFICATION, "active", "")
    document.values["classification_id"] = None

    rows = [academic, collected, employee,
            _tagged(finance, "ANOMALI-B4-5", "title", "kategori tidak cocok"),
            _tagged(document, "ANOMALI-B4-7", "document_name", "tanpa klasifikasi")]
    stamp = to_datetime(day)
    for row in rows:
        row.values.update({"created_at": stamp, "updated_at": stamp})
    return rows


def build_anomaly_rows(factory: RowFactory, reference_year: int, employee_number: int) -> list[SeedRow]:
    """Membentuk baris anomali B4 opsi `--anomali` (003a DS6).

    Nilai pelanggar sama dengan `b4_anomali_dev_a.sql`; tanggal 1 Juli Y₀; induk klasifikasi
    `DMY-P55` dan pegawai seed nomor 1; kolom penanda berformat DS7 dengan tag `ANOMALI-B4-n`.

    Args:
        factory: Pembentuk baris.
        reference_year: Tahun acuan Y₀.
        employee_number: Nomor pegawai untuk baris B4-4 (setelah pegawai preset).

    Returns:
        Sepuluh baris anomali.
    """
    day = date(reference_year, 7, 1)
    rows = _build_letters(factory, day) + [_build_classification(day)]
    return rows + _build_people_and_records(factory, day, reference_year, employee_number)

