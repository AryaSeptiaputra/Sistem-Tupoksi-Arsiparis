// assets/js/classification.js
{
    let allClassifications = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- INIT ---
    const initClassificationPage = async () => {
        console.log("Classification Page Loaded");

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
            allClassifications = await api.classification.getAll();
            // Sort by Code asc
            allClassifications.sort((a, b) => a.code.localeCompare(b.code));
            renderTable(allClassifications);
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

        data.forEach(item => {
            const tr = document.createElement("tr");

            let actionBadgeClass = '';
            let actionLabel = '';
            
            switch(item.final_action) {
                case 'permanent':
                    actionBadgeClass = 'background:#dbeafe; color:#1e40af; border:1px solid #bfdbfe;'; 
                    actionLabel = 'PERMANEN'; break;
                case 'assess':
                    actionBadgeClass = 'background:#fef3c7; color:#92400e; border:1px solid #fde68a;'; 
                    actionLabel = 'DINILAI KEMBALI'; break;
                case 'destroy':
                    actionBadgeClass = 'background:#fee2e2; color:#991b1b; border:1px solid #fecaca;'; 
                    actionLabel = 'MUSNAH'; break;
                default:
                    actionBadgeClass = 'background:#f3f4f6; color:#374151; border:1px solid #e5e7eb;';
                    actionLabel = (item.final_action || '-').toUpperCase();
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
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditClass(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteClass(${item.id})">🗑️</button>
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

        const pageTitle = document.getElementById("page-title");
        const pageSubtitle = document.getElementById("page-subtitle");

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
            document.getElementById("entry-id").value = data.id;
            document.getElementById("inputCode").value = data.code;
            document.getElementById("inputName").value = data.name;
            document.getElementById("inputDescription").value = data.description || "";
            document.getElementById("inputRetActive").value = data.retention_active_period || 1;
            document.getElementById("inputRetInactive").value = data.retention_inactive_period || 2;
            document.getElementById("inputFinalAction").value = data.final_action || 'destroy';
        } else {
            currentEditId = null;
            document.getElementById("inputRetActive").value = 1;
            document.getElementById("inputRetInactive").value = 2;
            document.getElementById("inputFinalAction").value = 'destroy';
        }
        
        updatePreview();
    };

    const showTableMode = () => {
        document.getElementById("view-form").classList.add("hidden");
        document.getElementById("view-table").classList.remove("hidden");
        document.getElementById("btn-add-new").classList.remove("hidden");
        document.getElementById("btn-back-list").classList.add("hidden");

        document.getElementById("page-title").textContent = "Data Klasifikasi";
        document.getElementById("page-subtitle").textContent = "Kelola kode referensi dan jadwal retensi arsip (JRA).";
    };

    const updatePreview = () => {
        const c = document.getElementById("inputCode").value.trim();
        const n = document.getElementById("inputName").value.trim();
        const pCode = document.getElementById("previewCodeTxt");
        const pName = document.getElementById("previewNameTxt");
        
        if(pCode) pCode.textContent = c || '000.0';
        if(pName) pName.textContent = n || 'Nama Kategori';
    };

    // --- LISTENERS ---
    const setupEventListeners = () => {
        const btnAdd = document.getElementById("btn-add-new");
        const btnBack = document.getElementById("btn-back-list");
        const btnCancel = document.getElementById("btnCancel");
        const btnSave = document.getElementById("btnSave");
        const btnReset = document.getElementById("btnResetFilter");
        const searchInput = document.getElementById("searchInput");

        const inputCode = document.getElementById("inputCode");
        const inputName = document.getElementById("inputName");

        if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
        if(btnBack) btnBack.addEventListener("click", showTableMode);
        if(btnCancel) btnCancel.addEventListener("click", showTableMode);

        if(inputCode) inputCode.addEventListener('input', updatePreview);
        if(inputName) inputName.addEventListener('input', updatePreview);

        if(searchInput) {
            searchInput.addEventListener("keyup", () => {
                const term = searchInput.value.toLowerCase();
                const filtered = allClassifications.filter(item => 
                    item.code.toLowerCase().includes(term) || 
                    item.name.toLowerCase().includes(term)
                );
                renderTable(filtered);
            });
        }

        if(btnReset) {
            btnReset.addEventListener("click", () => {
                searchInput.value = "";
                renderTable(allClassifications);
            });
        }

        if(btnSave) {
            btnSave.addEventListener("click", async (e) => {
                e.preventDefault();
                
                const code = document.getElementById("inputCode").value.trim();
                const name = document.getElementById("inputName").value.trim();
                
                if (!code || !name) {
                    alert("Harap lengkapi Kode dan Nama!");
                    return;
                }

                const payload = {
                    code: code,
                    name: name,
                    description: document.getElementById("inputDescription").value.trim() || null,
                    retention_active_period: parseInt(document.getElementById("inputRetActive").value) || 0,
                    retention_inactive_period: parseInt(document.getElementById("inputRetInactive").value) || 0,
                    final_action: document.getElementById("inputFinalAction").value
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
            });
        }
    };

    // --- GLOBAL ACTIONS ---
    window.triggerEditClass = (id) => {
        const item = allClassifications.find(x => x.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDeleteClass = async (id) => {
        if(confirm("Yakin ingin menghapus klasifikasi ini?")) {
            try {
                await api.classification.delete(id);
                loadData();
            } catch (err) {
                alert("Gagal hapus: " + err.message);
            }
        }
    };

    // START
    initClassificationPage();
}