// assets/js/employee_archive.js
{
    let allDocs = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- INIT ---
    const initEmployeePage = async () => {
        console.log("Employee Archive Page Loaded");

        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        await Promise.all([
            loadTeachers(), // Load Data Guru
            loadStorageLocations(),
            loadDocuments()
        ]);

        setupEventListeners();
    };

    // --- DATA ---
    const loadTeachers = async () => {
        try {
            const teachers = await api.teacher.getAll(); 
            
            const inputOwner = document.getElementById("owner_id");
            const filterOwner = document.getElementById("filterEmployee");

            if(inputOwner) {
                inputOwner.innerHTML = '<option value="">-- Pilih Guru / Pegawai --</option>';
                teachers.forEach(t => {
                    inputOwner.add(new Option(`${t.full_name} (${t.identity_number})`, t.id));
                });
            }

            if(filterOwner) {
                filterOwner.innerHTML = '<option value="">Semua Pegawai</option>';
                teachers.forEach(t => {
                    filterOwner.add(new Option(t.full_name, t.id));
                });
            }
        } catch (e) { console.error("Gagal memuat data guru:", e); }
    };

    const loadStorageLocations = async () => {
        try {
            const data = await api.storageLocation.getAll();
            const inputStorage = document.getElementById("storage_location_id");
            if(inputStorage) {
                inputStorage.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
                data.forEach(l => inputStorage.add(new Option(l.name, l.id)));
            }
        } catch (e) { console.error(e); }
    };

    const loadDocuments = async () => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;
        
        try {
            allDocs = await api.employeeArchive.getAll();
            renderTable(allDocs);
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Error: ${e.message}</td></tr>`;
        }
    };

    const renderTable = (data) => {
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
            
            const ownerName = item.owner_name || "Unknown";
            const ownerNip = item.owner_identity || "-";

            let typeLabel = item.document_type || "Lainnya";
            let badgeStyle = "background:#f3f4f6; color:#374151; border:1px solid #d1d5db;"; // Default
            
            switch(typeLabel) {
                case 'sk_cpns': typeLabel = "SK CPNS"; badgeStyle = "background:#dbeafe; color:#1e40af; border:1px solid #93c5fd;"; break;
                case 'sk_pangkat': typeLabel = "SK Pangkat"; badgeStyle = "background:#dbeafe; color:#1e40af; border:1px solid #93c5fd;"; break;
                case 'sk_berkala': typeLabel = "SK Berkala"; badgeStyle = "background:#dbeafe; color:#1e40af; border:1px solid #93c5fd;"; break;
                case 'ijazah': typeLabel = "Ijazah"; badgeStyle = "background:#fce7f3; color:#be185d; border:1px solid #fbcfe8;"; break;
                case 'sertifikat': typeLabel = "Sertifikat"; badgeStyle = "background:#dcfce7; color:#15803d; border:1px solid #86efac;"; break;
                case 'ktp_kk': typeLabel = "KTP / KK"; break;
            }

            let actionButtons = `
                <button class="btn-action-view" title="Lihat PDF" 
                    onclick="openFileEmployee(${item.id})" 
                    ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
            `;

            if (isAdmin) {
                actionButtons += `
                    <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditEmployee(${item.id})">✏️</button>
                    <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteEmployee(${item.id})">🗑️</button>
                `;
            }

            tr.innerHTML = `
                <td>
                    <div style="font-weight:600;">${item.document_name}</div>
                    <div style="font-size:12px; color:var(--text-muted);">Tahun: ${item.document_year || '-'}</div>
                </td>
                <td><span style="font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase; ${badgeStyle}">${typeLabel}</span></td>
                <td>
                    <div style="font-weight:500;">${ownerName}</div>
                    <div style="font-size:11px; color:#64748b;">${ownerNip}</div>
                </td>
                <td><div style="font-size:12px;">📍 ${locName}</div></td>
                <td style="text-align:center;">
                    <div class="btn-action-group" style="display:flex; justify-content:center; gap:4px;">
                        ${actionButtons}
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
        document.getElementById("view-pdf-fullscreen").classList.add("hidden");
        
        document.getElementById("btn-add-new").classList.add("hidden");
        document.getElementById("btn-back-list").classList.remove("hidden");

        const formTitle = document.getElementById("form-title");
        if(formTitle) formTitle.textContent = editMode ? "✏️ Edit Dokumen" : "📝 Tambah Dokumen";
        
        document.getElementById("form-entry").reset();
        resetFilePreview();

        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("entry-id").value = data.id;
            document.getElementById("document_name").value = data.document_name;
            document.getElementById("owner_id").value = data.owner_id; 
            document.getElementById("document_type").value = data.document_type;
            document.getElementById("document_year").value = data.document_year;
            document.getElementById("description").value = data.description || "";
            
            if(data.storage_location_id) document.getElementById("storage_location_id").value = data.storage_location_id;

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                const cleanPath = `/storage/documents/employee_archives/${fileName}`;
                showPreview(cleanPath); 
            }
        } else {
            currentEditId = null;
        }
    };

    const showTableMode = () => {
        document.getElementById("view-form").classList.add("hidden");
        document.getElementById("view-pdf-fullscreen").classList.add("hidden");
        document.getElementById("view-table").classList.remove("hidden");
        
        document.getElementById("btn-add-new").classList.remove("hidden");
        document.getElementById("btn-back-list").classList.add("hidden");
        
        const fullViewer = document.getElementById("fullscreen-pdf-viewer");
        if(fullViewer) fullViewer.src = "";
        
        resetFilePreview();
    };

    const showPreview = (url) => {
        document.getElementById("upload-box").style.display = 'none';
        document.getElementById("preview-box").style.display = 'block';
        document.getElementById("pdf-viewer").src = url;
    };

    const resetFilePreview = () => {
        document.getElementById("fileInput").value = "";
        document.getElementById("pdf-viewer").src = "";
        document.getElementById("preview-box").style.display = 'none';
        document.getElementById("upload-box").style.display = 'flex';
    };

    // --- EVENT LISTENERS ---
    const setupEventListeners = () => {
        const btnAdd = document.getElementById("btn-add-new");
        const btnBack = document.getElementById("btn-back-list");
        const btnSave = document.getElementById("btn-save-data");
        const btnCloseFull = document.getElementById("btn-close-preview-mode");
        const btnCancelUpload = document.getElementById("btn-cancel-upload");
        const btnReset = document.getElementById("btnResetFilter");
        const inputFile = document.getElementById("fileInput");

        if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
        if(btnBack) btnBack.addEventListener("click", showTableMode);
        
        if (btnCloseFull) {
            btnCloseFull.addEventListener("click", () => {
                const viewPdfFullscreen = document.getElementById("view-pdf-fullscreen");
                const fullscreenPdfViewer = document.getElementById("fullscreen-pdf-viewer");
                if(viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
                if(fullscreenPdfViewer) fullscreenPdfViewer.src = "";
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

        if(btnSave) {
            btnSave.addEventListener("click", async (e) => {
                e.preventDefault();
                
                const name = document.getElementById("document_name").value.trim();
                const owner = document.getElementById("owner_id").value;
                
                if (!name || !owner) {
                    alert("Harap lengkapi Nama Dokumen dan Pemilik (Guru).");
                    return;
                }

                const formData = new FormData();
                formData.append('document_name', name);
                formData.append('owner_id', owner);
                formData.append('document_type', document.getElementById("document_type").value);
                formData.append('document_year', document.getElementById("document_year").value);
                formData.append('description', document.getElementById("description").value);
                
                const storageId = document.getElementById("storage_location_id").value;
                if(storageId) formData.append('storage_location_id', storageId);
                
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
            });
        }

        // Filters
        const elSearch = document.getElementById("searchInput");
        const elType = document.getElementById("filterType");
        const elEmp = document.getElementById("filterEmployee");

        const runFilter = () => {
            const term = elSearch.value.toLowerCase();
            const type = elType.value;
            const ownerId = elEmp.value;

            const filtered = allDocs.filter(item => {
                const txtMatch = (item.document_name||"").toLowerCase().includes(term) ||
                               (item.owner_name||"").toLowerCase().includes(term);
                
                const typeMatch = type === "" || item.document_type === type;
                const empMatch = ownerId === "" || String(item.owner_id) === String(ownerId);

                return txtMatch && typeMatch && empMatch;
            });
            renderTable(filtered);
        };

        if(elSearch) elSearch.addEventListener("keyup", runFilter);
        if(elType) elType.addEventListener("change", runFilter);
        if(elEmp) elEmp.addEventListener("change", runFilter);

        if(btnReset) {
            btnReset.addEventListener("click", () => {
                elSearch.value = ""; elType.value = ""; elEmp.value = "";
                runFilter();
            });
        }
    };

    // --- GLOBAL ACTIONS ---
    window.triggerEditEmployee = (id) => {
        const item = allDocs.find(d => d.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDeleteEmployee = async (id) => {
        if(confirm("Hapus dokumen ini?")) {
            try { await api.employeeArchive.delete(id); loadDocuments(); }
            catch(e) { alert("Gagal hapus: " + e.message); }
        }
    };

    window.openFileEmployee = (id) => {
        const item = allDocs.find(d => d.id === id);
        if (!item || !item.file_path) { alert("File tidak tersedia."); return; }
        const fileName = item.file_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/employee_archives/${fileName}`;
        
        document.getElementById("view-table").classList.add("hidden"); 
        document.getElementById("view-form").classList.add("hidden"); 
        document.getElementById("btn-add-new").classList.add("hidden");

        const fullView = document.getElementById("view-pdf-fullscreen");
        const fullViewer = document.getElementById("fullscreen-pdf-viewer");
        
        if(fullView) {
            fullView.classList.remove("hidden");
            fullView.style.display = "flex";
            if(fullViewer) fullViewer.src = finalUrl;
        }
    };

    // START
    initEmployeePage();
}