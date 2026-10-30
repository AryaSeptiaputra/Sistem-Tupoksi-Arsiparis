"""Pembantu Selenium untuk halaman Sistem Arsip Digital."""
from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

WAIT_SECONDS = 10
# Teks sementara di tabel selama data masih diambil dari API
LOADING_TEXTS = ("Memuat", "Memindai")
MODAL = (By.CSS_SELECTOR, "#customModal.active")


def unique(prefix: str) -> str:
    """Nama unik agar data satu test tidak bentrok dengan test lain.

    Args:
        prefix: Awalan nama, misalnya "Klasifikasi".

    Returns:
        Contoh: "Klasifikasi 3fa9c1".
    """
    return f"{prefix} {secrets.token_hex(3)}"


def unique_code() -> str:
    """Kode pendek unik untuk kolom kode (maksimal 10 karakter), contoh: "T3FA9"."""
    return "T" + secrets.token_hex(2).upper()


class AppPage:
    """Satu sesi Chrome yang membuka aplikasi, beserta akun dan berkas uji."""

    def __init__(self, driver: WebDriver, base_url: str, credentials: dict[str, str],
                 files: Path, downloads: Path) -> None:
        self.driver = driver
        self.base_url = base_url
        self.credentials = credentials
        self.files = files
        self.downloads = downloads
        self.wait = WebDriverWait(driver, WAIT_SECONDS,
                                  ignored_exceptions=(StaleElementReferenceException,))

    # --- Navigasi dan sesi ---

    def open(self, path: str) -> None:
        """Membuka path aplikasi dan menunggu dokumen selesai dimuat."""
        self.driver.get(self.base_url + path)
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def open_list(self, path: str) -> None:
        """Membuka halaman daftar dan menunggu isi tabel selesai dimuat."""
        self.open(path)
        self.wait_table_loaded()

    def path(self) -> str:
        """Path URL yang sedang terbuka, contoh: "/page/dashboard"."""
        return self.driver.execute_script("return location.pathname")

    def wait_path(self, path: str) -> None:
        """Menunggu browser berpindah ke `path`."""
        self.wait.until(lambda d: d.execute_script("return location.pathname") == path,
                        f"Halaman tidak berpindah ke {path}")

    def token(self) -> str | None:
        """Token login yang tersimpan di localStorage halaman."""
        return self.driver.execute_script("return localStorage.getItem('access_token')")

    def set_token(self, value: str | None) -> None:
        """Mengganti atau menghapus token login di localStorage."""
        if value is None:
            self.driver.execute_script("localStorage.removeItem('access_token')")
        else:
            self.driver.execute_script("localStorage.setItem('access_token', arguments[0])", value)

    def submit_login(self, username: str, password: str) -> None:
        """Mengisi dan mengirim form login di halaman login."""
        self.fill("username", username)
        self.fill("password", password)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-login").click()

    def ensure_logged_in(self) -> None:
        """Memastikan ada token login; login lewat `api.auth.login` bila belum."""
        if not self.driver.current_url.startswith(self.base_url):
            self.open("/page/login")
        if self.token():
            return
        self.open("/page/login")
        self.run_js("await api.auth.login(args[0], args[1]);",
                    self.credentials["username"], self.credentials["password"])

    # --- JavaScript dan API halaman ---

    def run_js(self, body: str, *args: Any) -> Any:
        """Menjalankan isi fungsi async di halaman; argumen tersedia sebagai array `args`.

        Args:
            body: Isi fungsi async, boleh memakai `await` dan `return`.
            *args: Nilai yang bisa diubah ke JSON.

        Returns:
            Nilai `return` dari `body`.

        Raises:
            RuntimeError: Kalau `body` melempar error.
        """
        result = self.driver.execute_async_script(
            "const done = arguments[arguments.length - 1];"
            "const args = Array.prototype.slice.call(arguments, 0, -1);"
            f"(async () => {{ {body} }})()"
            ".then(value => done({ok: true, value: value === undefined ? null : value}),"
            " error => done({ok: false, error: String((error && error.message) || error)}));",
            *args)
        if not result["ok"]:
            raise RuntimeError(f"JavaScript gagal: {result['error']}")
        return result["value"]

    def api_create(self, module: str, data: dict[str, Any], form: bool = False) -> Any:
        """Membuat data lewat `api.<module>.create` milik halaman, sebagai persiapan test.

        Args:
            module: Nama grup di `api.js`, misalnya "classification" atau "incomingLetter".
            data: Isian data.
            form: True untuk endpoint yang menerima FormData (arsip dan surat).

        Returns:
            Respons API.
        """
        body = ("let payload = args[0];"
                "if (args[1]) { payload = new FormData();"
                " Object.entries(args[0]).forEach(([k, v]) => payload.append(k, v)); }"
                f"return await api.{module}.create(payload);")
        return self.run_js(body, data, form)

    def api_all(self, module: str) -> list[dict[str, Any]]:
        """Semua baris dari `api.<module>.getAll()`."""
        return self.run_js(f"return await api.{module}.getAll();")

    def api_find(self, module: str, field: str, value: Any) -> dict[str, Any] | None:
        """Baris pertama dari `api.<module>.getAll()` yang kolom `field`-nya sama dengan `value`."""
        return next((row for row in self.api_all(module) if row.get(field) == value), None)

    def http_status(self, url: str) -> int:
        """Status HTTP `url` bila diambil dari halaman yang sedang terbuka."""
        return self.run_js("const r = await fetch(args[0], {cache: 'no-store'}); return r.status;", url)

    # --- Modal dan toast (ui.js) ---

    def read_modal(self) -> tuple[str, str]:
        """Judul dan pesan modal yang sedang terbuka."""
        return (self.driver.find_element(By.ID, "modalTitle").text,
                self.driver.find_element(By.ID, "modalMessage").text)

    def wait_modal(self, title: str | None = None) -> tuple[str, str]:
        """Menunggu modal ui.alert/confirm/prompt terbuka.

        Args:
            title: Bila diisi, menunggu modal yang judulnya memuat teks ini.

        Returns:
            Judul dan pesan modal.
        """
        def opened(driver: WebDriver) -> tuple[str, str] | None:
            if not driver.find_elements(*MODAL):
                return None
            current = self.read_modal()
            return current if title is None or title in current[0] else None
        return self.wait.until(opened, f"Modal '{title or 'apa pun'}' tidak muncul")

    def press_modal(self, button_id: str) -> None:
        """Menekan tombol modal: btnModalOk, btnModalYes, btnModalCancel, atau btnModalSubmit."""
        self.wait.until(EC.element_to_be_clickable((By.ID, button_id))).click()

    def answer_prompt(self, text: str) -> None:
        """Mengisi kolom ui.prompt lalu menekan Kirim."""
        field = self.wait.until(EC.visibility_of_element_located((By.ID, "modalInput")))
        field.send_keys(text)
        self.press_modal("btnModalSubmit")

    def is_modal_open(self) -> bool:
        """True bila modal ui.js sedang terbuka."""
        return bool(self.driver.find_elements(*MODAL))

    def toast_texts(self) -> list[str]:
        """Teks semua toast yang sedang tampil."""
        return self.driver.execute_script(
            "return Array.from(document.querySelectorAll('#toastContainer .toast-box'))"
            ".map(e => e.textContent.trim());")

    def wait_toast(self, text: str) -> str:
        """Menunggu toast yang memuat `text`; toast hilang sendiri setelah 3 detik.

        Returns:
            Teks toast lengkap.
        """
        return self.wait.until(lambda _: next((t for t in self.toast_texts() if text in t), None),
                               f"Toast '{text}' tidak muncul")

    def wait_save_outcome(self, toast: str) -> tuple[str, ...]:
        """Menunggu hasil menekan tombol simpan.

        Args:
            toast: Teks toast sukses yang ditunggu.

        Returns:
            ("toast", teks) bila tersimpan, atau ("modal", judul, pesan) bila ditolak.
        """
        def outcome(_: WebDriver) -> tuple[str, ...] | None:
            if self.is_modal_open():
                return ("modal", *self.read_modal())
            text = next((t for t in self.toast_texts() if toast in t), None)
            return ("toast", text) if text else None
        return self.wait.until(outcome, f"Toast '{toast}' maupun modal tidak muncul")

    def save_expect_toast(self, button_id: str, toast: str) -> None:
        """Menekan tombol simpan lalu menunggu toast sukses.

        Raises:
            AssertionError: Kalau yang muncul justru modal validasi atau error; pesan memuat isi modal.
        """
        self.click(button_id)
        result = self.wait_save_outcome(toast)
        if result[0] == "modal":
            raise AssertionError(f"Muncul modal '{result[1]}': {result[2]}")

    # --- Form ---

    def find(self, element_id: str) -> WebElement:
        """Elemen dengan id tertentu, setelah ada di DOM."""
        return self.wait.until(EC.presence_of_element_located((By.ID, element_id)))

    def click(self, element_id: str) -> None:
        """Menggulir ke elemen lalu mengkliknya seperti pengguna."""
        element = self.wait.until(EC.element_to_be_clickable((By.ID, element_id)))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.click()

    def fill(self, element_id: str, value: Any) -> None:
        """Mengosongkan lalu mengisi input atau textarea.

        Input tanggal diisi lewat JavaScript, karena urutan ketikannya
        mengikuti locale Chrome. Event input dan change tetap dikirim.
        """
        element = self.find(element_id)
        if element.get_attribute("type") == "date":
            self.driver.execute_script(
                "arguments[0].value = arguments[1];"
                "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                element, str(value))
            return
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        if value != "":
            element.send_keys(str(value))

    def value(self, element_id: str) -> str:
        """Nilai input saat ini."""
        return self.find(element_id).get_attribute("value")

    def expect_text(self, element_id: str, expected: Any) -> None:
        """Menunggu teks elemen sama dengan `expected` (teks diisi JavaScript setelah data dimuat).

        Raises:
            AssertionError: Kalau sampai batas waktu teksnya tetap berbeda; pesan memuat teks aktual.
        """
        # Selenium mengubah spasi tak terputus (U+00A0) menjadi spasi biasa,
        # padahal Intl.NumberFormat, misalnya "Rp 2,3 jt", memakai U+00A0
        expected_text = str(expected).replace(" ", " ")
        try:
            self.wait.until(lambda d: d.find_element(By.ID, element_id).text.strip() == expected_text)
        except TimeoutException:
            actual = self.driver.find_element(By.ID, element_id).text.strip()
            raise AssertionError(f"#{element_id} menampilkan '{actual}', seharusnya '{expected_text}'") from None

    def select(self, element_id: str, *, value: Any = None, text: str | None = None) -> None:
        """Memilih opsi dropdown setelah opsinya selesai dimuat dari API.

        Args:
            element_id: Id elemen select.
            value: Nilai opsi yang dipilih.
            text: Bila `value` kosong, opsi pertama yang teksnya memuat teks ini.
        """
        element = self.find(element_id)

        def matching_option(_: WebDriver) -> WebElement | None:
            for option in Select(element).options:
                if value is not None and option.get_attribute("value") == str(value):
                    return option
                if value is None and text is not None and text in option.text:
                    return option
            return None

        option = self.wait.until(matching_option, f"Opsi '{value if value is not None else text}' tidak ada di #{element_id}")
        Select(element).select_by_value(option.get_attribute("value"))

    def option_texts(self, element_id: str) -> list[str]:
        """Teks semua opsi dropdown."""
        return [option.text for option in Select(self.find(element_id)).options]

    def upload(self, element_id: str, filename: str) -> None:
        """Memilih berkas uji dari folder kerja untuk input file (boleh tersembunyi)."""
        self.driver.find_element(By.ID, element_id).send_keys(str(self.files / filename))

    def is_visible(self, element_id: str) -> bool:
        """True bila elemen ada dan tampil di layar."""
        elements = self.driver.find_elements(By.ID, element_id)
        return bool(elements) and elements[0].is_displayed()

    # --- Tabel ---

    def row_texts(self) -> list[str]:
        """Teks setiap baris `#table-body`, dengan spasi dirapikan."""
        return self.driver.execute_script(
            "return Array.from(document.querySelectorAll('#table-body tr'))"
            ".map(r => r.textContent.replace(/\\s+/g, ' ').trim());")

    def wait_table_loaded(self) -> None:
        """Menunggu tabel selesai memuat data dari API."""
        def loaded(_: WebDriver) -> bool:
            rows = self.row_texts()
            return bool(rows) and not any(text in rows[0] for text in LOADING_TEXTS)
        self.wait.until(loaded, "Tabel tidak selesai dimuat")

    def find_row(self, text: str) -> WebElement:
        """Menunggu baris tabel yang memuat `text`."""
        def matching_row(driver: WebDriver) -> WebElement | None:
            for row in driver.find_elements(By.CSS_SELECTOR, "#table-body tr"):
                if text in " ".join(row.get_attribute("textContent").split()):
                    return row
            return None
        return self.wait.until(matching_row, f"Baris berisi '{text}' tidak muncul di tabel")

    def has_row(self, text: str) -> bool:
        """True bila saat ini ada baris yang memuat `text`."""
        return any(text in row for row in self.row_texts())

    def wait_row_gone(self, text: str) -> None:
        """Menunggu sampai tidak ada baris yang memuat `text`."""
        self.wait.until(lambda _: not self.has_row(text), f"Baris berisi '{text}' masih ada di tabel")

    def row_button(self, text: str, title: str) -> WebElement:
        """Tombol aksi (berdasarkan atribut title) di baris yang memuat `text`."""
        return self.find_row(text).find_element(By.CSS_SELECTOR, f"button[title='{title}']")

    def click_row_button(self, text: str, title: str) -> None:
        """Mengklik tombol aksi, misalnya "Edit" atau "Hapus", di baris yang memuat `text`."""
        button = self.row_button(text, title)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        button.click()

    # --- Konsol, jaringan, dan unduhan ---

    def console_errors(self) -> list[str]:
        """Pesan konsol level SEVERE sejak pemanggilan sebelumnya (buffer ikut dikosongkan)."""
        return [entry["message"] for entry in self.driver.get_log("browser")
                if entry["level"] == "SEVERE"]

    def external_requests(self) -> list[str]:
        """URL resource yang diambil dari luar origin aplikasi."""
        return self.driver.execute_script(
            "return performance.getEntriesByType('resource').map(e => e.name)"
            ".filter(u => !u.startsWith(location.origin) && !/^(data|blob):/.test(u));")

    def wait_download(self, filename: str, timeout: int = 20) -> Path:
        """Menunggu berkas `filename` selesai diunduh ke folder unduhan."""
        target = self.downloads / filename

        # Chrome menulis ke berkas .crdownload lalu mengganti namanya setelah unduhan selesai
        def finished(_: WebDriver) -> bool:
            return target.exists()
        WebDriverWait(self.driver, timeout).until(finished, f"Berkas {filename} tidak terunduh")
        return target
