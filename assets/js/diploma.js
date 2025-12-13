// assets/js/diploma.js
{
    let allDiplomas = []; 
    let isEditMode = false;
    let currentEditId = null;

    // --- INIT ---
    const initDiplomaPage = async () => {
        console.log("Diploma Page Loaded");

        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        await Promise.all([
            loadStorageLocations(), 
            loadData()
        ]);

        setupEventListeners();
    };

    // --- DATA ---
    const loadStorageLocations = async () => {
        try {
            const data = await api.storageLocation.getAll();
            const inputStorage = document.getElementById("storage_location_id");
            if(inputStorage) {
                inputStorage.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
                data.forEach(l => inputStorage.add(new Option(l.name, l.id)));
            }
        } catch (e) { console.error("Gagal load lokasi", e); }
    };

    const loadData = async () => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="5" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;
        try {
            allDiplomas = await api.diploma.getAll();
            renderTable(allDiplomas);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    };

    const renderTable = (data) => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        const user = api.auth.getUserData();
        const isAdmin = user && user.role === 'admin';

        // Sembunyikan tombol Add jika bukan admin (opsional, tergantung kebijakan)
        const btnAdd = document.getElementById("btn-add-new");
        if(btnAdd && !isAdmin) btnAdd.style.display = 'none';

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            // Status Logic
            const statusObj = item.status || {}; 
            const isCollected = statusObj.is_collected === true;
            const rawDate = statusObj.collected_at;
            const dateTaken = rawDate ? new Date(rawDate).toLocaleDateString("id-ID", { day: 'numeric', month: 'short', year: 'numeric' }) : "-";
            
            let statusPill = isCollected 
                ? `<span class="status-pill" style="background:#dcfce7; color:#15803d; border:1px solid #86efac; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Sudah Diambil</span>` 
                : `<span class="status-pill" style="background:#fef9c3; color:#a16207; border:1px solid #fde047; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Belum Diambil</span>`;

            const hasFile = !!item.attachment_path;
            const locName = item.storage_location_name || '<span style="color:#aaa; font-style:italic;">-</span>';

            // Tombol Aksi
            let actionButtons = `
                <button class="btn-action-view" title="Lihat File" 
                    onclick="openFileDiploma(${item.id})" 
                    ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
            `;

            if (isAdmin) {
                actionButtons += `
                    <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditDiploma(${item.id})">✏️</button>
                    <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteDiploma(${item.id})">🗑️</button>
                `;
            }

            tr.innerHTML = `
                <td>
                    <div class="text-main">${item.student_name}</div>
                    <div class="text-sub">No. Seri: ${item.number || '-'}</div>
                </td>
                
                <td>
                    <span class="major-badge" style="font-size:12px; font-weight:600; color:var(--primary); background:#eff6ff; padding:2px 6px; border-radius:4px;">${item.major || '-'}</span>
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

        const btnAdd = document.getElementById("btn-add-new");
        if(btnAdd) btnAdd.classList.add("hidden");
        document.getElementById("btn-back-list").classList.remove("hidden");

        const title = document.getElementById("form-title");
        if(title) title.textContent = editMode ? "✏️ Edit Data Ijazah" : "🎓 Input Data Baru";
        
        document.getElementById("form-entry").reset();
        resetFilePreview();
        
        const wrapperDate = document.getElementById("date-taken-wrapper");
        const inputIsTaken = document.getElementById("is_taken_checkbox");
        
        if(wrapperDate) wrapperDate.classList.add("hidden");

        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("entry-id").value = data.id;
            document.getElementById("student_name").value = data.student_name;
            document.getElementById("serial_number").value = data.number;
            document.getElementById("major").value = data.major;
            document.getElementById("academic_year").value = data.academic_year;
            
            if (data.storage_location_id) document.getElementById("storage_location_id").value = data.storage_location_id;

            const statusObj = data.status || {};
            if (statusObj.is_collected === true) {
                inputIsTaken.checked = true;
                wrapperDate.classList.remove("hidden");
                if(statusObj.collected_at) {
                    document.getElementById("date_taken").value = statusObj.collected_at.split('T')[0];
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
    };

    const showTableMode = () => {
        document.getElementById("view-form").classList.add("hidden");
        document.getElementById("view-pdf-fullscreen").classList.add("hidden");
        document.getElementById("view-table").classList.remove("hidden");
        
        const btnAdd = document.getElementById("btn-add-new");
        if(btnAdd) btnAdd.classList.remove("hidden");
        document.getElementById("btn-back-list").classList.add("hidden");
        
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

    // --- LISTENERS ---
    const setupEventListeners = () => {
        const btnAdd = document.getElementById("btn-add-new");
        const btnBack = document.getElementById("btn-back-list");
        const btnSave = document.getElementById("btn-save-data");
        const btnCloseFull = document.getElementById("btn-close-preview-mode");
        const btnCancelUpload = document.getElementById("btn-cancel-upload");
        const btnReset = document.getElementById("btnResetFilter");
        const inputIsTaken = document.getElementById("is_taken_checkbox");
        const inputFile = document.getElementById("fileInput");

        if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
        if(btnBack) btnBack.addEventListener("click", showTableMode);

        if (btnCloseFull) {
            btnCloseFull.addEventListener("click", () => {
                const viewPdfFullscreen = document.getElementById("view-pdf-fullscreen");
                const fullscreenPdfViewer = document.getElementById("fullscreen-pdf-viewer");
                if (viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
                if (fullscreenPdfViewer) fullscreenPdfViewer.src = ""; 
                showTableMode();
            });
        }

        if(inputIsTaken) {
            inputIsTaken.addEventListener("change", (e) => {
                const wrapper = document.getElementById("date-taken-wrapper");
                const inputDate = document.getElementById("date_taken");
                if(e.target.checked) {
                    wrapper.classList.remove("hidden");
                    if(!inputDate.value) inputDate.valueAsDate = new Date();
                } else {
                    wrapper.classList.add("hidden");
                    inputDate.value = "";
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

        if(btnSave) {
            btnSave.addEventListener("click", async (e) => {
                e.preventDefault();
                
                const inputName = document.getElementById("student_name").value;
                const inputSerial = document.getElementById("serial_number").value;
                const inputMajor = document.getElementById("major").value;
                const inputYear = document.getElementById("academic_year").value;
                
                if (!inputName || !inputSerial || !inputMajor) {
                    alert("Harap lengkapi Nama, No. Seri, dan Jurusan!");
                    return;
                }

                const formData = new FormData();
                formData.append('number', inputSerial); 
                formData.append('student_name', inputName);
                formData.append('major', inputMajor);
                formData.append('academic_year', inputYear);
                
                const isTaken = document.getElementById("is_taken_checkbox").checked;
                formData.append('is_collected', isTaken ? 'true' : 'false');
                
                const storageId = document.getElementById("storage_location_id").value;
                if(storageId) formData.append('storage_location_id', storageId);
                
                if(isTaken) {
                    const dateTaken = document.getElementById("date_taken").value;
                    if(dateTaken) formData.append('collected_at', dateTaken);
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
                        alert("Data berhasil diperbarui!");
                    } else {
                        await api.diploma.create(formData);
                        alert("Data berhasil disimpan!");
                    }
                    showTableMode();
                    loadData();
                } catch (err) {
                    console.error(err);
                    alert("Gagal: " + (err.message || "Kesalahan server"));
                } finally {
                    btn.textContent = originalText;
                    btn.disabled = false;
                }
            });
        }

        // Filters
        const elSearch = document.getElementById("searchInput");
        const elMajor = document.getElementById("filterMajor");
        const elYear = document.getElementById("filterYear");
        const elStatus = document.getElementById("filterStatus");

        const runFilter = () => {
            const term = elSearch.value.toLowerCase();
            const mjr = elMajor.value;
            const yr = elYear.value;
            const sts = elStatus.value; 

            const filtered = allDiplomas.filter(item => {
                const txtMatch = (item.student_name || "").toLowerCase().includes(term) || 
                               (item.number || "").toLowerCase().includes(term);
                const mjrMatch = mjr === "" || item.major === mjr;
                const yrMatch = yr === "" || item.academic_year === yr;
                const statusObj = item.status || {};
                const isCollected = statusObj.is_collected === true;
                let stsMatch = true;
                if (sts === "taken") stsMatch = isCollected;
                if (sts === "pending") stsMatch = !isCollected;

                return txtMatch && mjrMatch && yrMatch && stsMatch;
            });

            renderTable(filtered);
        };

        if(elSearch) elSearch.addEventListener("keyup", runFilter);
        if(elMajor) elMajor.addEventListener("change", runFilter);
        if(elYear) elYear.addEventListener("change", runFilter);
        if(elStatus) elStatus.addEventListener("change", runFilter);

        if(btnReset) {
            btnReset.addEventListener("click", () => {
                elSearch.value = ""; elMajor.value = ""; elYear.value = ""; elStatus.value = "";
                runFilter();
            });
        }
    };

    // --- GLOBAL ACTIONS ---
    window.triggerEditDiploma = (id) => {
        const item = allDiplomas.find(d => d.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDeleteDiploma = async (id) => {
        if(confirm("Yakin ingin menghapus data ijazah ini?")) {
            try { await api.diploma.delete(id); loadData(); } 
            catch (e) { alert("Gagal hapus: " + e.message); }
        }
    };

    window.openFileDiploma = (id) => {
        const item = allDiplomas.find(d => d.id === id);
        if (!item || !item.attachment_path) { alert("File tidak tersedia."); return; }
        const fileName = item.attachment_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/diplomas/${fileName}`;
        
        document.getElementById("view-table").classList.add("hidden"); 
        document.getElementById("view-form").classList.add("hidden"); 
        
        const btnAdd = document.getElementById("btn-add-new");
        if(btnAdd) btnAdd.classList.add("hidden");
        
        const fullView = document.getElementById("view-pdf-fullscreen");
        const fullViewer = document.getElementById("fullscreen-pdf-viewer");
        
        if(fullView) {
            fullView.classList.remove("hidden");
            fullView.style.display = "flex";
            if(fullViewer) fullViewer.src = finalUrl;
        }
    };

    // START
    initDiplomaPage();
}