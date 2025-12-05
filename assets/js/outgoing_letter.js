document.addEventListener("DOMContentLoaded", async () => {
    
    // --- 0. PERBAIKAN NAVIGASI ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => {
            window.location.href = el.dataset.route;
        });
    });

    // --- 1. CEK SESI ---
    if (typeof api.auth.checkSession === 'function') {
        if (!api.auth.checkSession()) return;
    } else {
        const token = localStorage.getItem("access_token");
        if (!token) { window.location.href = "/page/login"; return; }
    }

    // --- STATE VARIABLES ---
    let allLetters = []; 
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    
    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    const btnSave = document.getElementById("btn-save-data");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Inputs Form
    const inputId = document.getElementById("entry-id");
    const inputNumber = document.getElementById("number");
    const inputClassId = document.getElementById("classification_id");
    const inputLetterDate = document.getElementById("letter_date");
    const inputSentDate = document.getElementById("sent_date");
    const inputDestination = document.getElementById("destination");
    const inputSubject = document.getElementById("subject");
    const inputFile = document.getElementById("fileInput");

    // Preview
    const uploadBox = document.getElementById("upload-box");
    const previewBox = document.getElementById("preview-box");
    const pdfViewer = document.getElementById("pdf-viewer");
    const btnCancelUpload = document.getElementById("btn-cancel-upload");

    // Filters
    const elSearch = document.getElementById("searchInput");
    const elStartDate = document.getElementById("startDate");
    const elEndDate = document.getElementById("endDate");
    const elFilterClass = document.getElementById("filterClassification");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENT LISTENERS ---
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    
    if(inputFile) {
        inputFile.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file && file.type === "application/pdf") {
                const url = URL.createObjectURL(file);
                showPreview(url);
            } else {
                alert("Harap pilih file PDF.");
                inputFile.value = "";
            }
        });
    }

    if(btnCancelUpload) btnCancelUpload.addEventListener("click", resetFilePreview);
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    [elSearch, elStartDate, elEndDate, elFilterClass].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            elSearch.value = ""; elStartDate.value = ""; elEndDate.value = ""; elFilterClass.value = "";
            applyFilters();
        });
    }

    // --- FUNCTIONS ---

    async function initPage() {
        console.log("Memuat data surat keluar...");
        await loadClassifications();
        await loadLetters();
    }

    async function loadClassifications() {
        try {
            const data = await api.classification.getAll();
            if(inputClassId) inputClassId.innerHTML = '<option value="">-- Pilih Klasifikasi --</option>';
            if(elFilterClass) elFilterClass.innerHTML = '<option value="">Semua Klasifikasi</option>';

            data.forEach(c => {
                if(inputClassId) inputClassId.add(new Option(`${c.code} - ${c.name}`, c.id));
                if(elFilterClass) elFilterClass.add(new Option(`${c.code} - ${c.name}`, c.code));
            });
        } catch (e) {
            console.error("Gagal load klasifikasi", e);
        }
    }

    async function loadLetters() {
        const tbody = document.getElementById("table-body");
        if(!tbody) return;
        tbody.innerHTML = `<tr><td colspan="8" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;
        
        try {
            allLetters = await api.outgoingLetter.getAll();
            // Urutkan by sent_date desc
            allLetters.sort((a, b) => new Date(b.sent_date) - new Date(a.sent_date));
            renderTable(allLetters);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="8" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            const dateL = item.letter_date ? new Date(item.letter_date).toLocaleDateString("id-ID") : "-";
            const dateS = item.sent_date ? new Date(item.sent_date).toLocaleDateString("id-ID") : "-";
            const hasFile = !!item.file_path;

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600;">${item.number}</td>
                <td>${dateL}</td>
                <td style="color:var(--primary); font-weight:500;">${dateS}</td>
                <td>${item.destination}</td>
                <td>${item.subject}</td>
                <td><span class="code-badge">${item.classification_code || '-'}</span></td>
                <td style="font-size:12px;">👤 ${item.input_by || 'System'}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view" title="Lihat PDF" 
                            onclick="window.openFile('${item.file_path || ''}')" 
                            ${!hasFile ? 'disabled style="background:#eee; cursor:default"' : ''}>📄</button>
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEdit(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDelete(${item.id})">🗑️</button>
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
        btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");

        document.getElementById("form-title").textContent = editMode ? "✏️ Edit Surat Keluar" : "📝 Buat Surat Keluar";
        document.getElementById("form-entry").reset();
        resetFilePreview();

        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputNumber.value = data.number;
            inputDestination.value = data.destination;
            inputSubject.value = data.subject;
            
            if(data.letter_date) inputLetterDate.value = data.letter_date.split('T')[0];
            if(data.sent_date) inputSentDate.value = data.sent_date.split('T')[0];

            for (let i = 0; i < inputClassId.options.length; i++) {
                if (data.classification_code && inputClassId.options[i].text.startsWith(data.classification_code)) {
                    inputClassId.selectedIndex = i;
                    break;
                }
            }

            if (data.file_path) {
                const cleanPath = data.file_path.replace(/\\/g, "/");
                showPreview("/" + cleanPath); 
            }
        } else {
            currentEditId = null;
        }
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        viewTable.classList.remove("hidden");
        btnAdd.classList.remove("hidden");
        btnBack.classList.add("hidden");
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
            alert("Harap lengkapi field wajib (No Surat, Tujuan, Klasifikasi)!");
            return;
        }

        const formData = new FormData();
        formData.append('number', inputNumber.value);
        formData.append('destination', inputDestination.value);
        formData.append('subject', inputSubject.value);
        formData.append('letter_date', inputLetterDate.value);
        formData.append('sent_date', inputSentDate.value);
        formData.append('classification_id', inputClassId.value);
        
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
    }

    // --- GLOBAL ACTIONS ---
    window.triggerEdit = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        if (confirm("Yakin ingin menghapus data ini?")) {
            try {
                await api.outgoingLetter.delete(id);
                loadLetters();
            } catch (err) {
                alert("Gagal hapus: " + err.message);
            }
        }
    };

    window.openFile = (path) => {
        if (!path) return;
        const cleanPath = path.replace(/\\/g, "/");
        const url = cleanPath.startsWith("/") ? cleanPath : "/" + cleanPath;
        window.open(url, "_blank");
    };

    // --- FILTER ---
    function applyFilters() {
        const term = elSearch.value.toLowerCase();
        const start = elStartDate.value ? new Date(elStartDate.value) : null;
        const end = elEndDate.value ? new Date(elEndDate.value) : null;
        if (end) end.setHours(23,59,59);
        const cls = elFilterClass.value;

        const filtered = allLetters.filter(item => {
            const txtMatch = (item.number || "").toLowerCase().includes(term) || 
                           (item.destination || "").toLowerCase().includes(term) || 
                           (item.subject || "").toLowerCase().includes(term);
            const clsMatch = cls === "" || item.classification_code === cls;
            
            let dateMatch = true;
            if (item.sent_date) {
                const d = new Date(item.sent_date);
                if (start && d < start) dateMatch = false;
                if (end && d > end) dateMatch = false;
            }
            return txtMatch && clsMatch && dateMatch;
        });

        renderTable(filtered);
    }
});