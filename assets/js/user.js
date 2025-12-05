document.addEventListener("DOMContentLoaded", async () => {
    
    // --- NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- VARIABLES ---
    let allUsers = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    const pageTitle = document.getElementById("page-title");
    
    // Inputs
    const inputId = document.getElementById("entry-id");
    const inputNuptk = document.getElementById("inputNuptk");
    const inputUsername = document.getElementById("inputUsername");
    const inputPass = document.getElementById("inputPassword");
    const inputConfPass = document.getElementById("inputConfirmPassword");
    const inputRole = document.getElementById("inputRole");
    const inputStatusToggle = document.getElementById("inputStatusToggle");
    const statusLabelText = document.getElementById("statusLabelText");
    const displayStatusBadge = document.getElementById("displayStatusBadge");

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

    // --- EVENTS ---
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    if(btnCancel) btnCancel.addEventListener("click", showTableMode);
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    // Toggle Label Change
    if(inputStatusToggle) {
        inputStatusToggle.addEventListener("change", (e) => {
            const isActive = e.target.checked;
            statusLabelText.textContent = isActive ? "Aktif" : "Nonaktif";
            statusLabelText.style.color = isActive ? "#1f2937" : "#ef4444";
            
            // Update Info Panel badge realtime
            updateInfoPanelStatus(isActive);
        });
    }

    // Filter Events
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
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;

        try {
            allUsers = await api.user.getAll();
            renderTable(allUsers);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
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
            
            // Status Logic
            const isActive = user.is_active || user.status === 'active' || user.status === true;
            const statusBadge = isActive 
                ? `<span style="background:#dcfce7; color:#166534; padding:4px 10px; border-radius:99px; font-size:11px; font-weight:600;">Active</span>`
                : `<span style="background:#fee2e2; color:#991b1b; padding:4px 10px; border-radius:99px; font-size:11px; font-weight:600;">Inactive</span>`;

            // Role Badge logic
            let roleClass = "";
            if (user.role === 'headmaster') roleClass = "background:#F3E8FF; color:#9333EA;";
            else if (user.role === 'admin') roleClass = "background:#DBEAFE; color:#2563EB;";
            else roleClass = "background:#DCFCE7; color:#16A34A;";
            
            const dateCreated = user.created_at ? new Date(user.created_at).toLocaleDateString("id-ID") : "-";

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600;">${user.nuptk}</td>
                <td>${user.username}</td>
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

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;
        
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");

        // Reset inputs
        document.getElementById("form-entry").reset();
        
        if(editMode && data) {
            pageTitle.textContent = "Edit User";
            currentEditId = data.id;
            inputId.value = data.id;
            
            inputNuptk.value = data.nuptk;
            inputNuptk.readOnly = true; // NUPTK tidak boleh diubah saat edit
            
            inputUsername.value = data.username;
            inputRole.value = data.role;
            
            const isActive = data.is_active || data.status === 'active' || data.status === true;
            inputStatusToggle.checked = isActive;
            
            // Trigger visual update for toggle
            statusLabelText.textContent = isActive ? "Aktif" : "Nonaktif";
            updateInfoPanelStatus(isActive);
            
        } else {
            pageTitle.textContent = "Tambah User Baru";
            currentEditId = null;
            inputNuptk.readOnly = false;
            
            // Default Active
            inputStatusToggle.checked = true;
            statusLabelText.textContent = "Aktif";
            updateInfoPanelStatus(true);
        }
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        viewTable.classList.remove("hidden");
        btnAdd.classList.remove("hidden");
        btnBack.classList.add("hidden");
        pageTitle.textContent = "Data Pengguna";
    }

    function updateInfoPanelStatus(isActive) {
        if(isActive) {
            displayStatusBadge.innerHTML = `<span style="width:8px; height:8px; background:#16a34a; border-radius:50%;"></span> Aktif`;
            displayStatusBadge.style.color = "#16a34a";
        } else {
            displayStatusBadge.innerHTML = `<span style="width:8px; height:8px; background:#ef4444; border-radius:50%;"></span> Nonaktif`;
            displayStatusBadge.style.color = "#ef4444";
        }
    }

    async function handleSaveData(e) {
        e.preventDefault();

        // Validasi
        if(!inputNuptk.value || !inputUsername.value || !inputRole.value) {
            alert("Harap lengkapi NUPTK, Username, dan Role!");
            return;
        }

        // Cek Password
        const pass = inputPass.value;
        const conf = inputConfPass.value;
        
        if(!isEditMode && !pass) {
            alert("Password wajib diisi untuk user baru!");
            return;
        }
        if(pass && pass !== conf) {
            alert("Konfirmasi password tidak cocok!");
            return;
        }

        const payload = {
            nuptk: inputNuptk.value,
            username: inputUsername.value,
            role: inputRole.value,
            is_active: inputStatusToggle.checked // Boolean
        };
        
        // Kirim password hanya jika diisi
        if(pass) payload.password = pass;

        const btn = e.target;
        const originalText = btn.textContent;
        btn.textContent = "Menyimpan...";
        btn.disabled = true;

        try {
            if(isEditMode) {
                payload.id = currentEditId;
                await api.user.update(payload); // Pastikan backend terima JSON
                alert("User berhasil diperbarui!");
            } else {
                await api.user.create(payload);
                alert("User berhasil dibuat!");
            }
            showTableMode();
            loadData();
        } catch (err) {
            console.error(err);
            alert("Gagal: " + (err.message || "Server Error"));
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
        if(confirm("Yakin ingin menghapus user ini?")) {
            try {
                await api.user.delete(id);
                loadData();
            } catch (err) {
                alert("Gagal hapus: " + err.message);
            }
        }
    };
    
    // --- FILTER ---
    function applyFilters() {
        const term = searchInput.value.toLowerCase();
        const role = filterRole.value;
        const status = filterStatus.value;

        const filtered = allUsers.filter(u => {
            const txtMatch = (u.username||"").toLowerCase().includes(term) || (u.nuptk||"").includes(term);
            const roleMatch = role === "" || u.role === role;
            
            let statusMatch = true;
            const uActive = u.is_active || u.status === 'active' || u.status === true;
            if(status === 'active') statusMatch = uActive;
            if(status === 'inactive') statusMatch = !uActive;

            return txtMatch && roleMatch && statusMatch;
        });
        
        renderTable(filtered);
    }
});