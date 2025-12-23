document.addEventListener("DOMContentLoaded", async () => {
    
    // --- 0. SETUP NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- STATE VARIABLES ---
    let allDiplomas = []; 
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

    const inputId = document.getElementById("entry-id");
    const inputName = document.getElementById("student_name");
    const inputSerial = document.getElementById("serial_number");
    const inputMajor = document.getElementById("major");
    const inputYear = document.getElementById("academic_year");
    
    const inputStorageId = document.getElementById("storage_location_id");
    
    const inputIsTaken = document.getElementById("is_taken_checkbox");
    const wrapperDateTaken = document.getElementById("date-taken-wrapper");
    const inputDateTaken = document.getElementById("date_taken");

    const inputFile = document.getElementById("fileInput");
    const uploadBox = document.getElementById("upload-box");
    const previewBox = document.getElementById("preview-box");
    const pdfViewer = document.getElementById("pdf-viewer");
    const btnCancelUpload = document.getElementById("btn-cancel-upload");

    // Filters
    const elSearch = document.getElementById("searchInput");
    const elFilterMajor = document.getElementById("filterMajor");
    const elFilterYear = document.getElementById("filterYear");
    const elFilterStatus = document.getElementById("filterStatus");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENT LISTENERS ---
    
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);

    if (btnClosePreviewMode) {
        btnClosePreviewMode.addEventListener("click", () => {
            if (viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
            if (fullscreenPdfViewer) fullscreenPdfViewer.src = ""; 
            showTableMode();
        });
    }

    if(inputIsTaken) {
        inputIsTaken.addEventListener("change", (e) => {
            if(e.target.checked) {
                wrapperDateTaken.classList.remove("hidden");
                if(!inputDateTaken.value) inputDateTaken.valueAsDate = new Date();
            } else {
                wrapperDateTaken.classList.add("hidden");
                inputDateTaken.value = "";
            }
        });
    }

    if(inputFile) {
        inputFile.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                const url = URL.createObjectURL(file);
                showPreview(url);
            }
        });
    }
    if(btnCancelUpload) btnCancelUpload.addEventListener("click", resetFilePreview);
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    [elSearch, elFilterMajor, elFilterYear, elFilterStatus].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            elSearch.value = ""; elFilterMajor.value = ""; elFilterYear.value = ""; elFilterStatus.value = "";
            applyFilters();
            ui.toast("Filter direset", "info");
        });
    }

    // --- CORE FUNCTIONS ---

    async function initPage() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="5" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;

        await Promise.all([
            loadReferences(), 
            loadStorageLocations(), 
            loadData()
        ]);
    }

    async function loadReferences() {
        try {
            const response = await api.reference.getByCategory('school_major');
            const data = response.data || [];

            const populate = (el, placeholder) => {
                if(!el) return;
                el.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '';
                data.forEach(item => {
                    el.add(new Option(item.name, item.name));
                });
            };

            populate(elFilterMajor, "Semua Jurusan");
            populate(inputMajor, "Pilih Jurusan");

        } catch (e) {
            console.error("Gagal load jurusan:", e);
        }
    }

    async function loadStorageLocations() {
        try {
            const response = await api.storageLocation.getAll();
            const data = response.storage_locations || [];
            if(inputStorageId) {
                inputStorageId.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
                data.forEach(l => inputStorageId.add(new Option(l.name, l.id)));
            }
        } catch (e) { console.error("Gagal load lokasi", e); }
    }

    async function loadData() {
        try {
            const response = await api.diploma.getAll();
            allDiplomas = response.diplomas || [];
            renderTable(allDiplomas);
        } catch (e) {
            console.error(e);
            document.getElementById("table-body").innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        const user = api.auth.getUserData();
        const isAdmin = user && user.role === 'admin';

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            // --- FIX: Ambil langsung dari item sesuai model diploma.py ---
            const isCollected = item.is_collected === true || item.is_collected === 1;
            const rawDate = item.collected_at || item.collacted_at; // Handle typo jika belum ganti di python
            
            const dateTaken = (isCollected && rawDate) 
                ? new Date(rawDate).toLocaleDateString("id-ID", { day: 'numeric', month: 'short', year: 'numeric' }) 
                : "-";
            
            let statusPill = isCollected 
                ? `<span class="status-pill st-success">Sudah Diambil</span>` 
                : `<span class="status-pill st-warning">Belum Diambil</span>`;

            const hasFile = !!item.attachment_path;
            const locName = item.storage_location_name || '<span style="color:#aaa; font-style:italic;">-</span>';

            let actionButtons = `
                <button class="btn-action-view" title="Lihat File" 
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
                    <div class="text-main">${item.student_name}</div>
                    <div class="text-sub">No. Seri: ${item.number || '-'}</div>
                </td>
                <td>
                    <span class="major-badge">${item.major || '-'}</span>
                    <div class="text-sub" style="margin-top:4px;">Tahun: ${item.academic_year || '-'}</div>
                </td>
                <td>
                    <div class="text-sub" style="font-size:12px; margin-bottom:4px;">📍 ${locName}</div>
                    ${statusPill}
                </td>
                <td>
                    <div class="text-main" style="font-size:14px;">${dateTaken}</div>
                </td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        ${actionButtons}
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
        if(viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");

        if(btnAdd) btnAdd.classList.add("hidden");
        if(btnBack) btnBack.classList.remove("hidden");

        document.getElementById("form-title").textContent = editMode ? "✏️ Edit Data Ijazah" : "🎓 Input Data Baru";
        document.getElementById("form-entry").reset();
        resetFilePreview();
        wrapperDateTaken.classList.add("hidden");

        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputName.value = data.student_name;
            inputSerial.value = data.number;
            inputMajor.value = data.major; 
            inputYear.value = data.academic_year;
            
            if (data.storage_location_id) inputStorageId.value = data.storage_location_id;

            // --- FIX: Ambil dari root data ---
            if (data.is_collected === true || data.is_collected === 1) {
                inputIsTaken.checked = true;
                wrapperDateTaken.classList.remove("hidden");
                const rawDate = data.collected_at || data.collacted_at;
                if(rawDate) {
                    inputDateTaken.value = rawDate.split('T')[0];
                }
            }

            if (data.attachment_path) {
                const fileName = data.attachment_path.split(/[\\/]/).pop();
                const cleanPath = `/storage/documents/diplomas/${fileName}`;
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
        
        if (!inputName.value || !inputSerial.value || !inputMajor.value) {
            ui.alert("Data Belum Lengkap", "Harap lengkapi Nama, No. Seri, dan Jurusan!", "warning");
            return;
        }

        const formData = new FormData();
        formData.append('number', inputSerial.value); 
        formData.append('student_name', inputName.value);
        formData.append('major', inputMajor.value);
        formData.append('academic_year', inputYear.value);
        formData.append('is_collected', inputIsTaken.checked ? 'true' : 'false');
        
        if(inputStorageId.value) formData.append('storage_location_id', inputStorageId.value);
        
        if(inputIsTaken.checked && inputDateTaken.value) {
            formData.append('collected_at', inputDateTaken.value);
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
                await api.diploma.update(formData);
                ui.toast("Data berhasil diperbarui!", "success");
            } else {
                await api.diploma.create(formData);
                ui.toast("Data berhasil disimpan!", "success");
            }
            showTableMode();
            loadData();
        } catch (err) {
            console.error(err);
            ui.alert("Gagal Menyimpan", err.message || "Kesalahan server", "error");
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }

    window.triggerEdit = (id) => {
        const item = allDiplomas.find(d => d.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Hapus Data?", "Yakin ingin menghapus data ijazah ini secara permanen?", true);
        if(isConfirmed) {
            try { 
                await api.diploma.delete(id); 
                ui.toast("Data telah dihapus", "success");
                loadData(); 
            } 
            catch (e) { 
                ui.alert("Gagal Hapus", e.message, "error"); 
            }
        }
    };

    window.openFile = (id) => {
        const item = allDiplomas.find(d => d.id === id);
        if (!item || !item.attachment_path) { 
            ui.toast("File tidak tersedia", "error"); 
            return; 
        }
        const fileName = item.attachment_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/diplomas/${fileName}`;
        
        viewTable.classList.add("hidden"); viewForm.classList.add("hidden"); 
        if(btnAdd) btnAdd.classList.add("hidden");
        
        if(viewPdfFullscreen) {
            viewPdfFullscreen.classList.remove("hidden");
            viewPdfFullscreen.style.display = "flex";
            if(fullscreenPdfViewer) fullscreenPdfViewer.src = finalUrl;
        }
    };

    function applyFilters() {
        const term = elSearch.value.toLowerCase();
        const mjr = elFilterMajor.value;
        const yr = elFilterYear.value;
        const sts = elFilterStatus.value; 

        const filtered = allDiplomas.filter(item => {
            const txtMatch = (item.student_name || "").toLowerCase().includes(term) || 
                           (item.number || "").toLowerCase().includes(term);
            const mjrMatch = mjr === "" || item.major === mjr;
            const yrMatch = yr === "" || item.academic_year === yr;
            
            // --- FIX: Filter Status dari root data ---
            const isCollected = item.is_collected === true || item.is_collected === 1;
            let stsMatch = true;
            if (sts === "taken") stsMatch = isCollected;
            if (sts === "pending") stsMatch = !isCollected;

            return txtMatch && mjrMatch && yrMatch && stsMatch;
        });

        renderTable(filtered);
    }
});