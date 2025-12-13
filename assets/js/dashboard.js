// assets/js/dashboard.js

document.addEventListener("DOMContentLoaded", () => {
    // 1. Cek Token Login
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "/page/login";
        return;
    }

    // 2. Load Data
    loadUserInfo();
    loadStatsData(); // Load widget & Chart baru
    loadDocuments(); // Load notifikasi & activity chart samping
    
    // 3. Setup Event Listeners
    setupEventListeners();
});

/* ---------- 1. USER INFO ---------- */
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

/* ---------- 2. STATISTIK WIDGET & CHART UTAMA (BARU) ---------- */
async function loadStatsData() {
    const user = api.auth.getUserData();
    
    try {
        // A. Statistik Guru (Tetap)
        const teachers = await api.teacher.getAll(); 
        if (teachers && Array.isArray(teachers)) {
            const activeTeachers = teachers.filter(t => t.status === 'Aktif');
            
            const elCount = document.getElementById("stat-teacher-count");
            if(elCount) elCount.textContent = activeTeachers.length;

            const pnsCount = activeTeachers.filter(t => t.employment_status === 'PNS').length;
            const nonPnsCount = activeTeachers.length - pnsCount;
            const elDetail = document.getElementById("stat-teacher-detail");
            if(elDetail) elDetail.textContent = `${pnsCount} PNS, ${nonPnsCount} Non-ASN`;
        }

        // B. Data Keuangan (Widget & Chart)
        if (user.role === 'admin') {
            const finances = await api.financeArchive.getAll();
            
            if (finances && Array.isArray(finances)) {
                
                // 1. PERBAIKAN WIDGET: Total Arsip (Semua Tahun)
                // Kita tidak lagi memfilter berdasarkan tahun untuk widget ini agar angkanya tidak 0
                const elFin = document.getElementById("stat-finance-count");
                if(elFin) elFin.textContent = finances.length;

                // 2. RENDER CHART TREN (Area Chart)
                renderFinanceTrendChart(finances);

                // 3. RENDER CHART LOKASI (Bar Chart)
                renderStorageChart(finances);
            }
        }

    } catch (err) {
        console.error("Gagal memuat statistik widget:", err);
    }
}

/* --- LOGIC CHART 1: TREN KEUANGAN --- */
function renderFinanceTrendChart(data) {
    const container = document.querySelector("#chart-finance-trend");
    if(!container) return;

    // Siapkan array 12 bulan (Index 0=Jan, 11=Des)
    const monthlyTotals = Array(12).fill(0);
    const currentYear = new Date().getFullYear();

    data.forEach(item => {
        // Pastikan kita punya tanggal dan nominal
        const dateStr = item.date || item.created_at; 
        
        // Bersihkan format nominal (misal dari "Rp 9.000.000" menjadi angka murni)
        // Jika data API sudah angka, parsing ini tetap aman
        let rawNominal = item.nominal;
        if (typeof rawNominal === 'string') {
            rawNominal = rawNominal.replace(/[^0-9]/g, ''); // Hapus Rp dan titik
        }
        const nominal = parseInt(rawNominal) || 0;
        
        if (dateStr) {
            const d = new Date(dateStr);
            // Kita hanya masukkan data tahun ini ke grafik agar 'Tren' valid
            // Jika ingin semua tahun, hapus if(d.getFullYear() === currentYear)
            if(d.getFullYear() === currentYear) { 
                monthlyTotals[d.getMonth()] += nominal;
            }
        }
    });

    const options = {
        series: [{
            name: 'Total Nominal',
            data: monthlyTotals
        }],
        chart: {
            type: 'area',
            height: 300,
            fontFamily: 'Poppins, sans-serif',
            toolbar: { show: false }
        },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 2 },
        xaxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'],
            labels: { style: { fontSize: '11px', colors: '#6b7280' } }
        },
        yaxis: {
            labels: {
                formatter: (value) => {
                    // Format Jutaan/Ribuan (2jt, 500rb)
                    return new Intl.NumberFormat('id-ID', { notation: "compact", compactDisplay: "short" }).format(value);
                },
                style: { fontSize: '11px', colors: '#6b7280' }
            }
        },
        colors: ['#3b82f6'],
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.7,
                opacityTo: 0.1,
                stops: [0, 100]
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return "Rp " + new Intl.NumberFormat('id-ID').format(val);
                }
            }
        },
        grid: { borderColor: '#f3f4f6' }
    };

    const chart = new ApexCharts(container, options);
    chart.render();
}

/* --- LOGIC CHART 2: LOKASI PENYIMPANAN --- */
function renderStorageChart(data) {
    const container = document.querySelector("#chart-storage-dist");
    if(!container) return;

    // Hitung jumlah dokumen per lokasi
    const locationCounts = {};
    
    data.forEach(item => {
        // Ambil nama lokasi. Sesuaikan 'location' dengan key dari API kamu (misal: storage_location, shelf, dll)
        const locName = item.location || item.storage_location || "Lainnya";
        locationCounts[locName] = (locationCounts[locName] || 0) + 1;
    });

    // Urutkan lokasi dari yang terbanyak
    const sortedLocations = Object.entries(locationCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5); // Ambil Top 5 saja

    const labels = sortedLocations.map(([key]) => key);
    const values = sortedLocations.map(([,val]) => val);

    const options = {
        series: [{
            name: 'Jumlah Dokumen',
            data: values
        }],
        chart: {
            type: 'bar',
            height: 300,
            fontFamily: 'Poppins, sans-serif',
            toolbar: { show: false }
        },
        plotOptions: {
            bar: {
                borderRadius: 4,
                horizontal: true,
                barHeight: '50%',
                distributed: true // Warna beda tiap bar
            }
        },
        dataLabels: { 
            enabled: true,
            textAnchor: 'start',
            style: { colors: ['#fff'] },
            formatter: function (val, opt) {
                return val + ""
            },
            offsetX: 0,
        },
        xaxis: {
            categories: labels,
            labels: { show: false } // Sembunyikan label bawah agar bersih
        },
        yaxis: {
            labels: { style: { fontSize: '12px', colors: '#374151' } }
        },
        colors: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'], // Palette warna
        legend: { show: false },
        grid: { show: false } // Hilangkan garis grid
    };

    const chart = new ApexCharts(container, options);
    chart.render();
}

/* ---------- 3. DOKUMEN & WIDGET SAMPING (SEDERHANA) ---------- */
async function loadDocuments() {
    // Fungsi ini sekarang hanya handle Widget Pending & Side Chart (Activity)
    const user = api.auth.getUserData();
    const canViewSensitive = user && ['admin', 'headmaster'].includes(user.role);

    try {
        const promises = [
            api.incomingLetter.getAll(),
            api.outgoingLetter.getAll()
        ];
        if (canViewSensitive) promises.push(api.diploma.getAll());

        const results = await Promise.all(promises);
        const incoming = results[0] || [];
        const outgoing = results[1] || [];
        const diplomas = canViewSensitive ? (results[2] || []) : [];

        // 1. Widget Pending Approval
        const pendingLetters = outgoing.filter(d => d.approval_status === 'pending');
        const widgetPending = document.getElementById("widget-pending");
        if (pendingLetters.length > 0 && widgetPending) {
            widgetPending.style.display = "block";
            document.getElementById("stat-pending-count").textContent = pendingLetters.length;
            
            // Klik widget -> Ke halaman surat keluar
            widgetPending.onclick = () => window.location.href = '/page/outgoing_letter';
        }

        // 2. Widget Ijazah
        if (canViewSensitive) {
            const uncollected = diplomas.filter(d => d.is_collected === false || d.is_collected === 0);
            const elDip = document.getElementById("stat-diploma-pending");
            if(elDip) elDip.textContent = uncollected.length;
        }

        // 3. Side Widget Counts
        const elInCount = document.getElementById("count-incoming");
        const elOutCount = document.getElementById("count-outgoing");
        if(elInCount) elInCount.textContent = incoming.length;
        if(elOutCount) elOutCount.textContent = outgoing.length;

        // 4. Render Activity Chart (Grafik Batang Kecil di Kanan - Tetap Ada)
        renderActivityChart(incoming, outgoing);

    } catch (err) {
        console.error("Gagal load documents:", err);
    }
}

/* ---------- 4. RENDER GRAFIK SAMPING (ACTIVITY - Code Lama) ---------- */
function renderActivityChart(incomingData, outgoingData) {
    const chartContainer = document.getElementById("upload-chart");
    if (!chartContainer) return;

    chartContainer.innerHTML = "";
    
    const months = [];
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Ags", "Sep", "Okt", "Nov", "Des"];
    
    for (let i = 5; i >= 0; i--) {
        const d = new Date();
        d.setMonth(d.getMonth() - i);
        months.push({
            monthIndex: d.getMonth(),
            year: d.getFullYear(),
            label: monthNames[d.getMonth()],
            count: 0
        });
    }

    const allDocs = [...incomingData, ...outgoingData];
    allDocs.forEach(doc => {
        const dateStr = doc.created_at || doc.letter_date;
        if(!dateStr) return;
        const d = new Date(dateStr);
        const found = months.find(m => m.monthIndex === d.getMonth() && m.year === d.getFullYear());
        if(found) found.count++;
    });

    const maxVal = Math.max(...months.map(m => m.count), 1);

    months.forEach(m => {
        const heightPct = (m.count / maxVal) * 100;
        const finalHeight = heightPct < 10 && m.count > 0 ? 10 : heightPct;

        const barWrapper = document.createElement("div");
        Object.assign(barWrapper.style, {
            flex: "1", textAlign: "center", display: "flex", flexDirection: "column",
            justifyContent: "flex-end", height: "100%"
        });

        const bar = document.createElement("div");
        Object.assign(bar.style, {
            height: m.count === 0 ? "2px" : `${finalHeight}%`,
            background: m.count === 0 ? "#f3f4f6" : "#3b82f6", 
            borderRadius: "4px 4px 0 0", width: "70%", margin: "0 auto", transition: "height 0.5s ease"
        });
        bar.title = `${m.label}: ${m.count}`;

        const label = document.createElement("div");
        label.textContent = m.label;
        Object.assign(label.style, { fontSize: "10px", color: "#6b7280", marginTop: "4px" });

        barWrapper.appendChild(bar);
        barWrapper.appendChild(label);
        chartContainer.appendChild(barWrapper);
    });
}

function setupEventListeners() {
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", () => { api.auth.logout(); });
    }
}