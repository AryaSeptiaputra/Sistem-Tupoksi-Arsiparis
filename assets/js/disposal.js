document.addEventListener("DOMContentLoaded", async () => {

    // --- NAVIGASI ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- REFERENCES ---
    const tableBody = document.getElementById("table-body");
    const checkAll = document.getElementById("checkAll");
    const btnExecute = document.getElementById("btnExecute");
    const countBadge = document.getElementById("count-badge");

    let disposalList = [];
    let selectedItems = new Set(); // Menggunakan Set untuk menyimpan ID unik

    // --- INIT ---
    await loadDisposalData();

    // --- LISTENERS ---
    
    // 1. Check All Toggle
    if(checkAll) {
        checkAll.addEventListener("change", (e) => {
            const checkboxes = document.querySelectorAll(".item-check");
            checkboxes.forEach(cb => {
                cb.checked = e.target.checked;
                toggleSelection(cb.dataset.id, cb.dataset.source, e.target.checked);
            });
            updateButtonState();
        });
    }

    // 2. Execute Button
    if(btnExecute) {
        btnExecute.addEventListener("click", handleExecution);
    }

    // --- FUNCTIONS ---

    async function loadDisposalData() {
        tableBody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center; padding:20px;">Memindai database...</td></tr>`;
        
        try {
            const data = await api.disposal.check();
            disposalList = data;
            renderTable(disposalList);
        } catch (e) {
            console.error(e);
            tableBody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Gagal memuat data: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        tableBody.innerHTML = "";
        selectedItems.clear();
        updateButtonState();

        if (!data || data.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align:center; padding:40px;">
                        <div style="font-size:40px;">✅</div>
                        <h4 style="margin:10px 0; color:#059669;">Aman!</h4>
                        <p style="color:#6b7280; font-size:13px;">Tidak ada arsip yang perlu dimusnahkan saat ini.</p>
                    </td>
                </tr>`;
            countBadge.textContent = "0 Item";
            if(checkAll) checkAll.disabled = true;
            return;
        }

        if(checkAll) checkAll.disabled = false;
        countBadge.textContent = `${data.length} Item Kadaluwarsa`;

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            // Badge Source
            let badgeClass = 'src-in';
            let badgeLabel = 'Surat Masuk';
            if(item.table_source === 'outgoing_letter') { badgeClass = 'src-out'; badgeLabel = 'Surat Keluar'; }
            if(item.table_source === 'finance_archive') { badgeClass = 'src-fin'; badgeLabel = 'Keuangan'; }

            // Key unik untuk seleksi: "id|source" (karena ID bisa sama antar tabel)
            const uniqueKey = `${item.id}|${item.table_source}`;

            tr.innerHTML = `
                <td style="text-align:center;">
                    <input type="checkbox" class="item-check" data-id="${item.id}" data-source="${item.table_source}" value="${uniqueKey}">
                </td>
                <td><span class="badge-source ${badgeClass}">${badgeLabel}</span></td>
                <td>
                    <div style="font-weight:600; color:var(--text-main); font-size:14px;">${item.number || '-'}</div>
                    <div style="font-size:12px; color:var(--text-muted);">${item.title}</div>
                </td>
                <td style="font-family:monospace; font-size:13px;">${item.doc_year}</td>
                <td style="font-family:monospace; font-size:13px; color:#ef4444; font-weight:600;">${item.expiry_year}</td>
                <td><span class="code-badge">${item.classification}</span></td>
            `;
            tableBody.appendChild(tr);
        });

        // Pasang listener individual checkbox setelah render
        document.querySelectorAll(".item-check").forEach(cb => {
            cb.addEventListener("change", (e) => {
                toggleSelection(e.target.dataset.id, e.target.dataset.source, e.target.checked);
                updateButtonState();
            });
        });
    }

    function toggleSelection(id, source, isChecked) {
        // Objek item yang akan dikirim ke backend
        // Kita simpan string JSON agar mudah di Set, nanti diparse saat kirim
        const itemObj = JSON.stringify({ id: parseInt(id), table_source: source });
        
        if (isChecked) {
            selectedItems.add(itemObj);
        } else {
            selectedItems.delete(itemObj);
        }
    }

    function updateButtonState() {
        const count = selectedItems.size;
        if (count > 0) {
            btnExecute.disabled = false;
            btnExecute.innerHTML = `🔥 Musnahkan (${count} Arsip)`;
        } else {
            btnExecute.disabled = true;
            btnExecute.innerHTML = `🔥 Musnahkan Arsip Terpilih`;
        }
    }

    async function handleExecution() {
        const count = selectedItems.size;
        if (count === 0) return;

        const confirmMsg = `PERINGATAN KERAS!\n\n` +
            `Anda akan memusnahkan ${count} arsip secara permanen.\n` +
            `- File digital (Scan) akan DIHAPUS dari server.\n` +
            `- Status data akan diubah menjadi 'Musnah'.\n\n` +
            `Tindakan ini TIDAK BISA DIBATALKAN.\n` +
            `Ketik "SETUJU" untuk melanjutkan:`;

        const userInput = prompt(confirmMsg);

        if (userInput === "SETUJU") {
            const originalBtnText = btnExecute.innerHTML;
            btnExecute.innerHTML = "Memproses...";
            btnExecute.disabled = true;

            try {
                // Convert Set of JSON strings back to Array of Objects
                const itemsPayload = Array.from(selectedItems).map(str => JSON.parse(str));
                
                const response = await api.disposal.execute(itemsPayload);
                
                alert(`Sukses! ${response.count} arsip telah dimusnahkan.`);
                loadDisposalData(); // Refresh table
            } catch (e) {
                alert("Gagal eksekusi: " + e.message);
                btnExecute.innerHTML = originalBtnText;
                btnExecute.disabled = false;
            }
        } else {
            alert("Pemusnahan dibatalkan.");
        }
    }
});