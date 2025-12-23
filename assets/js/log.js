document.addEventListener("DOMContentLoaded", async () => {

    // --- 0. NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- STATE VARIABLES ---
    let allLogs = []; 
    
    // --- DOM REFERENCES ---
    const tbody = document.getElementById("table-body");
    
    // Filter Inputs
    const searchInput = document.getElementById("searchInput");
    const startDateInput = document.getElementById("startDate");
    const endDateInput = document.getElementById("endDate");
    const filterUser = document.getElementById("filterUser");
    const btnReset = document.getElementById("btnResetFilter");
    const btnExport = document.getElementById("btnExport");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENT LISTENERS ---
    
    // Trigger filter saat input berubah
    [searchInput, startDateInput, endDateInput, filterUser].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if (btnReset) {
        btnReset.addEventListener("click", () => {
            searchInput.value = "";
            startDateInput.value = "";
            endDateInput.value = "";
            filterUser.value = "";
            applyFilters();
            ui.toast("Filter direset", "info");
        });
    }

    if (btnExport) {
        btnExport.addEventListener("click", exportToCSV);
    }

    // --- FUNCTIONS ---

    async function initPage() {
        // Load User dulu untuk isi Dropdown Filter
        await loadUsersForFilter();
        // Baru Load Log
        await loadLogs();
    }

    async function loadUsersForFilter() {
        try {
            // Kita butuh list user agar admin bisa filter "Siapa yang melakukan aksi ini?"
            const response = await api.user.getAll();
            const users = response.users || [];
            
            // Bersihkan dan isi ulang opsi
            filterUser.innerHTML = '<option value="">Semua Pengguna</option>';
            
            users.forEach(u => {
                const opt = document.createElement("option");
                opt.value = u.username; // Kita filter by username yang tersimpan di log
                opt.textContent = u.username + (u.role ? ` (${u.role})` : '');
                filterUser.appendChild(opt);
            });
        } catch (e) {
            console.error("Gagal memuat list user untuk filter:", e);
            // Optional: ui.toast("Gagal memuat filter user", "error");
        }
    }

    async function loadLogs() {
        tbody.innerHTML = `<tr><td colspan="3" class="loading-text" style="text-align:center; padding:20px;">Memuat data log...</td></tr>`;
        
        try {
            const response = await api.log.getAll();
            allLogs = response.logs || [];
            
            // Urutkan dari yang terbaru (Descending by timestamp)
            allLogs.sort((a, b) => {
                const dateA = new Date(a.created_at || a.timestamp);
                const dateB = new Date(b.created_at || b.timestamp);
                return dateB - dateA; 
            });

            renderTable(allLogs);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="3" style="color:red; text-align:center;">Gagal memuat data: ${e.message}</td></tr>`;
            ui.toast("Gagal memuat data log", "error");
        }
    }

    function renderTable(data) {
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; padding:20px; color:var(--text-muted);">Tidak ada aktivitas tercatat.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");

            // 1. Format Waktu
            const rawDate = item.created_at || item.timestamp;
            let dateStr = "-";
            if (rawDate) {
                const d = new Date(rawDate);
                // Format: 05/12/2024 14:30:00
                dateStr = d.toLocaleString("id-ID", { 
                    day: '2-digit', month: '2-digit', year: 'numeric',
                    hour: '2-digit', minute: '2-digit', second: '2-digit'
                });
            }

            // 2. User Chip (Visual)
            // Backend biasanya kirim 'username' atau 'user.username'
            const username = item.username || (item.user ? item.user.username : "System/Unknown");
            
            // 3. Highlight Kata Kunci Aksi
            let actionText = item.action || item.activity || "-";
            actionText = highlightKeywords(actionText);

            tr.innerHTML = `
                <td style="font-family:monospace; font-size:13px; color:var(--text-muted);">${dateStr}</td>
                <td>
                    <span style="font-weight:600; color:var(--primary); background:#fff4ed; padding:4px 10px; border-radius:6px; font-size:12px;">
                        👤 ${username}
                    </span>
                </td>
                <td style="font-size:14px; line-height:1.5;">${actionText}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function highlightKeywords(text) {
        // Fungsi kosmetik untuk menebalkan kata kunci
        if(!text) return "-";
        
        let newText = text;
        // Penyesuaian kata kunci sesuai log backend
        newText = newText.replace(/menambahkan/gi, '<b style="color:#16a34a">menambahkan</b>');
        newText = newText.replace(/membuat/gi, '<b style="color:#16a34a">membuat</b>');
        newText = newText.replace(/mengupdate/gi, '<b style="color:#ca8a04">mengupdate</b>');
        newText = newText.replace(/mengubah/gi, '<b style="color:#ca8a04">mengubah</b>');
        newText = newText.replace(/menghapus/gi, '<b style="color:#dc2626">menghapus</b>');
        newText = newText.replace(/login/gi, '<b style="color:#2563eb">login</b>');
        newText = newText.replace(/logout/gi, '<b style="color:#475569">logout</b>');
        
        return newText;
    }

    function applyFilters() {
        const term = searchInput.value.toLowerCase();
        const userFilter = filterUser.value.toLowerCase();
        
        const start = startDateInput.value ? new Date(startDateInput.value) : null;
        const end = endDateInput.value ? new Date(endDateInput.value) : null;
        if(end) end.setHours(23, 59, 59); // Set ke akhir hari

        const filtered = allLogs.filter(item => {
            // Data fields
            const txt = (item.action || item.activity || "").toLowerCase();
            const usr = (item.username || (item.user ? item.user.username : "")).toLowerCase();
            const dateVal = new Date(item.created_at || item.timestamp);

            // 1. Text Search (Cari di aktivitas)
            const matchText = txt.includes(term);

            // 2. User Filter
            const matchUser = userFilter === "" || usr.includes(userFilter);

            // 3. Date Range
            let matchDate = true;
            if (start && dateVal < start) matchDate = false;
            if (end && dateVal > end) matchDate = false;

            return matchText && matchUser && matchDate;
        });

        renderTable(filtered);
    }

    function exportToCSV() {
        if (allLogs.length === 0) {
            // [UPDATE] Gunakan ui.alert
            ui.alert("Export Gagal", "Tidak ada data untuk diexport.", "warning");
            return;
        }

        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += "Timestamp,Username,Aktivitas\n"; // Header

        allLogs.forEach(row => {
            const date = row.created_at || row.timestamp;
            const user = row.username || (row.user ? row.user.username : "-");
            const act = (row.action || row.activity || "").replace(/,/g, " "); // Hapus koma agar tidak merusak CSV

            csvContent += `${date},${user},${act}\n`;
        });

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "log_aktivitas_sistem.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // [UPDATE] Tambahkan Toast
        ui.toast("File CSV berhasil diunduh", "success");
    }
});