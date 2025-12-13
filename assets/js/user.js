// assets/js/user.js
{
    let allUsers = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- INIT ---
    const initUserPage = async () => {
        console.log("User Page Loaded");

        // 1. Cek Login
        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        // 2. Load Data Utama & Data Guru (untuk dropdown)
        await Promise.all([
            loadUsers(),
            loadTeacherOptions()
        ]);

        // 3. Listeners
        setupEventListeners();
    };

    // --- DATA LOADERS ---
    const loadUsers = async () => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;
        try {
            allUsers = await api.user.getAll();
            renderTable(allUsers);
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Error: ${e.message}</td></tr>`;
        }
    };

    const loadTeacherOptions = async () => {
        const select = document.getElementById("inputTeacherId");
        if(!select) return;

        try {
            select.innerHTML = '<option value="">Memuat...</option>';
            const teachers = await api.teacher.getAll();
            
            select.innerHTML = '<option value="">-- Pilih Guru --</option>';
            
            // Filter: Sebaiknya backend memfilter guru yg belum punya akun, 
            // tapi untuk sekarang kita tampilkan semua atau filter di sisi klien jika perlu.
            teachers.forEach(t => {
                // Tampilkan Nama + NIP
                const opt = document.createElement("option");
                opt.value = t.id;
                opt.textContent = `${t.full_name} (${t.identity_number})`;
                select.appendChild(opt);
            });
        } catch (e) {
            select.innerHTML = '<option value="">Gagal memuat guru</option>';
            console.error(e);
        }
    };

    const renderTable = (data) => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");

            // Role Badge
            let roleClass = 'role-teacher';
            if (item.role === 'admin') roleClass = 'role-admin';
            if (item.role === 'headmaster') roleClass = 'role-headmaster';

            // Status Badge
            const statusClass = item.status === 'active' ? 'status-active' : 'status-inactive';
            const statusLabel = item.status === 'active' ? 'Active' : 'Inactive';

            // Format Tanggal
            const dateStr = item.created_at ? new Date(item.created_at).toLocaleDateString("id-ID") : "-";

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600; color:var(--primary);">${item.username}</td>
                <td>
                    <div style="font-weight:600; color:#374151;">${item.full_name || '-'}</div>
                </td>
                <td><span class="role-badge ${roleClass}">${item.role}</span></td>
                <td>
                    <div style="display:flex; align-items:center;">
                        <span class="status-dot ${statusClass}"></span>
                        <span class="status-text">${statusLabel}</span>
                    </div>
                </td>
                <td style="font-size:12px; color:#6b7280;">${dateStr}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditUser(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteUser(${item.id})">🗑️</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    };

    // --- FORM LOGIC ---
    const showFormMode = (editMode = false, data = null) => {
        isEditMode = editMode;
        document.getElementById("view-table").classList.add("hidden");
        document.getElementById("view-form").classList.remove("hidden");
        document.getElementById("btn-add-new").classList.add("hidden");
        document.getElementById("btn-back-list").classList.remove("hidden");

        const formTitle = document.getElementById("form-title");
        if(formTitle) formTitle.textContent = editMode ? "✏️ Edit Pengguna" : "📝 Tambah Pengguna Baru";
        
        document.getElementById("form-entry").reset();
        
        // Reset status toggle text
        const statusLabel = document.getElementById("statusLabelText");
        const statusToggle = document.getElementById("inputStatusToggle");
        if(statusLabel) statusLabel.textContent = "Aktif";
        if(statusToggle) statusToggle.checked = true;

        const inputTeacher = document.getElementById("inputTeacherId");

        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("entry-id").value = data.id;
            
            // Saat edit, Guru tidak bisa diganti (Readonly/Disabled) karena username=NIP unik
            inputTeacher.value = data.teacher_id; // Pastikan backend kirim teacher_id
            inputTeacher.disabled = true;
            inputTeacher.style.backgroundColor = "#f3f4f6";

            document.getElementById("inputRole").value = data.role;
            
            // Handle Status Toggle
            const isActive = data.status === 'active';
            statusToggle.checked = isActive;
            statusLabel.textContent = isActive ? "Aktif" : "Nonaktif";

        } else {
            currentEditId = null;
            inputTeacher.disabled = false;
            inputTeacher.style.backgroundColor = "";
        }
    };

    const showTableMode = () => {
        document.getElementById("view-form").classList.add("hidden");
        document.getElementById("view-table").classList.remove("hidden");
        document.getElementById("btn-add-new").classList.remove("hidden");
        document.getElementById("btn-back-list").classList.add("hidden");
    };

    // --- LISTENERS ---
    const setupEventListeners = () => {
        const btnAdd = document.getElementById("btn-add-new");
        const btnBack = document.getElementById("btn-back-list");
        const btnCancel = document.getElementById("btnCancel");
        const btnSave = document.getElementById("btnSave");
        const btnReset = document.getElementById("btnResetFilter");

        if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
        if(btnBack) btnBack.addEventListener("click", showTableMode);
        if(btnCancel) btnCancel.addEventListener("click", showTableMode);

        // Status Toggle Listener (Visual Text Change)
        const statusToggle = document.getElementById("inputStatusToggle");
        const statusLabel = document.getElementById("statusLabelText");
        if(statusToggle) {
            statusToggle.addEventListener("change", (e) => {
                statusLabel.textContent = e.target.checked ? "Aktif" : "Nonaktif";
            });
        }

        // Filter Listener
        const searchInput = document.getElementById("searchInput");
        const filterRole = document.getElementById("filterRole");
        const filterStatus = document.getElementById("filterStatus");

        const runFilter = () => {
            const term = searchInput.value.toLowerCase();
            const role = filterRole.value;
            const stat = filterStatus.value; // 'active' or 'inactive'

            const filtered = allUsers.filter(item => {
                const txtMatch = (item.username||"").toLowerCase().includes(term) || (item.full_name||"").toLowerCase().includes(term);
                const roleMatch = role === "" || item.role === role;
                const statMatch = stat === "" || item.status === stat;
                return txtMatch && roleMatch && statMatch;
            });
            renderTable(filtered);
        };

        if(searchInput) searchInput.addEventListener("keyup", runFilter);
        if(filterRole) filterRole.addEventListener("change", runFilter);
        if(filterStatus) filterStatus.addEventListener("change", runFilter);
        
        if(btnReset) {
            btnReset.addEventListener("click", () => {
                searchInput.value = ""; filterRole.value = ""; filterStatus.value = "";
                runFilter();
            });
        }

        // Save Data
        if(btnSave) {
            btnSave.addEventListener("click", async (e) => {
                e.preventDefault();
                
                const teacherId = document.getElementById("inputTeacherId").value;
                const password = document.getElementById("inputPassword").value;
                const confirmPass = document.getElementById("inputConfirmPassword").value;
                const role = document.getElementById("inputRole").value;
                const isActive = document.getElementById("inputStatusToggle").checked;

                if (!teacherId || !role) {
                    alert("Harap pilih Guru dan Role!");
                    return;
                }

                // Validasi Password (Hanya wajib saat Create)
                if (!isEditMode && !password) {
                    alert("Password wajib diisi untuk pengguna baru!");
                    return;
                }
                if (password && password !== confirmPass) {
                    alert("Konfirmasi password tidak cocok!");
                    return;
                }

                const payload = {
                    teacher_id: teacherId,
                    role: role,
                    status: isActive ? 'active' : 'inactive'
                };
                
                if (password) payload.password = password; // Kirim pass hanya jika diisi

                const originalText = btnSave.textContent;
                btnSave.textContent = "Menyimpan...";
                btnSave.disabled = true;

                try {
                    if (isEditMode) {
                        payload.id = currentEditId;
                        await api.user.update(payload);
                        alert("User berhasil diperbarui!");
                    } else {
                        await api.user.create(payload);
                        alert("User berhasil dibuat!");
                    }
                    showTableMode();
                    loadUsers();
                } catch (err) {
                    console.error(err);
                    alert("Gagal: " + (err.message || "Error Server"));
                } finally {
                    btnSave.textContent = originalText;
                    btnSave.disabled = false;
                }
            });
        }
    };

    // --- GLOBAL ACTIONS ---
    window.triggerEditUser = (id) => {
        const item = allUsers.find(u => u.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDeleteUser = async (id) => {
        if(confirm("Yakin ingin menghapus pengguna ini? Akses login akan hilang.")) {
            try {
                await api.user.delete(id);
                loadUsers();
            } catch (e) {
                alert("Gagal menghapus: " + e.message);
            }
        }
    };

    // START
    initUserPage();
}