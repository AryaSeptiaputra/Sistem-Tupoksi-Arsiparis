document.addEventListener("DOMContentLoaded", async () => {
    
    // --- 0. NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- STATE VARIABLES ---
    let allClassifications = [];
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
    const inputCode = document.getElementById("inputCode");
    const inputName = document.getElementById("inputName");
    const inputDesc = document.getElementById("inputDescription");
    const inputRetActive = document.getElementById("inputRetActive");
    const inputRetInactive = document.getElementById("inputRetInactive");
    const inputFinalAction = document.getElementById("inputFinalAction"); // Dynamic

    // Previews
    const previewCodeTxt = document.getElementById("previewCodeTxt");
    const previewNameTxt = document.getElementById("previewNameTxt");

    // Filter
    const searchInput = document.getElementById("searchInput");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENT LISTENERS ---
    
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    // [HAPUS] Event listener btnCancel

    if(inputCode && inputName) {
        inputCode.addEventListener('input', updatePreview);
        inputName.addEventListener('input', updatePreview);
    }

    if(btnSave) btnSave.addEventListener("click", handleSaveData);

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

    async function initPage() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="4" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;
        
        await Promise.all([
            loadReferences(), // [BARU]
            loadData()
        ]);
    }

    // [BARU] Load Referensi Final Action
    async function loadReferences() {
        try {
            const response = await api.reference.getByCategory('final_action');
            const data = response.data || [];

            if(inputFinalAction) {
                inputFinalAction.innerHTML = '';
                data.forEach(item => {
                    inputFinalAction.add(new Option(item.name, item.code));
                });
            }
        } catch (e) {
            console.error("Gagal load references:", e);
        }
    }

    async function loadData() {
        try {
            allClassifications = await api.classification.getAll();
            allClassifications.sort((a, b) => a.code.localeCompare(b.code));
            renderTable(allClassifications);
        } catch (e) {
            console.error(e);
            document.getElementById("table-body").innerHTML = `<tr><td colspan="4" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");

            // Logic Badge Warna berdasarkan String Code
            let actionBadgeClass = '';
            let actionLabel = item.final_action ? item.final_action.toUpperCase() : '-';
            
            // Mapping Style Manual (Label bisa juga di-mapping jika ingin lebih cantik dari sekedar uppercase code)
            switch(item.final_action) {
                case 'permanent':
                    actionBadgeClass = 'background:#dbeafe; color:#1e40af; border:1px solid #bfdbfe;'; 
                    break;
                case 'assess':
                    actionBadgeClass = 'background:#fef3c7; color:#92400e; border:1px solid #fde68a;'; 
                    break;
                case 'destroy':
                    actionBadgeClass = 'background:#fee2e2; color:#991b1b; border:1px solid #fecaca;'; 
                    break;
                default:
                    actionBadgeClass = 'background:#f3f4f6; color:#374151; border:1px solid #e5e7eb;';
            }

            tr.innerHTML = `
                <td><span class="code-badge">${item.code}</span></td>
                <td>
                    <div style="font-weight:500; font-size:15px; margin-bottom:4px;">${item.name}</div>
                    <div style="font-size:12px; color:#555; background:#f3f4f6; display:inline-block; padding:2px 8px; border-radius:4px;">
                        🕒 Aktif: <b>${item.retention_active_period} Thn</b> | Inaktif: <b>${item.retention_inactive_period} Thn</b>
                    </div>
                </td>
                <td>
                    <div style="margin-bottom:6px;">
                        <span style="font-size:11px; padding:3px 8px; border-radius:12px; font-weight:600; ${actionBadgeClass}">
                            ${actionLabel}
                        </span>
                    </div>
                    <div style="color:var(--text-muted); font-size:13px; line-height:1.4;">${item.description || '-'}</div>
                </td>
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

    // --- VIEW SWITCHING LOGIC (SPA) ---

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;
        
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");

        if(editMode) {
            pageTitle.textContent = "Edit Klasifikasi";
            pageSubtitle.textContent = "Perbarui data kode surat dan jadwal retensi.";
        } else {
            pageTitle.textContent = "Tambah Klasifikasi";
            pageSubtitle.textContent = "Buat referensi kode surat baru.";
        }

        document.getElementById("form-entry").reset();
        
        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputCode.value = data.code;
            inputName.value = data.name;
            inputDesc.value = data.description || "";
            inputRetActive.value = data.retention_active_period || 1;
            inputRetInactive.value = data.retention_inactive_period || 2;
            
            // Pastikan value dropdown sesuai code yang diload dari referensi
            if(data.final_action) inputFinalAction.value = data.final_action;
        } else {
            currentEditId = null;
            inputRetActive.value = 1;
            inputRetInactive.value = 2;
            // Default select usually takes the first option
        }
        
        updatePreview();
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        viewTable.classList.remove("hidden");
        btnAdd.classList.remove("hidden");
        btnBack.classList.add("hidden");

        pageTitle.textContent = "Data Klasifikasi";
        pageSubtitle.textContent = "Kelola kode referensi dan jadwal retensi arsip (JRA).";
    }

    function updatePreview() {
        const c = inputCode.value.trim();
        const n = inputName.value.trim();
        previewCodeTxt.textContent = c || '000.0';
        previewNameTxt.textContent = n || 'Nama Kategori';
    }

    // --- CRUD ACTIONS ---

    async function handleSaveData(e) {
        e.preventDefault();
        
        if (!inputCode.value.trim() || !inputName.value.trim()) {
            ui.alert("Data Belum Lengkap", "Harap lengkapi Kode dan Nama!", "warning");
            return;
        }

        const payload = {
            code: inputCode.value.trim(),
            name: inputName.value.trim(),
            description: inputDesc.value.trim() || null,
            retention_active_period: parseInt(inputRetActive.value) || 0,
            retention_inactive_period: parseInt(inputRetInactive.value) || 0,
            final_action: inputFinalAction.value
        };

        const originalText = btnSave.textContent;
        btnSave.textContent = "Menyimpan...";
        btnSave.disabled = true;

        try {
            if (isEditMode) {
                payload.id = currentEditId;
                await api.classification.update(payload);
                ui.toast("Data berhasil diperbarui!", "success");
            } else {
                await api.classification.create(payload);
                ui.toast("Data berhasil disimpan!", "success");
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

    window.triggerEdit = (id) => {
        const item = allClassifications.find(x => x.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Hapus Klasifikasi?", "Yakin ingin menghapus klasifikasi ini?", true);
        if(isConfirmed) {
            try {
                await api.classification.delete(id);
                ui.toast("Data dihapus", "success");
                loadData();
            } catch (err) {
                ui.alert("Gagal Hapus", err.message, "error");
            }
        }
    };

    function applyFilter() {
        const term = searchInput.value.toLowerCase();
        const filtered = allClassifications.filter(item => 
            item.code.toLowerCase().includes(term) || 
            item.name.toLowerCase().includes(term)
        );
        renderTable(filtered);
    }
});