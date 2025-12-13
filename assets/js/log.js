{
    let allLogs = []; 

    const initLogPage = async () => {
        console.log("Log Page Loaded");
        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        await Promise.all([
            loadUsersForFilter(),
            loadLogs()
        ]);
        
        setupEventListeners();
    };

    const loadUsersForFilter = async () => {
        const filterUser = document.getElementById("filterUser");
        if(!filterUser) return;
        try {
            const users = await api.user.getAll();
            filterUser.innerHTML = '<option value="">Semua Pengguna</option>';
            users.forEach(u => {
                const opt = document.createElement("option");
                opt.value = u.username;
                opt.textContent = u.username + (u.role ? ` (${u.role})` : '');
                filterUser.appendChild(opt);
            });
        } catch (e) { console.error("Gagal load users filter", e); }
    };

    const loadLogs = async () => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="3" class="loading-text" style="text-align:center; padding:20px;">Memuat data log...</td></tr>`;
        
        try {
            allLogs = await api.log.getAll();
            // Sort Descending
            allLogs.sort((a, b) => new Date(b.created_at || b.timestamp) - new Date(a.created_at || a.timestamp));
            renderTable(allLogs);
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="3" style="color:red; text-align:center;">Error: ${e.message}</td></tr>`;
        }
    };

    const renderTable = (data) => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; padding:20px; color:var(--text-muted);">Tidak ada aktivitas tercatat.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");
            const rawDate = item.created_at || item.timestamp;
            const dateStr = rawDate ? new Date(rawDate).toLocaleString("id-ID") : "-";
            const username = item.username || (item.user ? item.user.username : "System");
            
            // Highlight Keywords
            let actionText = item.action || item.activity || "-";
            actionText = actionText.replace(/menambahkan|membuat/gi, '<b style="color:#16a34a">$&</b>');
            actionText = actionText.replace(/mengupdate|mengubah/gi, '<b style="color:#ca8a04">$&</b>');
            actionText = actionText.replace(/menghapus/gi, '<b style="color:#dc2626">$&</b>');

            tr.innerHTML = `
                <td style="font-family:monospace; font-size:13px; color:var(--text-muted);">${dateStr}</td>
                <td><span style="font-weight:600; color:var(--primary); background:#fff4ed; padding:4px 10px; border-radius:6px; font-size:12px;">👤 ${username}</span></td>
                <td style="font-size:14px;">${actionText}</td>
            `;
            tbody.appendChild(tr);
        });
    };

    const setupEventListeners = () => {
        const searchInput = document.getElementById("searchInput");
        const filterUser = document.getElementById("filterUser");
        const btnReset = document.getElementById("btnResetFilter");
        const btnExport = document.getElementById("btnExport");
        const startDate = document.getElementById("startDate");
        const endDate = document.getElementById("endDate");

        const runFilter = () => {
            const term = searchInput.value.toLowerCase();
            const usr = filterUser.value.toLowerCase();
            const start = startDate.value ? new Date(startDate.value) : null;
            const end = endDate.value ? new Date(endDate.value) : null;
            if(end) end.setHours(23, 59, 59);

            const filtered = allLogs.filter(item => {
                const txt = (item.action || item.activity || "").toLowerCase();
                const u = (item.username || (item.user ? item.user.username : "")).toLowerCase();
                const d = new Date(item.created_at || item.timestamp);

                let dateMatch = true;
                if(start && d < start) dateMatch = false;
                if(end && d > end) dateMatch = false;

                return txt.includes(term) && u.includes(usr) && dateMatch;
            });
            renderTable(filtered);
        };

        if(searchInput) searchInput.addEventListener("keyup", runFilter);
        if(filterUser) filterUser.addEventListener("change", runFilter);
        if(startDate) startDate.addEventListener("change", runFilter);
        if(endDate) endDate.addEventListener("change", runFilter);

        if(btnReset) {
            btnReset.addEventListener("click", () => {
                searchInput.value = ""; filterUser.value = ""; startDate.value = ""; endDate.value = "";
                runFilter();
            });
        }

        if(btnExport) {
            btnExport.addEventListener("click", () => {
                if (allLogs.length === 0) { alert("Tidak ada data."); return; }
                let csv = "Timestamp,Username,Aktivitas\n";
                allLogs.forEach(r => {
                    const d = r.created_at || r.timestamp;
                    const u = r.username || (r.user ? r.user.username : "-");
                    const a = (r.action || r.activity || "").replace(/,/g, " ");
                    csv += `${d},${u},${a}\n`;
                });
                const link = document.createElement("a");
                link.href = "data:text/csv;charset=utf-8," + encodeURI(csv);
                link.download = "log_aktivitas.csv";
                link.click();
            });
        }
    };

    initLogPage();
}