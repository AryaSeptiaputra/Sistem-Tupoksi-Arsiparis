"""
Fixture test end-to-end: server sementara, data awal, Chrome, dan laporan hasil.

Menjalankan semua test dari folder project:
    .venv38\\Scripts\\python.exe -m pytest e2e -v
Browser ditampilkan bila env E2E_HEADED=1. Hasil ditulis ke e2e/hasil/.
ChromeDriver dicari Selenium Manager; isi env E2E_CHROMEDRIVER dengan path
chromedriver.exe bila Selenium Manager gagal mengunduh atau salah versi.

Server memakai cwd folder sementara, sehingga .env, database, upload, dan
backup milik project tidak tersentuh.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from helpers import AppPage

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HASIL_DIR = PROJECT_ROOT / "e2e" / "hasil"
SERVER_START_SECONDS = 30
# PDF satu halaman kosong; cukup untuk diunggah dan ditampilkan kembali
SAMPLE_PDF = (b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
              b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
              b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]>>endobj\n"
              b"trailer<</Root 1 0 R>>\n%%EOF\n")
RESULTS = pytest.StashKey[list]()


# --- Server sementara ---

def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _run_seed(env: dict[str, str], workdir: Path) -> None:
    result = subprocess.run([sys.executable, str(PROJECT_ROOT / "e2e" / "seed.py")],
                            cwd=workdir, env=env, capture_output=True, text=True,
                            encoding="utf-8", timeout=120)
    (HASIL_DIR / "seed.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        pytest.exit(f"Seed gagal; lihat {HASIL_DIR / 'seed.log'}", returncode=1)


def _wait_until_ready(url: str, process: subprocess.Popen) -> None:
    # Tanpa proxy: permintaan ke 127.0.0.1 tidak boleh lewat proxy sistem
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    deadline = time.monotonic() + SERVER_START_SECONDS
    while time.monotonic() < deadline:
        if process.poll() is not None:
            pytest.exit(f"Server berhenti saat start; lihat {HASIL_DIR / 'server.log'}", returncode=1)
        try:
            with opener.open(f"{url}/page/login", timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError, socket.timeout):
            time.sleep(0.3)
    pytest.exit(f"Server tidak siap dalam {SERVER_START_SECONDS} detik", returncode=1)


@pytest.fixture(scope="session")
def credentials() -> dict[str, str]:
    """Akun operator sekali pakai; dibangkitkan ulang setiap kali test dijalankan."""
    return {"username": f"uji_{secrets.token_hex(3)}",
            "password": f"Uji{secrets.token_hex(6)}9"}


@pytest.fixture(scope="session")
def workdir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Folder kerja server: database, upload, backup, dan berkas uji."""
    path = tmp_path_factory.mktemp("server")
    (path / "contoh.pdf").write_bytes(SAMPLE_PDF)
    (path / "bukan_pdf.txt").write_text("bukan pdf", encoding="utf-8")
    return path


@pytest.fixture(scope="session")
def server_env(workdir: Path, credentials: dict[str, str]) -> dict[str, str]:
    """Env server uji; kunci JWT dan sesi dibangkitkan acak setiap run."""
    env = {key: value for key, value in os.environ.items() if key != "LOG_FILE_PATH"}
    env.update(
        DATABASE_URL=f"sqlite:///{(workdir / 'e2e.db').as_posix()}",
        JWT_SECRET_KEY=secrets.token_hex(32),
        SECRET_KEY=secrets.token_hex(32),
        HOST="127.0.0.1",
        PORT=str(_free_port()),
        E2E_USERNAME=credentials["username"],
        E2E_PASSWORD=credentials["password"],
        PYTHONIOENCODING="utf-8",
    )
    return env


@pytest.fixture(scope="session")
def base_url(server_env: dict[str, str], workdir: Path):
    """URL server waitress (`serve.py`) yang berjalan selama sesi test."""
    HASIL_DIR.mkdir(exist_ok=True)
    _run_seed(server_env, workdir)
    with open(HASIL_DIR / "server.log", "w", encoding="utf-8") as log:
        process = subprocess.Popen([sys.executable, str(PROJECT_ROOT / "serve.py")], cwd=workdir,
                                   env=server_env, stdout=log, stderr=subprocess.STDOUT)
        url = f"http://127.0.0.1:{server_env['PORT']}"
        try:
            _wait_until_ready(url, process)
            yield url
        finally:
            process.terminate()
            process.wait(timeout=10)


# --- Browser ---

@pytest.fixture(scope="session")
def downloads(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Folder unduhan Chrome."""
    return tmp_path_factory.mktemp("unduhan")


@pytest.fixture(scope="session")
def driver(downloads: Path):
    """Chrome 1366x768 (resolusi umum laptop Windows 7), headless kecuali E2E_HEADED=1."""
    options = webdriver.ChromeOptions()
    if os.environ.get("E2E_HEADED") != "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,768")
    # Tanpa unduhan komponen latar belakang Chrome, agar folder unduhan hanya berisi berkas dari aplikasi
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-background-networking")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    options.add_experimental_option("prefs", {
        "download.default_directory": str(downloads),
        "download.prompt_for_download": False,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    # Tanpa E2E_CHROMEDRIVER, Service() menyerahkan pencarian driver ke Selenium Manager
    service = Service(executable_path=os.environ.get("E2E_CHROMEDRIVER"))
    browser = webdriver.Chrome(options=options, service=service)
    browser.set_script_timeout(30)
    browser.execute_cdp_cmd("Browser.setDownloadBehavior",
                            {"behavior": "allow", "downloadPath": str(downloads)})
    yield browser
    browser.quit()


@pytest.fixture(scope="session")
def app_page(driver, base_url: str, credentials: dict[str, str], workdir: Path,
             downloads: Path) -> AppPage:
    """AppPage tanpa jaminan sudah login; dipakai test login dan sesi."""
    return AppPage(driver, base_url, credentials, files=workdir, downloads=downloads)


@pytest.fixture
def page(app_page: AppPage) -> AppPage:
    """AppPage yang sudah login, dengan buffer log konsol dikosongkan."""
    app_page.ensure_logged_in()
    app_page.console_errors()
    return app_page


# --- Laporan hasil (e2e/hasil/hasil.md dan hasil.json) ---

def _parse_docstring(doc: str | None) -> tuple[str, str]:
    text = " ".join((doc or "").split())
    scenario, _, expected = text.partition("Diharapkan:")
    return scenario.strip(), expected.strip()


def _short_failure(report: pytest.TestReport) -> str:
    if report.passed:
        return ""
    if report.skipped:
        return str(report.longrepr[-1]) if isinstance(report.longrepr, tuple) else ""
    crash = getattr(report.longrepr, "reprcrash", None)
    message = crash.message if crash else str(report.longrepr)
    first_line = message.strip().splitlines()[0] if message.strip() else ""
    # Contoh: "selenium...TimeoutException: Message: Toast tidak muncul" -> "Toast tidak muncul"
    return re.sub(r"^([\w.]+(Error|Exception): )?(Message: )?", "", first_line)[:300]


def _to_result(item: pytest.Item, report: pytest.TestReport) -> dict[str, Any]:
    scenario, expected = _parse_docstring(item.function.__doc__)
    if hasattr(item, "callspec"):
        scenario = f"{scenario} [{item.callspec.id}]"
    status = "Lulus" if report.passed else ("Dilewati" if report.skipped else "Gagal")
    return {
        "modul": " ".join((item.cls.__doc__ or item.cls.__name__).split()) if item.cls else item.name,
        "skenario": scenario,
        "diharapkan": expected,
        "status": status,
        "catatan": _short_failure(report),
        "nodeid": item.nodeid,
        "durasi": round(report.duration, 2),
    }


def _save_screenshot(item: pytest.Item) -> None:
    app = item.funcargs.get("page") or item.funcargs.get("app_page")
    if app is None:
        return
    # Contoh: "test_05_surat.py::TestSuratMasuk::test_tambah" -> "test_05_surat.py__TestSuratMasuk__test_tambah"
    name = re.sub(r"[^\w.-]+", "_", item.nodeid.replace("::", "__"))[:150]
    folder = HASIL_DIR / "screenshot"
    folder.mkdir(parents=True, exist_ok=True)
    app.driver.save_screenshot(str(folder / f"{name}.png"))


def pytest_configure(config: pytest.Config) -> None:
    config.stash[RESULTS] = []
    # Screenshot run sebelumnya dihapus agar isi folder sesuai hasil.md yang baru
    shutil.rmtree(HASIL_DIR / "screenshot", ignore_errors=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" and (report.when != "setup" or report.passed):
        return
    if report.failed:
        _save_screenshot(item)
    item.config.stash[RESULTS].append(_to_result(item, report))


def _format_markdown(results: list[dict[str, Any]]) -> str:
    counts = {status: sum(r["status"] == status for r in results) for status in ("Lulus", "Gagal", "Dilewati")}
    lines = [
        "# Hasil test end-to-end",
        "",
        f"Dijalankan: {time.strftime('%Y-%m-%d %H:%M')}. "
        f"Total {len(results)} skenario: {counts['Lulus']} lulus, {counts['Gagal']} gagal, "
        f"{counts['Dilewati']} dilewati.",
        "",
        "| No | Modul | Skenario | Hasil yang diharapkan | Status | Catatan |",
        "|---|---|---|---|---|---|",
    ]
    for number, r in enumerate(results, start=1):
        cells = [str(number), r["modul"], r["skenario"], r["diharapkan"], r["status"], r["catatan"]]
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def pytest_sessionfinish(session: pytest.Session) -> None:
    results = session.config.stash.get(RESULTS, [])
    if not results:
        return
    HASIL_DIR.mkdir(exist_ok=True)
    (HASIL_DIR / "hasil.json").write_text(json.dumps(results, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    (HASIL_DIR / "hasil.md").write_text(_format_markdown(results), encoding="utf-8")
