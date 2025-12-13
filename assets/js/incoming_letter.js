// assets/js/incoming_letter.js
{
    let allLetters = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- INIT ---
    const initIncomingPage = async () => {
        console.log("Incoming Letter Page Loaded");

        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        await Promise.all([
            loadClassifications(),
            loadStorageLocations(),
            loadLetters()
        ]);

        setupEventListeners();
    };

    // --- DATA ---
    const loadClassifications = async () => {
        try {
            const data = await api.classification.getAll();
            const inputClass = document.getElementById("classification_id");
            const filterClass = document.getElementById("filterClassification");

            if (inputClass) inputClass.innerHTML = '<option value="">-- Pilih Klasifikasi --</option>';
            if (filterClass) filterClass.innerHTML = '<option value="">Semua Klasifikasi</option>';

            data.forEach(c => {
                const text = `${c.code} - ${c.name}`;
                if (inputClass) inputClass.add(new Option(text, c.id));
                if (filterClass) filterClass.add(new Option(text, c.code)); // Filter pakai Kode
            });
        } catch (e) { console.error("Gagal load klasifikasi", e); }
    };

    const loadStorageLocations = async () => {
        try {
            const data = await api.storageLocation.getAll();
            const inputStorage = document.getElementById("storage_location_id");
            if (inputStorage) {
                inputStorage.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
                data.forEach(loc => {
                    inputStorage.add(new Option(loc.name, loc.id));
                });
            }
        } catch (e) { console.error("Gagal load lokasi", e); }
    };

    const loadLetters = async () => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;
        
        try {
            allLetters = await api.incomingLetter.getAll();
            // Sort Descending by Received Date
            allLetters.sort((a, b) => new Date(b.received_date) - new Date(a.received_date));
            renderTable(allLetters);
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

            const dateLet = item.letter_date ? new Date(item.letter_date).toLocaleDateString("id-ID") : "-";
            const dateRec = item.received_date ? new Date(item.received_date).toLocaleDateString("id-ID") : "-";

            let statusPill = `<span class="status-pill st-active" style="background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Aktif</span>`;
            if (item.archive_status === 'inactive') statusPill = `<span class="status-pill" style="background:#fef9c3; color:#a16207; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Inaktif</span>`;
            else if (item.archive_status === 'destroyed') statusPill = `<span class="status-pill" style="background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Musnah</span>`;

            const locName = item.storage_location_name || '<span style="color:#aaa; font-style:italic;">-</span>';
            const hasFile = !!item.file_path;

            // Tombol Aksi (Rename Function Call)
            let actionButtons = `
                <button class="btn-action-view" title="Lihat PDF" 
                    onclick="openFileIncoming(${item.id})" 
                    ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
            `;

            if (isAdmin) {
                actionButtons += `
                    <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditIncoming(${item.id})">✏️</button>
                    <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteIncoming(${item.id})">🗑️</button>
                `;
            }

            tr.innerHTML = `
                <td>
                    <div style="font-family:monospace; color:var(--primary); font-weight:600;">${item.number}</div>
                    <div style="font-size:12px; color:#6b7280; margin-top:2px;"><span style="font-weight:600;">Srt:</span> ${dateLet}</div>
                </td>
                <td><div style="font-size:14px; font-weight:600;">${dateRec}</div></td>
                <td>
                    <div style="font-weight:600;">${item.sender}</div>
                    <div style="font-size:13px; color:#4b5563; margin-top:2px; overflow:hidden; text-overflow:ellipsis; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;" title="${item.subject}">${item.subject}</div>
                </td>
                <td><span style="background-color:#e0f2fe; color:#0284c7; padding:4px 8px; border-radius:6px; font-weight:600; font-family:monospace; font-size:12px;">${item.classification_code || '-'}</span></td>
                <td>
                    <div style="font-size:12px; margin-bottom:4px;">📍 ${locName}</div>
                    ${statusPill}
                </td>
                <td style="text-align:center;">
                    <div class="btn-action-group" style="display:flex; gap:4px; justify-content:center;">${actionButtons}</div>
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
        if(formTitle) formTitle.textContent = editMode ? "✏️ Edit Surat Masuk" : "📝 Tambah Surat Masuk";
        
        document.getElementById("form-entry").reset();
        resetFilePreview();

        const groupStatus = document.getElementById("group-archive-status");

        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("entry-id").value = data.id;
            document.getElementById("number").value = data.number;
            document.getElementById("sender").value = data.sender;
            document.getElementById("subject").value = data.subject;
            if (data.letter_date) document.getElementById("letter_date").value = data.letter_date.split('T')[0];
            if (data.received_date) document.getElementById("received_date").value = data.received_date.split('T')[0];
            
            if(data.classification_id) document.getElementById("classification_id").value = data.classification_id;
            if(data.storage_location_id) document.getElementById("storage_location_id").value = data.storage_location_id;
            
            if (groupStatus) {
                groupStatus.classList.remove("hidden");
                if(data.archive_status) document.getElementById("archive_status").value = data.archive_status;
            }

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                // Asumsi backend serve file static di path ini
                const finalUrl = `/storage/documents/incoming_letters/${fileName}`;
                showPreview(finalUrl);
            }
        } else {
            currentEditId = null;
            if (groupStatus) groupStatus.classList.add("hidden");
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
        const inputFile = document.getElementById("fileInput");
        const btnReset = document.getElementById("btnResetFilter");

        if (btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
        if (btnBack) btnBack.addEventListener("click", showTableMode);
        
        if (btnCloseFull) {
            btnCloseFull.addEventListener("click", showTableMode);
        }

        if (inputFile) {
            inputFile.addEventListener("change", (e) => {
                const file = e.target.files[0];
                if (file) {
                    if (file.type !== "application/pdf") {
                        alert("Harap pilih file PDF.");
                        inputFile.value = "";
                        return;
                    }
                    const url = URL.createObjectURL(file);
                    showPreview(url);
                }
            });
        }

        if (btnCancelUpload) btnCancelUpload.addEventListener("click", resetFilePreview);

        if (btnSave) {
            btnSave.addEventListener("click", async (e) => {
                e.preventDefault();
                
                const number = document.getElementById("number").value;
                const sender = document.getElementById("sender").value;
                const classId = document.getElementById("classification_id").value;
                
                if (!number || !sender || !classId) {
                    alert("Harap lengkapi Nomor Surat, Pengirim, dan Klasifikasi!");
                    return;
                }

                const formData = new FormData();
                formData.append('number', number);
                formData.append('sender', sender);
                formData.append('subject', document.getElementById("subject").value);
                formData.append('letter_date', document.getElementById("letter_date").value);
                formData.append('received_date', document.getElementById("received_date").value);
                formData.append('classification_id', classId);
                
                const storageId = document.getElementById("storage_location_id").value;
                if (storageId) formData.append('storage_location_id', storageId);
                
                if (isEditMode) {
                    const status = document.getElementById("archive_status").value;
                    if(status) formData.append('archive_status', status);
                }
                
                if (inputFile.files[0]) formData.append('file', inputFile.files[0]);

                const btn = e.target;
                const originalText = btn.textContent;
                btn.textContent = "Menyimpan...";
                btn.disabled = true;

                try {
                    if (isEditMode) {
                        formData.append('id', currentEditId);
                        await api.incomingLetter.update(formData);
                        alert("Data berhasil diperbarui!");
                    } else {
                        await api.incomingLetter.create(formData);
                        alert("Data berhasil disimpan!");
                    }
                    showTableMode();
                    loadLetters();
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
        const elClass = document.getElementById("filterClassification");
        const elStatus = document.getElementById("filterStatus");
        const elDateType = document.getElementById("filterDateType");
        const elStart = document.getElementById("startDate");
        const elEnd = document.getElementById("endDate");

        const runFilter = () => {
            const term = elSearch.value.toLowerCase();
            const cls = elClass.value;
            const status = elStatus.value;
            const dateType = elDateType.value;
            const start = elStart.value ? new Date(elStart.value) : null;
            const end = elEnd.value ? new Date(elEnd.value) : null;
            if (end) end.setHours(23, 59, 59);

            const filtered = allLetters.filter(item => {
                const txtMatch = (item.number || "").toLowerCase().includes(term) ||
                    (item.sender || "").toLowerCase().includes(term) ||
                    (item.subject || "").toLowerCase().includes(term);
                
                const clsMatch = cls === "" || item.classification_code === cls;
                const statusMatch = status === "" || item.archive_status === status;

                let dateMatch = true;
                let targetDateStr = (dateType === 'letter') ? item.letter_date : item.received_date;

                if (targetDateStr) {
                    const d = new Date(targetDateStr);
                    if (start && d < start) dateMatch = false;
                    if (end && d > end) dateMatch = false;
                } else {
                    // Jika tanggal kosong tapi filter tanggal aktif
                    if (start || end) dateMatch = false; 
                }

                return txtMatch && clsMatch && statusMatch && dateMatch;
            });
            renderTable(filtered);
        };

        if(elSearch) elSearch.addEventListener("keyup", runFilter);
        if(elClass) elClass.addEventListener("change", runFilter);
        if(elStatus) elStatus.addEventListener("change", runFilter);
        if(elStart) elStart.addEventListener("change", runFilter);
        if(elEnd) elEnd.addEventListener("change", runFilter);
        
        if(btnReset) {
            btnReset.addEventListener("click", () => {
                elSearch.value = ""; elClass.value = ""; elStatus.value = ""; 
                elStart.value = ""; elEnd.value = "";
                runFilter();
            });
        }
    };

    // --- GLOBAL ACTIONS ---
    window.triggerEditIncoming = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (item) showFormMode(true, item);
    };

    window.triggerDeleteIncoming = async (id) => {
        if (confirm("Yakin ingin menghapus data ini?")) {
            try {
                await api.incomingLetter.delete(id);
                loadLetters();
            } catch (err) { alert("Gagal hapus: " + err.message); }
        }
    };

    window.openFileIncoming = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (!item || !item.file_path) { alert("File tidak tersedia."); return; }
        const fileName = item.file_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/incoming_letters/${fileName}`;
        
        document.getElementById("view-table").classList.add("hidden");
        document.getElementById("view-form").classList.add("hidden");
        document.getElementById("btn-add-new").classList.add("hidden");
        
        const fullView = document.getElementById("view-pdf-fullscreen");
        fullView.classList.remove("hidden");
        fullView.style.display = "flex";
        document.getElementById("fullscreen-pdf-viewer").src = finalUrl;
    };

    // START
    initIncomingPage();
}