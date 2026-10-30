"""Test end-to-end Surat Masuk dan Surat Keluar. Surat berawalan "E2E/" berasal dari e2e/seed.py."""
import pytest
from selenium.webdriver.common.by import By

from helpers import unique

# (id isian yang dikosongkan, judul modal validasi)
INCOMING_REQUIRED = [
    ("number", "Nomor Surat Kosong"),
    ("sender", "Pengirim Kosong"),
    ("letter_date", "Tanggal Surat Kosong"),
    ("received_date", "Tanggal Diterima Kosong"),
    ("classification_id", "Klasifikasi Belum Dipilih"),
]


def _fill_incoming(page, number, sender="Dinas Pendidikan Provinsi"):
    page.fill("number", number)
    page.fill("sender", sender)
    page.select("classification_id", text="421 - Sekolah")
    page.select("storage_location_id", text="Lemari A - Rak 1")
    page.select("archive_status", value="active")
    page.fill("letter_date", "2026-10-20")
    page.fill("received_date", "2026-10-21")
    page.fill("subject", "Undangan sosialisasi kurikulum")


def _fill_outgoing(page, number, destination="Cabang Dinas Wilayah VII"):
    page.fill("number", number)
    page.fill("destination", destination)
    page.select("classification_id", text="421 - Sekolah")
    page.fill("letter_date", "2026-10-20")
    page.fill("sent_date", "2026-10-21")
    page.select("approval_status", value="approved")
    page.fill("subject", "Laporan kegiatan sekolah")


def _open_preview(page, number):
    button = page.row_button(number, "Lihat PDF")
    assert button.is_enabled(), "Tombol Lihat PDF nonaktif padahal surat punya lampiran"
    button.click()
    page.wait.until(lambda _: page.is_visible("view-pdf-fullscreen"), "Pratinjau PDF tidak terbuka")
    return page.find("fullscreen-pdf-viewer").get_attribute("src")


class TestSuratMasuk:
    """Surat Masuk"""

    def test_tambah_tanpa_lampiran(self, page):
        """Menambah surat masuk lengkap tanpa lampiran.

        Diharapkan: toast "Data berhasil disimpan!" dan surat tampil di tabel dengan tombol Lihat PDF nonaktif.
        """
        number = unique("421/IN")
        page.open_list("/page/incoming_letter")
        page.click("btn-add-new")
        _fill_incoming(page, number)
        page.save_expect_toast("btn-save-data", "Data berhasil disimpan")
        assert not page.row_button(number, "Lihat PDF").is_enabled()

    def test_tambah_dengan_pdf(self, page):
        """Menambah surat masuk dengan lampiran PDF.

        Diharapkan: pratinjau berkas tampil sebelum disimpan, toast "Data berhasil disimpan!", dan lampiran bisa dibuka (HTTP 200).
        """
        number = unique("421/PDF")
        page.open_list("/page/incoming_letter")
        page.click("btn-add-new")
        _fill_incoming(page, number)
        page.upload("fileInput", "contoh.pdf")
        page.wait.until(lambda _: page.find("pdf-viewer").get_attribute("src").startswith("blob:"),
                        "Pratinjau berkas tidak tampil")
        page.save_expect_toast("btn-save-data", "Data berhasil disimpan")
        src = _open_preview(page, number)
        assert "/storage/documents/incoming_letters/" in src
        assert page.http_status(src) == 200

    @pytest.mark.parametrize("field, title", INCOMING_REQUIRED, ids=[f for f, _ in INCOMING_REQUIRED])
    def test_validasi_wajib(self, page, field, title):
        """Menyimpan surat masuk dengan satu isian wajib dikosongkan.

        Diharapkan: modal validasi yang menyebut isian tersebut, dan data tidak tersimpan.
        """
        number = unique("421/VAL")
        page.open_list("/page/incoming_letter")
        page.click("btn-add-new")
        _fill_incoming(page, number)
        if field == "classification_id":
            page.select(field, value="")
        else:
            page.fill(field, "")
        page.click("btn-save-data")
        page.wait_modal(title)
        assert page.api_find("incomingLetter", "number", number) is None

    def test_file_bukan_pdf(self, page):
        """Memilih berkas teks (.txt) sebagai lampiran surat masuk.

        Diharapkan: modal "Format Salah" dan pilihan berkas dikosongkan.
        """
        page.open_list("/page/incoming_letter")
        page.click("btn-add-new")
        page.upload("fileInput", "bukan_pdf.txt")
        page.wait_modal("Format Salah")
        assert page.value("fileInput") == ""

    def test_pratinjau_lampiran(self, page):
        """Membuka lampiran surat lama E2E/2015/001 lewat tombol Lihat PDF, lalu menutupnya.

        Diharapkan: pratinjau layar penuh memuat berkas dari /storage (HTTP 200), dan tombol Tutup kembali ke tabel.
        """
        page.open_list("/page/incoming_letter")
        src = _open_preview(page, "E2E/2015/001")
        assert page.http_status(src) == 200
        page.click("btn-close-preview-mode")
        page.wait.until(lambda _: page.is_visible("view-table"), "Tabel tidak tampil lagi setelah Tutup")

    def test_edit(self, page):
        """Mengubah perihal surat E2E/MASUK/EDIT lewat tombol Edit.

        Diharapkan: isian terisi data lama (termasuk tanggal), toast "Data berhasil diperbarui!", dan tabel menampilkan perihal baru.
        """
        subject = unique("Perihal diperbarui")
        page.open_list("/page/incoming_letter")
        page.click_row_button("E2E/MASUK/EDIT", "Edit")
        assert page.value("letter_date") == "2026-08-01"
        page.fill("subject", subject)
        page.save_expect_toast("btn-save-data", "Data berhasil diperbarui")
        assert subject in page.find_row("E2E/MASUK/EDIT").get_attribute("textContent")

    def test_nomor_duplikat(self, page):
        """Menambah surat masuk dengan nomor yang sudah terdaftar (E2E/MASUK/001).

        Diharapkan: modal "Gagal Menyimpan" yang menyebut nomor surat sudah ada.
        """
        page.open_list("/page/incoming_letter")
        page.click("btn-add-new")
        _fill_incoming(page, "E2E/MASUK/001")
        page.click("btn-save-data")
        _, message = page.wait_modal("Gagal Menyimpan")
        assert "nomor" in message.lower(), f"Pesan tidak menyebut nomor surat: {message}"

    def test_cari_teks(self, page):
        """Mencari surat masuk dengan kata "Padjadjaran" (nama pengirim).

        Diharapkan: hanya surat E2E/MASUK/002 yang tampil.
        """
        page.open_list("/page/incoming_letter")
        page.fill("searchInput", "Padjadjaran")
        page.wait.until(lambda _: len(page.row_texts()) == 1, "Pencarian tidak menyaring tabel")
        assert "E2E/MASUK/002" in page.row_texts()[0]

    def test_filter_klasifikasi(self, page):
        """Menyaring surat masuk dengan klasifikasi 000.

        Diharapkan: semua baris berklasifikasi 000, termasuk E2E/MASUK/002, dan surat klasifikasi 421 tidak tampil.
        """
        page.open_list("/page/incoming_letter")
        page.select("filterClassification", value="000")
        page.wait.until(lambda _: not page.has_row("E2E/MASUK/001"), "Filter klasifikasi tidak menyaring tabel")
        assert page.has_row("E2E/MASUK/002")

    def test_filter_status(self, page):
        """Menyaring surat masuk dengan status arsip Inaktif.

        Diharapkan: hanya surat berstatus inaktif (E2E/2015/001) yang tampil.
        """
        page.open_list("/page/incoming_letter")
        page.select("filterStatus", value="inactive")
        page.wait.until(lambda _: len(page.row_texts()) == 1, "Filter status tidak menyaring tabel")
        assert "E2E/2015/001" in page.row_texts()[0]

    def test_filter_tanggal_dan_reset(self, page):
        """Menyaring surat masuk berdasarkan tanggal surat tahun 2015, lalu menekan Reset.

        Diharapkan: hanya surat bertanggal 2015 yang tampil; setelah Reset muncul toast "Filter direset" dan semua surat tampil lagi.
        """
        page.open_list("/page/incoming_letter")
        total = len(page.row_texts())
        page.select("filterDateType", value="letter")
        page.fill("startDate", "2015-01-01")
        page.fill("endDate", "2015-12-31")
        page.wait.until(lambda _: len(page.row_texts()) == 1, "Filter tanggal tidak menyaring tabel")
        assert "E2E/2015/001" in page.row_texts()[0]
        page.click("btnResetFilter")
        page.wait_toast("Filter direset")
        assert len(page.row_texts()) == total

    def test_hapus(self, page):
        """Menghapus surat E2E/MASUK/HAPUS.

        Diharapkan: konfirmasi "Hapus Data?", toast "Data telah dihapus", dan baris hilang dari tabel.
        """
        page.open_list("/page/incoming_letter")
        page.click_row_button("E2E/MASUK/HAPUS", "Hapus")
        page.wait_modal("Hapus Data")
        page.press_modal("btnModalYes")
        page.wait_toast("Data telah dihapus")
        page.wait_row_gone("E2E/MASUK/HAPUS")


class TestSuratKeluar:
    """Surat Keluar"""

    def test_tambah(self, page):
        """Menambah surat keluar jenis SK yang sudah disetujui.

        Diharapkan: toast "Data berhasil disimpan!" dan surat tampil di tabel dengan label SK dan status approved.
        """
        number = unique("421/OUT")
        page.open_list("/page/outgoing_letter")
        page.click("btn-add-new")
        _fill_outgoing(page, number)
        page.driver.find_element(By.CSS_SELECTOR, "input[name='is_decree'][value='true']").click()
        page.save_expect_toast("btn-save-data", "Data berhasil disimpan")
        row = page.find_row(number).get_attribute("textContent")
        assert "SK" in row and "approved" in row

    def test_wajib_kosong(self, page):
        """Menyimpan surat keluar tanpa tujuan.

        Diharapkan: modal "Data Belum Lengkap".
        """
        page.open_list("/page/outgoing_letter")
        page.click("btn-add-new")
        _fill_outgoing(page, unique("421/OUT"))
        page.fill("destination", "")
        page.click("btn-save-data")
        page.wait_modal("Data Belum Lengkap")

    def test_tanpa_tanggal(self, page):
        """Menyimpan surat keluar tanpa tanggal surat dan tanggal kirim.

        Diharapkan: ditolak dengan pesan yang menyebut tanggal wajib diisi.
        """
        page.open_list("/page/outgoing_letter")
        page.click("btn-add-new")
        _fill_outgoing(page, unique("421/OUT"))
        page.fill("letter_date", "")
        page.fill("sent_date", "")
        page.click("btn-save-data")
        _, message = page.wait_modal()
        assert "tanggal" in message.lower(), f"Pesan tidak menyebut tanggal: {message}"

    def test_lampiran_kosong(self, page):
        """Melihat tombol Lihat PDF pada surat E2E/KELUAR/001 yang tidak punya lampiran.

        Diharapkan: tombol Lihat PDF nonaktif.
        """
        page.open_list("/page/outgoing_letter")
        assert not page.row_button("E2E/KELUAR/001", "Lihat PDF").is_enabled()

    def test_filter_persetujuan(self, page):
        """Menyaring surat keluar dengan status persetujuan "Disetujui".

        Diharapkan: hanya surat yang disetujui (E2E/KELUAR/002) yang tampil.
        """
        page.open_list("/page/outgoing_letter")
        page.select("filterApproval", value="approved")
        page.wait.until(lambda _: not page.has_row("E2E/KELUAR/001"), "Filter persetujuan tidak menyaring tabel")
        assert all("approved" in row for row in page.row_texts())
        assert page.has_row("E2E/KELUAR/002")

    def test_cari_dan_reset(self, page):
        """Mencari surat keluar dengan kata "Yayasan", lalu menekan Reset.

        Diharapkan: hanya E2E/KELUAR/003 yang tampil; setelah Reset semua surat tampil lagi.
        """
        page.open_list("/page/outgoing_letter")
        total = len(page.row_texts())
        page.fill("searchInput", "Yayasan")
        page.wait.until(lambda _: len(page.row_texts()) == 1, "Pencarian tidak menyaring tabel")
        assert "E2E/KELUAR/003" in page.row_texts()[0]
        page.click("btnResetFilter")
        page.wait_toast("Filter direset")
        assert len(page.row_texts()) == total

    def test_edit(self, page):
        """Mengubah tujuan surat E2E/KELUAR/EDIT lewat tombol Edit.

        Diharapkan: toast "Data berhasil diperbarui!" dan tabel menampilkan tujuan baru.
        """
        destination = unique("Tujuan baru")
        page.open_list("/page/outgoing_letter")
        page.click_row_button("E2E/KELUAR/EDIT", "Edit")
        page.fill("destination", destination)
        page.save_expect_toast("btn-save-data", "Data berhasil diperbarui")
        assert destination in page.find_row("E2E/KELUAR/EDIT").get_attribute("textContent")

    def test_hapus(self, page):
        """Menghapus surat E2E/KELUAR/HAPUS.

        Diharapkan: konfirmasi "Hapus Surat?", toast "Data telah dihapus", dan baris hilang dari tabel.
        """
        page.open_list("/page/outgoing_letter")
        page.click_row_button("E2E/KELUAR/HAPUS", "Hapus")
        page.wait_modal("Hapus Surat")
        page.press_modal("btnModalYes")
        page.wait_toast("Data telah dihapus")
        page.wait_row_gone("E2E/KELUAR/HAPUS")
