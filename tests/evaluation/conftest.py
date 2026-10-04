import os

# Dipasang sebelum `app` atau `evaluation` di-import, supaya `.env` asli tidak pernah dipakai.
# Host 127.0.0.1 port 9 (discard) tidak melayani MySQL, jadi engine aplikasi lama tidak bisa terhubung.
os.environ["DATABASE_URL"] = "mysql+pymysql://test:test@127.0.0.1:9/tidak_ada"
os.environ["JWT_SECRET_KEY"] = "kunci-palsu-test"
os.environ["EVAL_OLD_DB_URL"] = ""
os.environ["EVAL_STORAGE_ROOT"] = "storage-test-tidak-dipakai"
os.environ["EVAL_OUTPUT_DIR"] = "outputs-test-tidak-dipakai"

from dataclasses import dataclass  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from evaluation import db as eval_db  # noqa: E402


@pytest.fixture(autouse=True)
def only_temporary_sqlite(monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory) -> None:
    """Menolak engine evaluasi yang bukan SQLite di folder sementara pytest."""
    original_create_engine = eval_db.create_engine
    temp_root = tmp_path_factory.getbasetemp().resolve()

    def guarded_create_engine(url: str, **kwargs: object) -> object:
        parsed = make_url(url)
        if parsed.get_backend_name() != "sqlite" or not parsed.database:
            raise AssertionError(f"Test hanya boleh memakai SQLite sementara, bukan {parsed.get_backend_name()}")
        if temp_root not in Path(parsed.database).resolve().parents:
            raise AssertionError("Berkas SQLite test harus berada di folder sementara pytest")
        return original_create_engine(url, **kwargs)

    monkeypatch.setattr(eval_db, "create_engine", guarded_create_engine)


@dataclass(frozen=True)
class OldDatabase:
    """Salinan kecil database lama untuk test, beserta folder storage-nya."""

    url: str
    storage_root: Path


def _seed_references(session: Session) -> None:
    from app.models.classification import Classification
    from app.models.master_reference import MasterReference
    from app.models.storage_location import StorageLocation

    session.add_all([
        Classification(id=1, code="KL-1", name="Umum musnah", retention_active_period=1,
                       retention_inactive_period=1, final_action="destroy"),
        Classification(id=2, code="KL-2", name="Permanen", retention_active_period=1,
                       retention_inactive_period=1, final_action="permanent"),
        # Anomali B4: final_action di luar domain
        Classification(id=3, code="KL-3", name="Aksi aneh", retention_active_period=1,
                       retention_inactive_period=1, final_action="musnah"),
        StorageLocation(id=1, name="Lemari A"),
        MasterReference(id=1, category="school_major", code="TKJ", name="Teknik Komputer"),
        MasterReference(id=2, category="teacher_emp_status", code="PNS", name="PNS"),
        MasterReference(id=3, category="teacher_rank", code="III/a", name="Penata Muda"),
        MasterReference(id=4, category="teacher_active_status", code="aktif", name="Aktif"),
        MasterReference(id=5, category="finance_category", code="bos_reguler", name="BOS Reguler"),
        MasterReference(id=6, category="emp_doc_type", code="sk", name="SK"),
    ])


def _seed_people(session: Session) -> None:
    from app.models.log import Log
    from app.models.teacher import Teacher
    from app.models.user import User

    session.add_all([
        Teacher(id=1, identity_number="100000000000000001", full_name="Pegawai Satu", gender="L",
                employment_status="PNS", rank=None, status="Aktif", address="Alamat palsu 1"),
        # Anomali B4: gender tidak bisa dipetakan
        Teacher(id=2, identity_number="100000000000000002", full_name="Pegawai Dua", gender="X",
                employment_status="PNS", rank="III/a", status="aktif"),
    ])
    session.flush()
    session.add_all([
        User(id=1, teacher_id=1, password="hash-palsu", role="admin", status="active"),
        User(id=2, teacher_id=2, password="hash-palsu", role="teacher", status="active"),
    ])
    session.flush()
    session.add(Log(id=1, action="Login", user_id=1))


def _seed_letters(session: Session) -> None:
    from app.models.incoming_letter import IncomingLetter
    from app.models.outgoing_letter import OutgoingLetter

    session.add_all([
        IncomingLetter(id=1, number="IN-1", letter_date=datetime(2015, 3, 1), received_date=datetime(2015, 3, 5),
                       sender="Dinas", subject="Undangan", classification_id=1, storage_location_id=1,
                       archive_status="active", attachment_path="storage/documents/incoming/ada.pdf"),
        IncomingLetter(id=2, number="IN-2", letter_date=datetime(2025, 1, 10), received_date=datetime(2025, 1, 10),
                       sender="Dinas", subject="Edaran", classification_id=1, archive_status="active",
                       attachment_path="storage/documents/incoming/hilang.pdf"),
        # Anomali B4: archive_status di luar domain
        IncomingLetter(id=3, number="IN-3", letter_date=datetime(2015, 4, 1), received_date=datetime(2015, 4, 2),
                       sender="Dinas", subject="Pemberitahuan", classification_id=1, archive_status="Aktif"),
        OutgoingLetter(id=1, number="OUT-1", letter_date=datetime(2015, 2, 1), sent_date=datetime(2015, 2, 2),
                       destination="Dinas", subject="Laporan", classification_id=1, archive_status="active",
                       approval_status="approved"),
        # Anomali B4: nomor surat keluar ganda dengan id 1
        OutgoingLetter(id=2, number="OUT-1", letter_date=datetime(2024, 5, 1), sent_date=datetime(2024, 5, 1),
                       destination="Dinas", subject="Laporan ulang", classification_id=1, archive_status="active",
                       approval_status="pending"),
    ])


def _seed_other_archives(session: Session) -> None:
    from app.models.diploma import Diploma
    from app.models.employee_archive import EmployeeArchive
    from app.models.finance_archive import FinanceArchive

    session.add_all([
        Diploma(id=1, number="IJ-1", student_name="Siswa Satu", major="TKJ", academic_year="2015/2016",
                is_collected=True, collected_at=datetime(2016, 7, 1)),
        # Anomali B4: tahun ajaran tidak berformat YYYY/YYYY
        Diploma(id=2, number="IJ-2", student_name="Siswa Dua", major="Teknik Komputer", academic_year="2019-2020",
                is_collected=False),
        # Anomali B4: ijazah diambil tanpa tanggal
        Diploma(id=3, number="IJ-3", student_name="Siswa Tiga", major="tkj ", academic_year="2020/2021",
                is_collected=True, collected_at=None),
        FinanceArchive(id=1, title="BOS 2015", fiscal_year=2015, category="bos_reguler", amount=1000000,
                       classification_id=1, archive_status="active"),
        # Anomali B4: string referensi tidak cocok dengan master_reference
        FinanceArchive(id=2, title="Dana X", fiscal_year=2024, category="dana_x", classification_id=1,
                       archive_status="active"),
        EmployeeArchive(id=1, document_name="SK CPNS", document_type="sk", document_year=2015, owner_id=1,
                        classification_id=1, archive_status="active"),
        # Anomali B4: dokumen pegawai tanpa klasifikasi
        EmployeeArchive(id=2, document_name="SK Pangkat", document_type="SK", document_year=None, owner_id=1,
                        classification_id=None, archive_status="active"),
    ])


@pytest.fixture
def old_db(tmp_path: Path) -> OldDatabase:
    """Database lama SQLite sementara: skema dari `app/models` + satu baris anomali per butir B4."""
    from app.core.database import Base as LegacyBase

    url = f"sqlite:///{tmp_path / 'lama.db'}"
    engine = create_engine(url)
    LegacyBase.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_references(session)
        session.flush()
        _seed_people(session)
        _seed_letters(session)
        _seed_other_archives(session)
        session.commit()
    engine.dispose()

    storage_root = tmp_path / "storage"
    (storage_root / "documents" / "incoming").mkdir(parents=True)
    (storage_root / "documents" / "incoming" / "ada.pdf").write_bytes(b"%PDF palsu")
    return OldDatabase(url=url, storage_root=storage_root)
