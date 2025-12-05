document.addEventListener("DOMContentLoaded", async () => {

    // --- 0. NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- STATE VARIABLES ---
    let backupLogs = [];
    let userMap = {}; // Object untuk mapping user_id -> username

    // --- DOM REFERENCES ---
    const btnBackup = document.getElementById("btnTriggerBackup");
    const tbody = document.getElementById("table-body");
    
    // Filters
    const searchInput = document.getElementById("searchInput");
    const startDate = document.getElementById("startDate");
    const endDate = document.getElementById("endDate");
    const filterStatus = document.getElementById("filterStatus");
    const filterInitiator = document.getElementById("filterInitiator");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENT LISTENERS ---
    
    // 1. Trigger Backup
    if (btnBackup) {
        btnBackup.addEventListener("click", handleManualBackup);
    }

    // 2. Filters
    [searchInput, startDate, endDate, filterStatus, filterInitiator].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if (btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            searchInput.value = "";
            startDate.value = "";
            endDate.value = "";
            filterStatus.value = "";
            filterInitiator.value = "";
            applyFilters();
        });
    }

    // --- CORE FUNCTIONS ---

    async function initPage() {
        // Load Data User dulu untuk mapping nama di tabel (karena log cuma simpan user_id)
        await loadUserMap();
        // Load Log Backup
        await loadBackupLogs();
    }

    async function loadUserMap() {
        try {
            const users = await api.user.getAll();
            
            // Isi Dropdown Filter Inisiator
            // filterInitiator sudah ada opsi default "SYSTEM" di HTML
            users.forEach(u => {
                userMap[u.id] = u.username; // Simpan di map
                
                // Tambah ke dropdown filter
                if(filterInitiator) {
                    const opt = document.createElement("option");
                    opt.value = u.username;
                    opt.textContent = u.username;
                    filterInitiator.appendChild(opt);
                }
            });
        } catch (e) {
            console.warn("Gagal memuat list user:", e);
        }
    }

    async function loadBackupLogs() {
        tbody.innerHTML = `<tr><td colspan="5" class="loading-text" style="text-align:center; padding:20px;">Memuat riwayat backup...</td></tr>`;
        
        try {
            // Panggil API getLogs dari api.js
            backupLogs = await api.backup.getLogs();
            renderTable(backupLogs);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">Gagal memuat data: ${e.message}</td></tr>`;
        }
    }

    async function handleManualBackup() {
        if(!confirm("Apakah Anda yakin ingin melakukan backup database sekarang?")) return;

        const originalText = btnBackup.innerHTML;
        btnBackup.innerHTML = `<span>⏳</span> Memproses...`;
        btnBackup.disabled = true;

        try {
            // Panggil API manual backup
            const result = await api.backup.manual();
            
            alert("Backup Berhasil! File tersimpan: " + (result.data ? result.data.filename : "Database"));
            
            // Refresh tabel log
            await loadBackupLogs();
            
        } catch (e) {
            console.error(e);
            alert("Backup Gagal: " + (e.message || "Terjadi kesalahan server"));
        } finally {
            btnBackup.innerHTML = originalText;
            btnBackup.disabled = false;
        }
    }

    function renderTable(data) {
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px; color:var(--text-muted);">Belum ada riwayat backup.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");

            // 1. Format Tanggal
            const dateStr = item.created_at ? new Date(item.created_at).toLocaleString("id-ID") : "-";

            // 2. Status Badge
            const isSuccess = (item.status || "").toLowerCase() === 'success';
            const statusBadge = isSuccess 
                ? `<span style="background:#dcfce7; color:#166534; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:600;">✅ Success</span>`
                : `<span style="background:#fee2e2; color:#991b1b; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:600;">❌ Failed</span>`;

            // 3. Inisiator (User atau System)
            let initiatorName = "SYSTEM (Auto)";
            if (item.user_id) {
                // Ambil dari map atau tampilkan ID jika user terhapus
                initiatorName = userMap[item.user_id] ? `👤 ${userMap[item.user_id]}` : `User ID: ${item.user_id}`;
            }

            // 4. File Size (Mockup jika API belum kirim size, atau ambil dari message)
            // Asumsi filename berisi path
            const filename = item.filename || "backup.sql";

            tr.innerHTML = `
                <td style="font-weight:500;">
                    <span style="font-family:monospace;">${filename}</span>
                </td>
                <td style="font-size:13px; color:#6b7280;">${dateStr}</td>
                <td>${statusBadge}</td>
                <td style="font-size:13px;">${initiatorName}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" style="background:#3b82f6;" title="Download" 
                            onclick="alert('Fitur download file ${filename} akan segera tersedia.')">
                            ⬇️
                        </button>
                        <button class="btn-action-view btn-delete" style="background:#f59e0b;" title="Restore Database" 
                            onclick="if(confirm('PERINGATAN: Restore akan menimpa database saat ini. Lanjutkan?')) alert('Fitur restore sedang dalam pengembangan.')">
                            🔄
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    function applyFilters() {
        const term = searchInput.value.toLowerCase();
        const status = filterStatus.value.toLowerCase();
        const initiator = filterInitiator.value; // Username atau 'SYSTEM'

        const start = startDate.value ? new Date(startDate.value) : null;
        const end = endDate.value ? new Date(endDate.value) : null;
        if(end) end.setHours(23, 59, 59);

        const filtered = backupLogs.filter(item => {
            // Text Search (Filename)
            const txtMatch = (item.filename || "").toLowerCase().includes(term);

            // Status Filter
            const itemStatus = (item.status || "").toLowerCase();
            const statusMatch = status === "" || itemStatus === status;

            // Initiator Filter
            let itemInitiator = "SYSTEM";
            if(item.user_id && userMap[item.user_id]) itemInitiator = userMap[item.user_id];
            
            // Logic khusus: filter 'SYSTEM' vs Username
            let initMatch = true;
            if (initiator === "SYSTEM") {
                initMatch = !item.user_id; // Kalau null berarti SYSTEM
            } else if (initiator !== "") {
                initMatch = itemInitiator === initiator;
            }

            // Date Filter
            let dateMatch = true;
            if (item.created_at) {
                const d = new Date(item.created_at);
                if (start && d < start) dateMatch = false;
                if (end && d > end) dateMatch = false;
            }

            return txtMatch && statusMatch && initMatch && dateMatch;
        });

        renderTable(filtered);
    }
});