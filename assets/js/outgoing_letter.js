/* FILE: outgoing_letter.js */

document.addEventListener("DOMContentLoaded", async () => {

    // --- 0. NAVIGASI & TOKEN CHECK ---
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
    const inputDestination = document.getElementById("destination");
    const inputSubject = document.getElementById("subject");
    const inputLetterDate = document.getElementById("letter_date");
    const inputSentDate = document.getElementById("sent_date");
    const inputClassId = document.getElementById("classification_id");
    const inputStorageId = document.getElementById("storage_location_id");
    
    // Dropdown Status (Dinamis)
    const inputArchiveStatus = document.getElementById("archive_status");
    const inputApprovalStatus = document.getElementById("approval_status");
    
    const radioInputs = document.getElementsByName("is_decree");
    const inputFile = document.getElementById("fileInput");
    
    // Upload UI
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
    const elFilterStatus = document.getElementById("filterStatus");     // Archive Status Filter
    const elFilterApproval = document.getElementById("filterApproval"); // Approval Status Filter

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
                    ui.alert("Format Salah", "Hanya file PDF yang diperbolehkan.", "warning");
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
    [elSearch, elDateType, elStartDate, elEndDate, elFilterClass, elFilterStatus, elFilterApproval].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            elSearch.value = ""; 
            elDateType.value = "sent"; 
            elStartDate.value = ""; elEndDate.value = ""; 
            elFilterClass.value = ""; 
            if(elFilterStatus) elFilterStatus.value = "";
            if(elFilterApproval) elFilterApproval.value = "";
            applyFilters();
            ui.toast("Filter direset", "info");
        });
    }

    // --- FUNCTIONS ---

    async function initPage() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;
        
        await Promise.all([
            loadClassifications(),
            loadStorageLocations(),
            loadReferences(), // Load Archive & Approval Status
            loadLetters()
        ]);
    }

    // [FUNGSI UTAMA] Mengambil data dari MasterReference
    async function loadReferences() {
        try {
            // Helper pengisi dropdown
            const populate = (element, data, placeholder) => {
                if(!element) return;
                element.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '';
                data.forEach(item => {
                    // item.code (misal: 'active', 'pending') -> value
                    // item.name (misal: 'Aktif', 'Menunggu') -> text
                    element.add(new Option(item.name, item.code));
                });
            };

            // 1. Load Archive Status (Shared)
            // Kategori di Python: ARCHIVE_STATUS = "archive_status"
            const respArchive = await api.reference.getByCategory('archive_status');
            if(respArchive && respArchive.data) {
                populate(elFilterStatus, respArchive.data, "Semua Status");
                populate(inputArchiveStatus, respArchive.data, null);
            }

            // 2. Load Letter Approval Status (Outgoing Specific)
            // Kategori di Python: LETTER_APPROVAL_STATUS = "letter_approval_status"
            const respApproval = await api.reference.getByCategory('letter_approval_status');
            if(respApproval && respApproval.data) {
                populate(elFilterApproval, respApproval.data, "Semua Persetujuan");
                populate(inputApprovalStatus, respApproval.data, null);
            }

        } catch (e) {
            console.error("Gagal load references:", e);
            ui.toast("Gagal memuat data referensi", "error");
        }
    }

    async function loadClassifications() {
        try {
            const response = await api.classification.getAll();
            const data = response.classifications || [];
            if(inputClassId) inputClassId.innerHTML = '<option value="">-- Pilih Klasifikasi --</option>';
            if(elFilterClass) elFilterClass.innerHTML = '<option value="">Semua Klasifikasi</option>';
            data.forEach(c => {
                const text = `${c.code} - ${c.name}`;
                if(inputClassId) inputClassId.add(new Option(text, c.id));
                if(elFilterClass) elFilterClass.add(new Option(text, c.code));
            });
        } catch (e) { console.error(e); }
    }

    async function loadStorageLocations() {
        try {
            const response = await api.storageLocation.getAll();
            const data = response.storage_locations || [];
            if(inputStorageId) {
                inputStorageId.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
                data.forEach(l => inputStorageId.add(new Option(l.name, l.id)));
            }
        } catch (e) { console.error(e); }
    }

    async function loadLetters() {
        try {
            const response = await api.outgoingLetter.getAll();
            allLetters = response.outgoing_letters || [];
            allLetters.sort((a, b) => new Date(b.sent_date) - new Date(a.sent_date));
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
            const tr = document.createElement("tr");
            
            const dateLet = item.letter_date ? new Date(item.letter_date).toLocaleDateString("id-ID") : "-";
            const dateSent = item.sent_date ? new Date(item.sent_date).toLocaleDateString("id-ID") : "-";
            const hasFile = !!item.file_path;
            
            // Badge Jenis Surat
            const isSK = item.is_decree; 
            const typeBadge = isSK 
                ? `<span class="type-badge tb-sk">SK</span>` 
                : `<span class="type-badge tb-biasa">Biasa</span>`;

            // --- Status Pill Logic (CSS) ---
            // Code dari DB ('active', 'inactive') dicocokkan untuk styling.
            // Text fallback pakai code jika name tidak tersedia di object response (biasanya backend join atau kita mapping).
            // Untuk simple-nya, kita gunakan mapping style manual, tapi TEXT bisa kita biarkan code atau mapping manual jika belum ada join.
            
            let statusPillClass = "st-active";
            // Mapping sederhana code -> class
            if (item.archive_status === 'inactive') statusPillClass = 'st-inactive';
            if (item.archive_status === 'destroyed') statusPillClass = 'st-destroyed';
            
            // Gunakan item.archive_status (code) sebagai text jika backend belum mengirim 'archive_status_name'
            // Idealnya backend mengirim 'archive_status_name' hasil join master_reference.
            const statusText = item.archive_status || "-"; 
            const statusPill = `<span class="status-pill ${statusPillClass}">${statusText}</span>`;

            // --- Approval Badge Logic (CSS) ---
            let approvalClass = "ap-pending";
            if (item.approval_status === 'approved') approvalClass = 'ap-approved';
            if (item.approval_status === 'rejected') approvalClass = 'ap-rejected';
            if (item.approval_status === 'draft') approvalClass = 'ap-draft';
            
            const approvalText = item.approval_status || "-";
            const approvalBadge = `<span class="approval-badge ${approvalClass}">${approvalText}</span>`;

            const locName = item.storage_location_name || '<span style="color:#aaa; font-style:italic;">-</span>';

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
                    <div class="text-sub"><span class="date-badge">TGL:</span> ${dateLet}</div>
                    <div style="margin-top:4px;">${approvalBadge}</div>
                </td>
                <td><div class="text-main" style="font-size:14px;">${dateSent}</div></td>
                <td>
                    <div class="text-main">${item.destination} ${typeBadge}</div>
                    <div class="text-desc" title="${item.subject}">${item.subject}</div>
                </td>
                <td><span class="code-badge" style="font-size:13px;">${item.classification_code || '-'}</span></td>
                <td>
                    <div class="text-sub" style="font-size:12px; margin-bottom:4px;">📍 ${locName}</div>
                    ${statusPill}
                </td>
                <td style="text-align:center;"><div class="btn-action-group">${actionButtons}</div></td>
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

        document.getElementById("form-title").textContent = editMode ? "✏️ Edit Surat Keluar" : "📝 Buat Surat Keluar";
        document.getElementById("form-entry").reset();
        resetFilePreview();

        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputNumber.value = data.number;
            inputDestination.value = data.destination;
            inputSubject.value = data.subject;
            if (data.letter_date) inputLetterDate.value = data.letter_date.split('T')[0];
            if (data.sent_date) inputSentDate.value = data.sent_date.split('T')[0];

            const isDecreeVal = data.is_decree ? "true" : "false";
            for(let rb of radioInputs) {
                if(rb.value === isDecreeVal) rb.checked = true;
            }

            if(data.classification_id) inputClassId.value = data.classification_id;
            if(data.storage_location_id) inputStorageId.value = data.storage_location_id;
            
            // Set Dynamic Status Values (pastikan option sudah ada dari loadReferences)
            if(data.archive_status) inputArchiveStatus.value = data.archive_status;
            if(data.approval_status) inputApprovalStatus.value = data.approval_status;

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                const cleanPath = `/storage/documents/outgoing_letters/${fileName}`;
                showPreview(cleanPath); 
            }
        } else {
            currentEditId = null;
            // Set Default Values (Opsional, pastikan 'active' dan 'pending' ada di database master reference Anda)
            // inputArchiveStatus.value = "active"; 
            // inputApprovalStatus.value = "pending";
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
        
        if (!inputNumber.value || !inputDestination.value || !inputClassId.value) {
            ui.alert("Data Belum Lengkap", "Harap lengkapi No Surat, Tujuan, dan Klasifikasi.", "warning");
            return;
        }

        const formData = new FormData();
        formData.append('number', inputNumber.value);
        formData.append('destination', inputDestination.value);
        formData.append('subject', inputSubject.value);
        formData.append('letter_date', inputLetterDate.value);
        formData.append('sent_date', inputSentDate.value);
        formData.append('classification_id', inputClassId.value);
        
        if(inputStorageId.value) formData.append('storage_location_id', inputStorageId.value);
        if(inputArchiveStatus.value) formData.append('archive_status', inputArchiveStatus.value);
        if(inputApprovalStatus.value) formData.append('approval_status', inputApprovalStatus.value);
        
        let isDecree = "false";
        for(let rb of radioInputs) if(rb.checked) isDecree = rb.value;
        formData.append('is_decree', isDecree);

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
                await api.outgoingLetter.update(formData);
                ui.toast("Data berhasil diperbarui!", "success");
            } else {
                await api.outgoingLetter.create(formData);
                ui.toast("Data berhasil disimpan!", "success");
            }
            showTableMode();
            loadLetters();
        } catch (err) {
            console.error(err);
            ui.alert("Gagal Menyimpan", err.message || "Kesalahan server", "error");
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }

    // --- GLOBAL HELPERS ---
    window.triggerEdit = (id) => {
        const item = allLetters.find(l => l.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Hapus Surat?", "Apakah Anda yakin ingin menghapus surat ini?", true);
        if(isConfirmed) {
            try { 
                await api.outgoingLetter.delete(id); 
                ui.toast("Data telah dihapus", "success");
                loadLetters(); 
            }
            catch(e) { 
                ui.alert("Gagal Hapus", e.message, "error"); 
            }
        }
    };

    window.openFile = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (!item || !item.file_path) { 
            ui.toast("File tidak tersedia", "error"); 
            return; 
        }
        const fileName = item.file_path.split(/[\\/]/).pop();
        const cleanPath = `/storage/documents/outgoing_letters/${fileName}`;
        viewTable.classList.add("hidden"); viewForm.classList.add("hidden"); 
        if(btnAdd) btnAdd.classList.add("hidden");

        if(viewPdfFullscreen) {
            viewPdfFullscreen.classList.remove("hidden");
            viewPdfFullscreen.style.display = "flex";
            if(fullscreenPdfViewer) fullscreenPdfViewer.src = cleanPath;
        }
    };

    function applyFilters() {
        const term = elSearch.value.toLowerCase();
        const cls = elFilterClass.value;
        const status = elFilterStatus ? elFilterStatus.value : "";
        const approval = elFilterApproval ? elFilterApproval.value : "";
        const dateType = elDateType.value;

        const start = elStartDate.value ? new Date(elStartDate.value) : null;
        const end = elEndDate.value ? new Date(elEndDate.value) : null;
        if(end) end.setHours(23, 59, 59);

        const filtered = allLetters.filter(item => {
            const txtMatch = (item.number||"").toLowerCase().includes(term) ||
                           (item.destination||"").toLowerCase().includes(term) ||
                           (item.subject||"").toLowerCase().includes(term);
            
            const clsMatch = cls === "" || item.classification_code === cls;
            const statusMatch = status === "" || item.archive_status === status;
            const approvalMatch = approval === "" || item.approval_status === approval;

            let dateMatch = true;
            let targetDateStr = (dateType === 'letter') ? item.letter_date : item.sent_date;
            
            if (targetDateStr) {
                const d = new Date(targetDateStr);
                if(start && d < start) dateMatch = false;
                if(end && d > end) dateMatch = false;
            } else {
                if (start || end) dateMatch = false; 
            }

            return txtMatch && clsMatch && statusMatch && approvalMatch && dateMatch;
        });
        renderTable(filtered);
    }
});