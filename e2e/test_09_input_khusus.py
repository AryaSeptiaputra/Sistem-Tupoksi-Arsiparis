"""Test end-to-end teks bertag HTML: harus tampil apa adanya, bukan dijalankan sebagai HTML.

Tag yang dipakai hanya <b>, sehingga tidak ada script yang berjalan selama test.
"""
import secrets

import pytest
from selenium.webdriver.common.by import By

from helpers import unique_code

HTML_TEXT = "<b>uji</b>"


def _create_classification(page, text):
    page.api_create("classification", {"code": unique_code(), "name": text, "description": None,
                                       "retention_active_period": 1, "retention_inactive_period": 1,
                                       "final_action": "permanent"})


def _create_location(page, text):
    page.api_create("storageLocation", {"name": text, "description": None})


def _create_teacher(page, text):
    nip = "19" + "".join(secrets.choice("0123456789") for _ in range(16))
    page.api_create("teacher", {"identity_number": nip, "full_name": text, "gender": "L",
                                "employment_status": "GTT", "rank": "", "status": "aktif",
                                "address": ""})


def _create_finance(page, text, fiscal_year=2026, code="421"):
    class_id = page.api_find("classification", "code", code)["id"]
    page.api_create("financeArchive", {"title": text, "fiscal_year": fiscal_year, "category": "BOS_REG",
                                       "amount": 1000, "description": "", "classification_id": class_id},
                    form=True)


def _create_expired_finance(page, text):
    # Tahun 2010 + retensi klasifikasi 000 (1 + 1 tahun) sudah lewat, jadi muncul di Penyusutan
    _create_finance(page, text, fiscal_year=2010, code="000")


def _create_incoming(page, text):
    class_id = page.api_find("classification", "code", "421")["id"]
    page.api_create("incomingLetter", {"number": unique_code(), "sender": text, "subject": "Uji",
                                       "letter_date": "2026-10-20", "received_date": "2026-10-21",
                                       "classification_id": class_id}, form=True)


def _create_outgoing(page, text):
    class_id = page.api_find("classification", "code", "421")["id"]
    page.api_create("outgoingLetter", {"number": unique_code(), "destination": text, "subject": "Uji",
                                       "letter_date": "2026-10-20", "sent_date": "2026-10-21",
                                       "classification_id": class_id, "is_decree": "false"}, form=True)


def _create_diploma(page, text):
    page.api_create("diploma", {"number": unique_code(), "student_name": text, "major": "Kimia Industri",
                                "academic_year": "2025/2026", "is_collected": "false"}, form=True)


def _create_employee_archive(page, text):
    owner_id = page.api_find("teacher", "full_name", "Budi Santoso")["id"]
    class_id = page.api_find("classification", "code", "421")["id"]
    page.api_create("employeeArchive", {"document_name": text, "owner_id": owner_id, "classification_id": class_id,
                                        "document_type": "SK_PANGKAT", "archive_status": "active",
                                        "document_year": 2026, "description": ""}, form=True)


def _create_reference(page, text):
    # Kategori school_major adalah kategori yang tampil pertama di halaman Master Referensi
    page.run_js("return await api.reference.create(args[0]);",
                {"category": "school_major", "code": unique_code().lower(), "name": text,
                 "sort_order": 9, "description": "", "is_active": True})


# (id test, pembuat data, halaman yang menampilkan teks itu)
CASES = [
    ("Klasifikasi", _create_classification, "/page/classification"),
    ("Lokasi Simpan", _create_location, "/page/storage_location"),
    ("Guru", _create_teacher, "/page/teacher"),
    ("Arsip Keuangan", _create_finance, "/page/finance_archive"),
    ("Log Aktivitas", _create_classification, "/page/log"),
    ("Surat Masuk", _create_incoming, "/page/incoming_letter"),
    ("Surat Keluar", _create_outgoing, "/page/outgoing_letter"),
    ("Data Ijazah", _create_diploma, "/page/diploma"),
    ("Arsip Pegawai", _create_employee_archive, "/page/employee_archive"),
    ("Master Referensi", _create_reference, "/page/reference"),
    ("Penyusutan Arsip", _create_expired_finance, "/page/disposal"),
]


def _rendered_bold(element):
    return [b for b in element.find_elements(By.TAG_NAME, "b") if b.text == "uji"]


class TestInputKhusus:
    """Input khusus"""

    @pytest.mark.parametrize("create, path", [(c, p) for _, c, p in CASES], ids=[name for name, _, _ in CASES])
    def test_tag_html_tampil_sebagai_teks(self, page, create, path):
        """Menyimpan nama berisi teks "<b>uji</b>", lalu membuka halaman daftarnya.

        Diharapkan: tabel menampilkan teks "<b>uji</b>" apa adanya, bukan kata "uji" bercetak tebal.
        """
        token = secrets.token_hex(3)
        create(page, f"Nama {HTML_TEXT} {token}")
        page.open_list(path)
        row = page.find_row(token)
        assert not _rendered_bold(row), "Teks dari pengguna dirender sebagai HTML (tag <b> dijalankan)"
        assert HTML_TEXT in row.get_attribute("textContent")

    def test_aktivitas_akun_saya(self, page):
        """Menyimpan klasifikasi berisi "<b>uji</b>", lalu membuka Aktivitas terakhir di Akun Saya.

        Diharapkan: aktivitas menampilkan teks "<b>uji</b>" apa adanya.
        """
        token = secrets.token_hex(3)
        _create_classification(page, f"Nama {HTML_TEXT} {token}")
        page.open("/page/user_profile")
        item = page.wait.until(
            lambda d: next((li for li in d.find_elements(By.CSS_SELECTOR, "#activity-list li")
                            if token in li.get_attribute("textContent")), None),
            "Aktivitas baru tidak tampil di Akun Saya")
        assert not _rendered_bold(item)
        assert HTML_TEXT in item.get_attribute("textContent")
