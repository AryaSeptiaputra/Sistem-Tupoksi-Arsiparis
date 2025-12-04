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
    // State Management
    let allLetters = [];

    // Referensi Elemen DOM
    const elTableBody = document.getElementById("table-body");
    const elSearch = document.getElementById("searchInput");
    const elStartDate = document.getElementById("startDate");
    const elEndDate = document.getElementById("endDate");
    const elClassFilter = document.getElementById("filterClassification");
    const elToggleDecree = document.getElementById("toggleDecreeContainer");
    const elBtnReset = document.getElementById("btnResetFilter");

    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => { if (el.dataset.route) window.location.href = el.dataset.route; });
    });
    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("access_token"); window.location.href = "/page/login";
    });

    // 2. Load Data Awal
    await initPage();

    // 3. Event Listeners untuk Filter
    elSearch.addEventListener("keyup", applyFilters);
    elStartDate.addEventListener("change", applyFilters);
    elEndDate.addEventListener("change", applyFilters);
    elClassFilter.addEventListener("change", applyFilters);
    
    // Logic Toggle SK
    elToggleDecree.addEventListener("click", () => {
        elToggleDecree.classList.toggle("active"); // Ubah visual toggle
        applyFilters(); // Trigger filter ulang
    });

    // Tombol Reset
    elBtnReset.addEventListener("click", () => {
        elSearch.value = "";
        elStartDate.value = "";
        elEndDate.value = "";
        elClassFilter.value = "";
        elToggleDecree.classList.remove("active");
        applyFilters();
    });

    async function initPage() {
        renderLoading();
        try {
            // Panggil API
            const data = await api.outgoingLetter.getAll();

            if (!data || data.length === 0) {
                renderEmpty("Belum ada data surat keluar.");
                return;
            }

            allLetters = data;

            // Urutkan default: Tanggal Surat (Terbaru diatas)
            allLetters.sort((a, b) => new Date(b.letter_date) - new Date(a.letter_date));

            // Populate Dropdown Klasifikasi
            populateClassificationOptions(allLetters);

            // Render Table
            renderTable(allLetters);

        } catch (error) {
            console.error(error);
            renderEmpty("Gagal memuat data dari server.", true);
        }
    }

    // --- LOGIKA FILTER ---
    function applyFilters() {
        const searchTerm = elSearch.value.toLowerCase();
        const startDate = elStartDate.value ? new Date(elStartDate.value) : null;
        const endDate = elEndDate.value ? new Date(elEndDate.value) : null;
        const classFilter = elClassFilter.value;
        const isDecreeOnly = elToggleDecree.classList.contains("active"); // Cek apakah toggle nyala

        if (endDate) endDate.setHours(23, 59, 59);

        const filteredData = allLetters.filter(item => {
            // 1. Filter Text (No Surat, Tujuan, Subjek)
            const textMatch = 
                (item.number && item.number.toLowerCase().includes(searchTerm)) ||
                (item.destination && item.destination.toLowerCase().includes(searchTerm)) ||
                (item.subject && item.subject.toLowerCase().includes(searchTerm));

            // 2. Filter Klasifikasi
            const classMatch = classFilter === "" || item.classification_code === classFilter;

            // 3. Filter Tanggal (Berdasarkan letter_date)
            let dateMatch = true;
            if (item.letter_date) {
                const itemDate = new Date(item.letter_date);
                if (startDate && itemDate < startDate) dateMatch = false;
                if (endDate && itemDate > endDate) dateMatch = false;
            }

            // 4. Filter Toggle SK (Jika aktif, hanya tampilkan yang is_decree == true)
            // Jika toggle mati, tampilkan semua (SK maupun Biasa)
            const decreeMatch = isDecreeOnly ? (item.is_decree === true) : true;

            return textMatch && classMatch && dateMatch && decreeMatch;
        });

        renderTable(filteredData);
    }

    // --- RENDER ---
    function renderTable(data) {
        elTableBody.innerHTML = "";
        if (data.length === 0) {
            renderEmpty("Data tidak ditemukan.");
            return;
        }

        data.forEach(item => {
            const row = document.createElement("tr");

            // Format Tanggal
            const dateLetter = item.letter_date 
                ? new Date(item.letter_date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' }) 
                : '-';

            // Logic SK Badge (Menggunakan class badge-sk dari style.css)
            // badge-sk di CSS warnanya biru muda
            const decreeBadge = item.is_decree 
                ? `<span class="badge-sk">SK</span>` 
                : `<span style="color:var(--text-muted); font-size:11px;">Biasa</span>`;

            // Logic File
            const hasFile = !!item.file_path;
            const fileAction = hasFile ? `viewFile('${item.file_path}')` : '';
            const fileIcon = hasFile ? '📄' : '❌';

            row.innerHTML = `
                <td style="font-weight: 500; font-family: 'Courier New';">${item.number || '-'}</td>
                <td>${dateLetter}</td>
                <td style="font-weight:500;">${item.destination || '-'}</td>
                <td>${item.subject || '-'}</td>
                <td>
                    ${item.classification_code 
                        ? `<span class="code-badge">${item.classification_code}</span>` 
                        : '-'}
                </td>
                <td style="text-align: center;">${decreeBadge}</td>
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

    // --- HELPERS ---
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

    function renderEmpty(msg, isError = false) {
        const color = isError ? 'red' : 'inherit';
        elTableBody.innerHTML = `<tr><td colspan="8" class="loading-text" style="color:${color};">${msg}</td></tr>`;
    }

    // Placeholder Actions
    window.viewFile = (path) => { alert("Membuka file: " + path); };
    window.editLetter = function(id) { window.location.href = `/page/form_outgoing_letter/edit?id=${id}`};
    window.deleteLetter = async (id) => {
        if (confirm("Hapus surat keluar ini?")) {
            try { 
                await api.outgoingLetter.delete(id); 
                // Refresh data setelah delete
                const currentData = await api.outgoingLetter.getAll();
                allLetters = currentData;
                allLetters.sort((a, b) => new Date(b.letter_date) - new Date(a.letter_date));
                applyFilters(); // Re-render dengan filter yang sedang aktif
            } catch (e) { alert("Gagal hapus: " + e.message); }
        }
    };
});

// window.editData = function(id) {
//     window.location.href = `/page/classification/edit?id=${id}`;