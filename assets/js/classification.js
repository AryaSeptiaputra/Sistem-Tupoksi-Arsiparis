document.addEventListener("DOMContentLoaded", async () => {

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // FIX NAVBAR NOT WORKING
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => {
            if (el.dataset.route) window.location.href = el.dataset.route;
        });
    });

    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("access_token");
        window.location.href = "/page/login";
    });
    // State Management untuk Data
    let allLetters = []; 

    // Referensi Elemen DOM
    const elTableBody = document.getElementById("table-body");
    const elSearch = document.getElementById("searchInput");
    const elStartDate = document.getElementById("startDate");
    const elEndDate = document.getElementById("endDate");
    const elClassFilter = document.getElementById("filterClassification");
    const elBtnReset = document.getElementById("btnResetFilter");

    // 1. Load Data Awal
    await initPage();

    // 2. Event Listeners untuk Filter (Real-time)
    elSearch.addEventListener("keyup", applyFilters);
    elStartDate.addEventListener("change", applyFilters);
    elEndDate.addEventListener("change", applyFilters);
    elClassFilter.addEventListener("change", applyFilters);
    
    // 3. Tombol Reset
    elBtnReset.addEventListener("click", () => {
        elSearch.value = "";
        elStartDate.value = "";
        elEndDate.value = "";
        elClassFilter.value = "";
        applyFilters(); // Render ulang tabel full
    });

    async function initPage() {
        renderLoading();
        try {
            // Menggunakan API existing Anda
            const data = await api.incomingLetter.getAll();
            
            if (!data || data.length === 0) {
                renderEmpty("Belum ada data surat masuk.");
                return;
            }

            // Simpan ke state global agar tidak perlu fetch ulang saat filter
            allLetters = data;

            // Urutkan default: Tanggal Diterima (Terbaru)
            allLetters.sort((a, b) => new Date(b.received_date) - new Date(a.received_date));

            // Isi Dropdown Klasifikasi berdasarkan data yang ada
            populateClassificationOptions(allLetters);

            // Tampilkan Data
            renderTable(allLetters);

        } catch (error) {
            console.error("Error fetching data:", error);
            renderEmpty("Gagal memuat data dari server.", true);
        }
    }

    // --- LOGIKA FILTER UTAMA ---
    function applyFilters() {
        const searchTerm = elSearch.value.toLowerCase();
        const startDate = elStartDate.value ? new Date(elStartDate.value) : null;
        const endDate = elEndDate.value ? new Date(elEndDate.value) : null;
        const classFilter = elClassFilter.value;

        // Reset jam pada endDate agar mencakup seluruh hari tersebut (23:59:59)
        if (endDate) endDate.setHours(23, 59, 59);

        const filteredData = allLetters.filter(item => {
            // 1. Filter Text (No Surat, Pengirim, Subjek)
            const textMatch = 
                (item.number && item.number.toLowerCase().includes(searchTerm)) ||
                (item.sender && item.sender.toLowerCase().includes(searchTerm)) ||
                (item.subject && item.subject.toLowerCase().includes(searchTerm));

            // 2. Filter Klasifikasi
            const classMatch = classFilter === "" || item.classification_code === classFilter;

            // 3. Filter Rentang Tanggal (Berdasarkan received_date)
            let dateMatch = true;
            if (item.received_date) {
                const itemDate = new Date(item.received_date);
                if (startDate && itemDate < startDate) dateMatch = false;
                if (endDate && itemDate > endDate) dateMatch = false;
            }

            return textMatch && classMatch && dateMatch;
        });

        renderTable(filteredData);
    }

    // --- RENDER TABLE ---
    function renderTable(data) {
        elTableBody.innerHTML = "";

        if (data.length === 0) {
            renderEmpty("Data tidak ditemukan dengan filter tersebut.");
            return;
        }

        data.forEach(item => {
            const row = document.createElement("tr");

            // Format Tanggal
            const dateReceived = item.received_date ? new Date(item.received_date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' }) : '-';
            
            // Logic File
            const hasFile = !!item.file_path;
            const fileBtnClass = hasFile ? 'btn-view-file' : 'btn-disabled';
            const fileIcon = hasFile ? '📄' : '❌';
            const fileAction = hasFile ? `viewFile('${item.file_path}')` : '';

            row.innerHTML = `
                <td style="font-weight: 500; font-family: 'Courier New';">${item.number || '-'}</td>
                <td><span style="color:var(--primary-color); font-weight:500;">${dateReceived}</span></td>
                <td>${item.sender || '-'}</td>
                <td>${item.subject || '-'}</td>
                <td>
                    ${item.classification_code 
                        ? `<span class="code-badge">${item.classification_code}</span>` 
                        : '-'}
                </td>
                <td>
                    <span style="font-size:12px; color:var(--text-muted);">
                        👤 ${item.input_by || 'System'}
                    </span>
                </td>
                <td style="text-align: center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view" onclick="${fileAction}" title="Lihat File" ${!hasFile ? 'disabled style="background:#ccc; box-shadow:none;"' : ''}>
                            ${fileIcon}
                        </button>
                        <button class="btn-action-view btn-edit" onclick="editLetter('${item.id}')" title="Edit">✏️</button>
                        <button class="btn-action-view btn-delete" onclick="deleteLetter('${item.id}')" title="Hapus">🗑️</button>
                    </div>
                </td>
            `;
            elTableBody.appendChild(row);
        });
    }

    // --- HELPER FUNCTIONS ---
    
    // Ambil list klasifikasi unik dari data yang ada untuk filter dropdown
    function populateClassificationOptions(data) {
        // Ambil unique codes, filter yang null
        const uniqueCodes = [...new Set(data.map(item => item.classification_code).filter(c => c))];
        
        // Urutkan A-Z
        uniqueCodes.sort();

        // Tambahkan ke dropdown
        uniqueCodes.forEach(code => {
            const option = document.createElement("option");
            option.value = code;
            option.textContent = code;
            elClassFilter.appendChild(option);
        });
    }

    function renderLoading() {
        elTableBody.innerHTML = `<tr><td colspan="7" class="loading-text">Sedang memuat data...</td></tr>`;
    }

    function renderEmpty(message, isError = false) {
        const color = isError ? 'red' : 'inherit';
        elTableBody.innerHTML = `<tr><td colspan="7" class="loading-text" style="color:${color};">${message}</td></tr>`;
    }
});