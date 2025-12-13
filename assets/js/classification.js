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
    const btnCancel = document.getElementById("btnCancel");
    const btnSave = document.getElementById("btnSave");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Form Inputs
    const inputId = document.getElementById("entry-id");
    const inputCode = document.getElementById("inputCode");
    const inputName = document.getElementById("inputName");
    const inputDesc = document.getElementById("inputDescription");
    // NEW: Retention Inputs
    const inputRetActive = document.getElementById("inputRetActive");
    const inputRetInactive = document.getElementById("inputRetInactive");
    const inputFinalAction = document.getElementById("inputFinalAction");

    // Previews
    const previewCodeTxt = document.getElementById("previewCodeTxt");
    const previewNameTxt = document.getElementById("previewNameTxt");

    // Filter
    const searchInput = document.getElementById("searchInput");

    // --- INITIALIZATION ---
    await loadData();

    // --- EVENT LISTENERS ---
    
    // 1. Navigation SPA
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    if(btnCancel) btnCancel.addEventListener("click", showTableMode);

    // 2. Real-time Preview Form
    if(inputCode && inputName) {
        inputCode.addEventListener('input', updatePreview);
        inputName.addEventListener('input', updatePreview);
    }

    // 3. Save Data
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    // 4. Search / Filter
    if(searchInput) {
        searchInput.addEventListener("keyup", applyFilter);
        searchInput.addEventListener("change", applyFilter);
    }
    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            searchInput.value = "";
            applyFilter();
        });
    }

    // --- FUNCTIONS ---

    async function loadData() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="4" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;
        
        try {
            allClassifications = await api.classification.getAll();
            // Sort by Code asc
            allClassifications.sort((a, b) => a.code.localeCompare(b.code));
            renderTable(allClassifications);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="4" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
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

            // Logic Badge Warna berdasarkan String
            let actionBadgeClass = '';
            let actionLabel = '';
            
            // Backend mengirim string: 'permanent', 'assess', 'destroy'
            switch(item.final_action) {
                case 'permanent':
                    actionBadgeClass = 'background:#dbeafe; color:#1e40af; border:1px solid #bfdbfe;'; 
                    actionLabel = 'PERMANEN';
                    break;
                case 'assess':
                    actionBadgeClass = 'background:#fef3c7; color:#92400e; border:1px solid #fde68a;'; 
                    actionLabel = 'DINILAI KEMBALI';
                    break;
                case 'destroy':
                    actionBadgeClass = 'background:#fee2e2; color:#991b1b; border:1px solid #fecaca;'; 
                    actionLabel = 'MUSNAH';
                    break;
                default:
                    // Fallback untuk string tak dikenal
                    actionBadgeClass = 'background:#f3f4f6; color:#374151; border:1px solid #e5e7eb;';
                    actionLabel = item.final_action.toUpperCase();
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
        
        // Hide Table, Show Form
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        
        // Adjust Header Buttons
        btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");

        // Set Texts
        if(editMode) {
            pageTitle.textContent = "Edit Klasifikasi";
            pageSubtitle.textContent = "Perbarui data kode surat dan jadwal retensi.";
        } else {
            pageTitle.textContent = "Tambah Klasifikasi";
            pageSubtitle.textContent = "Buat referensi kode surat baru.";
        }

        // Reset Form
        document.getElementById("form-entry").reset();
        
        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputCode.value = data.code;
            inputName.value = data.name;
            inputDesc.value = data.description || "";
            // Set Retention Data
            inputRetActive.value = data.retention_active_period || 1;
            inputRetInactive.value = data.retention_inactive_period || 2;
            inputFinalAction.value = data.final_action || 'destroy';
        } else {
            currentEditId = null;
            // Default Values
            inputRetActive.value = 1;
            inputRetInactive.value = 2;
            inputFinalAction.value = 'destroy';
        }
        
        // Update Preview Badge
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
            alert("Harap lengkapi Kode dan Nama!");
            return;
        }

        const payload = {
            code: inputCode.value.trim(),
            name: inputName.value.trim(),
            description: inputDesc.value.trim() || null,
            // New Payload Data
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
                alert("Data berhasil diperbarui!");
            } else {
                await api.classification.create(payload);
                alert("Data berhasil disimpan!");
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
    }

    window.triggerEdit = (id) => {
        const item = allClassifications.find(x => x.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        if(confirm("Yakin ingin menghapus klasifikasi ini?")) {
            try {
                await api.classification.delete(id);
                loadData();
            } catch (err) {
                alert("Gagal hapus: " + err.message);
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