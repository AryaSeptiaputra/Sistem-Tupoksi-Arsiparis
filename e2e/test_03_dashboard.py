"""Test end-to-end dashboard: grafik per tab dan angka statistik."""
import pytest
from selenium.webdriver.common.by import By

# (label tab, id pane, id kontainer grafik di pane itu)
TAB_CHARTS = [
    ("Ringkasan", "tab-ringkasan", ["chart-overview-comparison"]),
    ("Surat Masuk", "tab-surat-masuk", ["chart-incoming-trend", "chart-incoming-source"]),
    ("Surat Keluar", "tab-surat-keluar", ["chart-outgoing-status"]),
    ("Keuangan", "tab-keuangan", ["chart-finance-trend", "chart-storage-dist"]),
    ("Data Guru", "tab-guru", ["chart-guru-status"]),
    ("Data Ijazah", "tab-ijazah", ["chart-ijazah-trend"]),
    ("Arsip Pegawai", "tab-arsip-pegawai", ["chart-emp-type"]),
]
# Nilai status kepegawaian PNS: kode referensi dan nama yang disimpan form Guru
PNS_VALUES = ("PNS", "Pegawai Negeri Sipil")


@pytest.fixture
def dashboard(page):
    """Dashboard yang sudah terbuka; datanya berasal dari e2e/seed.py."""
    page.open("/page/dashboard")
    return page


def _open_tab(page, pane_id):
    page.driver.find_element(By.CSS_SELECTOR, f"button.tab-btn[data-tab='{pane_id}']").click()
    page.wait.until(lambda d: "active" in d.find_element(By.ID, pane_id).get_attribute("class"),
                    f"Tab {pane_id} tidak aktif")


class TestDashboard:
    """Dashboard"""

    def test_sapaan_dan_ringkasan(self, dashboard):
        """Membuka dashboard setelah login.

        Diharapkan: sapaan memuat nama operator, kartu Total Guru Aktif dan Total Arsip Keuangan sesuai jumlah data.
        """
        teachers = dashboard.api_all("teacher")
        finances = dashboard.api_all("financeArchive")
        dashboard.expect_text("user-welcome", "Halo, Operator Uji!")
        dashboard.expect_text("stat-teacher-count", sum(t["status"] == "Aktif" for t in teachers))
        dashboard.expect_text("stat-finance-count", len(finances))

    @pytest.mark.parametrize("pane_id, chart_ids", [(p, c) for _, p, c in TAB_CHARTS],
                             ids=[label for label, _, _ in TAB_CHARTS])
    def test_grafik_per_tab(self, dashboard, pane_id, chart_ids):
        """Membuka tab dashboard dan memeriksa grafiknya.

        Diharapkan: setiap grafik di tab itu tergambar oleh Chart.js dan terlihat (lebar lebih dari 0).
        """
        _open_tab(dashboard, pane_id)
        for chart_id in chart_ids:
            dashboard.wait.until(lambda d: d.execute_script(
                "const c = document.querySelector(arguments[0] + ' canvas');"
                "return !!(c && Chart.getChart(c) && c.clientWidth > 0);", f"#{chart_id}"),
                f"Grafik #{chart_id} tidak tergambar")

    def test_angka_surat(self, dashboard):
        """Membandingkan angka tab Surat Masuk dan Surat Keluar dengan data.

        Diharapkan: total surat masuk, total surat keluar, dan jumlah surat menunggu/ditolak sama dengan data di API.
        """
        incoming = dashboard.api_all("incomingLetter")
        outgoing = dashboard.api_all("outgoingLetter")
        _open_tab(dashboard, "tab-surat-masuk")
        dashboard.expect_text("in-total", len(incoming))
        _open_tab(dashboard, "tab-surat-keluar")
        dashboard.expect_text("out-total", len(outgoing))
        dashboard.expect_text("out-pending", sum(o["approval_status"] in ("pending", "rejected") for o in outgoing))

    def test_widget_surat_menunggu(self, dashboard):
        """Melihat widget surat keluar yang menunggu persetujuan, lalu menekannya.

        Diharapkan: widget tampil dengan jumlah surat berstatus pending dan membuka halaman Surat Keluar.
        """
        pending = sum(o["approval_status"] == "pending" for o in dashboard.api_all("outgoingLetter"))
        dashboard.wait.until(lambda d: d.find_element(By.ID, "widget-pending").is_displayed(),
                             "Widget surat menunggu tidak tampil")
        dashboard.expect_text("stat-pending-count", pending)
        dashboard.click("widget-pending")
        dashboard.wait_path("/page/outgoing_letter")

    def test_angka_guru(self, dashboard):
        """Membandingkan angka tab Data Guru dengan data guru aktif.

        Diharapkan: total guru aktif, jumlah PNS, dan jumlah Non-ASN sesuai data (guru PNS disimpan form Guru sebagai "Pegawai Negeri Sipil").
        """
        active = [t for t in dashboard.api_all("teacher") if t["status"] == "Aktif"]
        pns = sum(t["employment_status"] in PNS_VALUES for t in active)
        _open_tab(dashboard, "tab-guru")
        dashboard.expect_text("tab-guru-total", len(active))
        dashboard.expect_text("tab-guru-pns", pns)
        dashboard.expect_text("tab-guru-non", len(active) - pns)

    def test_angka_ijazah(self, dashboard):
        """Membandingkan angka tab Data Ijazah dengan data ijazah.

        Diharapkan: total, sudah diambil, dan belum diambil sesuai data.
        """
        diplomas = dashboard.api_all("diploma")
        collected = sum(bool(d["is_collected"]) for d in diplomas)
        _open_tab(dashboard, "tab-ijazah")
        dashboard.expect_text("tab-ijazah-total", len(diplomas))
        dashboard.expect_text("tab-ijazah-diambil", collected)
        dashboard.expect_text("tab-ijazah-belum", len(diplomas) - collected)

    def test_angka_arsip_pegawai(self, dashboard):
        """Membandingkan angka tab Arsip Pegawai dengan data.

        Diharapkan: total arsip pegawai sama dengan jumlah data.
        """
        _open_tab(dashboard, "tab-arsip-pegawai")
        dashboard.expect_text("tab-emp-total", len(dashboard.api_all("employeeArchive")))

    def test_total_nominal_keuangan(self, dashboard):
        """Membandingkan total nominal di tab Keuangan dengan jumlah nominal arsip keuangan.

        Diharapkan: jumlah arsip dan total nominal (format ringkas Rupiah, misalnya "Rp 1,5 jt") sesuai data.
        """
        finances = dashboard.api_all("financeArchive")
        total = sum(f["amount"] or 0 for f in finances)
        expected = dashboard.driver.execute_script(
            "return 'Rp ' + new Intl.NumberFormat('id-ID', {notation: 'compact'}).format(arguments[0]);", total)
        _open_tab(dashboard, "tab-keuangan")
        dashboard.expect_text("fin-total", len(finances))
        dashboard.expect_text("fin-nominal", expected)
