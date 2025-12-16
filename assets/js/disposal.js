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
    let selectedItems = new Set(); 

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
            
            // 1. Tentukan Label & Warna Badge
            let badgeClass = 'src-in';
            let badgeLabel = 'Surat Masuk';
            
            if(item.table_source === 'outgoing_letter') { 
                badgeClass = 'src-out'; badgeLabel = 'Surat Keluar'; 
            } else if(item.table_source === 'finance_archive') { 
                badgeClass = 'src-fin'; badgeLabel = 'Keuangan'; 
            } else if(item.table_source === 'employee_archive') { 
                badgeClass = 'src-emp'; badgeLabel = 'Pegawai'; 
                // Tambahkan style manual jika class css belum ada
                tr.style.cssText = "--emp-color: #7e22ce;"; 
            } else if(item.table_source === 'diploma') {
                badgeClass = 'src-dip'; badgeLabel = 'Ijazah';
            }

            // 2. Tentukan Judul (Fallback ke berbagai key)
            let rawTitle = item.title || item.subject || item.document_name || item.student_name || '(Tanpa Judul)';
            
            // Jika Ijazah, gabungkan nama + jurusan
            if (item.table_source === 'diploma' && item.student_name) {
                rawTitle = `${item.student_name} - ${item.major}`;
            }

            // 3. LOGIKA TAMPILAN PINTAR (SMART DISPLAY)
            // Jika ada Nomor, tampilkan Nomor (Bold) + Judul (Small)
            // Jika TIDAK ada Nomor, tampilkan Judul (Bold) + Tipe (Small)
            
            let mainText = item.number; // Default: Nomor jadi utama
            let subText = rawTitle;     // Default: Judul jadi sub
            
            // Cek jika nomor kosong/strip, ATAU ini adalah arsip keuangan/pegawai
            if (!item.number || item.number === '-' || item.number === 'null') {
                mainText = rawTitle;    // Judul NAIK jadi utama
                subText = item.type || badgeLabel; // Sub-nya jadi kategori (misal: "Arsip Keuangan")
            }

            const uniqueKey = `${item.id}|${item.table_source}`;

            tr.innerHTML = `
                <td style="text-align:center;">
                    <input type="checkbox" class="item-check" data-id="${item.id}" data-source="${item.table_source}" value="${uniqueKey}">
                </td>
                <td><span class="badge-source ${badgeClass}">${badgeLabel}</span></td>
                <td>
                    <div style="font-weight:600; color:var(--text-main); font-size:14px;">
                        ${mainText}
                    </div>
                    <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">
                        ${subText}
                    </div>
                </td>
                <td style="font-family:monospace; font-size:13px;">${item.doc_year}</td>
                <td style="font-family:monospace; font-size:13px; color:#ef4444; font-weight:600;">${item.expiry_year}</td>
                <td><span class="code-badge">${item.classification || '-'}</span></td>
            `;
            tableBody.appendChild(tr);
        });

        // Re-attach listeners
        document.querySelectorAll(".item-check").forEach(cb => {
            cb.addEventListener("change", (e) => {
                toggleSelection(e.target.dataset.id, e.target.dataset.source, e.target.checked);
                updateButtonState();
            });
        });
    }

    function toggleSelection(id, source, isChecked) {
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

        const userConfirmation = await ui.prompt(
            "Konfirmasi Pemusnahan", 
            `PERINGATAN KERAS!<br>
            Anda akan memusnahkan <b>${count} arsip</b> secara permanen.<br>
            - File digital (Scan) akan DIHAPUS.<br>
            - Status data diubah menjadi 'Musnah'.<br><br>
            Ketik <b>SETUJU</b> untuk melanjutkan:`,
            "Batal" 
        );

        if (userConfirmation === "SETUJU") {
            const originalBtnText = btnExecute.innerHTML;
            btnExecute.innerHTML = "Memproses...";
            btnExecute.disabled = true;

            try {
                const itemsPayload = Array.from(selectedItems).map(str => JSON.parse(str));
                
                const response = await api.disposal.execute(itemsPayload);
                
                ui.alert("Pemusnahan Berhasil", `Sukses! ${response.count} arsip telah dimusnahkan.`, "success");
                loadDisposalData(); 
            } catch (e) {
                ui.alert("Gagal Eksekusi", e.message, "error");
                btnExecute.innerHTML = originalBtnText;
                btnExecute.disabled = false;
            }
        } else if (userConfirmation !== null) {
            ui.toast("Konfirmasi salah. Pemusnahan dibatalkan.", "warning");
        }
    }
});