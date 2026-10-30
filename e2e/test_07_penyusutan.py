"""Test end-to-end Penyusutan Arsip memakai surat lama E2E/2015/001 dari e2e/seed.py."""
from selenium.webdriver.common.by import By

EXPIRED_NUMBER = "E2E/2015/001"
EXPIRED_FILE_URL = "/storage/documents/incoming_letters/e2e_surat_lama.pdf"


def _check_row(page, text):
    page.find_row(text).find_element(By.CSS_SELECTOR, ".item-check").click()


def _execute_button(page):
    return page.find("btnExecute")


class TestPenyusutan:
    """Penyusutan Arsip"""

    def test_daftar_kedaluwarsa(self, page):
        """Membuka halaman Penyusutan saat ada surat masuk tahun 2015 berklasifikasi musnah (retensi 1+1 tahun).

        Diharapkan: surat E2E/2015/001 tampil sebagai Surat Masuk dengan tahun kedaluwarsa 2017, dan penanda jumlah menyebut item kedaluwarsa.
        """
        page.open_list("/page/disposal")
        row = page.find_row(EXPIRED_NUMBER).get_attribute("textContent")
        assert "Surat Masuk" in row and "2017" in row
        assert "Kadaluwarsa" in page.find("count-badge").text

    def test_tombol_aktif_setelah_dicentang(self, page):
        """Mencentang lalu menghapus centang satu arsip kedaluwarsa.

        Diharapkan: tombol Musnahkan aktif dengan jumlah "(1 Arsip)" saat dicentang, dan nonaktif lagi saat centang dihapus.
        """
        page.open_list("/page/disposal")
        assert not _execute_button(page).is_enabled()
        _check_row(page, EXPIRED_NUMBER)
        assert _execute_button(page).is_enabled() and "(1 Arsip)" in _execute_button(page).text
        _check_row(page, EXPIRED_NUMBER)
        assert not _execute_button(page).is_enabled()

    def test_pilih_semua(self, page):
        """Mencentang kotak "pilih semua" di kepala tabel.

        Diharapkan: semua arsip tercentang dan tombol Musnahkan menyebut jumlah seluruh arsip.
        """
        page.open_list("/page/disposal")
        page.click("checkAll")
        boxes = page.driver.find_elements(By.CSS_SELECTOR, ".item-check")
        assert boxes and all(box.is_selected() for box in boxes)
        assert f"({len(boxes)} Arsip)" in _execute_button(page).text

    def test_konfirmasi_salah(self, page):
        """Menekan Musnahkan lalu mengetik "setuju" (huruf kecil) di kotak konfirmasi.

        Diharapkan: toast "Konfirmasi salah. Pemusnahan dibatalkan." dan arsip tetap ada.
        """
        page.open_list("/page/disposal")
        _check_row(page, EXPIRED_NUMBER)
        page.click("btnExecute")
        page.wait_modal("Konfirmasi Pemusnahan")
        page.answer_prompt("setuju")
        page.wait_toast("Konfirmasi salah")
        assert page.has_row(EXPIRED_NUMBER)

    def test_batal(self, page):
        """Menekan Musnahkan lalu menekan Batal di kotak konfirmasi.

        Diharapkan: modal tertutup dan arsip tetap ada di daftar.
        """
        page.open_list("/page/disposal")
        _check_row(page, EXPIRED_NUMBER)
        page.click("btnExecute")
        page.wait_modal("Konfirmasi Pemusnahan")
        page.press_modal("btnModalCancel")
        assert not page.is_modal_open()
        assert page.has_row(EXPIRED_NUMBER)
        assert page.api_find("incomingLetter", "number", EXPIRED_NUMBER)["archive_status"] != "destroyed"

    def test_musnahkan(self, page):
        """Memusnahkan surat E2E/2015/001 dengan mengetik "SETUJU".

        Diharapkan: modal "Pemusnahan Berhasil" (1 arsip), arsip hilang dari daftar, statusnya "Musnah" di halaman Surat Masuk, dan lampirannya terhapus (HTTP 404).
        """
        page.open_list("/page/disposal")
        assert page.http_status(EXPIRED_FILE_URL) == 200, "Lampiran awal tidak tersedia"
        _check_row(page, EXPIRED_NUMBER)
        page.click("btnExecute")
        page.wait_modal("Konfirmasi Pemusnahan")
        page.answer_prompt("SETUJU")
        _, message = page.wait_modal("Pemusnahan Berhasil")
        assert "1 arsip" in message
        page.press_modal("btnModalOk")
        page.wait_row_gone(EXPIRED_NUMBER)

        page.open_list("/page/incoming_letter")
        assert "Musnah" in page.find_row(EXPIRED_NUMBER).get_attribute("textContent")
        assert page.http_status(EXPIRED_FILE_URL) == 404
