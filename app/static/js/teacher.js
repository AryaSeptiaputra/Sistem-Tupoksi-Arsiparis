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
    // Data guru menyimpan kode referensi (PNS, aktif, III/a); peta ini memberi nama untuk tabel
    let refNames = { emp: {}, active: {}, rank: {} };
    // Daftar referensi lengkap (termasuk nonaktif) untuk label nilai lama di form edit
    let refLists = { emp: [], active: [], rank: [] };

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    const pageTitle = document.getElementById("page-title");
    
    // Inputs
    const inputId = document.getElementById("entry-id");
    const inputIdentity = document.getElementById("inputIdentity"); 
    const inputName = document.getElementById("inputName");
    const inputGender = document.getElementById("inputGender");
    const inputRank = document.getElementById("inputRank"); // Sekarang ini adalah <select>
    const inputEmpStatus = document.getElementById("inputEmpStatus");
    const inputStatus = document.getElementById("inputStatus");
    const inputAddress = document.getElementById("inputAddress");

    // Buttons
    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    const btnSave = document.getElementById("btnSave");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Filters
    const searchInput = document.getElementById("searchInput");
    const filterStatus = document.getElementById("filterStatus");
    const filterEmpStatus = document.getElementById("filterEmpStatus");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENTS ---
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
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

        // Referensi dimuat dulu agar tabel langsung bisa menampilkan nama dari kode
        await loadReferences();
        await loadData();
    }

    async function loadReferences() {
        try {
            const toNameMap = (data) => Object.fromEntries(data.map(item => [item.code, item.name]));

            // 1. Status Kepegawaian
            const respEmp = await api.reference.getByCategory('teacher_emp_status');
            if(respEmp && respEmp.data) {
                refLists.emp = respEmp.data;
                refNames.emp = toNameMap(respEmp.data);
                ui.fillSelect(filterEmpStatus, respEmp.data, { placeholder: "Semua Kepegawaian" });
                ui.fillSelect(inputEmpStatus, respEmp.data, { placeholder: "- Pilih Status -", activeOnly: true });
            }

            // 2. Status Keaktifan
            const respActive = await api.reference.getByCategory('teacher_active_status');
            if(respActive && respActive.data) {
                refLists.active = respActive.data;
                refNames.active = toNameMap(respActive.data);
                ui.fillSelect(filterStatus, respActive.data, { placeholder: "Semua Status" });
                ui.fillSelect(inputStatus, respActive.data, { activeOnly: true });
            }

            // 3. Pangkat / Golongan
            const respRank = await api.reference.getByCategory('teacher_rank');
            if(respRank && respRank.data) {
                refLists.rank = respRank.data;
                refNames.rank = toNameMap(respRank.data);
                ui.fillSelect(inputRank, respRank.data, { placeholder: "- Pilih Golongan -", activeOnly: true });
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
            document.getElementById("table-body").innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Gagal: ${escapeHtml(e.message)}</td></tr>`;
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
            
            // Kode yang tidak ada di referensi ditampilkan apa adanya
            const statusName = refNames.active[item.status] || item.status;
            const empName = refNames.emp[item.employment_status] || item.employment_status;
            const rankName = item.rank && refNames.rank[item.rank] ? `${item.rank} - ${refNames.rank[item.rank]}` : (item.rank || '-');

            let badgeClass = 'badge-other';
            if(item.status === 'aktif') badgeClass = 'badge-active';
            else if(item.status === 'pensiun') badgeClass = 'badge-inactive';
            const statusBadge = `<span class="${badgeClass}">${escapeHtml(statusName)}</span>`;

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600;">${escapeHtml(item.identity_number)}</td>
                <td>
                    <div style="font-weight:600;">${escapeHtml(item.full_name)}</div>
                    <div style="font-size:11px; color:#64748b;">${escapeHtml(rankName)}</div>
                </td>
                <td>${escapeHtml(item.gender)}</td>
                <td>${escapeHtml(empName)}</td>
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

        document.getElementById("form-entry").reset();
        
        if(editMode && data) {
            pageTitle.textContent = "Edit Data Guru";
            currentEditId = data.id;
            
            inputIdentity.value = data.identity_number;
            inputIdentity.readOnly = true; 
            
            inputName.value = data.full_name;
            inputGender.value = data.gender;
            ui.selectValue(inputRank, data.rank, refLists.rank);
            ui.selectValue(inputEmpStatus, data.employment_status, refLists.emp);
            ui.selectValue(inputStatus, data.status, refLists.active);
            inputAddress.value = data.address || "";

        } else {
            pageTitle.textContent = "Tambah Guru Baru";
            currentEditId = null;
            inputIdentity.readOnly = false;
            ui.selectValue(inputStatus, "aktif", refLists.active);
            // Pangkat kosong dan status kepegawaian belum dipilih
            ui.selectValue(inputRank, null);
            ui.selectValue(inputEmpStatus, null);
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
            ui.alert("Data Belum Lengkap", "Harap lengkapi field wajib!", "warning");
            return;
        }

        const payload = {
            identity_number: inputIdentity.value,
            full_name: inputName.value,
            gender: inputGender.value,
            employment_status: inputEmpStatus.value, 
            rank: inputRank.value, // Mengambil value dari dropdown
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
            ui.alert("Gagal Menyimpan", escapeHtml(err.message || "Server Error"), "error");
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }

    window.triggerEdit = (id) => {
        const item = allData.find(u => u.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Hapus Guru?", "Yakin ingin menghapus data ini?", true);
        if(isConfirmed) {
            try {
                await api.teacher.delete(id);
                ui.toast("Data guru dihapus", "success");
                loadData();
            } catch (err) {
                ui.alert("Gagal Hapus", escapeHtml(err.message), "error");
            }
        }
    };
    
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