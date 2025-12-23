document.addEventListener("DOMContentLoaded", async () => {
    
    // --- NAVIGASI ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- VARIABLES ---
    let allUsers = [];
    let allTeachers = []; // Store master guru
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    const pageTitle = document.getElementById("page-title");
    
    // Inputs
    const inputTeacherId = document.getElementById("inputTeacherId"); // Dropdown Guru
    const inputPass = document.getElementById("inputPassword");
    const inputConfPass = document.getElementById("inputConfirmPassword");
    const inputRole = document.getElementById("inputRole");
    const inputStatusToggle = document.getElementById("inputStatusToggle");
    const statusLabelText = document.getElementById("statusLabelText");

    // Buttons
    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    const btnCancel = document.getElementById("btnCancel");
    const btnSave = document.getElementById("btnSave");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Filters
    const searchInput = document.getElementById("searchInput");
    const filterRole = document.getElementById("filterRole");
    const filterStatus = document.getElementById("filterStatus");

    // --- INITIALIZATION ---
    await loadData();
    await loadTeachers(); // Load data guru untuk dropdown

    // --- EVENTS ---
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    if(btnCancel) btnCancel.addEventListener("click", showTableMode);
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    if(inputStatusToggle) {
        inputStatusToggle.addEventListener("change", (e) => {
            statusLabelText.textContent = e.target.checked ? "Aktif" : "Nonaktif";
            statusLabelText.style.color = e.target.checked ? "#1f2937" : "#ef4444";
        });
    }

    [searchInput, filterRole, filterStatus].forEach(el => {
        if(el) {
            el.addEventListener("keyup", applyFilters);
            el.addEventListener("change", applyFilters);
        }
    });

    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            searchInput.value = ""; filterRole.value = ""; filterStatus.value = "";
            applyFilters();
        });
    }

    // --- FUNCTIONS ---

    async function loadData() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;
        try {
            const response = await api.user.getAll();
            allUsers = response.users || [];
            renderTable(allUsers);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    }

    async function loadTeachers() {
        try {
            allTeachers = await api.teacher.getAll();
        } catch (e) {
            console.error("Gagal load teacher", e);
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        data.forEach(user => {
            const tr = document.createElement("tr");
            
            // Handle Status String
            const isActive = user.status === 'active';
            const statusBadge = isActive 
                ? `<span style="background:#dcfce7; color:#166534; padding:4px 10px; border-radius:99px; font-size:11px; font-weight:600;">Active</span>`
                : `<span style="background:#fee2e2; color:#991b1b; padding:4px 10px; border-radius:99px; font-size:11px; font-weight:600;">Inactive</span>`;

            // Handle Role String
            let roleClass = "background:#DCFCE7; color:#16A34A;"; // default teacher
            if (user.role === 'headmaster') roleClass = "background:#F3E8FF; color:#9333EA;";
            else if (user.role === 'admin') roleClass = "background:#DBEAFE; color:#2563EB;";
            
            const dateCreated = user.created_at ? new Date(user.created_at).toLocaleDateString("id-ID") : "-";

            // Tampilkan NIP (identity_number) sebagai username login
            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600;">${user.identity_number || '-'}</td>
                <td>${user.full_name || 'Unknown'}</td>
                <td><span style="padding:4px 10px; border-radius:6px; font-size:11px; font-weight:600; text-transform:capitalize; ${roleClass}">${user.role}</span></td>
                <td>${statusBadge}</td>
                <td style="font-size:13px; color:#6b7280;">${dateCreated}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEdit(${user.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDelete(${user.id})">🗑️</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    function populateTeacherDropdown(selectedTeacherId = null) {
        inputTeacherId.innerHTML = '<option value="">-- Pilih Guru --</option>';
        
        // Filter guru:
        // 1. Jika Edit Mode: Tampilkan Guru yang sedang diedit (biar namanya muncul)
        // 2. Jika Add Mode: Tampilkan HANYA guru yang BELUM punya akun di list allUsers
        
        allTeachers.forEach(t => {
            const hasAccount = allUsers.some(u => u.identity_number === t.identity_number);
            
            // Jika Edit Mode, kita izinkan ID guru yang sedang diedit muncul
            if (isEditMode && t.id == selectedTeacherId) {
                const opt = document.createElement("option");
                opt.value = t.id;
                opt.textContent = `${t.identity_number} - ${t.full_name}`;
                opt.selected = true;
                inputTeacherId.appendChild(opt);
            } 
            // Jika Add Mode, hanya tampilkan yang belum punya akun
            else if (!hasAccount) {
                const opt = document.createElement("option");
                opt.value = t.id;
                opt.textContent = `${t.identity_number} - ${t.full_name}`;
                inputTeacherId.appendChild(opt);
            }
        });

        if(inputTeacherId.options.length === 1 && !isEditMode){
             const opt = document.createElement("option");
             opt.disabled = true;
             opt.textContent = "Semua guru sudah memiliki akun.";
             inputTeacherId.appendChild(opt);
        }
    }

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;
        
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");

        document.getElementById("form-entry").reset();
        
        // Populate Dropdown
        const teacherId = data ? data.teacher_id : null; // Note: pastikan API get_all return teacher_id jika butuh, tp kita bisa cari via NIP
        
        // Kita butuh ID Guru untuk dropdown. Karena API user.get_all mungkin tidak return teacher_id scr eksplisit (hanya identity_number), 
        // kita cari ID teacher dari allTeachers berdasarkan identity_number
        let realTeacherId = null;
        if(data && data.identity_number) {
            const t = allTeachers.find(x => x.identity_number === data.identity_number);
            if(t) realTeacherId = t.id;
        }

        populateTeacherDropdown(realTeacherId);

        if(editMode && data) {
            pageTitle.textContent = "Edit Akun User";
            currentEditId = data.id;
            
            // Disable dropdown guru saat edit (tidak boleh ganti pemilik akun)
            inputTeacherId.value = realTeacherId;
            inputTeacherId.disabled = true; 
            
            inputRole.value = data.role;
            const isActive = data.status === 'active';
            inputStatusToggle.checked = isActive;
            statusLabelText.textContent = isActive ? "Aktif" : "Nonaktif";
            
        } else {
            pageTitle.textContent = "Buat Akun Baru";
            currentEditId = null;
            inputTeacherId.disabled = false;
            
            inputStatusToggle.checked = true;
            statusLabelText.textContent = "Aktif";
        }
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        viewTable.classList.remove("hidden");
        btnAdd.classList.remove("hidden");
        btnBack.classList.add("hidden");
        pageTitle.textContent = "Data Pengguna";
    }

    async function handleSaveData(e) {
        e.preventDefault();

        // Validasi
        if(!inputTeacherId.value || !inputRole.value) {
            ui.alert("Harap pilih Guru dan Role!");
            return;
        }

        const pass = inputPass.value;
        const conf = inputConfPass.value;
        
        if(!isEditMode && !pass) {
            ui.alert("Password wajib diisi untuk akun baru!");
            return;
        }
        if(pass && pass !== conf) {
            ui.alert("Konfirmasi password tidak cocok!");
            return;
        }

        const payload = {
            teacher_id: inputTeacherId.value, // Kirim ID Guru
            role: inputRole.value,
            status: inputStatusToggle.checked ? 'active' : 'inactive' // Kirim String
        };
        
        if(pass) payload.password = pass;

        const btn = e.target;
        const originalText = btn.textContent;
        btn.textContent = "Menyimpan...";
        btn.disabled = true;

        try {
            if(isEditMode) {
                payload.id = currentEditId;
                await api.user.update(payload); 
                ui.toast("Akun berhasil diperbarui!");
            } else {
                await api.user.create(payload);
                ui.toast("Akun berhasil dibuat!");
            }
            showTableMode();
            loadData();
        } catch (err) {
            console.error(err);
            ui.alert("Gagal: " + (err.message || "Server Error"));
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }

    // --- GLOBAL ---
    window.triggerEdit = (id) => {
        const item = allUsers.find(u => u.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        if(confirm("Hapus akun ini? Guru pemilik akun tidak akan terhapus, hanya akses loginnya.")) {
            try {
                await api.user.delete(id);
                loadData();
            } catch (err) {
                ui.confirm("Gagal hapus: " + err.message);
            }
        }
    };
    
    // --- FILTER ---
    function applyFilters() {
        const term = searchInput.value.toLowerCase();
        const role = filterRole.value;
        const status = filterStatus.value;

        const filtered = allUsers.filter(u => {
            const txtMatch = (u.full_name||"").toLowerCase().includes(term) || (u.identity_number||"").includes(term);
            const roleMatch = role === "" || u.role === role;
            const statusMatch = status === "" || u.status === status;

            return txtMatch && roleMatch && statusMatch;
        });
        
        renderTable(filtered);
    }
});