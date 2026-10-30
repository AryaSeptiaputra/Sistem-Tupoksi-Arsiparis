"""Test end-to-end halaman login dan penanganan sesi."""
import pytest
from selenium.webdriver.common.by import By

# Halaman yang membutuhkan login: (id test, path)
PROTECTED_PAGES = [
    ("Dashboard", "/page/dashboard"),
    ("Surat Masuk", "/page/incoming_letter"),
    ("Surat Keluar", "/page/outgoing_letter"),
    ("Data Ijazah", "/page/diploma"),
    ("Arsip Keuangan", "/page/finance_archive"),
    ("Arsip Pegawai", "/page/employee_archive"),
    ("Guru", "/page/teacher"),
    ("Klasifikasi", "/page/classification"),
    ("Lokasi Simpan", "/page/storage_location"),
    ("Penyusutan", "/page/disposal"),
    ("Log Aktivitas", "/page/log"),
    ("Master Referensi", "/page/reference"),
    ("Backup", "/page/backup"),
    ("Akun Saya", "/page/user_profile"),
]


@pytest.fixture
def logged_out(app_page):
    """Halaman login yang terbuka tanpa token."""
    app_page.open("/page/login")
    app_page.set_token(None)
    app_page.open("/page/login")
    return app_page


class TestLogin:
    """Login & sesi"""

    def test_login_berhasil(self, logged_out):
        """Login dengan username dan kata sandi yang benar.

        Diharapkan: diarahkan ke dashboard, token tersimpan, dan sapaan memuat nama operator.
        """
        logged_out.submit_login(logged_out.credentials["username"], logged_out.credentials["password"])
        logged_out.wait_path("/page/dashboard")
        assert logged_out.token(), "Token login tidak tersimpan"
        welcome = logged_out.wait.until(
            lambda d: d.find_element(By.ID, "user-welcome").text if "Halo" in d.find_element(By.ID, "user-welcome").text else None)
        assert "Operator Uji" in welcome

    def test_login_sandi_salah(self, logged_out):
        """Login dengan kata sandi yang salah.

        Diharapkan: modal "Gagal Masuk" berisi pesan sandi salah, tetap di halaman login, tanpa token.
        """
        logged_out.submit_login(logged_out.credentials["username"], "SalahSekali123")
        title, message = logged_out.wait_modal("Gagal Masuk")
        assert "salah" in message.lower()
        assert logged_out.path() == "/page/login"
        assert logged_out.token() is None

    def test_login_isian_kosong(self, logged_out):
        """Menekan tombol Login tanpa mengisi username dan kata sandi.

        Diharapkan: form tidak terkirim (validasi isian wajib browser), tetap di halaman login.
        """
        logged_out.driver.find_element(By.CSS_SELECTOR, ".btn-login").click()
        assert logged_out.driver.execute_script("return document.getElementById('username').validity.valueMissing")
        assert not logged_out.is_modal_open()
        assert logged_out.path() == "/page/login"
        assert logged_out.token() is None

    @pytest.mark.parametrize("path", [p for _, p in PROTECTED_PAGES], ids=[name for name, _ in PROTECTED_PAGES])
    def test_halaman_tanpa_login(self, logged_out, path):
        """Membuka halaman aplikasi tanpa login.

        Diharapkan: diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir").
        """
        logged_out.open(path)

        def redirected(_):
            if logged_out.is_modal_open():
                logged_out.press_modal("btnModalOk")
            return logged_out.path() == "/page/login"
        logged_out.wait.until(redirected)

    def test_token_rusak(self, logged_out):
        """Membuka dashboard dengan token yang tidak valid.

        Diharapkan: muncul modal "Sesi Berakhir", lalu diarahkan ke login dan token dihapus.
        """
        logged_out.set_token("token.tidak.valid")
        logged_out.open("/page/dashboard")
        logged_out.wait_modal("Sesi Berakhir")
        logged_out.press_modal("btnModalOk")
        logged_out.wait_path("/page/login")
        assert logged_out.token() is None

    def test_logout(self, page):
        """Menekan menu Keluar di sidebar, lalu membuka dashboard lagi.

        Diharapkan: kembali ke halaman login, token dihapus, dan dashboard tidak bisa dibuka tanpa login ulang.
        """
        page.open("/page/dashboard")
        page.click("btn-logout")
        page.wait_path("/page/login")
        assert page.token() is None
        page.open("/page/dashboard")
        page.wait_path("/page/login")

    def test_tombol_mata_sandi(self, logged_out):
        """Menekan ikon mata di kolom kata sandi halaman login dua kali.

        Diharapkan: kata sandi tampil sebagai teks, lalu tersembunyi lagi.
        """
        logged_out.fill("password", "Rahasia123")
        logged_out.click("toggle-password")
        assert logged_out.find("password").get_attribute("type") == "text"
        logged_out.click("toggle-password")
        assert logged_out.find("password").get_attribute("type") == "password"

    @pytest.mark.parametrize("short_path, target", [
        ("/", "/page/login"),
        ("/dashboard", "/page/dashboard"),
    ], ids=["/", "/dashboard"])
    def test_url_pendek(self, page, short_path, target):
        """Membuka URL pendek tanpa awalan /page.

        Diharapkan: diarahkan ke halaman tujuan.
        """
        page.open(short_path)
        page.wait_path(target)


# Endpoint data yang harus menolak permintaan tanpa token: (id test, method, path)
PROTECTED_APIS = [
    ("GET guru", "GET", "/teacher/get_all"),
    ("GET klasifikasi", "GET", "/classification/get_all"),
    ("GET surat masuk", "GET", "/incoming_letter/get_all"),
    ("GET surat keluar", "GET", "/outgoing_letter/get_all"),
    ("GET ijazah", "GET", "/diploma/get_all"),
    ("GET arsip keuangan", "GET", "/finance_archive/get_all"),
    ("GET arsip pegawai", "GET", "/employee_archive/get_all"),
    ("GET lokasi simpan", "GET", "/storage_location/get_all"),
    ("GET log", "GET", "/log/get_all"),
    ("GET akun", "GET", "/user/me"),
    ("GET referensi", "GET", "/api/references/archive_status"),
    ("POST referensi", "POST", "/api/references"),
    ("POST cari guru", "POST", "/teacher/get_by_keys"),
    ("GET penyusutan", "GET", "/disposal/check"),
    ("GET riwayat backup", "GET", "/backup/logs"),
]


class TestHakAksesApi:
    """Hak akses API"""

    @pytest.mark.parametrize("method, path", [(m, p) for _, m, p in PROTECTED_APIS],
                             ids=[name for name, _, _ in PROTECTED_APIS])
    def test_api_tanpa_token(self, page, method, path):
        """Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie).

        Diharapkan: server menolak dengan status 401.
        """
        status = page.run_js(
            "const r = await fetch(args[0], {method: args[1], credentials: 'omit',"
            " headers: {'Content-Type': 'application/json'},"
            " body: args[1] === 'POST' ? JSON.stringify({category: 'school_major', code: 'x', name: 'x', filters: {}}) : undefined});"
            "return r.status;", path, method)
        assert status == 401, f"{method} {path} tanpa token dibalas {status}, bukan 401"
