/**
 * assets/js/dashboard.js
 * Logika Frontend untuk Dashboard Utama
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Cek Token Login
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "/page/login";
        return;
    }

    // 2. Load Data & UI
    loadUserInfo();
    setupTabs();         // Inisialisasi Logic Pindah Tab
    
    // 3. Load Data Statistik
    loadStatsData();     // Ringkasan & Keuangan (Widget Atas)
    loadDocuments();     // Surat Masuk & Keluar
    loadExtendedStats(); // [BARU] Guru, Ijazah, Arsip Pegawai
    
    setupEventListeners();
});

/* ========================================= */
/* 1. USER INFO & TABS LOGIC                 */
/* ========================================= */

function loadUserInfo() {
    const welcomeEl = document.getElementById("user-welcome");
    const nameEl = document.getElementById("profile-name");
    const roleEl = document.getElementById("profile-role");
    const avatarEl = document.getElementById("dashboard-avatar");

    const user = api.auth.getUserData();
    if (!user) return;

    const displayName = user.username || "Pengguna";
    const displayRole = user.role || "Staf";
    const initial = displayName.charAt(0).toUpperCase();

    if (welcomeEl) welcomeEl.textContent = `Halo, ${displayName}!`;
    if (nameEl) nameEl.textContent = displayName;
    if (roleEl) roleEl.textContent = displayRole.charAt(0).toUpperCase() + displayRole.slice(1);
    if (avatarEl) avatarEl.textContent = initial; 
}

function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const panes = document.querySelectorAll('.tab-pane');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Hapus class active dari semua tab & pane
            tabs.forEach(t => t.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));

            // Tambah class active ke yang diklik
            tab.classList.add('active');
            
            // Ambil ID target dari data-tab
            const targetId = tab.getAttribute('data-tab');
            const targetPane = document.getElementById(targetId);
            
            if (targetPane) {
                targetPane.classList.add('active');
                // Trigger resize agar chart menyesuaikan lebar container baru
                window.dispatchEvent(new Event('resize'));
            }
        });
    });
}

/* ========================================= */
/* 2. LOGIKA DATA LAMA (Ringkasan, Keuangan) */
/* ========================================= */

async function loadStatsData() {
    const user = api.auth.getUserData();
    
    try {
        // A. Data Guru (Untuk Widget Ringkasan Atas)
        const teachers = await api.teacher.getAll(); 
        if (teachers && Array.isArray(teachers)) {
            const activeTeachers = teachers.filter(t => t.status === 'Aktif');
            
            updateText("stat-teacher-count", activeTeachers.length);

            const pnsCount = activeTeachers.filter(t => t.employment_status === 'PNS').length;
            const nonPnsCount = activeTeachers.length - pnsCount;
            updateText("stat-teacher-detail", `${pnsCount} PNS, ${nonPnsCount} Non-ASN`);
        }

        // B. Data Keuangan
        if (user.role === 'admin') {
            const finances = await api.financeArchive.getAll();
            
            if (finances && Array.isArray(finances)) {
                // Widget Overview
                updateText("stat-finance-count", finances.length);
                updateText("fin-total", finances.length);

                // Hitung Total Nominal
                let totalNominal = 0;
                finances.forEach(item => {
                    let raw = item.nominal;
                    if (typeof raw === 'string') raw = raw.replace(/[^0-9]/g, '');
                    totalNominal += (parseInt(raw) || 0);
                });
                
                // Format Rupiah
                const formattedNominal = "Rp " + new Intl.NumberFormat('id-ID', { notation: "compact" }).format(totalNominal);
                updateText("fin-nominal", formattedNominal);

                // Render Chart
                renderFinanceTrendChart(finances);
                renderStorageChart(finances);
            }
        }

    } catch (err) {
        console.error("Gagal memuat statistik dasar:", err);
    }
}

/* ========================================= */
/* 3. LOGIKA SURAT (Masuk & Keluar)          */
/* ========================================= */

async function loadDocuments() {
    try {
        const [incoming, outgoing] = await Promise.all([
            api.incomingLetter.getAll() || [],
            api.outgoingLetter.getAll() || []
        ]);

        // --- A. RINGKASAN & SIDEBAR ---
        renderOverviewChart(incoming, outgoing); // Chart Batang Perbandingan
        
        // Widget Pending (Surat Keluar)
        const pendingLetters = outgoing.filter(d => d.approval_status === 'pending');
        const widgetPending = document.getElementById("widget-pending");
        if (pendingLetters.length > 0 && widgetPending) {
            widgetPending.style.display = "block";
            updateText("stat-pending-count", pendingLetters.length);
            widgetPending.onclick = () => window.location.href = '/page/outgoing_letter';
        }

        // Sidebar Counts
        updateText("count-incoming", incoming.length);
        updateText("count-outgoing", outgoing.length);
        
        // Chart Kecil di Sidebar
        renderActivityChart(incoming, outgoing);

        // --- B. TAB SURAT MASUK ---
        if(incoming.length >= 0) {
            updateText('in-total', incoming.length);
            
            // Hitung bulan ini
            const now = new Date();
            const thisMonthCount = incoming.filter(d => {
                const date = new Date(d.date || d.created_at);
                return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
            }).length;
            updateText('in-month', `+${thisMonthCount}`);

            // Info Terakhir
            if(incoming.length > 0) {
                const latest = incoming.sort((a,b) => new Date(b.created_at) - new Date(a.created_at))[0];
                updateText('in-last-date', new Date(latest.created_at).toLocaleDateString('id-ID'));
                updateText('in-last-from', latest.sender || "Tanpa Pengirim");
            }

            renderTrendChart("#chart-incoming-trend", incoming, "Surat Masuk", "#3b82f6");
            renderTopSenderChart(incoming);
        }

        // --- C. TAB SURAT KELUAR ---
        if(outgoing.length >= 0) {
            updateText('out-total', outgoing.length);
            
            const pendingReject = outgoing.filter(d => ['pending', 'rejected'].includes(d.approval_status)).length;
            updateText('out-pending', pendingReject);

            const now = new Date();
            const approvedMonth = outgoing.filter(d => {
                const date = new Date(d.date || d.created_at);
                return d.approval_status === 'approved' && 
                       date.getMonth() === now.getMonth() && 
                       date.getFullYear() === now.getFullYear();
            }).length;
            updateText('out-month', `+${approvedMonth}`);

            renderStatusChart(outgoing);
        }

    } catch (err) {
        console.error("Gagal load documents:", err);
    }
}

/* ========================================= */
/* 4. [BARU] LOGIKA TAB TAMBAHAN             */
/* (Guru, Ijazah, Arsip Pegawai)             */
/* ========================================= */

async function loadExtendedStats() {
    try {
        // Request Parallel agar loading cepat
        const [teachers, diplomas, empArchives] = await Promise.all([
            api.teacher.getAll().catch(() => []),
            api.diploma.getAll().catch(() => []),
            api.employeeArchive.getAll().catch(() => [])
        ]);

        // --- A. DATA GURU ---
        if (teachers && Array.isArray(teachers)) {
            const active = teachers.filter(t => t.status === 'Aktif');
            const pns = active.filter(t => t.employment_status === 'PNS').length;
            const nonAsn = active.length - pns;
            
            updateText("tab-guru-total", active.length);
            updateText("tab-guru-pns", pns);
            updateText("tab-guru-non", nonAsn);

            // Chart Status Kepegawaian (Donut)
            renderDonutChart("#chart-guru-status", [pns, nonAsn], ['PNS', 'Non-ASN']);
        }

        // --- B. DATA IJAZAH ---
        if (diplomas && Array.isArray(diplomas)) {
            const total = diplomas.length;
            const collected = diplomas.filter(d => d.is_collected).length;
            const notCollected = total - collected;

            updateText("tab-ijazah-total", total);
            updateText("tab-ijazah-diambil", collected);
            updateText("tab-ijazah-belum", notCollected);

            // Chart Tren Ijazah per Tahun Ajaran (Bar)
            renderBarChartIjazah(diplomas);
        }

        // --- C. ARSIP PEGAWAI ---
        if (empArchives && Array.isArray(empArchives)) {
            updateText("tab-emp-total", empArchives.length);
            
            // Chart Tipe Dokumen (Bar Horizontal)
            renderBarChartArsip(empArchives);
        }

    } catch (err) {
        console.error("Gagal memuat data tambahan:", err);
    }
}

/* ========================================= */
/* 5. HELPER CHARTS (APEXCHARTS)             */
/* ========================================= */

// --- Helper Update Text Aman ---
function updateText(id, value) {
    const el = document.getElementById(id);
    if(el) el.textContent = value;
}

// 1. Chart Area: Tren Bulanan (Generic)
function renderTrendChart(selector, data, name, color) {
    if(!document.querySelector(selector)) return;
    
    const monthly = Array(12).fill(0);
    const currentYear = new Date().getFullYear();

    data.forEach(item => {
        const date = new Date(item.date || item.created_at);
        if(date.getFullYear() === currentYear) {
            monthly[date.getMonth()]++;
        }
    });

    const options = {
        series: [{ name: name, data: monthly }],
        chart: { type: 'area', height: 280, toolbar: { show: false }, fontFamily: 'Poppins' },
        stroke: { curve: 'smooth', width: 2 },
        fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.1 } },
        colors: [color],
        xaxis: { categories: ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des'] },
        grid: { borderColor: '#f3f4f6' }
    };
    new ApexCharts(document.querySelector(selector), options).render();
}

// 2. Chart Bar: Top 5 Pengirim (Surat Masuk)
function renderTopSenderChart(data) {
    if(!document.querySelector("#chart-incoming-source")) return;

    const counts = {};
    data.forEach(d => {
        const sender = d.sender || "Lainnya";
        counts[sender] = (counts[sender] || 0) + 1;
    });

    const sorted = Object.entries(counts).sort((a,b) => b[1] - a[1]).slice(0, 5);

    const options = {
        series: [{ name: 'Jumlah', data: sorted.map(i => i[1]) }],
        chart: { type: 'bar', height: 280, toolbar: { show: false }, fontFamily: 'Poppins' },
        plotOptions: { bar: { borderRadius: 4, horizontal: true, distributed: true } },
        colors: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'],
        dataLabels: { enabled: true },
        xaxis: { categories: sorted.map(i => i[0]) },
        legend: { show: false }
    };
    new ApexCharts(document.querySelector("#chart-incoming-source"), options).render();
}

// 3. Chart Donut: Status (Surat Keluar)
function renderStatusChart(data) {
    if(!document.querySelector("#chart-outgoing-status")) return;

    const approved = data.filter(d => d.approval_status === 'approved').length;
    const pending = data.filter(d => d.approval_status === 'pending').length;
    const rejected = data.filter(d => d.approval_status === 'rejected').length;

    const options = {
        series: [approved, pending, rejected],
        labels: ['Disetujui', 'Menunggu', 'Ditolak'],
        chart: { type: 'donut', height: 280, fontFamily: 'Poppins' },
        colors: ['#10b981', '#f59e0b', '#ef4444'],
        legend: { position: 'bottom' },
        plotOptions: { pie: { donut: { size: '65%' } } }
    };
    new ApexCharts(document.querySelector("#chart-outgoing-status"), options).render();
}

// 4. Chart Overview: Comparison (Masuk vs Keluar)
function renderOverviewChart(inData, outData) {
    if(!document.querySelector("#chart-overview-comparison")) return;
    
    const inMonthly = Array(12).fill(0);
    const outMonthly = Array(12).fill(0);
    const year = new Date().getFullYear();

    inData.forEach(d => { if(new Date(d.date||d.created_at).getFullYear() === year) inMonthly[new Date(d.date||d.created_at).getMonth()]++ });
    outData.forEach(d => { if(new Date(d.date||d.created_at).getFullYear() === year) outMonthly[new Date(d.date||d.created_at).getMonth()]++ });

    const options = {
        series: [
            { name: 'Surat Masuk', data: inMonthly },
            { name: 'Surat Keluar', data: outMonthly }
        ],
        chart: { type: 'bar', height: 320, toolbar: { show: false }, fontFamily: 'Poppins' },
        colors: ['#3b82f6', '#10b981'],
        xaxis: { categories: ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des'] },
        grid: { borderColor: '#f3f4f6' },
        plotOptions: { bar: { borderRadius: 4, columnWidth: '55%' } }
    };
    new ApexCharts(document.querySelector("#chart-overview-comparison"), options).render();
}

// 5. Charts Keuangan
function renderFinanceTrendChart(data) {
    if(!document.querySelector("#chart-finance-trend")) return;
    const monthly = Array(12).fill(0);
    const year = new Date().getFullYear();

    data.forEach(item => {
        let raw = item.nominal;
        if (typeof raw === 'string') raw = raw.replace(/[^0-9]/g, '');
        const nominal = parseInt(raw) || 0;
        const d = new Date(item.date || item.created_at);
        if(d.getFullYear() === year) monthly[d.getMonth()] += nominal;
    });

    const options = {
        series: [{ name: 'Nominal', data: monthly }],
        chart: { type: 'area', height: 280, toolbar: { show: false }, fontFamily: 'Poppins' },
        stroke: { curve: 'smooth', width: 2 },
        colors: ['#10b981'],
        xaxis: { categories: ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des'] },
        yaxis: { labels: { formatter: (val) => new Intl.NumberFormat('id-ID', { notation: "compact" }).format(val) } }
    };
    new ApexCharts(document.querySelector("#chart-finance-trend"), options).render();
}

function renderStorageChart(data) {
    if(!document.querySelector("#chart-storage-dist")) return;
    const counts = {};
    data.forEach(item => {
        const loc = item.location || "Lainnya";
        counts[loc] = (counts[loc] || 0) + 1;
    });
    const sorted = Object.entries(counts).sort((a,b) => b[1] - a[1]).slice(0, 5);

    const options = {
        series: [{ name: 'Dokumen', data: sorted.map(i => i[1]) }],
        chart: { type: 'bar', height: 280, toolbar: { show: false }, fontFamily: 'Poppins' },
        plotOptions: { bar: { borderRadius: 4, horizontal: true, distributed: true } },
        xaxis: { categories: sorted.map(i => i[0]) },
        legend: { show: false }
    };
    new ApexCharts(document.querySelector("#chart-storage-dist"), options).render();
}

// 6. [BARU] Chart Donut Simple (Untuk Guru)
function renderDonutChart(selector, seriesData, labelsData) {
    if(!document.querySelector(selector)) return;
    const options = {
        series: seriesData,
        labels: labelsData,
        chart: { type: 'donut', height: 250, fontFamily: 'Poppins' },
        colors: ['#3b82f6', '#f59e0b', '#10b981'],
        legend: { position: 'bottom' },
        plotOptions: { pie: { donut: { size: '60%' } } }
    };
    new ApexCharts(document.querySelector(selector), options).render();
}

// 7. [BARU] Chart Ijazah per Tahun
function renderBarChartIjazah(data) {
    if(!document.querySelector("#chart-ijazah-trend")) return;
    
    const counts = {};
    data.forEach(d => {
        const year = d.academic_year || "Lainnya";
        counts[year] = (counts[year] || 0) + 1;
    });

    const sortedKeys = Object.keys(counts).sort();
    const seriesData = sortedKeys.map(k => counts[k]);

    const options = {
        series: [{ name: 'Jumlah Ijazah', data: seriesData }],
        chart: { type: 'bar', height: 280, toolbar: { show: false }, fontFamily: 'Poppins' },
        colors: ['#8b5cf6'], // Ungu
        xaxis: { categories: sortedKeys },
        plotOptions: { bar: { borderRadius: 4 } }
    };
    new ApexCharts(document.querySelector("#chart-ijazah-trend"), options).render();
}

// 8. [BARU] Chart Arsip Pegawai (Tipe Dokumen)
function renderBarChartArsip(data) {
    if(!document.querySelector("#chart-emp-type")) return;
    
    const counts = {};
    data.forEach(d => {
        let type = d.document_type || "Lainnya";
        // Format teks: 'sk_cpns' -> 'Sk Cpns'
        type = type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        counts[type] = (counts[type] || 0) + 1;
    });

    const sortedEntry = Object.entries(counts).sort((a,b) => b[1] - a[1]).slice(0, 8);
    
    const options = {
        series: [{ name: 'Jumlah', data: sortedEntry.map(x => x[1]) }],
        chart: { type: 'bar', height: 280, toolbar: { show: false }, fontFamily: 'Poppins' },
        plotOptions: { bar: { borderRadius: 4, horizontal: true } },
        colors: ['#ef4444'], // Merah
        xaxis: { categories: sortedEntry.map(x => x[0]) }
    };
    new ApexCharts(document.querySelector("#chart-emp-type"), options).render();
}

/* ========================================= */
/* 6. SIDEBAR ACTIVITY CHART (KECIL)         */
/* ========================================= */

function renderActivityChart(incoming, outgoing) {
    const container = document.getElementById("upload-chart");
    if (!container) return;
    container.innerHTML = "";
    
    const months = [];
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"];
    
    for (let i = 5; i >= 0; i--) {
        const d = new Date();
        d.setMonth(d.getMonth() - i);
        months.push({ idx: d.getMonth(), year: d.getFullYear(), label: monthNames[d.getMonth()], count: 0 });
    }

    [...incoming, ...outgoing].forEach(doc => {
        const d = new Date(doc.date || doc.created_at);
        const f = months.find(m => m.idx === d.getMonth() && m.year === d.getFullYear());
        if(f) f.count++;
    });

    const maxVal = Math.max(...months.map(m => m.count), 1);

    months.forEach(m => {
        const h = (m.count / maxVal) * 100;
        const finalH = h < 10 && m.count > 0 ? 10 : h;
        
        const wrapper = document.createElement("div");
        Object.assign(wrapper.style, { flex: "1", textAlign: "center", display: "flex", flexDirection: "column", justifyContent: "flex-end", height: "100%" });

        const bar = document.createElement("div");
        Object.assign(bar.style, { height: m.count===0 ? "2px" : `${finalH}%`, background: m.count===0 ? "#f3f4f6" : "#3b82f6", borderRadius: "4px 4px 0 0", width: "70%", margin: "0 auto", transition: "height 0.5s" });
        bar.title = `${m.label}: ${m.count}`;

        const lbl = document.createElement("div");
        lbl.textContent = m.label;
        Object.assign(lbl.style, { fontSize: "10px", color: "#6b7280", marginTop: "4px" });

        wrapper.append(bar, lbl);
        container.append(wrapper);
    });
}

function setupEventListeners() {
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) btnLogout.addEventListener("click", () => api.auth.logout());
}