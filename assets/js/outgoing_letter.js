// assets/js/outgoing_letter.js
{
    let allLetters = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- INIT ---
    const initOutgoingPage = async () => {
        console.log("Outgoing Letter Page Loaded");

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
                if (filterClass) filterClass.add(new Option(text, c.code));
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
            allLetters = await api.outgoingLetter.getAll();
            // Sort Descending by Letter Date
            allLetters.sort((a, b) => new Date(b.letter_date) - new Date(a.letter_date));
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
            const dateSent = item.sent_date ? new Date(item.sent_date).toLocaleDateString("id-ID") : "-";

            // Status Badge (Arsip Fisik)
            let statusPill = `<span class="status-pill st-active" style="background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Aktif</span>`;
            if (item.archive_status === 'inactive') statusPill = `<span class="status-pill" style="background:#fef9c3; color:#a16207; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Inaktif</span>`;
            else if (item.archive_status === 'destroyed') statusPill = `<span class="status-pill" style="background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Musnah</span>`;

            // Approval Badge
            let appBadge = `<span class="approval-badge" style="background:#f3f4f6; color:#4b5563; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:600;">Draft</span>`;
            if (item.approval_status === 'pending') appBadge = `<span class="approval-badge" style="background:#fff7ed; color:#c2410c; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:600;">⏳ Menunggu</span>`;
            else if (item.approval_status === 'approved') appBadge = `<span class="approval-badge" style="background:#ecfdf5; color:#047857; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:600;">✅ Disetujui</span>`;
            else if (item.approval_status === 'rejected') appBadge = `<span class="approval-badge" style="background:#fef2f2; color:#b91c1c; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:600;">❌ Ditolak</span>`;

            // Type Badge (SK vs Biasa)
            const typeBadge = item.is_decree ? 
                `<span style="font-size:10px; padding:2px 6px; border-radius:4px; font-weight:700; margin-left:6px; background:#fae8ff; color:#86198f;">SK</span>` : 
                `<span style="font-size:10px; padding:2px 6px; border-radius:4px; font-weight:700; margin-left:6px; background:#e0f2fe; color:#0369a1;">Biasa</span>`;

            const locName = item.storage_location_name || '<span style="color:#aaa;">-</span>';
            const hasFile = !!item.file_path;

            let actionButtons = `
                <button class="btn-action-view" title="Lihat PDF" 
                    onclick="openFileOutgoing(${item.id})" 
                    ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
            `;

            if (isAdmin) {
                actionButtons += `
                    <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditOutgoing(${item.id})">✏️</button>
                    <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteOutgoing(${item.id})">🗑️</button>
                `;
            }

            tr.innerHTML = `
                <td>
                    <div style="display:flex; align-items:center;">
                        <span style="font-family:monospace; color:var(--primary); font-weight:600;">${item.number}</span>
                        ${typeBadge}
                    </div>
                    <div style="font-size:12px; color:#6b7280; margin-top:2px;">${dateLet}</div>
                </td>
                <td><div style="font-size:14px; font-weight:600;">${dateSent}</div></td>
                <td>
                    <div style="font-weight:600;">${item.destination}</div>
                    <div style="font-size:13px; color:#4b5563; margin-top:2px; overflow:hidden; text-overflow:ellipsis; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;" title="${item.subject}">${item.subject}</div>
                </td>
                <td><span style="background-color:#e0f2fe; color:#0284c7; padding:4px 8px; border-radius:6px; font-weight:600; font-family:monospace; font-size:12px;">${item.classification_code || '-'}</span></td>
                <td>
                    <div style="margin-bottom:4px;">${appBadge}</div>
                    <div style="font-size:12px; margin-bottom:2px;">📍 ${locName}</div>
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
        if(formTitle) formTitle.textContent = editMode ? "✏️ Edit Surat Keluar" : "📝 Buat Surat Keluar";
        
        document.getElementById("form-entry").reset();
        resetFilePreview();

        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("entry-id").value = data.id;
            
            // Set Radio Button
            const radios = document.getElementsByName("is_decree");
            for(const r of radios) {
                if(r.value === String(data.is_decree)) r.checked = true;
            }

            document.getElementById("number").value = data.number;
            document.getElementById("destination").value = data.destination;
            document.getElementById("subject").value = data.subject;
            
            if (data.letter_date) document.getElementById("letter_date").value = data.letter_date.split('T')[0];
            if (data.sent_date) document.getElementById("sent_date").value = data.sent_date.split('T')[0];
            
            if(data.classification_id) document.getElementById("classification_id").value = data.classification_id;
            if(data.storage_location_id) document.getElementById("storage_location_id").value = data.storage_location_id;
            
            if(data.archive_status) document.getElementById("archive_status").value = data.archive_status;
            if(data.approval_status) document.getElementById("approval_status").value = data.approval_status;

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                const finalUrl = `/storage/documents/outgoing_letters/${fileName}`;
                showPreview(finalUrl);
            }
        } else {
            currentEditId = null;
            // Default radio to 'false' (Biasa)
            document.querySelector('input[name="is_decree"][value="false"]').checked = true;
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
                const dest = document.getElementById("destination").value;
                const classId = document.getElementById("classification_id").value;
                
                if (!number || !dest || !classId) {
                    alert("Harap lengkapi Nomor Surat, Tujuan, dan Klasifikasi!");
                    return;
                }

                // Get Radio Value
                const isDecree = document.querySelector('input[name="is_decree"]:checked').value;

                const formData = new FormData();
                formData.append('is_decree', isDecree); // 'true' or 'false'
                formData.append('number', number);
                formData.append('destination', dest);
                formData.append('subject', document.getElementById("subject").value);
                formData.append('letter_date', document.getElementById("letter_date").value);
                formData.append('sent_date', document.getElementById("sent_date").value);
                formData.append('classification_id', classId);
                
                const storageId = document.getElementById("storage_location_id").value;
                if (storageId) formData.append('storage_location_id', storageId);
                
                // Always send status & approval
                formData.append('archive_status', document.getElementById("archive_status").value);
                formData.append('approval_status', document.getElementById("approval_status").value);
                
                if (inputFile.files[0]) formData.append('file', inputFile.files[0]);

                const btn = e.target;
                const originalText = btn.textContent;
                btn.textContent = "Menyimpan...";
                btn.disabled = true;

                try {
                    if (isEditMode) {
                        formData.append('id', currentEditId);
                        await api.outgoingLetter.update(formData);
                        alert("Data berhasil diperbarui!");
                    } else {
                        await api.outgoingLetter.create(formData);
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
        const elApproval = document.getElementById("filterApproval");
        const elDateType = document.getElementById("filterDateType");
        const elStart = document.getElementById("startDate");
        const elEnd = document.getElementById("endDate");

        const runFilter = () => {
            const term = elSearch.value.toLowerCase();
            const cls = elClass.value;
            const status = elStatus.value;
            const app = elApproval.value;
            const dateType = elDateType.value;
            const start = elStart.value ? new Date(elStart.value) : null;
            const end = elEnd.value ? new Date(elEnd.value) : null;
            if (end) end.setHours(23, 59, 59);

            const filtered = allLetters.filter(item => {
                const txtMatch = (item.number || "").toLowerCase().includes(term) ||
                    (item.destination || "").toLowerCase().includes(term) ||
                    (item.subject || "").toLowerCase().includes(term);
                
                const clsMatch = cls === "" || item.classification_code === cls;
                const statusMatch = status === "" || item.archive_status === status;
                const appMatch = app === "" || item.approval_status === app;

                let dateMatch = true;
                let targetDateStr = (dateType === 'letter') ? item.letter_date : item.sent_date;

                if (targetDateStr) {
                    const d = new Date(targetDateStr);
                    if (start && d < start) dateMatch = false;
                    if (end && d > end) dateMatch = false;
                } else {
                    if (start || end) dateMatch = false; 
                }

                return txtMatch && clsMatch && statusMatch && appMatch && dateMatch;
            });
            renderTable(filtered);
        };

        if(elSearch) elSearch.addEventListener("keyup", runFilter);
        if(elClass) elClass.addEventListener("change", runFilter);
        if(elStatus) elStatus.addEventListener("change", runFilter);
        if(elApproval) elApproval.addEventListener("change", runFilter);
        if(elStart) elStart.addEventListener("change", runFilter);
        if(elEnd) elEnd.addEventListener("change", runFilter);
        
        if(btnReset) {
            btnReset.addEventListener("click", () => {
                elSearch.value = ""; elClass.value = ""; elStatus.value = ""; 
                elApproval.value = ""; elStart.value = ""; elEnd.value = "";
                runFilter();
            });
        }
    };

    // --- GLOBAL ACTIONS ---
    window.triggerEditOutgoing = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (item) showFormMode(true, item);
    };

    window.triggerDeleteOutgoing = async (id) => {
        if (confirm("Yakin ingin menghapus data ini?")) {
            try {
                await api.outgoingLetter.delete(id);
                loadLetters();
            } catch (err) { alert("Gagal hapus: " + err.message); }
        }
    };

    window.openFileOutgoing = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (!item || !item.file_path) { alert("File tidak tersedia."); return; }
        const fileName = item.file_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/outgoing_letters/${fileName}`;
        
        document.getElementById("view-table").classList.add("hidden");
        document.getElementById("view-form").classList.add("hidden");
        document.getElementById("btn-add-new").classList.add("hidden");
        
        const fullView = document.getElementById("view-pdf-fullscreen");
        fullView.classList.remove("hidden");
        fullView.style.display = "flex";
        document.getElementById("fullscreen-pdf-viewer").src = finalUrl;
    };

    // START
    initOutgoingPage();
}