document.addEventListener("DOMContentLoaded", async () => {
    
    // --- 0. NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- STATE VARIABLES ---
    let allLocations = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");

    // Buttons
    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    // [HAPUS] btnCancel
    const btnSave = document.getElementById("btnSave");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Form Inputs
    const inputId = document.getElementById("entry-id");
    const inputName = document.getElementById("inputName");
    const inputDesc = document.getElementById("inputDescription");

    // Preview Label
    const previewLabelTxt = document.getElementById("previewLabelTxt");
    const previewDescTxt = document.getElementById("previewDescTxt");

    // Filter
    const searchInput = document.getElementById("searchInput");

    // --- INITIALIZATION ---
    await loadData();

    // --- EVENT LISTENERS ---
    
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    // [HAPUS] Event listener btnCancel
    
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    // Live Preview Label
    if(inputName) {
        inputName.addEventListener("input", (e) => {
            previewLabelTxt.textContent = e.target.value || "LEMARI X";
        });
    }

    if(searchInput) {
        searchInput.addEventListener("keyup", applyFilter);
        searchInput.addEventListener("change", applyFilter);
    }
    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            searchInput.value = "";
            applyFilter();
            ui.toast("Filter direset", "info");
        });
    }

    // --- FUNCTIONS ---

    async function loadData() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="4" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;
        
        try {
            const response = await api.storageLocation.getAll();
            allLocations = response.storage_locations || [];
            // Sort A-Z
            allLocations.sort((a, b) => a.name.localeCompare(b.name));
            renderTable(allLocations);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="4" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:20px;">Belum ada data lokasi. Silakan tambah baru.</td></tr>`;
            return;
        }

        data.forEach((item, index) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>
                    <div style="font-weight:600; color:var(--text-main); font-size:14px;">
                        🗄️ ${item.name}
                    </div>
                </td>
                <td style="color:var(--text-muted); font-size:13px;">${item.description || '-'}</td>
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

    // --- VIEW SWITCHING ---

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;
        
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");

        if(editMode) {
            pageTitle.textContent = "Edit Lokasi";
            pageSubtitle.textContent = "Perbarui nama atau keterangan lokasi.";
        } else {
            pageTitle.textContent = "Tambah Lokasi Baru";
            pageSubtitle.textContent = "Daftarkan lemari atau rak arsip baru.";
        }

        document.getElementById("form-entry").reset();
        
        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputName.value = data.name;
            inputDesc.value = data.description || "";
            // Trigger preview update
            if(previewLabelTxt) previewLabelTxt.textContent = data.name;
        } else {
            currentEditId = null;
            if(previewLabelTxt) previewLabelTxt.textContent = "LEMARI BARU";
        }
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        viewTable.classList.remove("hidden");
        btnAdd.classList.remove("hidden");
        btnBack.classList.add("hidden");

        pageTitle.textContent = "Lokasi Penyimpanan";
        pageSubtitle.textContent = "Kelola daftar lemari, rak, atau boks arsip fisik.";
    }

    // --- CRUD ACTIONS ---

    async function handleSaveData(e) {
        e.preventDefault();
        
        if (!inputName.value.trim()) {
            ui.alert("Data Tidak Lengkap", "Nama Lokasi wajib diisi!", "warning");
            return;
        }

        const payload = {
            name: inputName.value.trim(),
            description: inputDesc.value.trim() || null
        };

        const originalText = btnSave.textContent;
        btnSave.textContent = "Menyimpan...";
        btnSave.disabled = true;

        try {
            if (isEditMode) {
                payload.id = currentEditId;
                await api.storageLocation.update(payload);
                ui.toast("Berhasil diperbarui!", "success");
            } else {
                await api.storageLocation.create(payload);
                ui.toast("Berhasil disimpan!", "success");
            }
            showTableMode();
            loadData();
        } catch (err) {
            console.error(err);
            ui.alert("Gagal Menyimpan", err.message || "Error Server", "error");
        } finally {
            btnSave.textContent = originalText;
            btnSave.disabled = false;
        }
    }

    // Expose functions to window for onclick events in HTML
    window.triggerEdit = (id) => {
        const item = allLocations.find(x => x.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Hapus Lokasi?", "Yakin ingin menghapus lokasi ini? Pastikan tidak ada arsip yang tersimpan di sini.", true);
        if(isConfirmed) {
            try {
                await api.storageLocation.delete(id);
                ui.toast("Lokasi dihapus", "success");
                loadData();
            } catch (err) {
                ui.alert("Gagal Hapus", err.message, "error");
            }
        }
    };

    function applyFilter() {
        const term = searchInput.value.toLowerCase();
        const filtered = allLocations.filter(item => 
            item.name.toLowerCase().includes(term) || 
            (item.description && item.description.toLowerCase().includes(term))
        );
        renderTable(filtered);
    }
});