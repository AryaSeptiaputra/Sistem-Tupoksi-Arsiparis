document.addEventListener("DOMContentLoaded", async () => {

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // NAVIGASI SIDEBAR
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => {
            if (el.dataset.route) window.location.href = el.dataset.route;
        });
    });

    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("access_token");
        window.location.href = "/page/login";
    });

    // STATE MANAGEMENT
    let allData = []; 

    // REFERENSI ELEMENT
    const elTableBody = document.getElementById("table-body");
    const elSearch = document.getElementById("searchInput");
    const elBtnReset = document.getElementById("btnResetFilter");

    // 1. LOAD DATA AWAL
    await initPage();

    // 2. EVENT LISTENER FILTER
    elSearch.addEventListener("keyup", applyFilters);
    
    // 3. TOMBOL RESET
    elBtnReset.addEventListener("click", () => {
        elSearch.value = "";
        applyFilters(); 
    });

    async function initPage() {
        renderLoading();
        try {
            // Panggil API Classification
            const data = await api.classification.getAll();
            
            if (!data || data.length === 0) {
                renderEmpty("Belum ada data klasifikasi.");
                return;
            }

            // Simpan ke state global
            allData = data;

            // Urutkan berdasarkan Kode (A-Z)
            allData.sort((a, b) => a.code.localeCompare(b.code));

            // Tampilkan Data
            renderTable(allData);

        } catch (error) {
            console.error("Error fetching data:", error);
            renderEmpty("Gagal memuat data dari server.", true);
        }
    }

    // --- LOGIKA FILTER ---
    function applyFilters() {
        const searchTerm = elSearch.value.toLowerCase();

        const filteredData = allData.filter(item => {
            // Filter Text: Kode atau Nama
            const codeMatch = item.code && item.code.toLowerCase().includes(searchTerm);
            const nameMatch = item.name && item.name.toLowerCase().includes(searchTerm);
            const descMatch = item.description && item.description.toLowerCase().includes(searchTerm);

            return codeMatch || nameMatch || descMatch;
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

            // Menggunakan class 'code-badge' dari style.css untuk Kode
            row.innerHTML = `
                <td>
                    <span class="code-badge">${item.code || '-'}</span>
                </td>
                <td style="font-weight: 500; color: var(--text-main);">
                    ${item.name || '-'}
                </td>
                <td>
                    <span class="desc-text">${item.description || '-'}</span>
                </td>
                <td style="text-align: center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" onclick="editData('${item.id}', '${item.code}', '${item.name}')" title="Edit">
                            ✏️
                        </button>
                        
                        <button class="btn-action-view btn-delete" onclick="deleteData('${item.id}')" title="Hapus">
                            🗑️
                        </button>
                    </div>
                </td>
            `;
            elTableBody.appendChild(row);
        });
    }

    // --- HELPERS UTILS ---
    
    function renderLoading() {
        elTableBody.innerHTML = `<tr><td colspan="4" class="loading-text">Sedang memuat data...</td></tr>`;
    }

    function renderEmpty(message, isError = false) {
        const color = isError ? 'red' : 'inherit';
        elTableBody.innerHTML = `<tr><td colspan="4" class="loading-text" style="color:${color};">${message}</td></tr>`;
    }

    // --- ACTION HANDLERS (Global Scope agar bisa diakses onclick HTML) ---
    
    window.deleteData = async function(id) {
        if (confirm("Apakah Anda yakin ingin menghapus klasifikasi ini?")) {
            try {
                await api.classification.delete(id);
                alert("Klasifikasi berhasil dihapus.");
                initPage(); // Refresh tabel
            } catch (error) {
                alert("Gagal menghapus: " + error.message);
            }
        }
    };

    window.editData = function(id) {
    window.location.href = `/page/classification/edit?id=${id}`;

    };
});