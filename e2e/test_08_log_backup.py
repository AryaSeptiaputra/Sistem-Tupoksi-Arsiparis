"""Test end-to-end Log Aktivitas dan Backup Database."""
import csv
import datetime
import io
import secrets
import time

from helpers import unique, unique_code

SQLITE_HEADER = b"SQLite format 3\x00"
# Nama tampilan akun uji dari e2e/seed.py; kolom pelaku di Log menampilkan nama ini, bukan username
OPERATOR_NAME = "Operator Uji"


def _create_classification(page, name):
    page.api_create("classification", {"code": unique_code(), "name": name, "description": None,
                                       "retention_active_period": 1, "retention_inactive_period": 1,
                                       "final_action": "permanent"})


def _export_csv(page):
    # Berkas lama dihapus dulu; kalau tidak, Chrome menyimpan unduhan baru sebagai "... (1).csv"
    csv_path = page.downloads / "log_aktivitas_sistem.csv"
    if csv_path.exists():
        csv_path.unlink()
    page.click("btnExport")
    page.wait_toast("File CSV berhasil diunduh")
    # utf-8-sig membuang BOM yang ditambahkan untuk Excel
    content = page.wait_download(csv_path.name).read_text(encoding="utf-8-sig")
    return list(csv.reader(io.StringIO(content)))


class TestLog:
    """Log Aktivitas"""

    def test_aksi_tercatat(self, page):
        """Menambah klasifikasi, lalu membuka Log Aktivitas.

        Diharapkan: ada baris "Menambah Klasifikasi" dengan nama klasifikasi itu dan pelakunya nama operator.
        """
        name = unique("Klasifikasi Log")
        _create_classification(page, name)
        page.open_list("/page/log")
        row = page.find_row(name).get_attribute("textContent")
        assert "Menambah Klasifikasi" in row and OPERATOR_NAME in row

    def test_cari(self, page):
        """Mencari log dengan kata unik dari nama klasifikasi.

        Diharapkan: hanya baris log yang memuat kata itu yang tampil.
        """
        token = secrets.token_hex(4)
        _create_classification(page, f"Cari {token}")
        page.open_list("/page/log")
        page.fill("searchInput", token)
        page.wait.until(lambda _: len(page.row_texts()) == 1, "Pencarian log tidak menyaring tabel")
        assert token in page.row_texts()[0]

    def test_filter_pelaku(self, page):
        """Menyaring log dengan pelaku Operator, lalu Sistem.

        Diharapkan: filter Operator hanya menampilkan log akun operator; filter Sistem tidak menampilkan log akun operator.
        """
        page.open_list("/page/log")
        page.select("filterUser", value="operator")
        page.wait.until(lambda _: all(OPERATOR_NAME in row for row in page.row_texts()),
                        "Filter Operator menampilkan log pelaku lain")
        page.select("filterUser", value="sistem")
        page.wait.until(lambda _: not any(OPERATOR_NAME in row for row in page.row_texts()),
                        "Filter Sistem masih menampilkan log operator")

    def test_filter_tanggal_dan_reset(self, page):
        """Menyaring log mulai besok, lalu menekan Reset.

        Diharapkan: muncul "Tidak ada aktivitas tercatat."; setelah Reset muncul toast "Filter direset" dan semua log tampil lagi.
        """
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        page.open_list("/page/log")
        total = len(page.row_texts())
        page.fill("startDate", tomorrow)
        page.wait.until(lambda _: "Tidak ada aktivitas tercatat" in page.row_texts()[0],
                        "Filter tanggal tidak menyaring log")
        page.click("btnResetFilter")
        page.wait_toast("Filter direset")
        assert len(page.row_texts()) == total

    def test_export_csv(self, page):
        """Menekan Export CSV.

        Diharapkan: toast "File CSV berhasil diunduh" dan berkas log_aktivitas_sistem.csv berisi header plus satu baris per log.
        """
        page.open_list("/page/log")
        total_logs = len(page.api_all("log"))
        rows = _export_csv(page)
        assert rows[0] == ["Timestamp", "Username", "Aktivitas"]
        assert len(rows) - 1 == total_logs, f"CSV berisi {len(rows) - 1} log, seharusnya {total_logs}"

    def test_export_csv_tanda_pagar(self, page):
        """Menambah klasifikasi bernama "Rak #2 ...", lalu menekan Export CSV.

        Diharapkan: CSV tetap memuat semua log, termasuk log klasifikasi bertanda # itu.
        """
        token = secrets.token_hex(3)
        _create_classification(page, f"Rak #2 {token}")
        page.open_list("/page/log")
        total_logs = len(page.api_all("log"))
        rows = _export_csv(page)
        assert any(f"Rak #2 {token}" in row[2] for row in rows[1:]), "Isi CSV terpotong di tanda #"
        assert len(rows) - 1 == total_logs


class TestBackup:
    """Backup Database"""

    def _backup_now(self, page):
        # Nama berkas backup memakai stempel waktu per detik; jeda ini mencegah dua backup bernama sama
        time.sleep(1.1)
        page.open_list("/page/backup")
        page.click("btnTriggerBackup")
        page.wait_modal("Backup Database")
        page.press_modal("btnModalYes")
        page.wait_toast("Backup Berhasil Disimpan")
        page.wait_table_loaded()
        # Riwayat diurutkan dari yang terbaru; nama berkas ada di awal baris
        return page.row_texts()[0].split()[0]

    def test_backup_manual(self, page):
        """Menekan "Backup Sekarang" dan mengonfirmasi.

        Diharapkan: toast "Backup Berhasil Disimpan!", baris baru berisi nama berkas .db, dan berkasnya ada di folder backup server.
        """
        filename = self._backup_now(page)
        assert filename.startswith("backup_") and filename.endswith(".db")
        assert (page.files / "database" / "backups" / filename).exists()

    def test_cari(self, page):
        """Mencari riwayat backup dengan nama berkas, lalu dengan kata yang tidak ada.

        Diharapkan: berkas yang dicari tampil; kata yang tidak ada menampilkan "Belum ada riwayat backup."
        """
        filename = self._backup_now(page)
        page.fill("searchInput", filename)
        page.wait.until(lambda _: len(page.row_texts()) == 1 and filename in page.row_texts()[0],
                        "Pencarian riwayat backup tidak menyaring tabel")
        page.fill("searchInput", "tidakada")
        page.wait.until(lambda _: "Belum ada riwayat backup" in page.row_texts()[0],
                        "Pencarian tanpa hasil tidak menampilkan pesan kosong")

    def test_filter_status_gagal(self, page):
        """Memilih filter Status "Failed (Gagal)" saat semua backup berhasil.

        Diharapkan: backup yang berhasil tidak ditampilkan.
        """
        self._backup_now(page)
        page.select("filterStatus", value="failed")
        page.wait.until(lambda _: not any("Success" in row for row in page.row_texts()),
                        "Filter status tidak menyaring riwayat backup")

    def test_unduh(self, page):
        """Menekan tombol unduh pada riwayat backup.

        Diharapkan: toast "Mengunduh file..." dan berkas yang terunduh adalah database SQLite yang valid.
        """
        filename = self._backup_now(page)
        page.click_row_button(filename, "Download")
        page.wait_toast("Mengunduh file")
        assert page.wait_download(filename).read_bytes()[:16] == SQLITE_HEADER

    def test_restore(self, page):
        """Membuat backup, menambah klasifikasi, lalu me-restore backup tadi dengan dua kali konfirmasi.

        Diharapkan: modal "Restore Sukses", klasifikasi yang dibuat setelah backup hilang, dan berkas pengaman pre_restore_*.db dibuat.
        """
        backups = page.files / "database" / "backups"
        filename = self._backup_now(page)
        name = unique("Setelah Backup")
        _create_classification(page, name)
        page.click_row_button(filename, "Restore Database")
        page.wait_modal("Peringatan Restore")
        page.press_modal("btnModalYes")
        page.wait_modal("Konfirmasi Terakhir")
        page.press_modal("btnModalYes")
        page.wait_modal("Restore Sukses")
        page.press_modal("btnModalOk")
        page.wait_table_loaded()
        assert page.api_find("classification", "name", name) is None
        assert list(backups.glob("pre_restore_*.db")), "Berkas pre_restore_*.db tidak dibuat"
