document.addEventListener("DOMContentLoaded", async () => {
    // State Data
    let allDiplomas = [];

    // Referensi Elemen DOM
    const elTableBody = document.getElementById("table-body");
    const elSearch = document.getElementById("searchInput");
    const elFilterMajor = document.getElementById("filterMajor");
    const elFilterYear = document.getElementById("filterYear");
    const elToggleStatus = document.getElementById("toggleStatusContainer");
    const elBtnReset = document.getElementById("btnResetFilter");

    // 1. Cek Auth & Setup Navigasi Sidebar
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => { if (el.dataset.route) window.location.href = el.dataset.route; });
    });
    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("access_token"); window.location.href = "/page/login";
    });

    // 2. Load Data Awal
    await initPage();

    // 3. Event Listeners Filters
    elSearch.addEventListener("keyup", applyFilters);
    elFilterMajor.addEventListener("change", applyFilters);
    elFilterYear.addEventListener("change", applyFilters);
    
    // Logic Toggle "Belum Diambil"
    elToggleStatus.addEventListener("click", () => {
        elToggleStatus.classList.toggle("active");
        applyFilters();
    });

    // Logic Reset Filter
    elBtnReset.addEventListener("click", () => {
        elSearch.value = "";
        elFilterMajor.value = "";
        elFilterYear.value = "";
        elToggleStatus.classList.remove("active");
        applyFilters();
    });

    async function initPage() {
        renderLoading();
        try {
            // Asumsi endpoint API: /diploma/get_all
            // Ganti sesuai api.js Anda jika berbeda
            const data = await fetchAPI('/diploma/get_all', 'GET'); 
            
            if (!data || data.length === 0) {
                renderEmpty("Belum ada data ijazah.");
                return;
            }

            allDiplomas = data;

            // Sort default: Tahun Ajaran terbaru, lalu Nama Siswa A-Z
            allDiplomas.sort((a, b) => {
                if (b.academic_year !== a.academic_year) {
                    return b.academic_year.localeCompare(a.academic_year);
                }
                return a.student_name.localeCompare(b.student_name);
            });

            // Isi Dropdown Filter secara dinamis
            populateFilters(allDiplomas);

            // Render Tabel
            renderTable(allDiplomas);

        } catch (error) {
            console.error(error);
            renderEmpty("Gagal memuat data.", true);
        }
    }

    // --- LOGIKA FILTER ---
    function applyFilters() {
        const searchTerm = elSearch.value.toLowerCase();
        const selectedMajor = elFilterMajor.value;
        const selectedYear = elFilterYear.value;
        const showUncollectedOnly = elToggleStatus.classList.contains("active");

        const filteredData = allDiplomas.filter(item => {
            // 1. Filter Search (Nama & No Seri)
            const textMatch = 
                (item.student_name && item.student_name.toLowerCase().includes(searchTerm)) ||
                (item.number && item.number.toLowerCase().includes(searchTerm));

            // 2. Filter Jurusan
            const majorMatch = selectedMajor === "" || item.major === selectedMajor;

            // 3. Filter Tahun Ajaran
            const yearMatch = selectedYear === "" || item.academic_year === selectedYear;

            // 4. Filter Status (Jika Toggle ON, hanya tampilkan yang belum diambil)
            // item.status.is_collected boolean dari server
            const statusMatch = showUncollectedOnly ? (item.status.is_collected === false) : true;

            return textMatch && majorMatch && yearMatch && statusMatch;
        });

        renderTable(filteredData);
    }

    // --- RENDER FUNCTIONS ---
    function renderTable(data) {
        elTableBody.innerHTML = "";
        if (data.length === 0) {
            renderEmpty("Data tidak ditemukan.");
            return;
        }

        data.forEach(item => {
            const row = document.createElement("tr");

            // Logic Badge Status
            // Menggunakan class badge-taken / badge-pending dari style.css
            const isCollected = item.status && item.status.is_collected;
            const statusBadge = isCollected 
                ? `<span class="badge-taken">Sudah Diambil</span>` 
                : `<span class="badge-pending">Belum Diambil</span>`;

            // Format Tanggal Ambil
            let collectedDate = '-';
            if (isCollected && item.status.collected_at) {
                collectedDate = new Date(item.status.collected_at).toLocaleDateString('id-ID', {
                    day: 'numeric', month: 'short', year: 'numeric'
                });
            }

            // Logic File (Jika ada scan ijazah)
            const hasFile = !!item.attachment_path;
            const fileBtn = hasFile 
                ? `<button class="btn-action-view" onclick="viewFile('${item.attachment_path}')" title="Lihat Scan">📄</button>`
                : `<button class="btn-action-view" style="background:#ccc; cursor:default;" title="Tidak ada file">❌</button>`;

            row.innerHTML = `
                <td style="font-weight: 500; font-family:'Courier New'; color:var(--text-main);">${item.number || '-'}</td>
                <td style="font-weight:600; color:var(--text-main);">${item.student_name || '-'}</td>
                <td>${item.major || '-'}</td>
                <td><span class="code-badge" style="background:#f3f4f6; color:#4b5563;">${item.academic_year || '-'}</span></td>
                <td>${statusBadge}</td>
                <td style="font-size:12px; color:var(--text-muted);">${collectedDate}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        ${fileBtn}
                        <button class="btn-action-view btn-edit" onclick="editDiploma('${item.id}')" title="Edit">✏️</button>
                        <button class="btn-action-view btn-delete" onclick="deleteDiploma('${item.id}')" title="Hapus">🗑️</button>
                    </div>
                </td>
            `;
            elTableBody.appendChild(row);
        });
    }

    function populateFilters(data) {
        // Ambil Unique Majors
        const majors = [...new Set(data.map(item => item.major).filter(m => m))].sort();
        majors.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m;
            opt.textContent = m;
            elFilterMajor.appendChild(opt);
        });

        // Ambil Unique Academic Years
        const years = [...new Set(data.map(item => item.academic_year).filter(y => y))].sort().reverse();
        years.forEach(y => {
            const opt = document.createElement('option');
            opt.value = y;
            opt.textContent = y;
            elFilterYear.appendChild(opt);
        });
    }

    function renderLoading() {
        elTableBody.innerHTML = `<tr><td colspan="7" class="loading-text">Sedang memuat data...</td></tr>`;
    }

    function renderEmpty(msg, isError = false) {
        const color = isError ? 'red' : 'inherit';
        elTableBody.innerHTML = `<tr><td colspan="7" class="loading-text" style="color:${color};">${msg}</td></tr>`;
    }

    // --- Helper Fetch ---
    // (Jika belum ada di api.js, gunakan wrapper sederhana ini)
    async function fetchAPI(url, method) {
        const token = localStorage.getItem("access_token");
        const res = await fetch(url, {
            method: method,
            headers: { 
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"
            }
        });
        if (!res.ok) throw new Error("API Error");
        return await res.json();
    }

    // Placeholder Actions
    window.viewFile = (path) => { alert("Membuka scan ijazah: " + path); };
    window.editDiploma = function(id) { window.location.href = `/page/form_diploma/edit?id=${id}`};
    window.deleteDiploma = (id) => { 
        if(confirm("Hapus data ini?")) alert("Implementasi delete ID: " + id); 
    };
});