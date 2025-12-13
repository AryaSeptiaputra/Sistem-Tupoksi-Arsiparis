document.addEventListener("DOMContentLoaded", async () => {

    // --- 0. NAVIGASI ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => { window.location.href = el.dataset.route; });
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- STATE VARIABLES ---
    let allDocs = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    const viewPdfFullscreen = document.getElementById("view-pdf-fullscreen");
    const fullscreenPdfViewer = document.getElementById("fullscreen-pdf-viewer");
    const btnClosePreviewMode = document.getElementById("btn-close-preview-mode");

    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    const btnSave = document.getElementById("btn-save-data");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Inputs Form
    const inputId = document.getElementById("entry-id");
    const inputName = document.getElementById("document_name");
    
    // [UPDATE] Referensi ke input Owner (Guru)
    const inputOwnerId = document.getElementById("owner_id"); 
    
    const inputDocType = document.getElementById("document_type");
    const inputYear = document.getElementById("document_year");
    const inputStorageId = document.getElementById("storage_location_id");
    const inputDesc = document.getElementById("description");

    // File Upload
    const inputFile = document.getElementById("fileInput");
    const uploadBox = document.getElementById("upload-box");
    const previewBox = document.getElementById("preview-box");
    const pdfViewer = document.getElementById("pdf-viewer");
    const btnCancelUpload = document.getElementById("btn-cancel-upload");

    // Filters
    const elSearch = document.getElementById("searchInput");
    const elFilterType = document.getElementById("filterType");
    const elFilterEmployee = document.getElementById("filterEmployee");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENT LISTENERS ---
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    
    if (btnClosePreviewMode) {
        btnClosePreviewMode.addEventListener("click", () => {
            viewPdfFullscreen.classList.add("hidden");
            fullscreenPdfViewer.src = "";
            showTableMode();
        });
    }

    if (inputFile) {
        inputFile.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                if(file.type !== "application/pdf") {
                    alert("Hanya file PDF yang diperbolehkan.");
                    inputFile.value = "";
                    return;
                }
                const url = URL.createObjectURL(file);
                showPreview(url);
            }
        });
    }
    if(btnCancelUpload) btnCancelUpload.addEventListener("click", resetFilePreview);
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    // Filter Listeners
    [elSearch, elFilterType, elFilterEmployee].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            elSearch.value = ""; elFilterType.value = ""; elFilterEmployee.value = "";
            applyFilters();
        });
    }

    // --- FUNCTIONS ---

    async function initPage() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;

        await Promise.all([
            loadTeachers(), // Load Data Guru
            loadStorageLocations(),
            loadDocuments()
        ]);
    }

    async function loadTeachers() {
        try {
            // [UPDATE] Mengambil data dari API Teacher (Master Data)
            const teachers = await api.teacher.getAll(); 
            
            // Populate Dropdown di Form
            if(inputOwnerId) {
                inputOwnerId.innerHTML = '<option value="">-- Pilih Guru / Pegawai --</option>';
                teachers.forEach(t => {
                    inputOwnerId.add(new Option(`${t.full_name} (${t.identity_number})`, t.id));
                });
            }

            // Populate Dropdown di Filter
            if(elFilterEmployee) {
                elFilterEmployee.innerHTML = '<option value="">Semua Pegawai</option>';
                teachers.forEach(t => {
                    elFilterEmployee.add(new Option(t.full_name, t.id));
                });
            }
        } catch (e) { console.error("Gagal memuat data guru:", e); }
    }

    async function loadStorageLocations() {
        try {
            const data = await api.storageLocation.getAll();
            if(inputStorageId) {
                inputStorageId.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
                data.forEach(l => inputStorageId.add(new Option(l.name, l.id)));
            }
        } catch (e) { console.error(e); }
    }

    async function loadDocuments() {
        try {
            allDocs = await api.employeeArchive.getAll();
            renderTable(allDocs);
        } catch (e) {
            document.getElementById("table-body").innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Error: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        const user = api.auth.getUserData();
        const isAdmin = user && user.role === 'admin';

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            const hasFile = !!item.file_path;
            const locName = item.storage_location_name || '<span style="color:#ccc;">-</span>';
            
            // [UPDATE] Tampilkan nama pemilik dari response backend
            const ownerName = item.owner_name || "Unknown";
            const ownerNip = item.owner_identity || "-";

            // Badge Type Logic
            let typeLabel = item.document_type || "Lainnya";
            let badgeClass = "doc-lain";
            
            switch(typeLabel) {
                case 'sk_cpns': typeLabel = "SK CPNS"; badgeClass = "doc-sk"; break;
                case 'sk_pangkat': typeLabel = "SK Pangkat"; badgeClass = "doc-sk"; break;
                case 'sk_berkala': typeLabel = "SK Berkala"; badgeClass = "doc-sk"; break;
                case 'ijazah': typeLabel = "Ijazah"; badgeClass = "doc-ijazah"; break;
                case 'sertifikat': typeLabel = "Sertifikat"; badgeClass = "doc-sertifikat"; break;
                case 'ktp_kk': typeLabel = "KTP / KK"; badgeClass = "doc-lain"; break;
                default: typeLabel = "Lainnya"; badgeClass = "doc-lain";
            }

            let actionButtons = `
                <button class="btn-action-view" title="Lihat PDF" 
                    onclick="window.openFile(${item.id})" 
                    ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
            `;

            if (isAdmin) {
                actionButtons += `
                    <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEdit(${item.id})">✏️</button>
                    <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDelete(${item.id})">🗑️</button>
                `;
            }

            tr.innerHTML = `
                <td>
                    <div style="font-weight:600;">${item.document_name}</div>
                    <div style="font-size:12px; color:var(--text-muted);">Tahun: ${item.document_year || '-'}</div>
                </td>
                <td><span class="badge-doc ${badgeClass}">${typeLabel}</span></td>
                <td>
                    <div style="font-weight:500;">${ownerName}</div>
                    <div style="font-size:11px; color:#64748b;">${ownerNip}</div>
                </td>
                <td><div style="font-size:12px;">📍 ${locName}</div></td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        ${actionButtons}
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // --- FORM LOGIC ---

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        if(viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
        
        if(btnAdd) btnAdd.classList.add("hidden");
        if(btnBack) btnBack.classList.remove("hidden");

        document.getElementById("form-title").textContent = editMode ? "✏️ Edit Dokumen" : "📝 Tambah Dokumen";
        document.getElementById("form-entry").reset();
        resetFilePreview();

        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputName.value = data.document_name;
            
            // [UPDATE] Set Owner ID
            inputOwnerId.value = data.owner_id; 

            inputDocType.value = data.document_type;
            inputYear.value = data.document_year;
            inputDesc.value = data.description || "";
            
            if(data.storage_location_id) inputStorageId.value = data.storage_location_id;

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                // Asumsi file helper menyimpan di folder ini
                const cleanPath = `/storage/documents/employee_archives/${fileName}`;
                showPreview(cleanPath); 
            }
        } else {
            currentEditId = null;
        }
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        if(viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
        viewTable.classList.remove("hidden");
        if(btnAdd) btnAdd.classList.remove("hidden");
        if(btnBack) btnBack.classList.add("hidden");
        resetFilePreview();
    }

    function showPreview(url) {
        uploadBox.style.display = 'none';
        previewBox.style.display = 'block';
        pdfViewer.src = url;
    }

    function resetFilePreview() {
        inputFile.value = "";
        pdfViewer.src = "";
        previewBox.style.display = 'none';
        uploadBox.style.display = 'flex';
    }

    async function handleSaveData(e) {
        e.preventDefault();
        
        // [UPDATE] Validasi Owner ID
        if (!inputName.value.trim() || !inputOwnerId.value) {
            alert("Harap lengkapi Nama Dokumen dan Pemilik (Guru).");
            return;
        }

        const formData = new FormData();
        formData.append('document_name', inputName.value.trim());
        
        // [UPDATE] Kirim owner_id
        formData.append('owner_id', inputOwnerId.value);
        
        formData.append('document_type', inputDocType.value);
        formData.append('document_year', inputYear.value);
        formData.append('description', inputDesc.value);
        
        if(inputStorageId.value) {
            formData.append('storage_location_id', inputStorageId.value);
        }
        
        if (inputFile.files[0]) {
            formData.append('file', inputFile.files[0]);
        }

        const btn = e.target;
        const originalText = btn.textContent;
        btn.textContent = "Menyimpan...";
        btn.disabled = true;

        try {
            if (isEditMode) {
                formData.append('id', currentEditId);
                await api.employeeArchive.update(formData);
                alert("Berhasil diperbarui!");
            } else {
                await api.employeeArchive.create(formData);
                alert("Berhasil disimpan!");
            }
            showTableMode();
            loadDocuments();
        } catch (err) {
            console.error(err);
            alert("Gagal: " + (err.message || "Error server"));
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }

    // --- GLOBAL ACTIONS ---
    window.triggerEdit = (id) => {
        const item = allDocs.find(d => d.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        if(confirm("Hapus dokumen ini?")) {
            try { await api.employeeArchive.delete(id); loadDocuments(); }
            catch(e) { alert("Gagal hapus: " + e.message); }
        }
    };

    window.openFile = (id) => {
        const item = allDocs.find(d => d.id === id);
        if (!item || !item.file_path) { alert("File tidak tersedia."); return; }
        const fileName = item.file_path.split(/[\\/]/).pop();
        const cleanPath = `/storage/documents/employee_archives/${fileName}`;
        
        viewTable.classList.add("hidden"); viewForm.classList.add("hidden"); 
        if(btnAdd) btnAdd.classList.add("hidden");

        if(viewPdfFullscreen) {
            viewPdfFullscreen.classList.remove("hidden");
            viewPdfFullscreen.style.display = "flex";
            if(fullscreenPdfViewer) fullscreenPdfViewer.src = cleanPath;
        }
    };

    // --- FILTER LOGIC ---
    function applyFilters() {
        const term = elSearch.value.toLowerCase();
        const type = elFilterType.value;
        const ownerId = elFilterEmployee.value; // Filter by Owner ID

        const filtered = allDocs.filter(item => {
            const txtMatch = (item.document_name||"").toLowerCase().includes(term) ||
                           (item.owner_name||"").toLowerCase().includes(term);
            
            const typeMatch = type === "" || item.document_type === type;
            
            // Compare Owner ID
            const empMatch = ownerId === "" || String(item.owner_id) === String(ownerId);

            return txtMatch && typeMatch && empMatch;
        });
        renderTable(filtered);
    }
});