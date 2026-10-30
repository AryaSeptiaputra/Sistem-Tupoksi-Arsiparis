"""Test end-to-end Data Ijazah, Arsip Keuangan, dan Arsip Pegawai. Data contoh berasal dari e2e/seed.py."""
from helpers import unique


def _open_file_preview(page, row_text, title):
    button = page.row_button(row_text, title)
    assert button.is_enabled(), f"Tombol {title} nonaktif padahal arsip punya lampiran"
    button.click()
    page.wait.until(lambda _: page.is_visible("view-pdf-fullscreen"), "Pratinjau berkas tidak terbuka")
    return page.find("fullscreen-pdf-viewer").get_attribute("src")


class TestIjazah:
    """Data Ijazah"""

    def _fill(self, page, name, serial, year="2025/2026"):
        page.fill("student_name", name)
        page.fill("serial_number", serial)
        page.select("major", text="Kimia Industri")
        page.fill("academic_year", year)
        page.select("storage_location_id", text="Lemari A - Rak 1")

    def _create(self, page, name):
        page.api_create("diploma", {"number": unique("DN"), "student_name": name, "major": "Analisis Kimia",
                                    "academic_year": "2025/2026", "is_collected": "false"}, form=True)

    def test_tambah_belum_diambil(self, page):
        """Menambah data ijazah yang belum diambil siswa.

        Diharapkan: toast "Data berhasil disimpan!" dan baris baru berstatus "Belum Diambil".
        """
        name = unique("Siswa")
        page.open_list("/page/diploma")
        page.click("btn-add-new")
        self._fill(page, name, unique("DN"))
        page.save_expect_toast("btn-save-data", "Data berhasil disimpan")
        assert "Belum Diambil" in page.find_row(name).get_attribute("textContent")

    def test_tambah_sudah_diambil(self, page):
        """Menambah ijazah dengan mencentang "Ijazah Sudah Diambil?".

        Diharapkan: kolom tanggal pengambilan muncul terisi hari ini, toast "Data berhasil disimpan!", dan baris berstatus "Sudah Diambil".
        """
        name = unique("Siswa Lulus")
        page.open_list("/page/diploma")
        page.click("btn-add-new")
        self._fill(page, name, unique("DN"))
        page.click("is_taken_checkbox")
        assert page.is_visible("date-taken-wrapper") and page.value("date_taken") != ""
        page.save_expect_toast("btn-save-data", "Data berhasil disimpan")
        assert "Sudah Diambil" in page.find_row(name).get_attribute("textContent")

    def test_wajib_kosong(self, page):
        """Menyimpan ijazah tanpa memilih jurusan.

        Diharapkan: modal "Data Belum Lengkap".
        """
        page.open_list("/page/diploma")
        page.click("btn-add-new")
        page.fill("student_name", unique("Siswa"))
        page.fill("serial_number", unique("DN"))
        page.click("btn-save-data")
        page.wait_modal("Data Belum Lengkap")

    def test_tahun_ajaran_kosong(self, page):
        """Menyimpan ijazah tanpa tahun ajaran.

        Diharapkan: ditolak dengan pesan yang menyebut tahun ajaran, dan data tidak tersimpan.
        """
        name = unique("Siswa Tanpa Tahun")
        page.open_list("/page/diploma")
        page.click("btn-add-new")
        self._fill(page, name, unique("DN"), year="")
        page.click("btn-save-data")
        result = page.wait_save_outcome("Data berhasil disimpan")
        assert result[0] == "modal", "Ijazah tanpa tahun ajaran ikut tersimpan"
        assert "tahun" in result[2].lower(), f"Pesan tidak menyebut tahun ajaran: {result[2]}"

    def test_nomor_seri_duplikat(self, page):
        """Menambah ijazah dengan nomor seri yang sudah ada (DN-E2E-001).

        Diharapkan: modal "Gagal Menyimpan" yang menyebut nomor sudah dipakai.
        """
        page.open_list("/page/diploma")
        page.click("btn-add-new")
        self._fill(page, unique("Siswa Kembar"), "DN-E2E-001")
        page.click("btn-save-data")
        _, message = page.wait_modal("Gagal Menyimpan")
        assert "nomor" in message.lower(), f"Pesan tidak menyebut nomor: {message}"

    def test_tambah_dengan_lampiran(self, page):
        """Menambah ijazah dengan lampiran PDF, lalu membukanya.

        Diharapkan: toast "Data berhasil disimpan!" dan lampiran bisa dibuka dari tombol Lihat File (HTTP 200).
        """
        name = unique("Siswa Berkas")
        page.open_list("/page/diploma")
        page.click("btn-add-new")
        self._fill(page, name, unique("DN"))
        page.upload("fileInput", "contoh.pdf")
        page.save_expect_toast("btn-save-data", "Data berhasil disimpan")
        src = _open_file_preview(page, name, "Lihat File")
        assert page.http_status(src) == 200

    def test_filter_jurusan(self, page):
        """Menyaring ijazah dengan jurusan Farmasi.

        Diharapkan: semua baris berjurusan Farmasi, termasuk Rina Lestari.
        """
        page.open_list("/page/diploma")
        page.select("filterMajor", value="Farmasi")
        page.wait.until(lambda _: all("Farmasi" in row for row in page.row_texts()), "Filter jurusan tidak menyaring tabel")
        assert page.has_row("Rina Lestari")

    def test_filter_status_diambil(self, page):
        """Menyaring ijazah dengan status "Sudah Diambil".

        Diharapkan: semua baris berstatus Sudah Diambil, termasuk Andi Pratama.
        """
        page.open_list("/page/diploma")
        page.select("filterStatus", value="taken")
        page.wait.until(lambda _: all("Sudah Diambil" in row for row in page.row_texts()),
                        "Filter status tidak menyaring tabel")
        assert page.has_row("Andi Pratama")

    def test_filter_tahun_ajaran(self, page):
        """Membuka pilihan filter Tahun saat ada ijazah tahun ajaran 2025/2026.

        Diharapkan: tahun ajaran 2025/2026 tersedia di filter Tahun.
        """
        page.open_list("/page/diploma")
        assert "2025/2026" in page.option_texts("filterYear"), \
            f"Pilihan filter tahun hanya {page.option_texts('filterYear')}"

    def test_edit(self, page):
        """Mengubah nama siswa lewat tombol Edit.

        Diharapkan: toast "Data berhasil diperbarui!" dan tabel menampilkan nama baru.
        """
        old_name, new_name = unique("Siswa Lama"), unique("Siswa Baru")
        self._create(page, old_name)
        page.open_list("/page/diploma")
        page.click_row_button(old_name, "Edit")
        page.fill("student_name", new_name)
        page.save_expect_toast("btn-save-data", "Data berhasil diperbarui")
        page.find_row(new_name)

    def test_hapus(self, page):
        """Menghapus data ijazah.

        Diharapkan: konfirmasi, toast "Data telah dihapus", dan baris hilang dari tabel.
        """
        name = unique("Siswa Hapus")
        self._create(page, name)
        page.open_list("/page/diploma")
        page.click_row_button(name, "Hapus")
        page.wait_modal("Hapus Data")
        page.press_modal("btnModalYes")
        page.wait_toast("Data telah dihapus")
        page.wait_row_gone(name)


class TestArsipKeuangan:
    """Arsip Keuangan"""

    def _fill(self, page, title, amount="2500000"):
        page.fill("title", title)
        page.fill("fiscal_year", 2026)
        page.select("period_month", value="10")
        page.select("category", value="BOS_REG")
        page.fill("amount", amount)
        page.select("classification_id", text="421 - Sekolah")
        page.select("storage_location_id", text="Lemari A - Rak 1")
        page.fill("description", "Dibuat oleh test")

    def _create(self, page, title):
        class_id = page.api_find("classification", "code", "421")["id"]
        page.api_create("financeArchive", {"title": title, "fiscal_year": 2026, "category": "BOS_REG",
                                           "amount": 100000, "description": "", "classification_id": class_id},
                        form=True)

    def test_tambah(self, page):
        """Menambah arsip keuangan dengan judul, periode, kategori, nominal, dan klasifikasi.

        Diharapkan: toast "Berhasil disimpan!" dan baris baru menampilkan nominal Rp 2.500.000.
        """
        title = unique("SPJ BOS")
        page.open_list("/page/finance_archive")
        page.click("btn-add-new")
        self._fill(page, title)
        page.save_expect_toast("btn-save-data", "Berhasil disimpan")
        assert "2.500.000" in page.find_row(title).get_attribute("textContent")

    def test_wajib_kosong(self, page):
        """Menyimpan arsip keuangan tanpa nominal.

        Diharapkan: modal "Data Belum Lengkap".
        """
        page.open_list("/page/finance_archive")
        page.click("btn-add-new")
        self._fill(page, unique("SPJ"), amount="")
        page.click("btn-save-data")
        page.wait_modal("Data Belum Lengkap")

    def test_file_bukan_pdf(self, page):
        """Memilih berkas teks (.txt) sebagai lampiran arsip keuangan.

        Diharapkan: modal "Format Salah".
        """
        page.open_list("/page/finance_archive")
        page.click("btn-add-new")
        page.upload("fileInput", "bukan_pdf.txt")
        page.wait_modal("Format Salah")

    def test_lampiran_dan_hapus_lampiran(self, page):
        """Menambah arsip keuangan dengan PDF, membukanya, lalu menghapus lampirannya lewat Edit.

        Diharapkan: lampiran bisa dibuka (HTTP 200); setelah "Hapus File" dan simpan, tombol Lihat PDF nonaktif dan berkas lama tidak bisa diakses lagi (HTTP 404).
        """
        title = unique("SPJ Berkas")
        page.open_list("/page/finance_archive")
        page.click("btn-add-new")
        self._fill(page, title)
        page.upload("fileInput", "contoh.pdf")
        page.save_expect_toast("btn-save-data", "Berhasil disimpan")
        src = _open_file_preview(page, title, "Lihat PDF")
        assert page.http_status(src) == 200

        page.open_list("/page/finance_archive")
        page.click_row_button(title, "Edit")
        page.click("btn-remove-file")
        page.save_expect_toast("btn-save-data", "Berhasil diperbarui")
        page.wait.until(lambda _: not page.row_button(title, "Lihat PDF").is_enabled(),
                        "Tombol Lihat PDF masih aktif setelah lampiran dihapus")
        assert page.http_status(src) == 404

    def test_filter_tahun(self, page):
        """Menyaring arsip keuangan dengan tahun 2025.

        Diharapkan: hanya arsip tahun 2025 (Iuran Komite 2025) yang tampil.
        """
        page.open_list("/page/finance_archive")
        page.select("filterYear", value="2025")
        page.wait.until(lambda _: len(page.row_texts()) == 1, "Filter tahun tidak menyaring tabel")
        assert "Iuran Komite 2025" in page.row_texts()[0]

    def test_filter_kategori(self, page):
        """Menyaring arsip keuangan dengan kategori Komite / SPP Siswa.

        Diharapkan: hanya arsip berkategori SPP yang tampil.
        """
        page.open_list("/page/finance_archive")
        page.select("filterCategory", value="SPP")
        page.wait.until(lambda _: not page.has_row("Laporan BOS Triwulan 3"), "Filter kategori tidak menyaring tabel")
        assert all("SPP" in row for row in page.row_texts())

    def test_edit(self, page):
        """Mengubah judul arsip keuangan lewat tombol Edit.

        Diharapkan: pilihan Status Arsip muncul di mode edit, toast "Berhasil diperbarui!", dan tabel menampilkan judul baru.
        """
        old_title, new_title = unique("SPJ Lama"), unique("SPJ Baru")
        self._create(page, old_title)
        page.open_list("/page/finance_archive")
        page.click_row_button(old_title, "Edit")
        assert page.is_visible("group-archive-status")
        page.fill("title", new_title)
        page.save_expect_toast("btn-save-data", "Berhasil diperbarui")
        page.find_row(new_title)

    def test_hapus(self, page):
        """Menghapus arsip keuangan.

        Diharapkan: konfirmasi, toast "Data telah dihapus", dan baris hilang dari tabel.
        """
        title = unique("SPJ Hapus")
        self._create(page, title)
        page.open_list("/page/finance_archive")
        page.click_row_button(title, "Hapus")
        page.wait_modal("Hapus Data")
        page.press_modal("btnModalYes")
        page.wait_toast("Data telah dihapus")
        page.wait_row_gone(title)


class TestArsipPegawai:
    """Arsip Pegawai"""

    def _fill(self, page, name, owner="Sari Wulandari"):
        page.fill("document_name", name)
        page.select("owner_id", text=owner)
        page.select("document_type", value="SK_CPNS")
        page.select("classification_id", text="421 - Sekolah")
        page.fill("document_year", 2026)
        page.select("archive_status", value="active")
        page.select("storage_location_id", text="Lemari A - Rak 1")

    def _create(self, page, name):
        owner_id = page.api_find("teacher", "full_name", "Sari Wulandari")["id"]
        class_id = page.api_find("classification", "code", "421")["id"]
        page.api_create("employeeArchive", {"document_name": name, "owner_id": owner_id,
                                            "classification_id": class_id, "document_type": "SK_CPNS",
                                            "archive_status": "active", "document_year": 2026,
                                            "description": ""}, form=True)

    def test_tambah(self, page):
        """Menambah arsip pegawai milik Sari Wulandari.

        Diharapkan: toast "Data disimpan" dan baris baru menampilkan nama dokumen dan pemiliknya.
        """
        name = unique("SK CPNS")
        page.open_list("/page/employee_archive")
        page.click("btn-add-new")
        self._fill(page, name)
        page.save_expect_toast("btn-save-data", "Data disimpan")
        assert "Sari Wulandari" in page.find_row(name).get_attribute("textContent")

    def test_tanpa_lokasi(self, page):
        """Menambah arsip pegawai tanpa memilih lokasi simpan (lokasi tidak wajib).

        Diharapkan: toast "Data disimpan" dan baris baru tampil.
        """
        name = unique("SK Tanpa Lokasi")
        page.open_list("/page/employee_archive")
        page.click("btn-add-new")
        self._fill(page, name)
        page.select("storage_location_id", value="")
        page.save_expect_toast("btn-save-data", "Data disimpan")
        page.find_row(name)

    def test_klasifikasi_kosong(self, page):
        """Menyimpan arsip pegawai tanpa klasifikasi.

        Diharapkan: modal "Data Belum Lengkap".
        """
        page.open_list("/page/employee_archive")
        page.click("btn-add-new")
        self._fill(page, unique("SK"))
        page.select("classification_id", value="")
        page.click("btn-save-data")
        page.wait_modal("Data Belum Lengkap")

    def test_nama_dokumen_kosong(self, page):
        """Menyimpan arsip pegawai tanpa nama dokumen.

        Diharapkan: ditolak dengan pesan validasi, dan tidak ada arsip tanpa nama yang tersimpan.
        """
        page.open_list("/page/employee_archive")
        page.click("btn-add-new")
        self._fill(page, "")
        page.click("btn-save-data")
        result = page.wait_save_outcome("Data disimpan")
        assert result[0] == "modal", "Arsip pegawai tanpa nama dokumen ikut tersimpan"

    def test_tanpa_pemilik(self, page):
        """Menyimpan arsip pegawai tanpa memilih pemilik (guru/pegawai).

        Diharapkan: ditolak dengan pesan validasi yang menyebut pemilik, dan data tidak tersimpan.
        """
        name = unique("SK Tanpa Pemilik")
        page.open_list("/page/employee_archive")
        page.click("btn-add-new")
        self._fill(page, name)
        page.select("owner_id", value="")
        page.click("btn-save-data")
        result = page.wait_save_outcome("Data disimpan")
        assert result[0] == "modal", "Arsip tanpa pemilik ikut tersimpan"
        assert page.api_find("employeeArchive", "document_name", name) is None
        assert any(word in result[2].lower() for word in ("pemilik", "pegawai", "guru")), \
            f"Pesan tidak menyebut pemilik: {result[2]}"

    def test_dengan_lampiran(self, page):
        """Menambah arsip pegawai dengan lampiran PDF, lalu membukanya.

        Diharapkan: toast "Data disimpan" dan lampiran bisa dibuka dari tombol Lihat PDF (HTTP 200).
        """
        name = unique("SK Berkas")
        page.open_list("/page/employee_archive")
        page.click("btn-add-new")
        self._fill(page, name)
        page.upload("fileInput", "contoh.pdf")
        page.save_expect_toast("btn-save-data", "Data disimpan")
        src = _open_file_preview(page, name, "Lihat PDF")
        assert page.http_status(src) == 200

    def test_filter_pegawai(self, page):
        """Menyaring arsip pegawai milik Budi Santoso.

        Diharapkan: semua baris milik Budi Santoso, termasuk "SK Pangkat Budi".
        """
        page.open_list("/page/employee_archive")
        page.select("filterEmployee", text="Budi Santoso")
        page.wait.until(lambda _: all("Budi Santoso" in row for row in page.row_texts()),
                        "Filter pegawai tidak menyaring tabel")
        assert page.has_row("SK Pangkat Budi")

    def test_reset_filter(self, page):
        """Mengisi pencarian dan filter pegawai, lalu menekan Reset.

        Diharapkan: kolom pencarian dan filter kosong lagi, dan semua arsip tampil.
        """
        page.open_list("/page/employee_archive")
        total = len(page.row_texts())
        page.fill("searchInput", "Budi")
        page.select("filterEmployee", text="Budi Santoso")
        page.click("btnResetFilter")
        page.wait.until(lambda _: page.value("searchInput") == "" and len(page.row_texts()) == total,
                        "Tombol Reset tidak mengosongkan filter")

    def test_edit(self, page):
        """Mengubah nama dokumen lewat tombol Edit.

        Diharapkan: toast "Data disimpan" dan tabel menampilkan nama baru.
        """
        old_name, new_name = unique("SK Lama"), unique("SK Baru")
        self._create(page, old_name)
        page.open_list("/page/employee_archive")
        page.click_row_button(old_name, "Edit")
        page.fill("document_name", new_name)
        page.save_expect_toast("btn-save-data", "Data disimpan")
        page.find_row(new_name)

    def test_hapus(self, page):
        """Menghapus arsip pegawai.

        Diharapkan: konfirmasi, toast "Berhasil dihapus", dan baris hilang dari tabel.
        """
        name = unique("SK Hapus")
        self._create(page, name)
        page.open_list("/page/employee_archive")
        page.click_row_button(name, "Hapus")
        page.wait_modal("Hapus Data")
        page.press_modal("btnModalYes")
        page.wait_toast("Berhasil dihapus")
        page.wait_row_gone(name)
