document.addEventListener("DOMContentLoaded", async () => {

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // FIX NAVBAR NOT WORKING
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => {
            if (el.dataset.route) window.location.href = el.dataset.route;
        });
    });

    // State Management untuk Data
    let allLetters = [];

    // Referensi Elemen DOM
    const elTableBody = document.getElementById("table-body");
    const elSearch = document.getElementById("searchInput");

    // Filter Tgl Diterima
    const elStartDate = document.getElementById("startDate");
    const elEndDate = document.getElementById("endDate");

    // Filter Tgl Surat (BARU)
    const elLetterStartDate = document.getElementById("letterStartDate");
    const elLetterEndDate = document.getElementById("letterEndDate");

    const elClassFilter = document.getElementById("filterClassification");
    const elBtnReset = document.getElementById("btnResetFilter");

    // 1. Load Data Awal
    await initPage();

    // 2. Event Listeners untuk Filter (Real-time)
    elSearch.addEventListener("keyup", applyFilters);
    elStartDate.addEventListener("change", applyFilters);
    elEndDate.addEventListener("change", applyFilters);
    elLetterStartDate.addEventListener("change", applyFilters); // Listener Baru
    elLetterEndDate.addEventListener("change", applyFilters);   // Listener Baru
    elClassFilter.addEventListener("change", applyFilters);

    // 3. Tombol Reset
    elBtnReset.addEventListener("click", () => {
        elSearch.value = "";
        elStartDate.value = "";
        elEndDate.value = "";
        elLetterStartDate.value = ""; // Reset Baru
        elLetterEndDate.value = "";   // Reset Baru
        elClassFilter.value = "";
        applyFilters();
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

            allLetters = data;

            // Urutkan default: Tanggal Diterima (Terbaru)
            allLetters.sort((a, b) => new Date(b.received_date) - new Date(a.received_date));

            populateClassificationOptions(allLetters);
            renderTable(allLetters);

        } catch (error) {
            console.error("Error fetching data:", error);
            renderEmpty("Gagal memuat data dari server.", true);
        }
    }

    // --- LOGIKA FILTER UTAMA ---
    function applyFilters() {
        const searchTerm = elSearch.value.toLowerCase();

        // Filter Tanggal Diterima
        const startDate = elStartDate.value ? new Date(elStartDate.value) : null;
        const endDate = elEndDate.value ? new Date(elEndDate.value) : null;
        if (endDate) endDate.setHours(23, 59, 59);

        // Filter Tanggal Surat (BARU)
        const letterStartDate = elLetterStartDate.value ? new Date(elLetterStartDate.value) : null;
        const letterEndDate = elLetterEndDate.value ? new Date(elLetterEndDate.value) : null;
        if (letterEndDate) letterEndDate.setHours(23, 59, 59);

        const classFilter = elClassFilter.value;

        const filteredData = allLetters.filter(item => {
            // 1. Filter Text
            const textMatch =
                (item.number && item.number.toLowerCase().includes(searchTerm)) ||
                (item.sender && item.sender.toLowerCase().includes(searchTerm)) ||
                (item.subject && item.subject.toLowerCase().includes(searchTerm));

            // 2. Filter Klasifikasi
            const classMatch = classFilter === "" || item.classification_code === classFilter;

            // 3. Filter Rentang Tanggal Diterima (received_date)
            let receivedDateMatch = true;
            if (item.received_date) {
                const itemDate = new Date(item.received_date);
                if (startDate && itemDate < startDate) receivedDateMatch = false;
                if (endDate && itemDate > endDate) receivedDateMatch = false;
            }

            // 4. Filter Rentang Tanggal Surat (letter_date) - LOGIKA BARU
            let letterDateMatch = true;
            if (item.letter_date) {
                const itemLetDate = new Date(item.letter_date);
                if (letterStartDate && itemLetDate < letterStartDate) letterDateMatch = false;
                if (letterEndDate && itemLetDate > letterEndDate) letterDateMatch = false;
            }

            return textMatch && classMatch && receivedDateMatch && letterDateMatch;
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

            // Format Tanggal Diterima
            const dateReceived = item.received_date
                ? new Date(item.received_date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
                : '-';

            // Format Tanggal Surat (BARU)
            const dateLetter = item.letter_date
                ? new Date(item.letter_date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
                : '-';

            // Logic File
            const hasFile = !!item.file_path;
            const fileIcon = hasFile ? '📄' : '❌';
            const fileAction = hasFile ? `viewFile('${item.file_path}')` : '';

            row.innerHTML = `
                <td style="font-weight: 500; font-family: 'Courier New';">${item.number || '-'}</td>
                <td>${dateLetter}</td> <td><span style="color:var(--primary-color); font-weight:500;">${dateReceived}</span></td>
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
    function populateClassificationOptions(data) {
        const uniqueCodes = [...new Set(data.map(item => item.classification_code).filter(c => c))];
        uniqueCodes.sort();
        uniqueCodes.forEach(code => {
            const option = document.createElement("option");
            option.value = code;
            option.textContent = code;
            elClassFilter.appendChild(option);
        });
    }

    function renderLoading() {
        elTableBody.innerHTML = `<tr><td colspan="8" class="loading-text">Sedang memuat data...</td></tr>`;
    }

    function renderEmpty(message, isError = false) {
        const color = isError ? 'red' : 'inherit';
        elTableBody.innerHTML = `<tr><td colspan="8" class="loading-text" style="color:${color};">${message}</td></tr>`;
    }

    // Placeholder Actions (Global)
    window.viewFile = (path) => { alert("Membuka file: " + path); };
    window.editLetter = (id) => { alert("Edit ID: " + id); };
    window.deleteLetter = async (id) => {
        if (confirm("Hapus data ini?")) alert("Implementasi delete ID: " + id);
    };
});