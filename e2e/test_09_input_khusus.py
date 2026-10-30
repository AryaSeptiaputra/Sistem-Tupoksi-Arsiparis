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
                                "employment_status": "Guru Tidak Tetap", "rank": "", "status": "Aktif",
                                "address": ""})


def _create_finance(page, text):
    class_id = page.api_find("classification", "code", "421")["id"]
    page.api_create("financeArchive", {"title": text, "fiscal_year": 2026, "category": "BOS_REG",
                                       "amount": 1000, "description": "", "classification_id": class_id},
                    form=True)


# (id test, pembuat data, halaman yang menampilkan teks itu)
CASES = [
    ("Klasifikasi", _create_classification, "/page/classification"),
    ("Lokasi Simpan", _create_location, "/page/storage_location"),
    ("Guru", _create_teacher, "/page/teacher"),
    ("Arsip Keuangan", _create_finance, "/page/finance_archive"),
    ("Log Aktivitas", _create_classification, "/page/log"),
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
