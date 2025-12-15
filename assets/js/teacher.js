document.addEventListener("DOMContentLoaded", async () => {
    
    // --- NAVIGASI ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- VARIABLES ---
    let allData = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    const pageTitle = document.getElementById("page-title");
    
    // Inputs
    const inputId = document.getElementById("entry-id");
    const inputIdentity = document.getElementById("inputIdentity"); // NIP/NUPTK
    const inputName = document.getElementById("inputName");
    const inputGender = document.getElementById("inputGender");
    const inputRank = document.getElementById("inputRank");
    const inputEmpStatus = document.getElementById("inputEmpStatus"); // Dynamic
    const inputStatus = document.getElementById("inputStatus");       // Dynamic
    const inputAddress = document.getElementById("inputAddress");

    // Buttons
    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    // [HAPUS] btnCancel dihapus
    const btnSave = document.getElementById("btnSave");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Filters
    const searchInput = document.getElementById("searchInput");
    const filterStatus = document.getElementById("filterStatus"); // Dynamic
    const filterEmpStatus = document.getElementById("filterEmpStatus"); // Dynamic

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENTS ---
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    // [HAPUS] Event listener btnCancel dihapus
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    // Filter Events
    [searchInput, filterStatus, filterEmpStatus].forEach(el => {
        if(el) {
            el.addEventListener("keyup", applyFilters);
            el.addEventListener("change", applyFilters);
        }
    });

    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            searchInput.value = ""; 
            filterStatus.value = ""; 
            filterEmpStatus.value = "";
            applyFilters();
            ui.toast("Filter direset", "info");
        });
    }

    // --- FUNCTIONS ---

    async function initPage() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;

        // Load references first, then data
        await Promise.all([
            loadReferences(),
            loadData()
        ]);
    }

    // [BARU] Load Referensi Status
    async function loadReferences() {
        try {
            const populate = (el, data, placeholder) => {
                if(!el) return;
                el.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '';
                data.forEach(item => {
                    el.add(new Option(item.name, item.name)); // Value pake name karena legacy DB mungkin simpan string
                });
            };

            // 1. Status Kepegawaian (PNS, Honorer, dll)
            const respEmp = await api.reference.getByCategory('teacher_emp_status');
            if(respEmp && respEmp.data) {
                populate(filterEmpStatus, respEmp.data, "Semua Kepegawaian");
                populate(inputEmpStatus, respEmp.data, "- Pilih Status -");
            }

            // 2. Status Keaktifan (Aktif, Pensiun, dll)
            const respActive = await api.reference.getByCategory('teacher_active_status');
            if(respActive && respActive.data) {
                populate(filterStatus, respActive.data, "Semua Status");
                populate(inputStatus, respActive.data, null);
            }

        } catch (e) {
            console.error("Gagal load references:", e);
        }
    }

    async function loadData() {
        try {
            allData = await api.teacher.getAll();
            renderTable(allData);
        } catch (e) {
            console.error(e);
            document.getElementById("table-body").innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            // Badge Styling Logic
            let statusBadge = `<span class="badge-other">${item.status}</span>`;
            if(item.status === 'Aktif') statusBadge = `<span class="badge-active">Aktif</span>`;
            else if(item.status === 'Pensiun' || item.status === 'Keluar') statusBadge = `<span class="badge-inactive">${item.status}</span>`;

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600;">${item.identity_number}</td>
                <td>
                    <div style="font-weight:600;">${item.full_name}</div>
                    <div style="font-size:11px; color:#64748b;">${item.rank || '-'}</div>
                </td>
                <td>${item.gender}</td>
                <td>${item.employment_status}</td>
                <td>${statusBadge}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEdit(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDelete(${item.id})">🗑️</button>
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

        // Reset form
        document.getElementById("form-entry").reset();
        
        if(editMode && data) {
            pageTitle.textContent = "Edit Data Guru";
            currentEditId = data.id;
            
            inputIdentity.value = data.identity_number;
            inputIdentity.readOnly = true; 
            
            inputName.value = data.full_name;
            inputGender.value = data.gender;
            inputRank.value = data.rank || "";
            
            // Set values for dynamic dropdowns
            inputEmpStatus.value = data.employment_status;
            inputStatus.value = data.status;
            
            inputAddress.value = data.address || "";
            
        } else {
            pageTitle.textContent = "Tambah Guru Baru";
            currentEditId = null;
            inputIdentity.readOnly = false;
            
            // Default Values (pastikan 'Aktif' ada di master reference)
            inputStatus.value = "Aktif";
        }
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        viewTable.classList.remove("hidden");
        btnAdd.classList.remove("hidden");
        btnBack.classList.add("hidden");
        pageTitle.textContent = "Master Data Guru";
    }

    async function handleSaveData(e) {
        e.preventDefault();

        if(!inputIdentity.value || !inputName.value || !inputGender.value || !inputEmpStatus.value) {
            ui.alert("Data Belum Lengkap", "Harap lengkapi field wajib: NIP, Nama, Gender, dan Status Pegawai!", "warning");
            return;
        }

        const payload = {
            identity_number: inputIdentity.value,
            full_name: inputName.value,
            gender: inputGender.value,
            employment_status: inputEmpStatus.value, 
            rank: inputRank.value,
            status: inputStatus.value,
            address: inputAddress.value
        };

        const btn = e.target;
        const originalText = btn.textContent;
        btn.textContent = "Menyimpan...";
        btn.disabled = true;

        try {
            if(isEditMode) {
                payload.id = currentEditId;
                await api.teacher.update(payload); 
                ui.toast("Data guru berhasil diperbarui!", "success");
            } else {
                await api.teacher.create(payload);
                ui.toast("Guru berhasil ditambahkan!", "success");
            }
            showTableMode();
            loadData();
        } catch (err) {
            console.error(err);
            ui.alert("Gagal Menyimpan", err.message || "Server Error", "error");
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }

    // --- GLOBAL ---
    window.triggerEdit = (id) => {
        const item = allData.find(u => u.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Hapus Guru?", "Yakin ingin menghapus data ini? Data User dan Arsip terkait mungkin akan ikut terhapus.", true);
        if(isConfirmed) {
            try {
                await api.teacher.delete(id);
                ui.toast("Data guru dihapus", "success");
                loadData();
            } catch (err) {
                ui.alert("Gagal Hapus", err.message, "error");
            }
        }
    };
    
    // --- FILTER ---
    function applyFilters() {
        const term = searchInput.value.toLowerCase();
        const status = filterStatus.value;
        const empStatus = filterEmpStatus.value;

        const filtered = allData.filter(item => {
            const txtMatch = (item.full_name||"").toLowerCase().includes(term) || (item.identity_number||"").includes(term);
            const statusMatch = status === "" || item.status === status;
            const empMatch = empStatus === "" || item.employment_status === empStatus;

            return txtMatch && statusMatch && empMatch;
        });
        
        renderTable(filtered);
    }
});