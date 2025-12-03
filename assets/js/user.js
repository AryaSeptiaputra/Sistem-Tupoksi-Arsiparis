document.addEventListener("DOMContentLoaded", async () => {
    // State Data
    let allUsers = [];

    // Referensi DOM
    const elTableBody = document.getElementById("table-body");
    const elSearch = document.getElementById("searchInput");
    const elFilterRole = document.getElementById("filterRole");
    const elFilterStatus = document.getElementById("filterStatus");
    const elFilterSort = document.getElementById("filterSort");
    const elBtnReset = document.getElementById("btnResetFilter");

    // 1. Cek Login & Navigasi
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => { if (el.dataset.route) window.location.href = el.dataset.route; });
    });
    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("access_token"); window.location.href = "/page/login";
    });

    // 2. Load Data
    await initPage();

    // 3. Event Listeners
    elSearch.addEventListener("keyup", applyFilters);
    elFilterRole.addEventListener("change", applyFilters);
    elFilterStatus.addEventListener("change", applyFilters);
    elFilterSort.addEventListener("change", applyFilters);

    elBtnReset.addEventListener("click", () => {
        elSearch.value = "";
        elFilterRole.value = "";
        elFilterStatus.value = "";
        elFilterSort.value = "newest";
        applyFilters();
    });

    async function initPage() {
        renderLoading();
        try {
            const data = await api.user.getAll();

            if (!data || data.length === 0) {
                renderEmpty("Belum ada data pengguna.");
                return;
            }

            allUsers = data;
            
            // Render awal
            applyFilters();

        } catch (error) {
            console.error(error);
            renderEmpty("Gagal memuat data pengguna.", true);
        }
    }

    // --- LOGIKA FILTER & SORT ---
    function applyFilters() {
        const searchTerm = elSearch.value.toLowerCase();
        const roleFilter = elFilterRole.value; // 'headmaster', 'admin', 'teacher'
        const statusFilter = elFilterStatus.value; // 'active', 'inactive'
        const sortValue = elFilterSort.value;

        // 1. Filtering
        let filteredData = allUsers.filter(user => {
            // Check Search (NUPTK or Username)
            const textMatch = 
                (user.username && user.username.toLowerCase().includes(searchTerm)) ||
                (user.nuptk && user.nuptk.toLowerCase().includes(searchTerm));

            // Check Role
            // Server return role sebagai string (ex: 'Role.admin' atau 'admin')
            // Kita normalisasi stringnya
            const userRole = String(user.role).toLowerCase(); 
            const roleMatch = roleFilter === "" || userRole.includes(roleFilter);

            // Check Status
            const userStatus = String(user.status).toLowerCase();
            const statusMatch = statusFilter === "" || userStatus === statusFilter;

            return textMatch && roleMatch && statusMatch;
        });

        // 2. Sorting
        filteredData.sort((a, b) => {
            if (sortValue === 'newest') {
                // Sort by created_at (descending)
                return new Date(b.created_at) - new Date(a.created_at);
            } else if (sortValue === 'name_asc') {
                return (a.username || '').localeCompare(b.username || '');
            } else if (sortValue === 'name_desc') {
                return (b.username || '').localeCompare(a.username || '');
            }
            return 0;
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

        data.forEach(user => {
            const row = document.createElement("tr");

            // --- Logic Styling ---
            // Role Badge (menggunakan class dari style.css)
            let roleClass = '';
            let roleLabel = '';
            const rawRole = String(user.role).toLowerCase();

            if (rawRole.includes('admin')) { 
                roleClass = 'role-admin'; roleLabel = 'Admin / TU'; 
            } else if (rawRole.includes('headmaster')) { 
                roleClass = 'role-headmaster'; roleLabel = 'Kepala Sekolah'; 
            } else { 
                roleClass = 'role-teacher'; roleLabel = 'Guru'; 
            }

            // Status Dot
            const rawStatus = String(user.status).toLowerCase();
            const isActive = rawStatus === 'active';
            const statusDot = isActive ? 'status-active' : 'status-inactive';
            const statusTextClass = isActive ? 'text-active' : 'text-inactive';
            const statusLabel = isActive ? 'Aktif' : 'Nonaktif';

            // Format Tanggal
            const dateJoined = user.created_at 
                ? new Date(user.created_at).toLocaleDateString('id-ID', {day: 'numeric', month: 'short', year: 'numeric'}) 
                : '-';

            row.innerHTML = `
                <td style="font-family: 'Courier New'; font-weight: 500;">
                    ${user.nuptk || '-'}
                </td>
                <td>
                    <div style="font-weight:600; color:var(--text-main);">${user.username || '-'}</div>
                </td>
                <td>
                    <span class="role-badge ${roleClass}">${roleLabel}</span>
                </td>
                <td>
                    <div style="display:flex; align-items:center;">
                        <span class="status-dot ${statusDot}"></span>
                        <span class="status-text ${statusTextClass}">${statusLabel}</span>
                    </div>
                </td>
                <td style="font-size:13px; color:var(--text-muted);">
                    ${dateJoined}
                </td>
                <td style="text-align: center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" onclick="editUser('${user.id}')" title="Edit Akun">✏️</button>
                        <button class="btn-action-view btn-delete" onclick="deleteUser('${user.id}')" title="Hapus Akun">🗑️</button>
                    </div>
                </td>
            `;
            elTableBody.appendChild(row);
        });
    }

    // --- HELPERS ---
    function renderLoading() {
        elTableBody.innerHTML = `<tr><td colspan="6" class="loading-text">Sedang memuat data...</td></tr>`;
    }

    function renderEmpty(msg, isError = false) {
        const color = isError ? 'red' : 'inherit';
        elTableBody.innerHTML = `<tr><td colspan="6" class="loading-text" style="color:${color};">${msg}</td></tr>`;
    }

    // Placeholder Actions
    window.addUser = () => { alert("Buka Modal Tambah User"); };
    window.editUser = (id) => { alert("Edit User ID: " + id); };
    window.deleteUser = async (id) => {
        if (confirm("Hapus pengguna ini? Akses mereka akan dicabut.")) {
            try { 
                await api.user.delete(id); 
                // Refresh data (tanpa reload page)
                const currentData = await api.user.getAll();
                allUsers = currentData;
                applyFilters(); // Re-render dengan filter yang sedang aktif
            } 
            catch (e) { alert("Gagal hapus: " + e.message); }
        }
    };
});