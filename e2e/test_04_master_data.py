"""Test end-to-end master data: Klasifikasi, Lokasi Simpan, Guru, dan Master Referensi."""
import secrets

from helpers import unique, unique_code


def _create_classification(page, name, code=None):
    page.api_create("classification", {
        "code": code or unique_code(), "name": name, "description": None,
        "retention_active_period": 1, "retention_inactive_period": 2, "final_action": "permanent"})
    return page.api_find("classification", "name", name)


def _create_finance_archive(page, title, classification_id, storage_location_id=None):
    data = {"title": title, "fiscal_year": 2026, "category": "BOS_REG", "amount": 100000,
            "description": "", "classification_id": classification_id}
    if storage_location_id:
        data["storage_location_id"] = storage_location_id
    page.api_create("financeArchive", data, form=True)


def _nip() -> str:
    return "19" + "".join(secrets.choice("0123456789") for _ in range(16))


class TestKlasifikasi:
    """Klasifikasi"""

    def test_tambah(self, page):
        """Menambah klasifikasi dengan kode, nama, retensi, nasib akhir, dan deskripsi.

        Diharapkan: toast "Data berhasil disimpan!" dan klasifikasi baru tampil di tabel.
        """
        code, name = unique_code(), unique("Klasifikasi")
        page.open_list("/page/classification")
        page.click("btn-add-new")
        page.fill("inputCode", code)
        page.fill("inputName", name)
        page.fill("inputRetActive", 2)
        page.fill("inputRetInactive", 3)
        page.select("inputFinalAction", value="destroy")
        page.fill("inputDescription", "Dibuat oleh test")
        page.click("btnSave")
        page.wait_toast("Data berhasil disimpan")
        row = page.find_row(name).get_attribute("textContent")
        assert code in row and "DESTROY" in row

    def test_pratinjau_badge(self, page):
        """Mengetik kode dan nama di form tambah klasifikasi.

        Diharapkan: pratinjau badge langsung menampilkan kode dan nama yang diketik.
        """
        page.open_list("/page/classification")
        page.click("btn-add-new")
        page.fill("inputCode", "421.9")
        page.fill("inputName", "Uji Pratinjau")
        assert page.find("previewCodeTxt").text == "421.9"
        assert page.find("previewNameTxt").text == "Uji Pratinjau"

    def test_wajib_kosong(self, page):
        """Menyimpan klasifikasi tanpa kode.

        Diharapkan: modal "Data Belum Lengkap" dan data tidak tersimpan.
        """
        name = unique("Tanpa Kode")
        page.open_list("/page/classification")
        page.click("btn-add-new")
        page.fill("inputName", name)
        page.click("btnSave")
        page.wait_modal("Data Belum Lengkap")
        assert page.api_find("classification", "name", name) is None

    def test_kode_duplikat(self, page):
        """Menambah klasifikasi dengan kode yang sudah dipakai klasifikasi lain.

        Diharapkan: modal "Gagal Menyimpan" yang menyebut kode atau nama sudah ada.
        """
        existing = _create_classification(page, unique("Asli"))
        page.open_list("/page/classification")
        page.click("btn-add-new")
        page.fill("inputCode", existing["code"])
        page.fill("inputName", unique("Duplikat"))
        page.click("btnSave")
        _, message = page.wait_modal("Gagal Menyimpan")
        assert "sudah ada" in message.lower()

    def test_edit(self, page):
        """Mengubah nama klasifikasi lewat tombol Edit.

        Diharapkan: toast "Data berhasil diperbarui!" dan tabel menampilkan nama baru.
        """
        old_name, new_name = unique("Lama"), unique("Baru")
        _create_classification(page, old_name)
        page.open_list("/page/classification")
        page.click_row_button(old_name, "Edit")
        assert page.value("inputName") == old_name
        page.fill("inputName", new_name)
        page.click("btnSave")
        page.wait_toast("Data berhasil diperbarui")
        page.find_row(new_name)
        assert not page.has_row(old_name)

    def test_cari_dan_reset(self, page):
        """Mencari klasifikasi berdasarkan nama, lalu menekan Reset.

        Diharapkan: hanya baris yang cocok yang tampil; setelah Reset semua baris tampil lagi.
        """
        target = unique("Dicari")
        _create_classification(page, target)
        page.open_list("/page/classification")
        total = len(page.row_texts())
        page.fill("searchInput", target)
        page.wait.until(lambda _: len(page.row_texts()) == 1, "Pencarian tidak menyaring tabel")
        assert target in page.row_texts()[0]
        page.click("btnResetFilter")
        page.wait_toast("Filter direset")
        assert len(page.row_texts()) == total

    def test_hapus(self, page):
        """Menghapus klasifikasi yang belum dipakai arsip mana pun.

        Diharapkan: muncul konfirmasi, lalu toast "Data dihapus" dan baris hilang dari tabel.
        """
        name = unique("Dihapus")
        _create_classification(page, name)
        page.open_list("/page/classification")
        page.click_row_button(name, "Hapus")
        page.wait_modal("Hapus Klasifikasi")
        page.press_modal("btnModalYes")
        page.wait_toast("Data dihapus")
        page.wait_row_gone(name)

    def test_hapus_yang_dipakai(self, page):
        """Menghapus klasifikasi yang masih dipakai arsip keuangan.

        Diharapkan: modal "Gagal Hapus" yang menyebut klasifikasi masih digunakan, dan baris tetap ada.
        """
        name = unique("Dipakai")
        classification = _create_classification(page, name)
        _create_finance_archive(page, unique("Arsip pemakai"), classification["id"])
        page.open_list("/page/classification")
        page.click_row_button(name, "Hapus")
        page.press_modal("btnModalYes")
        _, message = page.wait_modal("Gagal Hapus")
        assert "digunakan" in message.lower()
        assert page.api_find("classification", "name", name) is not None


class TestLokasiSimpan:
    """Lokasi Simpan"""

    def test_tambah(self, page):
        """Menambah lokasi simpan dengan nama dan keterangan.

        Diharapkan: toast "Berhasil disimpan!" dan lokasi baru tampil di tabel.
        """
        name = unique("Lemari")
        page.open_list("/page/storage_location")
        page.click("btn-add-new")
        page.fill("inputName", name)
        page.fill("inputDescription", "Rak paling atas")
        page.click("btnSave")
        page.wait_toast("Berhasil disimpan")
        assert "Rak paling atas" in page.find_row(name).get_attribute("textContent")

    def test_nama_kosong(self, page):
        """Menyimpan lokasi tanpa nama.

        Diharapkan: modal "Data Tidak Lengkap".
        """
        page.open_list("/page/storage_location")
        page.click("btn-add-new")
        page.fill("inputDescription", "Tanpa nama")
        page.click("btnSave")
        page.wait_modal("Data Tidak Lengkap")

    def test_nama_duplikat(self, page):
        """Menambah lokasi dengan nama yang sudah ada.

        Diharapkan: modal "Gagal Menyimpan" dan tidak ada baris ganda.
        """
        page.open_list("/page/storage_location")
        page.click("btn-add-new")
        page.fill("inputName", "Lemari A - Rak 1")
        page.click("btnSave")
        page.wait_modal("Gagal Menyimpan")
        assert sum("Lemari A - Rak 1" == row["name"] for row in page.api_all("storageLocation")) == 1

    def test_edit(self, page):
        """Mengubah nama lokasi lewat tombol Edit.

        Diharapkan: toast "Berhasil diperbarui!" dan tabel menampilkan nama baru.
        """
        old_name, new_name = unique("Rak Lama"), unique("Rak Baru")
        page.api_create("storageLocation", {"name": old_name, "description": None})
        page.open_list("/page/storage_location")
        page.click_row_button(old_name, "Edit")
        page.fill("inputName", new_name)
        page.click("btnSave")
        page.wait_toast("Berhasil diperbarui")
        page.find_row(new_name)

    def test_cari_dan_reset(self, page):
        """Mencari lokasi berdasarkan nama, lalu menekan Reset.

        Diharapkan: hanya baris yang cocok yang tampil; setelah Reset semua baris tampil lagi.
        """
        target = unique("Boks")
        page.api_create("storageLocation", {"name": target, "description": None})
        page.open_list("/page/storage_location")
        total = len(page.row_texts())
        page.fill("searchInput", target)
        page.wait.until(lambda _: len(page.row_texts()) == 1, "Pencarian tidak menyaring tabel")
        page.click("btnResetFilter")
        page.wait_toast("Filter direset")
        assert len(page.row_texts()) == total

    def test_hapus(self, page):
        """Menghapus lokasi yang belum dipakai arsip.

        Diharapkan: toast "Lokasi dihapus" dan baris hilang dari tabel.
        """
        name = unique("Rak Hapus")
        page.api_create("storageLocation", {"name": name, "description": None})
        page.open_list("/page/storage_location")
        page.click_row_button(name, "Hapus")
        page.wait_modal("Hapus Lokasi")
        page.press_modal("btnModalYes")
        page.wait_toast("Lokasi dihapus")
        page.wait_row_gone(name)

    def test_hapus_yang_dipakai(self, page):
        """Menghapus lokasi yang masih dipakai arsip keuangan.

        Diharapkan: penghapusan ditolak (seperti klasifikasi yang masih dipakai) dan lokasi arsip tidak hilang.
        """
        name, title = unique("Rak Dipakai"), unique("Arsip di rak")
        page.api_create("storageLocation", {"name": name, "description": None})
        location = page.api_find("storageLocation", "name", name)
        class_id = page.api_find("classification", "code", "421")["id"]
        _create_finance_archive(page, title, class_id, location["id"])
        page.open_list("/page/storage_location")
        page.click_row_button(name, "Hapus")
        page.press_modal("btnModalYes")
        page.wait.until(lambda _: page.is_modal_open() or not page.has_row(name), "Tidak ada respons setelah hapus")
        archive = page.api_find("financeArchive", "title", title)
        assert page.api_find("storageLocation", "name", name) is not None,             f"Lokasi terhapus; lokasi arsip yang memakainya kini {archive['storage_location_name']!r}"


class TestGuru:
    """Guru"""

    def _fill_form(self, page, nip, name):
        page.fill("inputIdentity", nip)
        page.fill("inputName", name)
        page.select("inputGender", value="L")
        page.select("inputRank", text="Penata Muda Tingkat I")
        page.select("inputEmpStatus", text="Pegawai Negeri Sipil")
        page.fill("inputAddress", "Jl. Uji No. 1")

    def test_tambah(self, page):
        """Menambah guru dengan NIP, nama, jenis kelamin, pangkat, dan status kepegawaian.

        Diharapkan: toast "Guru berhasil ditambahkan!" dan guru baru tampil di tabel dengan status Aktif.
        """
        nip, name = _nip(), unique("Guru")
        page.open_list("/page/teacher")
        page.click("btn-add-new")
        self._fill_form(page, nip, name)
        page.click("btnSave")
        page.wait_toast("Guru berhasil ditambahkan")
        row = page.find_row(nip).get_attribute("textContent")
        assert name in row and "Aktif" in row

    def test_wajib_kosong(self, page):
        """Menyimpan guru tanpa memilih jenis kelamin.

        Diharapkan: modal "Data Belum Lengkap".
        """
        page.open_list("/page/teacher")
        page.click("btn-add-new")
        page.fill("inputIdentity", _nip())
        page.fill("inputName", unique("Guru"))
        page.select("inputEmpStatus", text="Guru Tidak Tetap")
        page.click("btnSave")
        page.wait_modal("Data Belum Lengkap")

    def test_nip_duplikat(self, page):
        """Menambah guru dengan NIP yang sudah dipakai guru lain.

        Diharapkan: modal "Gagal Menyimpan" dan tidak ada guru ganda.
        """
        page.open_list("/page/teacher")
        page.click("btn-add-new")
        self._fill_form(page, "198001012005011001", unique("Guru Kembar"))
        page.click("btnSave")
        page.wait_modal("Gagal Menyimpan")
        assert sum(t["identity_number"] == "198001012005011001" for t in page.api_all("teacher")) == 1

    def test_edit(self, page):
        """Mengubah nama guru lewat tombol Edit.

        Diharapkan: kolom NIP terkunci, toast "Data guru berhasil diperbarui!", dan tabel menampilkan nama baru.
        """
        nip, new_name = _nip(), unique("Guru Baru")
        page.api_create("teacher", {"identity_number": nip, "full_name": unique("Guru Lama"), "gender": "P",
                                    "employment_status": "GTT", "rank": "", "status": "aktif",
                                    "address": ""})
        page.open_list("/page/teacher")
        page.click_row_button(nip, "Edit")
        assert page.find("inputIdentity").get_attribute("readonly") is not None
        page.fill("inputName", new_name)
        page.click("btnSave")
        page.wait_toast("Data guru berhasil diperbarui")
        assert new_name in page.find_row(nip).get_attribute("textContent")

    def test_filter_status_kepegawaian(self, page):
        """Menyaring guru berdasarkan status kepegawaian "Guru Tidak Tetap".

        Diharapkan: semua baris yang tampil berstatus Guru Tidak Tetap.
        """
        page.open_list("/page/teacher")
        page.select("filterEmpStatus", value="GTT")
        page.wait.until(lambda _: all("Guru Tidak Tetap" in row for row in page.row_texts()),
                        "Filter status kepegawaian tidak menyaring tabel")
        assert any("Sari Wulandari" in row for row in page.row_texts())

    def test_hapus(self, page):
        """Menghapus guru yang tidak punya arsip.

        Diharapkan: toast "Data guru dihapus" dan baris hilang dari tabel.
        """
        nip = _nip()
        page.api_create("teacher", {"identity_number": nip, "full_name": unique("Guru Hapus"), "gender": "L",
                                    "employment_status": "GTT", "rank": "", "status": "aktif",
                                    "address": ""})
        page.open_list("/page/teacher")
        page.click_row_button(nip, "Hapus")
        page.wait_modal("Hapus Guru")
        page.press_modal("btnModalYes")
        page.wait_toast("Data guru dihapus")
        page.wait_row_gone(nip)

    def test_hapus_yang_punya_arsip(self, page):
        """Menghapus guru yang masih memiliki arsip pegawai.

        Diharapkan: penghapusan ditolak (seperti klasifikasi dan lokasi yang masih dipakai), dan arsip pegawainya tetap ada.
        """
        nip, document = _nip(), unique("SK Guru")
        page.api_create("teacher", {"identity_number": nip, "full_name": unique("Guru Berarsip"), "gender": "L",
                                    "employment_status": "GTT", "rank": "", "status": "aktif",
                                    "address": ""})
        owner_id = page.api_find("teacher", "identity_number", nip)["id"]
        class_id = page.api_find("classification", "code", "421")["id"]
        page.api_create("employeeArchive", {"document_name": document, "owner_id": owner_id,
                                            "classification_id": class_id, "document_type": "SK_PANGKAT",
                                            "archive_status": "active", "document_year": 2026,
                                            "description": ""}, form=True)
        page.open_list("/page/teacher")
        page.click_row_button(nip, "Hapus")
        page.press_modal("btnModalYes")
        page.wait.until(lambda _: page.is_modal_open() or not page.has_row(nip), "Tidak ada respons setelah hapus")
        assert page.api_find("employeeArchive", "document_name", document) is not None, \
            "Guru terhapus beserta arsip pegawainya tanpa peringatan"


class TestMasterReferensi:
    """Master Referensi"""

    def _open_category(self, page, category):
        page.open_list("/page/reference")
        page.select("categoryFilter", value=category)
        page.wait_table_loaded()

    def test_ganti_kategori(self, page):
        """Memilih kategori "Kategori Keuangan".

        Diharapkan: tabel menampilkan referensi kategori itu, misalnya "BOS Reguler".
        """
        self._open_category(page, "finance_category")
        page.find_row("BOS Reguler")
        assert not page.has_row("Kimia Industri")

    def test_tambah_dengan_kode_otomatis(self, page):
        """Menambah referensi keuangan baru dengan mengetik namanya saja.

        Diharapkan: kode terisi otomatis dari nama (huruf kecil, spasi menjadi garis bawah), toast "Data berhasil ditambahkan!", dan baris baru tampil.
        """
        token = secrets.token_hex(3)
        self._open_category(page, "finance_category")
        page.click("btn-add-new")
        page.fill("inputName", f"Dana Uji {token}")
        assert page.value("inputCode") == f"dana_uji_{token}"
        page.click("btnSave")
        page.wait_toast("Data berhasil ditambahkan")
        page.find_row(f"Dana Uji {token}")

    def test_wajib_kosong(self, page):
        """Menyimpan referensi tanpa nama dan kode.

        Diharapkan: modal "Data Kurang".
        """
        self._open_category(page, "finance_category")
        page.click("btn-add-new")
        page.click("btnSave")
        page.wait_modal("Data Kurang")

    def test_tambah_status_nonaktif(self, page):
        """Menambah referensi dengan pilihan status Non-Aktif di form.

        Diharapkan: referensi tersimpan dengan status Non-Aktif.
        """
        name = unique("Dana Nonaktif")
        self._open_category(page, "finance_category")
        page.click("btn-add-new")
        page.fill("inputName", name)
        page.select("inputIsActive", value="false")
        page.click("btnSave")
        page.wait_toast("Data berhasil ditambahkan")
        assert "Non-Aktif" in page.find_row(name).get_attribute("textContent"), "Referensi tersimpan sebagai Aktif"

    def test_edit(self, page):
        """Mengubah nama referensi lewat tombol Edit.

        Diharapkan: kolom kode terkunci, toast "Data berhasil diperbarui!", dan tabel menampilkan nama baru.
        """
        token = secrets.token_hex(3)
        page.run_js("return await api.reference.create(args[0]);",
                    {"category": "finance_category", "code": f"edit_{token}", "name": f"Edit {token}",
                     "sort_order": 9, "description": "", "is_active": True})
        self._open_category(page, "finance_category")
        page.click_row_button(f"Edit {token}", "Edit")
        assert page.find("inputCode").get_attribute("readonly") is not None
        page.fill("inputName", f"Sudah Diedit {token}")
        page.click("btnSave")
        page.wait_toast("Data berhasil diperbarui")
        page.find_row(f"Sudah Diedit {token}")

    def test_nonaktifkan(self, page):
        """Menonaktifkan referensi lewat tombol Non-aktifkan.

        Diharapkan: konfirmasi, toast "Data dinonaktifkan", dan baris berlabel Non-Aktif.
        """
        token = secrets.token_hex(3)
        page.run_js("return await api.reference.create(args[0]);",
                    {"category": "finance_category", "code": f"off_{token}", "name": f"Matikan {token}",
                     "sort_order": 9, "description": "", "is_active": True})
        self._open_category(page, "finance_category")
        page.click_row_button(f"Matikan {token}", "Non-aktifkan")
        page.wait_modal("Non-aktifkan")
        page.press_modal("btnModalYes")
        page.wait_toast("Data dinonaktifkan")
        page.wait.until(lambda _: "Non-Aktif" in page.find_row(f"Matikan {token}").get_attribute("textContent"),
                        "Baris tidak berlabel Non-Aktif")

    def test_nonaktif_hilang_dari_dropdown(self, page):
        """Menonaktifkan kategori keuangan, lalu membuka form tambah Arsip Keuangan.

        Diharapkan: kategori yang nonaktif tidak muncul di dropdown Kategori (sesuai pesan "disembunyikan dari dropdown sistem").
        """
        token = secrets.token_hex(3)
        name = f"Kategori Lama {token}"
        page.run_js("return await api.reference.create(args[0]);",
                    {"category": "finance_category", "code": f"lama_{token}", "name": name,
                     "sort_order": 9, "description": "", "is_active": True})
        ref_id = page.run_js("const r = await api.reference.getByCategory('finance_category');"
                             "return r.data.find(x => x.code === args[0]).id;", f"lama_{token}")
        page.run_js("return await api.reference.delete(args[0]);", ref_id)
        page.open_list("/page/finance_archive")
        page.click("btn-add-new")
        page.select("category", value="BOS_REG")
        assert name not in page.option_texts("category"), "Kategori nonaktif masih muncul di dropdown form"

    def test_nilai_nonaktif_tetap_saat_edit(self, page):
        """Membuka edit arsip keuangan yang kategorinya sudah dinonaktifkan, lalu menyimpannya tanpa perubahan.

        Diharapkan: dropdown Kategori menampilkan kategori lama berlabel "(nonaktif)", dan setelah disimpan kategori arsip tidak berubah.
        """
        token = secrets.token_hex(3)
        code, title = f"pakai_{token}", unique("Arsip Kategori Lama")
        page.run_js("return await api.reference.create(args[0]);",
                    {"category": "finance_category", "code": code, "name": f"Kategori Dipakai {token}",
                     "sort_order": 9, "description": "", "is_active": True})
        class_id = page.api_find("classification", "code", "421")["id"]
        page.api_create("financeArchive", {"title": title, "fiscal_year": 2026, "category": code, "amount": 1000,
                                           "description": "", "classification_id": class_id}, form=True)
        ref_id = page.run_js("const r = await api.reference.getByCategory('finance_category');"
                             "return r.data.find(x => x.code === args[0]).id;", code)
        page.run_js("return await api.reference.delete(args[0]);", ref_id)

        page.open_list("/page/finance_archive")
        page.click_row_button(title, "Edit")
        assert page.value("category") == code
        selected = page.driver.execute_script(
            "const s = document.getElementById('category'); return s.options[s.selectedIndex].text;")
        assert "(nonaktif)" in selected
        page.save_expect_toast("btn-save-data", "Berhasil diperbarui")
        assert page.api_find("financeArchive", "title", title)["category"] == code
