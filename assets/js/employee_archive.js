document.addEventListener("DOMContentLoaded", async () => {

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    let allDocs = [];
    let isEditMode = false;
    let currentEditId = null;
    let refDocTypes = [];

    // --- DOM ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    const viewPdfFullscreen = document.getElementById("view-pdf-fullscreen");
    const fullscreenPdfViewer = document.getElementById("fullscreen-pdf-viewer");
    const btnClosePreviewMode = document.getElementById("btn-close-preview-mode");

    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    const btnSave = document.getElementById("btn-save-data");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Inputs
    const inputArchiveStatus = document.getElementById("archive_status");
    const inputDocType = document.getElementById("document_type");
    const inputOwnerId = document.getElementById("owner_id");
    const inputClassId = document.getElementById("classification_id"); // NEW
    const fileInput = document.getElementById("fileInput");
    const uploadBox = document.getElementById("upload-box");
    const previewBox = document.getElementById("preview-box");
    const pdfViewer = document.getElementById("pdf-viewer");
    const btnCancelUpload = document.getElementById("btn-cancel-upload");

    // Filters
    const elSearch = document.getElementById("searchInput");
    const elFilterType = document.getElementById("filterType");
    const elFilterEmployee = document.getElementById("filterEmployee");
    const elFilterStatus = document.getElementById("filterStatus");
    const elFilterClass = document.getElementById("filterClassification"); // NEW

    await initPage();

    async function initPage() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">Memuat data...</td></tr>`;

        await Promise.all([
            loadReferences(),
            loadClassifications(), // NEW
            loadTeachers(), 
            loadStorageLocations(),
            loadDocuments()
        ]);
    }

    // --- NEW: Load Classifications ---
    async function loadClassifications() {
        try {
            const data = await api.classification.getAll();
            
            // Populate Form
            if(inputClassId) {
                inputClassId.innerHTML = '<option value="">-- Pilih Klasifikasi --</option>';
                data.forEach(c => inputClassId.add(new Option(`${c.code} - ${c.name}`, c.id)));
            }
            
            // Populate Filter
            if(elFilterClass) {
                elFilterClass.innerHTML = '<option value="">Semua Klasifikasi</option>';
                data.forEach(c => elFilterClass.add(new Option(`${c.code} - ${c.name}`, c.code)));
            }
        } catch (e) { console.error("Gagal load klasifikasi", e); }
    }

    async function loadReferences() {
        try {
            const respType = await api.reference.getByCategory('emp_doc_type');
            refDocTypes = respType.data || [];
            const respStatus = await api.reference.getByCategory('archive_status');
            const refStatus = respStatus.data || [];

            const populate = (el, data, placeholder) => {
                if(!el) return;
                el.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '';
                data.forEach(item => el.add(new Option(item.name, item.code)));
            };

            populate(elFilterType, refDocTypes, "Semua Jenis");
            populate(elFilterStatus, refStatus, "Semua Status");
            populate(inputDocType, refDocTypes, null);
            populate(inputArchiveStatus, refStatus, null);
        } catch (e) { console.error(e); }
    }

    async function loadTeachers() {
        try {
            const teachers = await api.teacher.getAll(); 
            if(inputOwnerId) {
                inputOwnerId.innerHTML = '<option value="">-- Pilih Guru / Pegawai --</option>';
                teachers.forEach(t => inputOwnerId.add(new Option(t.full_name, t.id)));
            }
            if(elFilterEmployee) {
                elFilterEmployee.innerHTML = '<option value="">Semua Pegawai</option>';
                teachers.forEach(t => elFilterEmployee.add(new Option(t.full_name, t.id)));
            }
        } catch (e) { console.error(e); }
    }

    async function loadStorageLocations() {
        try {
            const data = await api.storageLocation.getAll();
            const elStore = document.getElementById("storage_location_id");
            if(elStore) {
                elStore.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
                data.forEach(l => elStore.add(new Option(l.name, l.id)));
            }
        } catch (e) { console.error(e); }
    }

    async function loadDocuments() {
        try {
            allDocs = await api.employeeArchive.getAll();
            renderTable(allDocs);
        } catch (e) { console.error(e); }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            let statusClass = "st-active";
            if (item.archive_status === 'inactive') statusClass = "st-inactive";
            if (item.archive_status === 'destroyed') statusClass = "st-destroyed";

            const typeLabel = refDocTypes.find(r => r.code === item.document_type)?.name || item.document_type;
            const hasFile = !!item.file_path;
            
            // Badge Klasifikasi
            const classBadge = item.classification_code 
                ? `<span style="background:#eef2ff; color:#4338ca; padding:2px 6px; border-radius:4px; font-size:10px; border:1px solid #c7d2fe; margin-right:4px;">${item.classification_code}</span>` 
                : '';

            // --- PERBAIKAN LOGIKA TOMBOL VIEW DI SINI ---
            // Jika ada file: pakai class 'btn-view-file' (Oranye). Jika tidak: default (Abu-abu)
            const viewButtonClass = hasFile ? "btn-action-view btn-view-file" : "btn-action-view";
            
            // Atur style disabled jika tidak ada file (agar tetap abu-abu dan transparan)
            const viewAttr = !hasFile ? 'disabled style="opacity:0.5; cursor:default;"' : `onclick="window.openFile(${item.id})"`;

            tr.innerHTML = `
                <td>
                    <div style="font-weight:600; color:var(--primary);">${item.document_name}</div>
                    <div style="margin-top:2px;">
                        ${classBadge}
                        <span style="font-size:11px; color:#666;">Tahun: ${item.document_year || '-'}</span>
                    </div>
                </td>
                <td><span class="badge-doc doc-lain">${typeLabel}</span></td>
                <td>
                    <div style="font-weight:500;">${item.owner_name}</div>
                    <div style="font-size:11px; color:#999;">${item.owner_identity || '-'}</div>
                </td>
                <td>
                    <div style="font-size:12px; margin-bottom:4px;">📍 ${item.storage_location_name || '-'}</div>
                    <span class="status-pill ${statusClass}">${item.archive_status}</span>
                </td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="${viewButtonClass}" title="Lihat PDF" ${viewAttr}>📄</button>
                        
                        <button class="btn-action-view btn-edit" onclick="triggerEdit(${item.id})" title="Edit">✏️</button>
                        <button class="btn-action-view btn-delete" onclick="triggerDelete(${item.id})" title="Hapus">🗑️</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // --- Form Logic ---
    window.showFormMode = (editMode = false, data = null) => {
        isEditMode = editMode;
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        if(btnAdd) btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");
        
        document.getElementById("form-entry").reset();
        resetFilePreview();

        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("document_name").value = data.document_name;
            inputOwnerId.value = data.owner_id;
            inputDocType.value = data.document_type;
            inputArchiveStatus.value = data.archive_status;
            document.getElementById("document_year").value = data.document_year;
            document.getElementById("storage_location_id").value = data.storage_location_id || "";
            document.getElementById("description").value = data.description || "";
            
            // NEW: Set Classification
            if (data.classification_id) inputClassId.value = data.classification_id;

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                showPreview(`/storage/documents/employee_archives/${fileName}`);
            }
        } else {
            inputArchiveStatus.value = "active";
        }
    };

    async function handleSaveData(e) {
        e.preventDefault();
        
        // Validation
        if (!inputClassId.value) {
            ui.alert("Data Belum Lengkap", "Harap pilih Klasifikasi Surat", "warning");
            return;
        }

        const formData = new FormData();
        formData.append('document_name', document.getElementById("document_name").value);
        formData.append('owner_id', inputOwnerId.value);
        formData.append('classification_id', inputClassId.value); // NEW
        formData.append('document_type', inputDocType.value);
        formData.append('archive_status', inputArchiveStatus.value);
        formData.append('document_year', document.getElementById("document_year").value);
        formData.append('description', document.getElementById("description").value);
        formData.append('storage_location_id', document.getElementById("storage_location_id").value);
        
        if (fileInput.files[0]) formData.append('file', fileInput.files[0]);

        try {
            if (isEditMode) {
                formData.append('id', currentEditId);
                await api.employeeArchive.update(formData);
            } else {
                await api.employeeArchive.create(formData);
            }
            ui.toast("Data disimpan", "success");
            showTableMode();
            loadDocuments();
        } catch (err) { ui.alert("Gagal", err.message, "error"); }
    }

    // --- Filters ---
    [elSearch, elFilterType, elFilterEmployee, elFilterStatus, elFilterClass].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    function applyFilters() {
        const term = elSearch.value.toLowerCase();
        const res = allDocs.filter(i => {
            const matchesText = i.document_name.toLowerCase().includes(term) || i.owner_name.toLowerCase().includes(term);
            const matchesType = elFilterType.value === "" || i.document_type === elFilterType.value;
            const matchesStatus = elFilterStatus.value === "" || i.archive_status === elFilterStatus.value;
            const matchesOwner = elFilterEmployee.value === "" || String(i.owner_id) === elFilterEmployee.value;
            
            // NEW: Filter Classification
            const matchesClass = elFilterClass.value === "" || i.classification_code === elFilterClass.value;

            return matchesText && matchesType && matchesStatus && matchesOwner && matchesClass;
        });
        renderTable(res);
    }

    // ... (Sisa fungsi standard seperti triggerEdit, triggerDelete, viewPdf, showTableMode tetap sama) ...
    // Pastikan fungsi window.openFile, triggerEdit, triggerDelete ada di sini (dicopy dari kode asli)
    
    window.openFile = (id) => {
        const item = allDocs.find(d => d.id === id);
        if (!item || !item.file_path) { ui.toast("File tidak ditemukan", "error"); return; }
        const fileName = item.file_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/employee_archives/${fileName}`;
        viewTable.classList.add("hidden");
        viewForm.classList.add("hidden");
        if(btnAdd) btnAdd.classList.add("hidden");
        viewPdfFullscreen.classList.remove("hidden");
        viewPdfFullscreen.classList.add("active-flex");
        fullscreenPdfViewer.src = finalUrl;
    };
    
    if (btnClosePreviewMode) {
        btnClosePreviewMode.addEventListener("click", () => {
            viewPdfFullscreen.classList.add("hidden");
            viewPdfFullscreen.classList.remove("active-flex");
            fullscreenPdfViewer.src = "";
            viewTable.classList.remove("hidden");
            if(btnAdd) btnAdd.classList.remove("hidden");
        });
    }

    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file && file.type === "application/pdf") { showPreview(URL.createObjectURL(file)); } 
        else { ui.alert("Format Salah", "Pilih file PDF", "warning"); fileInput.value = ""; }
    });

    function showPreview(url) {
        uploadBox.style.display = 'none';
        previewBox.style.display = 'block';
        pdfViewer.src = url;
    }

    function resetFilePreview() {
        fileInput.value = "";
        pdfViewer.src = "";
        previewBox.style.display = 'none';
        uploadBox.style.display = 'flex';
    }
    
    btnCancelUpload.addEventListener("click", resetFilePreview);

    window.triggerEdit = (id) => { const item = allDocs.find(d => d.id === id); if(item) showFormMode(true, item); };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Hapus Data?", "Yakin ingin menghapus arsip ini?", true);
        if (isConfirmed) {
            try { await api.employeeArchive.delete(id); ui.toast("Berhasil dihapus", "success"); loadDocuments(); } 
            catch (e) { ui.alert("Error", e.message, "error"); }
        }
    };
    
    function showTableMode() {
        viewForm.classList.add("hidden");
        viewTable.classList.remove("hidden");
        if(btnAdd) btnAdd.classList.remove("hidden");
        btnBack.classList.add("hidden");
    }

    if (btnSave) btnSave.addEventListener("click", handleSaveData);
    if (btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if (btnBack) btnBack.addEventListener("click", showTableMode);
});