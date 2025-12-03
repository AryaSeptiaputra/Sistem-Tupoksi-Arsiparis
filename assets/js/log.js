document.addEventListener("DOMContentLoaded", async () => {
    // State Data
    let allLogs = [];

    // Referensi DOM
    const elTableBody = document.getElementById("table-body");
    const elSearch = document.getElementById("searchInput");
    const elStartDate = document.getElementById("startDate");
    const elEndDate = document.getElementById("endDate");
    const elFilterUser = document.getElementById("filterUser");
    const elBtnReset = document.getElementById("btnResetFilter");

    // 1. Cek Login & Navigasi
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => { if (el.dataset.route) window.location.href = el.dataset.route; });
    });
    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("access_token"); window.location.href = "/page/login";
    });

    // 2. Load Data Awal
    await initPage();

    // 3. Event Listeners Filters
    elSearch.addEventListener("keyup", applyFilters);
    elStartDate.addEventListener("change", applyFilters);
    elEndDate.addEventListener("change", applyFilters);
    elFilterUser.addEventListener("change", applyFilters);

    elBtnReset.addEventListener("click", () => {
        elSearch.value = "";
        elStartDate.value = "";
        elEndDate.value = "";
        elFilterUser.value = "";
        applyFilters();
    });

    async function initPage() {
        renderLoading();
        try {
            const data = await api.log.getAll();

            if (!data || data.length === 0) {
                renderEmpty("Belum ada aktivitas tercatat.");
                return;
            }

            allLogs = data;

            // Sort Default: Terbaru diatas
            allLogs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

            // Isi Dropdown User secara otomatis dari data log yang ada
            populateUserFilter(allLogs);

            // Render Tabel
            renderTable(allLogs);

        } catch (error) {
            console.error(error);
            renderEmpty("Gagal memuat log aktivitas.", true);
        }
    }

    // --- LOGIKA FILTER ---
    function applyFilters() {
        const searchTerm = elSearch.value.toLowerCase();
        const startDate = elStartDate.value ? new Date(elStartDate.value) : null;
        const endDate = elEndDate.value ? new Date(elEndDate.value) : null;
        const userFilter = elFilterUser.value;

        // Reset jam pada endDate agar mencakup seluruh hari tersebut (23:59:59)
        if (endDate) endDate.setHours(23, 59, 59);

        const filteredData = allLogs.filter(item => {
            // 1. Filter Text (Action & Username)
            const actionText = (item.action || '').toLowerCase();
            const usernameText = (item.username || '').toLowerCase();
            const textMatch = actionText.includes(searchTerm) || usernameText.includes(searchTerm);

            // 2. Filter Dropdown User
            const userMatch = userFilter === "" || item.username === userFilter;

            // 3. Filter Tanggal
            let dateMatch = true;
            if (item.timestamp) {
                const itemDate = new Date(item.timestamp);
                if (startDate && itemDate < startDate) dateMatch = false;
                if (endDate && itemDate > endDate) dateMatch = false;
            }

            return textMatch && userMatch && dateMatch;
        });

        renderTable(filteredData);
    }

    // --- RENDER TABLE ---
    function renderTable(data) {
        elTableBody.innerHTML = "";

        if (data.length === 0) {
            renderEmpty("Data tidak ditemukan.");
            return;
        }

        data.forEach(item => {
            const row = document.createElement("tr");

            // Format Waktu
            const dateObj = new Date(item.timestamp);
            const dateStr = dateObj.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
            const timeStr = dateObj.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' }).replace(/\./g, ':');

            // Beautify Username
            const userDisplay = item.username ? item.username : 'System';

            // Highlight Keywords pada Action
            let actionHTML = item.action || '-';
            actionHTML = highlightAction(actionHTML);

            row.innerHTML = `
                <td style="white-space:nowrap;">
                    <div class="timestamp-text">
                        <span>${dateStr}</span> • <span style="color:#1f2937; font-weight:600;">${timeStr}</span>
                    </div>
                </td>
                <td>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="background:#ffedd5; padding:4px 8px; border-radius:50%; font-size:12px;">👤</span>
                        <span class="user-link">${userDisplay}</span>
                    </div>
                </td>
                <td>
                    <div class="action-desc">${actionHTML}</div>
                </td>
            `;
            elTableBody.appendChild(row);
        });
    }

    // --- HELPER FUNCTIONS ---

    // Fungsi untuk mewarnai kata kunci agar log lebih mudah dibaca (Scanning)
    function highlightAction(text) {
        return text
            .replace(/menambahkan/gi, '<span style="color:#15803d; font-weight:600;">menambahkan</span>') // Hijau
            .replace(/membuat/gi, '<span style="color:#15803d; font-weight:600;">membuat</span>') // Hijau
            .replace(/mengupdate/gi, '<span style="color:#d97706; font-weight:600;">mengupdate</span>') // Orange
            .replace(/mengedit/gi, '<span style="color:#d97706; font-weight:600;">mengedit</span>') // Orange
            .replace(/menghapus/gi, '<span style="color:#dc2626; font-weight:600;">menghapus</span>') // Merah
            .replace(/login/gi, '<span style="color:#2563eb; font-weight:600;">login</span>') // Biru
            .replace(/logout/gi, '<span style="color:#4b5563; font-weight:600;">logout</span>'); // Abu
    }

    // Mengambil list user unik dari log yang ada untuk mengisi dropdown filter
    function populateUserFilter(data) {
        const uniqueUsers = [...new Set(data.map(item => item.username).filter(u => u))].sort();
        
        uniqueUsers.forEach(user => {
            const option = document.createElement("option");
            option.value = user;
            option.textContent = user;
            elFilterUser.appendChild(option);
        });
    }

    function renderLoading() {
        elTableBody.innerHTML = `<tr><td colspan="3" class="loading-text">Sedang memuat log...</td></tr>`;
    }

    function renderEmpty(msg, isError = false) {
        const color = isError ? 'red' : 'inherit';
        elTableBody.innerHTML = `<tr><td colspan="3" class="loading-text" style="color:${color};">${msg}</td></tr>`;
    }
});