document.addEventListener("DOMContentLoaded", async () => {

    // --- 0. NAVIGASI ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => { window.location.href = el.dataset.route; });
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- STATE VARIABLES ---
    let allLetters = [];
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
    const inputNumber = document.getElementById("number");
    const inputSender = document.getElementById("sender");
    const inputSubject = document.getElementById("subject");
    const inputLetterDate = document.getElementById("letter_date");
    const inputReceivedDate = document.getElementById("received_date");
    const inputClassId = document.getElementById("classification_id");
    
    const inputStorageId = document.getElementById("storage_location_id");
    const inputArchiveStatus = document.getElementById("archive_status");
    const groupArchiveStatus = document.getElementById("group-archive-status");
    
    const inputFile = document.getElementById("fileInput");
    const uploadBox = document.getElementById("upload-box");
    const previewBox = document.getElementById("preview-box");
    const pdfViewer = document.getElementById("pdf-viewer");
    const btnCancelUpload = document.getElementById("btn-cancel-upload");

    // --- FILTER REFERENCES ---
    const elSearch = document.getElementById("searchInput");
    const elDateType = document.getElementById("filterDateType");
    const elStartDate = document.getElementById("startDate");
    const elEndDate = document.getElementById("endDate");
    const elFilterClass = document.getElementById("filterClassification");
    const elFilterStatus = document.getElementById("filterStatus");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENT LISTENERS ---
    if (btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if (btnBack) btnBack.addEventListener("click", showTableMode);
    
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
    if (btnSave) btnSave.addEventListener("click", handleSaveData);

    // Apply filters listener
    [elSearch, elDateType, elStartDate, elEndDate, elFilterClass, elFilterStatus].forEach(el => {
        if (el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if (btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            elSearch.value = ""; 
            elDateType.value = "received"; 
            elStartDate.value = ""; elEndDate.value = ""; 
            elFilterClass.value = ""; elFilterStatus.value = "";
            applyFilters();
        });
    }

    // --- FUNCTIONS ---

    async function initPage() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;

        await Promise.all([
            loadClassifications(),
            loadStorageLocations(),
            loadLetters()
        ]);
    }

    async function loadClassifications() {
        try {
            const data = await api.classification.getAll();
            if (inputClassId) inputClassId.innerHTML = '<option value="">-- Pilih Klasifikasi --</option>';
            if (elFilterClass) elFilterClass.innerHTML = '<option value="">Semua Klasifikasi</option>';

            data.forEach(c => {
                const text = `${c.code} - ${c.name}`;
                if (inputClassId) inputClassId.add(new Option(text, c.id));
                if (elFilterClass) elFilterClass.add(new Option(text, c.code));
            });
        } catch (e) { console.error("Gagal load klasifikasi:", e); }
    }

    async function loadStorageLocations() {
        try {
            const data = await api.storageLocation.getAll();
            if (inputStorageId) {
                inputStorageId.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
                data.forEach(loc => {
                    inputStorageId.add(new Option(loc.name, loc.id));
                });
            }
        } catch (e) { console.error("Gagal load lokasi:", e); }
    }

    async function loadLetters() {
        try {
            allLetters = await api.incomingLetter.getAll();
            allLetters.sort((a, b) => new Date(b.received_date) - new Date(a.received_date));
            renderTable(allLetters);
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
            // [FIX] DEFINISIKAN TR DI SINI
            const tr = document.createElement("tr");

            // [FIX] FORMAT TANGGAL
            const dateLet = item.letter_date ? new Date(item.letter_date).toLocaleDateString("id-ID") : "-";
            const dateRec = item.received_date ? new Date(item.received_date).toLocaleDateString("id-ID") : "-";

            // [FIX] Status Pill Logic
            let statusPill = `<span class="status-pill st-active">Aktif</span>`;
            if (item.archive_status === 'inactive') statusPill = `<span class="status-pill st-inactive">Inaktif</span>`;
            else if (item.archive_status === 'destroyed') statusPill = `<span class="status-pill st-destroyed">Musnah</span>`;

            const locName = item.storage_location_name || '<span style="color:#aaa; font-style:italic;">-</span>';
            const hasFile = !!item.file_path;

            // [FIX] ACTION BUTTONS
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
                    <div class="text-main" style="font-family:monospace; color:var(--primary);">${item.number}</div>
                    <div class="text-sub"><span class="date-badge">Srt:</span> ${dateLet}</div>
                </td>
                <td>
                    <div class="text-main" style="font-size:14px;">${dateRec}</div>
                </td>
                <td>
                    <div class="text-main">${item.sender}</div>
                    <div class="text-desc" title="${item.subject}">${item.subject}</div>
                </td>
                <td>
                    <span class="code-badge" style="font-size:13px;">${item.classification_code || '-'}</span>
                </td>
                <td>
                    <div class="text-sub" style="font-size:12px; margin-bottom:4px;">📍 ${locName}</div>
                    ${statusPill}
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

    // --- FILTER LOGIC ---

    function applyFilters() {
        const term = elSearch.value.toLowerCase();
        const cls = elFilterClass.value;
        const status = elFilterStatus.value;
        const dateType = elDateType.value; // 'received' atau 'letter'

        const start = elStartDate.value ? new Date(elStartDate.value) : null;
        const end = elEndDate.value ? new Date(elEndDate.value) : null;
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
                if (start || end) dateMatch = false; 
            }

            return txtMatch && clsMatch && statusMatch && dateMatch;
        });

        renderTable(filtered);
    }

    // --- FORM LOGIC ---

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        if(viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
        if(btnAdd) btnAdd.classList.add("hidden");
        if(btnBack) btnBack.classList.remove("hidden");

        document.getElementById("form-title").textContent = editMode ? "✏️ Edit Surat Masuk" : "📝 Tambah Surat Masuk";
        document.getElementById("form-entry").reset();
        resetFilePreview();

        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputNumber.value = data.number;
            inputSender.value = data.sender;
            inputSubject.value = data.subject;
            if (data.letter_date) inputLetterDate.value = data.letter_date.split('T')[0];
            if (data.received_date) inputReceivedDate.value = data.received_date.split('T')[0];
            
            if(data.classification_id) inputClassId.value = data.classification_id;
            if(data.storage_location_id) inputStorageId.value = data.storage_location_id;
            
            if (groupArchiveStatus) {
                groupArchiveStatus.classList.remove("hidden");
                if(data.archive_status) inputArchiveStatus.value = data.archive_status;
            }

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                const finalUrl = `/storage/documents/incoming_letters/${fileName}`;
                showPreview(finalUrl);
            }
        } else {
            currentEditId = null;
            if (groupArchiveStatus) groupArchiveStatus.classList.add("hidden");
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
        if (!inputNumber.value || !inputSender.value || !inputClassId.value) {
            alert("Harap lengkapi Nomor Surat, Pengirim, dan Klasifikasi!");
            return;
        }

        const formData = new FormData();
        formData.append('number', inputNumber.value);
        formData.append('sender', inputSender.value);
        formData.append('subject', inputSubject.value);
        formData.append('letter_date', inputLetterDate.value);
        formData.append('received_date', inputReceivedDate.value);
        formData.append('classification_id', inputClassId.value);
        
        if (inputStorageId.value) formData.append('storage_location_id', inputStorageId.value);
        if (isEditMode && inputArchiveStatus.value) formData.append('archive_status', inputArchiveStatus.value);
        
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
    }

    // --- GLOBAL HELPERS ---
    window.triggerEdit = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        if (confirm("Yakin ingin menghapus data ini?")) {
            try {
                await api.incomingLetter.delete(id);
                loadLetters();
            } catch (err) { alert("Gagal hapus: " + err.message); }
        }
    };

    window.openFile = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (!item || !item.file_path) { alert("File tidak tersedia."); return; }
        const fileName = item.file_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/incoming_letters/${fileName}`;
        
        viewTable.classList.add("hidden");
        viewForm.classList.add("hidden");
        if(btnAdd) btnAdd.classList.add("hidden");
        
        viewPdfFullscreen.classList.remove("hidden");
        viewPdfFullscreen.style.display = "flex";
        fullscreenPdfViewer.src = finalUrl;
    };
});