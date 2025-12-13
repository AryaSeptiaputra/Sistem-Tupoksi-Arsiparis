// assets/js/dashboard.js

{
    /* ---------- FUNGSI UTAMA (INIT) ---------- */
    const initDashboard = async () => {
        console.log("Dashboard Loaded");

        // 1. Cek Token Login
        const token = localStorage.getItem("access_token");
        if (!token) {
            // Gunakan navigateTo dari router.js jika ada, atau fallback
            if(window.navigateTo) window.navigateTo("/login");
            else window.location.href = "/login";
            return;
        }

        // 2. Load Data Awal
        loadUserInfo();
        
        // 3. Load Data Async
        await Promise.all([
            loadStatsData(),
            loadDocuments()
        ]);

        // 4. Setup Event Listeners lokal
        setupLocalListeners();
    };

    /* ---------- 1. USER INFO ---------- */
    const loadUserInfo = () => {
        const welcomeEl = document.getElementById("user-welcome");
        const nameEl = document.getElementById("profile-name");
        const roleEl = document.getElementById("profile-role");
        const avatarEl = document.getElementById("dashboard-avatar");

        const user = api.auth.getUserData(); // Menggunakan api.js global

        if (!user) return;

        const displayName = user.username || "Pengguna";
        const displayRole = user.role || "Staf";
        const initial = displayName.charAt(0).toUpperCase();

        if (welcomeEl) welcomeEl.textContent = `Halo, ${displayName}!`;
        if (nameEl) nameEl.textContent = displayName;
        if (roleEl) roleEl.textContent = displayRole.charAt(0).toUpperCase() + displayRole.slice(1);
        if (avatarEl) avatarEl.textContent = initial; 
        
        // Handle Tampilan Berdasarkan Role (Pengganti {% if %} Jinja2)
        const widgetFinance = document.getElementById("widget-finance");
        const widgetDiploma = document.getElementById("widget-diploma");

        if(widgetFinance) {
            widgetFinance.style.display = (user.role === 'admin') ? 'block' : 'none';
        }
        if(widgetDiploma) {
            widgetDiploma.style.display = ['admin', 'headmaster'].includes(user.role) ? 'block' : 'none';
        }
    };

    /* ---------- 2. STATISTIK WIDGET & CHART ---------- */
    const loadStatsData = async () => {
        const user = api.auth.getUserData();
        
        try {
            // A. Statistik Guru
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

            // B. Data Keuangan (Hanya Admin)
            if (user.role === 'admin') {
                const finances = await api.financeArchive.getAll();
                
                if (finances && Array.isArray(finances)) {
                    const elFin = document.getElementById("stat-finance-count");
                    if(elFin) elFin.textContent = finances.length;

                    renderFinanceTrendChart(finances);
                    renderStorageChart(finances);
                }
            }

        } catch (err) {
            console.error("Gagal memuat statistik:", err);
        }
    };

    /* --- CHART 1: TREN KEUANGAN --- */
    const renderFinanceTrendChart = (data) => {
        const container = document.querySelector("#chart-finance-trend");
        // Cek jika container ada (karena di SPA elemen bisa hilang jika pindah halaman cepat)
        if(!container) return; 

        const monthlyTotals = Array(12).fill(0);
        const currentYear = new Date().getFullYear();

        data.forEach(item => {
            const dateStr = item.date || item.created_at || item.fiscal_year + "-01-01"; // Fallback date
            let rawNominal = item.nominal || item.amount; // Handle variasi nama field

            if (typeof rawNominal === 'string') {
                rawNominal = rawNominal.replace(/[^0-9]/g, '');
            }
            const nominal = parseInt(rawNominal) || 0;
            
            if (dateStr) {
                const d = new Date(dateStr);
                // Cek tahun fiscal atau tanggal
                const year = item.fiscal_year ? parseInt(item.fiscal_year) : d.getFullYear();
                
                if(year === currentYear) { 
                    // Jika ada field period_month (1-12), gunakan itu
                    if(item.period_month) {
                        monthlyTotals[item.period_month - 1] += nominal;
                    } else {
                        monthlyTotals[d.getMonth()] += nominal;
                    }
                }
            }
        });

        const options = {
            series: [{ name: 'Total Nominal', data: monthlyTotals }],
            chart: { type: 'area', height: 300, fontFamily: 'Poppins, sans-serif', toolbar: { show: false } },
            dataLabels: { enabled: false },
            stroke: { curve: 'smooth', width: 2 },
            xaxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'],
                labels: { style: { fontSize: '11px', colors: '#6b7280' } }
            },
            yaxis: {
                labels: {
                    formatter: (val) => new Intl.NumberFormat('id-ID', { notation: "compact" }).format(val),
                    style: { fontSize: '11px', colors: '#6b7280' }
                }
            },
            colors: ['#3b82f6'],
            fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.7, opacityTo: 0.1, stops: [0, 100] } },
            grid: { borderColor: '#f3f4f6' }
        };

        const chart = new ApexCharts(container, options);
        chart.render();
    };

    /* --- CHART 2: LOKASI PENYIMPANAN --- */
    const renderStorageChart = (data) => {
        const container = document.querySelector("#chart-storage-dist");
        if(!container) return;

        const locationCounts = {};
        data.forEach(item => {
            const locName = item.storage_location_name || item.location || "Lainnya";
            locationCounts[locName] = (locationCounts[locName] || 0) + 1;
        });

        const sortedLocations = Object.entries(locationCounts).sort(([,a], [,b]) => b - a).slice(0, 5);
        const labels = sortedLocations.map(([key]) => key);
        const values = sortedLocations.map(([,val]) => val);

        const options = {
            series: [{ name: 'Dokumen', data: values }],
            chart: { type: 'bar', height: 300, fontFamily: 'Poppins, sans-serif', toolbar: { show: false } },
            plotOptions: { bar: { borderRadius: 4, horizontal: true, barHeight: '50%', distributed: true } },
            dataLabels: { enabled: true, textAnchor: 'start', offsetX: 0 },
            xaxis: { categories: labels, labels: { show: false } },
            colors: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'],
            legend: { show: false },
            grid: { show: false }
        };

        const chart = new ApexCharts(container, options);
        chart.render();
    };

    /* ---------- 3. DOKUMEN & WIDGET SAMPING ---------- */
    const loadDocuments = async () => {
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

            // Widget Pending
            const pendingLetters = outgoing.filter(d => d.approval_status === 'pending');
            const widgetPending = document.getElementById("widget-pending");
            if (pendingLetters.length > 0 && widgetPending) {
                widgetPending.style.display = "block";
                document.getElementById("stat-pending-count").textContent = pendingLetters.length;
                
                // Gunakan navigateTo
                widgetPending.onclick = () => {
                    if(window.navigateTo) window.navigateTo('/outgoing_letter');
                };
            }

            // Widget Ijazah
            if (canViewSensitive) {
                const uncollected = diplomas.filter(d => d.is_collected === false || d.is_collected === 0);
                const elDip = document.getElementById("stat-diploma-pending");
                if(elDip) elDip.textContent = uncollected.length;
            }

            // Counts
            const elInCount = document.getElementById("count-incoming");
            const elOutCount = document.getElementById("count-outgoing");
            if(elInCount) elInCount.textContent = incoming.length;
            if(elOutCount) elOutCount.textContent = outgoing.length;

            renderActivityChart(incoming, outgoing);

        } catch (err) {
            console.error("Gagal load documents:", err);
        }
    };

    const renderActivityChart = (incomingData, outgoingData) => {
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
    };

    const setupLocalListeners = () => {
        const avatarLink = document.querySelector("#dashboard-avatar");
        if(avatarLink) {
            avatarLink.addEventListener("click", (e) => {
                // Pastikan event delegation di router.js menangani ini,
                // atau panggil manual jika perlu
                if(window.navigateTo) {
                    e.preventDefault();
                    window.navigateTo("/user_profile");
                }
            });
        }
    };

    // EKSEKUSI FUNGSI INIT
    initDashboard();
}