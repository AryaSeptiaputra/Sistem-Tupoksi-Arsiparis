"""Test end-to-end halaman Akun Saya. Dijalankan paling akhir karena mengganti kata sandi akun uji."""
import secrets

from selenium.webdriver.common.by import By

RULES = ("length", "upper", "lower", "digit", "match")


def _rule_met(page, rule):
    item = page.driver.find_element(By.CSS_SELECTOR, f"#password-rules [data-rule='{rule}']")
    return "is-met" in item.get_attribute("class")


def _open_account(page):
    page.open("/page/user_profile")
    page.wait.until(lambda d: d.find_element(By.ID, "display-username").text.startswith("@"),
                    "Data akun tidak termuat")


class TestAkunSaya:
    """Akun Saya"""

    def test_data_akun(self, page):
        """Membuka Akun Saya.

        Diharapkan: banner menampilkan nama, @username, status Aktif, dan waktu login terakhir.
        """
        _open_account(page)
        assert page.find("display-name").text == "Operator Uji"
        assert page.find("display-username").text == "@" + page.credentials["username"]
        assert page.find("display-status-text").text == "Aktif"
        assert page.find("display-last-login").text != "-"

    def test_aktivitas_terakhir(self, page):
        """Melihat kartu Aktivitas terakhir.

        Diharapkan: tampil paling banyak 5 aktivitas, dan yang teratas adalah log terbaru.
        """
        latest = page.run_js("const logs = await api.log.getRecent(1); return logs[0].action;")
        _open_account(page)
        items = page.wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, "#activity-list li:not(.ak-activity-empty)"),
                                "Aktivitas terakhir kosong")
        assert 1 <= len(items) <= 5
        assert latest in items[0].get_attribute("textContent")

    def test_tombol_simpan_dan_batalkan(self, page):
        """Mengubah nama tampilan, lalu menekan Batalkan.

        Diharapkan: Simpan dan Batalkan nonaktif sebelum ada perubahan, aktif setelah nama diubah, dan Batalkan mengembalikan nama semula.
        """
        _open_account(page)
        assert not page.find("btn-profile-save").is_enabled()
        assert not page.find("btn-profile-reset").is_enabled()
        page.fill("input-display-name", "Operator Uji Sementara")
        assert page.find("btn-profile-save").is_enabled() and page.find("btn-profile-reset").is_enabled()
        page.click("btn-profile-reset")
        assert page.value("input-display-name") == "Operator Uji"
        assert not page.find("btn-profile-save").is_enabled()

    def test_nama_kosong(self, page):
        """Mengosongkan nama tampilan.

        Diharapkan: tombol Simpan nonaktif, Batalkan tetap aktif.
        """
        _open_account(page)
        page.fill("input-display-name", "")
        assert not page.find("btn-profile-save").is_enabled()
        assert page.find("btn-profile-reset").is_enabled()

    def test_ubah_nama(self, page):
        """Mengganti nama tampilan lalu menyimpan, kemudian mengembalikannya.

        Diharapkan: toast "Informasi akun tersimpan" dan banner langsung menampilkan nama baru.
        """
        _open_account(page)
        page.fill("input-display-name", "Operator Uji Baru")
        page.save_expect_toast("btn-profile-save", "Informasi akun tersimpan")
        page.expect_text("display-name", "Operator Uji Baru")
        page.fill("input-display-name", "Operator Uji")
        page.save_expect_toast("btn-profile-save", "Informasi akun tersimpan")

    def test_checklist_sandi(self, page):
        """Mengetik kata sandi baru yang lemah, lalu yang memenuhi syarat.

        Diharapkan: checklist berubah langsung sesuai isian, dan tombol Ganti baru aktif setelah semua syarat terpenuhi dan sandi lama terisi.
        """
        _open_account(page)
        page.fill("input-new-password", "abc")
        assert [_rule_met(page, rule) for rule in RULES] == [False, False, True, False, False]
        page.fill("input-new-password", "Abcdefg1")
        page.fill("input-confirm-password", "Abcdefg1")
        assert all(_rule_met(page, rule) for rule in RULES)
        assert not page.find("btn-password-save").is_enabled()
        page.fill("input-old-password", "apa saja")
        assert page.find("btn-password-save").is_enabled()

    def test_tombol_mata(self, page):
        """Menekan tombol mata pada kolom kata sandi baru dua kali.

        Diharapkan: sandi tampil sebagai teks (aria-pressed true), lalu tersembunyi lagi; kolom lain tidak ikut berubah.
        """
        _open_account(page)
        eye = page.driver.find_element(By.CSS_SELECTOR, ".ak-eye[data-target='input-new-password']")
        eye.click()
        assert page.find("input-new-password").get_attribute("type") == "text"
        assert eye.get_attribute("aria-pressed") == "true"
        assert page.find("input-old-password").get_attribute("type") == "password"
        eye.click()
        assert page.find("input-new-password").get_attribute("type") == "password"

    def test_sandi_lama_salah(self, page):
        """Mengganti kata sandi dengan sandi lama yang salah.

        Diharapkan: modal "Gagal mengganti" yang menyebut kata sandi lama salah, dan tetap login.
        """
        _open_account(page)
        page.fill("input-old-password", "SalahSekali9")
        page.fill("input-new-password", "SandiBaru123")
        page.fill("input-confirm-password", "SandiBaru123")
        page.click("btn-password-save")
        _, message = page.wait_modal("Gagal mengganti")
        assert "lama salah" in message.lower()
        assert page.token()

    def test_ganti_sandi(self, page):
        """Mengganti kata sandi dengan sandi lama yang benar, lalu login ulang.

        Diharapkan: modal "Berhasil", diarahkan ke login, sandi lama ditolak, dan sandi baru diterima.
        """
        old_password = page.credentials["password"]
        new_password = f"Baru{secrets.token_hex(5)}7"
        _open_account(page)
        page.fill("input-old-password", old_password)
        page.fill("input-new-password", new_password)
        page.fill("input-confirm-password", new_password)
        page.click("btn-password-save")
        page.wait_modal("Berhasil")
        page.press_modal("btnModalOk")
        page.wait_path("/page/login")
        page.credentials["password"] = new_password

        page.submit_login(page.credentials["username"], old_password)
        page.wait_modal("Gagal Masuk")
        page.press_modal("btnModalOk")
        page.submit_login(page.credentials["username"], new_password)
        page.wait_path("/page/dashboard")
