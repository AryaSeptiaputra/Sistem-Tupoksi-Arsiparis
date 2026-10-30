document.addEventListener("DOMContentLoaded", async () => {

    // --- 0. NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

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
    let backupLogs = [];
    await loadBackupLogs();

    // --- EVENT LISTENERS ---
    if (btnBackup) btnBackup.addEventListener("click", handleManualBackup);

    [searchInput, startDate, endDate, filterStatus, filterInitiator].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if (btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            searchInput.value = ""; startDate.value = ""; endDate.value = "";
            filterStatus.value = ""; filterInitiator.value = "";
            applyFilters();
            ui.toast("Filter direset", "info");
        });
    }

    // --- CORE FUNCTIONS ---

    async function loadBackupLogs() {
        tbody.innerHTML = `<tr><td colspan="5" class="loading-text" style="text-align:center; padding:20px;">Memuat riwayat backup...</td></tr>`;
        try {
            const response = await fetch('/backup/logs', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if(!response.ok) throw new Error("Gagal mengambil data logs");

            backupLogs = await response.json();
            
            // Urutkan dari yang terbaru (Created At descending)
            backupLogs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            populateInitiatorFilter();
            // Filter yang sedang dipilih tetap berlaku setelah riwayat dimuat ulang
            applyFilters();
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">Gagal memuat data: ${escapeHtml(e.message)}</td></tr>`;
        }
    }

    async function handleManualBackup() {
        // [MODIFIKASI] Gunakan ui.confirm pengganti confirm() biasa
        const isConfirmed = await ui.confirm(
            "Backup Database?", 
            "Proses ini akan menyimpan salinan database saat ini. Lanjutkan?"
        );
        
        if(!isConfirmed) return;

        const originalText = btnBackup.innerHTML;
        btnBackup.innerHTML = `<span>⏳</span> Memproses...`;
        btnBackup.disabled = true;

        try {
            const response = await fetch('/backup/manual', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if(!response.ok) {
                const err = await response.json();
                throw new Error(err.error || "Gagal melakukan backup");
            }

            const result = await response.json();
            
            // [MODIFIKASI] Gunakan Toast untuk sukses
            ui.toast("Backup Berhasil Disimpan!", "success");
            
            await loadBackupLogs();
        } catch (e) {
            console.error(e);
            // [MODIFIKASI] Gunakan Modal Error untuk gagal
            await ui.alert("Backup Gagal", escapeHtml(e.message || "Terjadi kesalahan server"), "error");
        } finally {
            btnBackup.innerHTML = originalText;
            btnBackup.disabled = false;
        }
    }

    // --- [FITUR DOWNLOAD & RESTORE] ---

    window.downloadBackup = (filename) => {
        const url = `/backup/download/${filename}`;
        
        const originalCursor = document.body.style.cursor;
        document.body.style.cursor = "wait";

        // [MODIFIKASI] Beri feedback visual bahwa download dimulai
        ui.toast("Mengunduh file...", "info");

        fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (!response.ok) {
                 const contentType = response.headers.get("content-type");
                 if (contentType && !contentType.includes("application/json")) {
                     throw new Error(`Server Error (${response.status}). Path salah atau file hilang.`);
                 }
                 throw new Error("Gagal mengunduh file.");
            }
            return response.blob();
        })
        .then(blob => {
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename; 
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(downloadUrl);
        })
        .catch(err => {
            console.error(err);
            // [MODIFIKASI] Error download pakai Modal
            ui.alert("Gagal Download", escapeHtml(err.message), "error");
        })
        .finally(() => {
            document.body.style.cursor = originalCursor;
        });
    };

    window.restoreBackup = async (filename) => {
        // [MODIFIKASI] Ganti Prompt ketik 'SETUJU' dengan Double Confirmation (2x Klik)
        
        // Konfirmasi Tahap 1
        const step1 = await ui.confirm(
            "⚠️ Peringatan Restore", 
            `Anda akan merestore database ke versi: ${escapeHtml(filename)}.\n\nSemua data baru setelah tanggal backup ini akan HILANG. Lanjutkan?`, 
            true // True = Tombol Merah (Danger)
        );
        
        if (!step1) return;

        // Konfirmasi Tahap 2 (Double Check)
        const step2 = await ui.confirm(
            "❗ Konfirmasi Terakhir",
            "Tindakan ini TIDAK DAPAT DIBATALKAN. Sistem mungkin tidak dapat diakses selama proses restore. Yakin?",
            true
        );

        if (!step2) return;

        document.body.style.cursor = "wait";
        
        // Tampilkan loading toast
        ui.toast("Sedang merestore database...", "info");
        
        try {
            const response = await fetch('/backup/restore', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ filename: filename })
            });

            // Cek tipe konten
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                const text = await response.text();
                throw new Error(`Server Error (${response.status}): Respon tidak valid.`);
            }

            const result = await response.json();

            if (!response.ok) throw new Error(result.error || "Gagal restore database");

            // [MODIFIKASI] Sukses pakai Modal
            await ui.alert("Restore Sukses", "Database telah dikembalikan. Sistem akan dimuat ulang.", "success");
            window.location.reload();

        } catch (e) {
            console.error(e);
            // [MODIFIKASI] Error pakai Modal
            await ui.alert("Gagal Restore", escapeHtml(e.message), "error");
        } finally {
            document.body.style.cursor = "default";
        }
    };

    function renderTable(data) {
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px; color:var(--text-muted);">Belum ada riwayat backup.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");

            const dateStr = item.created_at ? new Date(item.created_at).toLocaleString("id-ID") : "-";
            const filename = item.filename || "-";
            // Entri lama tanpa status dianggap berhasil
            const isSuccess = String(item.status || "SUCCESS").toUpperCase() === "SUCCESS";
            const statusBadge = isSuccess
                ? `<span style="background:#dcfce7; color:#166534; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:600;">✅ Berhasil</span>`
                : `<span style="background:#fee2e2; color:#991b1b; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:600;">❌ Gagal</span>`;
            const failureNote = isSuccess ? "" : `<div style="font-size:11px; color:#991b1b; margin-top:4px;">${escapeHtml(item.message || "")}</div>`;
            // Unduh dan restore hanya untuk backup berhasil yang punya berkas
            const actions = isSuccess && item.filename
                ? `<button class="btn-action-view btn-edit btn-download" style="background:#3b82f6;" title="Download"
                        data-filename="${escapeHtml(filename)}">⬇️</button>
                   <button class="btn-action-view btn-delete btn-restore" style="background:#f59e0b;" title="Restore Database"
                        data-filename="${escapeHtml(filename)}">🔄</button>`
                : `<span style="color:#9ca3af; font-size:12px;">-</span>`;

            tr.innerHTML = `
                <td style="font-weight:500;">
                    <span style="font-family:monospace;">${escapeHtml(filename)}</span>
                    ${failureNote}
                </td>
                <td style="font-size:13px; color:#6b7280;">${dateStr}</td>
                <td>${statusBadge}</td>
                <td style="font-size:13px;">${escapeHtml(item.created_by || 'System')}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">${actions}</div>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll(".btn-download").forEach(btn =>
            btn.addEventListener("click", () => window.downloadBackup(btn.dataset.filename)));
        tbody.querySelectorAll(".btn-restore").forEach(btn =>
            btn.addEventListener("click", () => window.restoreBackup(btn.dataset.filename)));
    }

    // Pilihan inisiator diambil dari riwayat: nama operator atau SYSTEM untuk backup otomatis
    function populateInitiatorFilter() {
        const selected = filterInitiator.value;
        const initiators = [...new Set(backupLogs.map(item => item.created_by).filter(Boolean))].sort();
        filterInitiator.innerHTML = '<option value="">Semua Inisiator</option>';
        initiators.forEach(name => filterInitiator.add(new Option(name, name)));
        filterInitiator.value = initiators.includes(selected) ? selected : "";
    }

    function applyFilters() {
        const term = searchInput.value.toLowerCase();
        const status = filterStatus.value;
        const initiator = filterInitiator.value;
        const start = startDate.value ? new Date(startDate.value) : null;
        const end = endDate.value ? new Date(endDate.value) : null;
        if(end) end.setHours(23, 59, 59);

        const filtered = backupLogs.filter(item => {
            const txtMatch = (item.filename || "").toLowerCase().includes(term);
            // Nilai filter "success"/"failed", sedangkan riwayat menyimpan "SUCCESS"/"FAILED"
            const statusMatch = status === "" || String(item.status || "SUCCESS").toLowerCase() === status;
            const initiatorMatch = initiator === "" || item.created_by === initiator;
            let dateMatch = true;
            if (item.created_at) {
                const d = new Date(item.created_at);
                if (start && d < start) dateMatch = false;
                if (end && d > end) dateMatch = false;
            }
            return txtMatch && statusMatch && initiatorMatch && dateMatch;
        });

        renderTable(filtered);
    }
});