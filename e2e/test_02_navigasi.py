"""Test end-to-end navigasi sidebar, kebersihan konsol, dan ketergantungan internet."""
import pytest
from selenium.webdriver.common.by import By

# (label menu, path, teks judul halaman, penanda halaman selesai dimuat)
MENUS = [
    ("Dashboard", "/page/dashboard", "Halo", "chart"),
    ("Surat Masuk", "/page/incoming_letter", "Surat Masuk", "table"),
    ("Surat Keluar", "/page/outgoing_letter", "Surat Keluar", "table"),
    ("Data Ijazah", "/page/diploma", "Data Ijazah Siswa", "table"),
    ("Arsip Keuangan", "/page/finance_archive", "Arsip Keuangan", "table"),
    ("Arsip Pegawai", "/page/employee_archive", "Arsip Kepegawaian", "table"),
    ("Guru", "/page/teacher", "Master Data Guru", "table"),
    ("Klasifikasi", "/page/classification", "Data Klasifikasi", "table"),
    ("Lokasi Simpan", "/page/storage_location", "Lokasi Penyimpanan", "table"),
    ("Penyusutan Arsip", "/page/disposal", "Manajemen Penyusutan", "table"),
    ("Log Aktivitas", "/page/log", "Log Aktivitas Sistem", "table"),
    ("Master Referensi", "/page/reference", "Master Data Referensi", "table"),
    ("Backup Database", "/page/backup", "Backup & Restore", "table"),
    ("Akun Saya", "/page/user_profile", "Akun Saya", "account"),
]


def _wait_ready(page, marker):
    if marker == "table":
        page.wait_table_loaded()
    elif marker == "chart":
        page.wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "#chart-overview-comparison canvas"),
                        "Grafik dashboard tidak tergambar")
        page.wait.until(lambda d: "Halo" in d.find_element(By.ID, "user-welcome").text,
                        "Sapaan dashboard tidak muncul")
    else:
        page.wait.until(lambda d: d.find_element(By.ID, "display-username").text.startswith("@"),
                        "Data akun tidak termuat")


class TestNavigasi:
    """Navigasi"""

    @pytest.mark.parametrize("label, path, heading, marker", MENUS, ids=[m[0] for m in MENUS])
    def test_menu_sidebar(self, page, label, path, heading, marker):
        """Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data.

        Diharapkan: URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi.
        """
        page.open("/page/dashboard" if path != "/page/dashboard" else "/page/user_profile")
        page.console_errors()
        link = page.driver.find_element(
            By.XPATH, f"//aside//a[contains(@class,'nav-item')][normalize-space(.)='{label}']")
        link.click()
        page.wait_path(path)
        _wait_ready(page, marker)

        assert heading in page.driver.find_element(By.TAG_NAME, "h1").text
        active = page.driver.find_element(By.CSS_SELECTOR, "aside a.nav-item.active").text.strip()
        assert active == label, f"Menu aktif '{active}', seharusnya '{label}'"
        assert page.console_errors() == []
        assert page.external_requests() == []

    def test_avatar_ke_akun_saya(self, page):
        """Menekan avatar inisial di kanan atas halaman Klasifikasi.

        Diharapkan: avatar menampilkan huruf awal nama operator, lalu membuka halaman Akun Saya.
        """
        page.open_list("/page/classification")
        avatar = page.find("header-avatar")
        assert avatar.text == "O"
        avatar.click()
        page.wait_path("/page/user_profile")
