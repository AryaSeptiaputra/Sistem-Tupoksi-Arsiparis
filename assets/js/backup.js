document.addEventListener("DOMContentLoaded", async () => {
    // State Data
    let allBackups = [];

    // Referensi DOM
    const elTableBody = document.getElementById("table-body");
    const elSearch = document.getElementById("searchInput");
    const elStartDate = document.getElementById("startDate");
    const elEndDate = document.getElementById("endDate");
    const elFilterStatus = document.getElementById("filterStatus");
    const elFilterInitiator = document.getElementById("filterInitiator");
    const elBtnReset = document.getElementById("btnResetFilter");
    const elBtnTrigger = document.getElementById("btnTriggerBackup");

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
    elFilterStatus.addEventListener("change", applyFilters);
    elFilterInitiator.addEventListener("change", applyFilters);

    elBtnReset.addEventListener("click", () => {
        elSearch.value = "";
        elStartDate.value = "";
        elEndDate.value = "";
        elFilterStatus.value = "";
        elFilterInitiator.value = "";
        applyFilters();
    });

    // Event Trigger Backup Manual
    elBtnTrigger.addEventListener("click", triggerManualBackup);

    async function initPage() {
        renderLoading();
        try {
            // Fetch data dari API (Asumsi method getLogs() sudah ada di api.js)
            const data = await api.backup.getLogs();

            if (!data || data.length === 0) {
                renderEmpty("Belum ada riwayat backup.");
                return;
            }

            allBackups = data;

            // Sort Default: Terbaru (Created At Descending)
            allBackups.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

            // Isi Dropdown Inisiator (User selain SYSTEM)
            populateInitiatorFilter(allBackups);

            // Render Tabel
            renderTable(allBackups);

        } catch (error) {
            console.error(error);
            renderEmpty("Gagal memuat data backup.", true);
        }
    }

    // --- LOGIKA FILTER ---
    function applyFilters() {
        const searchTerm = elSearch.value.toLowerCase();
        const startDate = elStartDate.value ? new Date(elStartDate.value) : null;
        const endDate = elEndDate.value ? new Date(elEndDate.value) : null;
        const statusFilter = elFilterStatus.value.toLowerCase();
        const initiatorFilter = elFilterInitiator.value;

        // Set End Date ke akhir hari
        if (endDate) endDate.setHours(23, 59, 59);

        const filteredData = allBackups.filter(item => {
            // 1. Filter Text (Filename)
            const textMatch = (item.filename || '').toLowerCase().includes(searchTerm);

            // 2. Filter Status
            const itemStatus = (item.status || '').toLowerCase();
            const statusMatch = statusFilter === "" || itemStatus === statusFilter;

            // 3. Filter Initiator
            const itemInitiator = item.triggered_by || 'SYSTEM';
            const initiatorMatch = initiatorFilter === "" || itemInitiator === initiatorFilter;

            // 4. Filter Tanggal
            let dateMatch = true;
            if (item.created_at) {
                const itemDate = new Date(item.created_at);
                if (startDate && itemDate < startDate) dateMatch = false;
                if (endDate && itemDate > endDate) dateMatch = false;
            }

            return textMatch && statusMatch && initiatorMatch && dateMatch;
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

            // Format Tanggal
            const dateObj = new Date(item.created_at);
            const dateStr = dateObj.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
            const timeStr = dateObj.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });

            // Visual Status
            const isSuccess = (item.status || '').toLowerCase() === 'success';
            const statusBadge = isSuccess 
                ? `<span class="badge-taken" style="font-size:11px;">Success</span>` 
                : `<span class="badge-pending" style="background:#fee2e2; color:#b91c1c;">Failed</span>`;

            // Visual Initiator
            const isSystem = (item.triggered_by === 'SYSTEM');
            const initiatorDisplay = isSystem 
                ? `<span style="font-weight:600; color:var(--text-muted);">🤖 SYSTEM</span>`
                : `<span style="font-weight:600; color:var(--primary);">👤 ${item.triggered_by}</span>`;

            // Disable download button if failed
            const downloadAttr = isSuccess ? `onclick="downloadBackup('${item.filename}')"` : 'disabled style="background:#ccc; cursor:not-allowed;"';

            row.innerHTML = `
                <td style="font-weight: 500; font-family:'Courier New'; color:var(--text-main);">
                    📦 ${item.filename || '-'}
                </td>
                <td>
                    <div style="font-size:13px;">${dateStr} <span style="color:#9ca3af; font-size:12px;">(${timeStr})</span></div>
                </td>
                <td>${statusBadge}</td>
                <td>${initiatorDisplay}</td>
                <td style="text-align: center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-download" title="Download File" ${downloadAttr}>
                            ⬇️
                        </button>
                        <button class="btn-action-view btn-restore" onclick="restoreBackup('${item.filename}')" title="Restore Database" style="background:#f59e0b;">
                            ♻️
                        </button>
                    </div>
                </td>
            `;
            elTableBody.appendChild(row);
        });
    }

    // --- ACTIONS ---
    async function triggerManualBackup() {
        if(!confirm("Apakah Anda yakin ingin melakukan backup database sekarang?")) return;

        const btn = elBtnTrigger;
        const originalText = btn.innerHTML;
        
        try {
            btn.disabled = true;
            btn.innerHTML = "<span>⏳</span> Memproses...";
            
            // Panggil API Backup Manual
            await api.backup.manual(); 
            
            alert("Backup berhasil dibuat!");
            
            // Reload data
            const newData = await api.backup.getLogs();
            allBackups = newData;
            applyFilters(); // Re-render

        } catch (error) {
            alert("Gagal melakukan backup: " + error.message);
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }

    // --- HELPERS ---
    function populateInitiatorFilter(data) {
        // Ambil user unik selain SYSTEM
        const users = [...new Set(data.map(item => item.triggered_by).filter(u => u && u !== 'SYSTEM'))].sort();
        
        users.forEach(user => {
            const option = document.createElement("option");
            option.value = user;
            option.textContent = user;
            elFilterInitiator.appendChild(option);
        });
    }

    function renderLoading() {
        elTableBody.innerHTML = `<tr><td colspan="5" class="loading-text">Sedang memuat data...</td></tr>`;
    }

    function renderEmpty(msg, isError = false) {
        const color = isError ? 'red' : 'inherit';
        elTableBody.innerHTML = `<tr><td colspan="5" class="loading-text" style="color:${color};">${msg}</td></tr>`;
    }

    // Placeholder Global Functions
    window.downloadBackup = (filename) => {
        // Implementasi download real: window.location.href = `/api/backup/download/${filename}`;
        alert("Mengunduh file: " + filename);
    };

    window.restoreBackup = (filename) => {
        if(confirm(`PERINGATAN BAHAYA:\nRestore akan menimpa database saat ini dengan file '${filename}'.\n\nData baru yang dibuat setelah backup ini akan HILANG.\nApakah Anda yakin?`)) {
            alert("Memproses restore untuk: " + filename);
        }
    };
});