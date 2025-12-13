// assets/js/storage_location.js
{
    let allLocations = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- INIT ---
    const initStoragePage = async () => {
        console.log("Storage Location Page Loaded");

        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        await loadData();
        setupEventListeners();
    };

    // --- DATA ---
    const loadData = async () => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="4" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;
        
        try {
            allLocations = await api.storageLocation.getAll();
            renderTable(allLocations);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="4" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    };

    const renderTable = (data) => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        data.forEach((item, index) => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td style="text-align:center;">${index + 1}</td>
                <td>
                    <div style="font-weight:600; color:#374151; font-size:15px;">${item.name}</div>
                </td>
                <td>
                    <div style="color:#6b7280; font-size:13px; font-style:italic;">${item.description || '-'}</div>
                </td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditStorage(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteStorage(${item.id})">🗑️</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    };

    // --- FORM & PREVIEW ---
    const showFormMode = (editMode = false, data = null) => {
        isEditMode = editMode;
        
        document.getElementById("view-table").classList.add("hidden");
        document.getElementById("view-form").classList.remove("hidden");
        document.getElementById("btn-add-new").classList.add("hidden");
        document.getElementById("btn-back-list").classList.remove("hidden");

        const pageTitle = document.getElementById("page-title");
        if(pageTitle) pageTitle.textContent = editMode ? "Edit Lokasi" : "Tambah Lokasi";

        document.getElementById("form-entry").reset();
        
        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("entry-id").value = data.id;
            document.getElementById("inputName").value = data.name;
            document.getElementById("inputDescription").value = data.description || "";
        } else {
            currentEditId = null;
        }
        
        updatePreview();
    };

    const showTableMode = () => {
        document.getElementById("view-form").classList.add("hidden");
        document.getElementById("view-table").classList.remove("hidden");
        document.getElementById("btn-add-new").classList.remove("hidden");
        document.getElementById("btn-back-list").classList.add("hidden");

        const pageTitle = document.getElementById("page-title");
        if(pageTitle) pageTitle.textContent = "Lokasi Penyimpanan";
    };

    const updatePreview = () => {
        const name = document.getElementById("inputName").value.trim();
        const desc = document.getElementById("inputDescription").value.trim();
        
        const prevLabel = document.getElementById("previewLabelTxt");
        const prevDesc = document.getElementById("previewDescTxt");

        if(prevLabel) prevLabel.textContent = name || 'NAMA LOKASI';
        if(prevDesc) prevDesc.textContent = desc || 'Keterangan isi arsip...';
    };

    // --- LISTENERS ---
    const setupEventListeners = () => {
        const btnAdd = document.getElementById("btn-add-new");
        const btnBack = document.getElementById("btn-back-list");
        const btnCancel = document.getElementById("btnCancel");
        const btnSave = document.getElementById("btnSave");
        const btnReset = document.getElementById("btnResetFilter");
        const searchInput = document.getElementById("searchInput");

        const inputName = document.getElementById("inputName");
        const inputDesc = document.getElementById("inputDescription");

        if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
        if(btnBack) btnBack.addEventListener("click", showTableMode);
        if(btnCancel) btnCancel.addEventListener("click", showTableMode);

        // Real-time Preview Listeners
        if(inputName) inputName.addEventListener('input', updatePreview);
        if(inputDesc) inputDesc.addEventListener('input', updatePreview);

        if(searchInput) {
            searchInput.addEventListener("keyup", () => {
                const term = searchInput.value.toLowerCase();
                const filtered = allLocations.filter(item => 
                    item.name.toLowerCase().includes(term) || 
                    (item.description && item.description.toLowerCase().includes(term))
                );
                renderTable(filtered);
            });
        }

        if(btnReset) {
            btnReset.addEventListener("click", () => {
                searchInput.value = "";
                renderTable(allLocations);
            });
        }

        if(btnSave) {
            btnSave.addEventListener("click", async (e) => {
                e.preventDefault();
                
                const name = document.getElementById("inputName").value.trim();
                const desc = document.getElementById("inputDescription").value.trim();
                
                if (!name) {
                    alert("Nama Lokasi wajib diisi!");
                    return;
                }

                const payload = {
                    name: name,
                    description: desc
                };

                const originalText = btnSave.textContent;
                btnSave.textContent = "Menyimpan...";
                btnSave.disabled = true;

                try {
                    if (isEditMode) {
                        payload.id = currentEditId;
                        await api.storageLocation.update(payload);
                        alert("Lokasi berhasil diperbarui!");
                    } else {
                        await api.storageLocation.create(payload);
                        alert("Lokasi berhasil disimpan!");
                    }
                    showTableMode();
                    loadData();
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
    window.triggerEditStorage = (id) => {
        const item = allLocations.find(x => x.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDeleteStorage = async (id) => {
        if(confirm("Yakin ingin menghapus lokasi ini? Pastikan tidak ada arsip yang tersimpan di sini.")) {
            try {
                await api.storageLocation.delete(id);
                loadData();
            } catch (err) {
                alert("Gagal hapus: " + err.message);
            }
        }
    };

    // START
    initStoragePage();
}