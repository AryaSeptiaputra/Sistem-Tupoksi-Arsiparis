// assets/js/disposal.js
{
    let disposalList = [];
    let selectedItems = new Set(); // Menyimpan string JSON {id, source}

    // --- INIT ---
    const initDisposalPage = async () => {
        console.log("Disposal Page Loaded");

        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        await loadDisposalData();
        setupEventListeners();
    };

    // --- DATA ---
    const loadDisposalData = async () => {
        const tbody = document.getElementById("table-body");
        if(!tbody) return;

        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center; padding:20px;">Memindai database...</td></tr>`;
        
        try {
            // API ini akan mengecek semua tabel (surat masuk/keluar/keuangan)
            // dan mengambil item yang expired
            const data = await api.disposal.check();
            disposalList = data;
            renderTable(disposalList);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Gagal memuat data: ${e.message}</td></tr>`;
        }
    };

    const renderTable = (data) => {
        const tbody = document.getElementById("table-body");
        const countBadge = document.getElementById("count-badge");
        const checkAll = document.getElementById("checkAll");
        
        if(!tbody) return;

        tbody.innerHTML = "";
        selectedItems.clear(); // Reset pilihan saat refresh
        updateButtonState();

        if (!data || data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align:center; padding:40px;">
                        <div style="font-size:40px;">✅</div>
                        <h4 style="margin:10px 0; color:#059669;">Aman!</h4>
                        <p style="color:#6b7280; font-size:13px;">Tidak ada arsip yang perlu dimusnahkan saat ini.</p>
                    </td>
                </tr>`;
            if(countBadge) countBadge.textContent = "0 Item";
            if(checkAll) checkAll.disabled = true;
            return;
        }

        if(checkAll) {
            checkAll.disabled = false;
            checkAll.checked = false; // Reset header check
        }
        if(countBadge) countBadge.textContent = `${data.length} Item Kadaluwarsa`;

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            // Badge Sumber Data
            let badgeStyle = 'background: #dbeafe; color: #1e40af;'; // Default In
            let badgeLabel = 'Surat Masuk';
            
            if(item.table_source === 'outgoing_letter') { 
                badgeStyle = 'background: #fce7f3; color: #be185d;'; 
                badgeLabel = 'Surat Keluar'; 
            }
            if(item.table_source === 'finance_archive') { 
                badgeStyle = 'background: #ffedd5; color: #9a3412;'; 
                badgeLabel = 'Keuangan'; 
            }

            // Key unik: "id|source"
            // Kita simpan sebagai JSON string di value checkbox
            const uniqueVal = JSON.stringify({ id: item.id, table_source: item.table_source });

            tr.innerHTML = `
                <td style="text-align:center;">
                    <input type="checkbox" class="item-check" value='${uniqueVal}'>
                </td>
                <td><span style="font-size:10px; padding:2px 8px; border-radius:4px; font-weight:700; text-transform:uppercase; ${badgeStyle}">${badgeLabel}</span></td>
                <td>
                    <div style="font-weight:600; color:#1f2937; font-size:14px;">${item.number || '-'}</div>
                    <div style="font-size:12px; color:#6b7280;">${item.title}</div>
                </td>
                <td style="font-family:monospace; font-size:13px;">${item.doc_year}</td>
                <td style="font-family:monospace; font-size:13px; color:#ef4444; font-weight:600;">${item.expiry_year}</td>
                <td><span class="code-badge" style="background:#e0f2fe; color:#0284c7; padding:4px 8px; border-radius:6px; font-size:12px; font-weight:600;">${item.classification}</span></td>
            `;
            tbody.appendChild(tr);
        });

        // Pasang listener ke checkbox individu SETELAH render
        document.querySelectorAll(".item-check").forEach(cb => {
            cb.addEventListener("change", (e) => {
                toggleSelection(e.target.value, e.target.checked);
            });
        });
    };

    const toggleSelection = (jsonString, isChecked) => {
        if (isChecked) {
            selectedItems.add(jsonString);
        } else {
            selectedItems.delete(jsonString);
        }
        updateButtonState();
    };

    const updateButtonState = () => {
        const btnExecute = document.getElementById("btnExecute");
        const count = selectedItems.size;
        
        if(!btnExecute) return;

        if (count > 0) {
            btnExecute.disabled = false;
            btnExecute.innerHTML = `🔥 Musnahkan (${count} Arsip)`;
            btnExecute.style.backgroundColor = "#ef4444";
            btnExecute.style.cursor = "pointer";
        } else {
            btnExecute.disabled = true;
            btnExecute.innerHTML = `🔥 Musnahkan Arsip Terpilih`;
            btnExecute.style.backgroundColor = "#fca5a5";
            btnExecute.style.cursor = "not-allowed";
        }
    };

    // --- EVENT LISTENERS ---
    const setupEventListeners = () => {
        const checkAll = document.getElementById("checkAll");
        const btnExecute = document.getElementById("btnExecute");

        // 1. Check All
        if(checkAll) {
            checkAll.addEventListener("change", (e) => {
                const isChecked = e.target.checked;
                const checkboxes = document.querySelectorAll(".item-check");
                
                checkboxes.forEach(cb => {
                    cb.checked = isChecked;
                    toggleSelection(cb.value, isChecked);
                });
            });
        }

        // 2. Execute Button
        if(btnExecute) {
            btnExecute.addEventListener("click", handleExecution);
        }
    };

    const handleExecution = async () => {
        const count = selectedItems.size;
        if (count === 0) return;

        // Custom Confirm (Bisa pakai ui.confirm atau prompt bawaan)
        // Kita pakai prompt bawaan agar user harus mengetik (Safety)
        const confirmMsg = `PERINGATAN KERAS!\n\n` +
            `Anda akan memusnahkan ${count} arsip secara permanen.\n` +
            `- File digital (Scan) akan DIHAPUS dari server.\n` +
            `- Status data akan diubah menjadi 'Musnah'.\n\n` +
            `Tindakan ini TIDAK BISA DIBATALKAN.\n` +
            `Ketik "SETUJU" untuk melanjutkan:`;

        const userInput = prompt(confirmMsg);

        if (userInput === "SETUJU") {
            const btnExecute = document.getElementById("btnExecute");
            const originalBtnText = btnExecute.innerHTML;
            btnExecute.innerHTML = "Memproses...";
            btnExecute.disabled = true;

            try {
                // Convert Set of JSON strings -> Array of Objects
                const itemsPayload = Array.from(selectedItems).map(str => JSON.parse(str));
                
                const response = await api.disposal.execute(itemsPayload);
                
                alert(`Sukses! ${response.count} arsip telah dimusnahkan.`);
                
                // Refresh data
                await loadDisposalData(); 
            } catch (e) {
                alert("Gagal eksekusi: " + e.message);
                btnExecute.innerHTML = originalBtnText;
                btnExecute.disabled = false;
            }
        } else if (userInput !== null) {
            alert("Pemusnahan dibatalkan (Kata kunci salah).");
        }
    };

    // START
    initDisposalPage();
}