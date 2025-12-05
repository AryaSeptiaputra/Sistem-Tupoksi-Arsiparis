document.addEventListener("DOMContentLoaded", async () => {

    // --- 0. PERBAIKAN NAVIGASI SIDEBAR ---
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
        if (!token) {
            window.location.href = "/page/login";
            return;
        }
    }

    // --- STATE VARIABLES ---
    let allLetters = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");

    // REFERENSI MODE PREVIEW
    const viewPdfFullscreen = document.getElementById("view-pdf-fullscreen");
    const fullscreenPdfViewer = document.getElementById("fullscreen-pdf-viewer");
    const btnClosePreviewMode = document.getElementById("btn-close-preview-mode");

    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    const btnSave = document.getElementById("btn-save-data");
    const btnResetFilter = document.getElementById("btnResetFilter");

    const inputId = document.getElementById("entry-id");
    const inputNumber = document.getElementById("number");
    const inputSender = document.getElementById("sender");
    const inputSubject = document.getElementById("subject");
    const inputLetterDate = document.getElementById("letter_date");
    const inputReceivedDate = document.getElementById("received_date");
    const inputClassId = document.getElementById("classification_id");
    const inputFile = document.getElementById("fileInput");

    const uploadBox = document.getElementById("upload-box");
    const previewBox = document.getElementById("preview-box");
    const pdfViewer = document.getElementById("pdf-viewer");
    const btnCancelUpload = document.getElementById("btn-cancel-upload");

    const elSearch = document.getElementById("searchInput");
    const elStartDate = document.getElementById("startDate");
    const elEndDate = document.getElementById("endDate");
    const elFilterClass = document.getElementById("filterClassification");

    // --- INITIALIZATION ---
    await initPage();

    // --- EVENT LISTENERS ---

    // Navigasi View (Tambah / Kembali)
    if (btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if (btnBack) btnBack.addEventListener("click", showTableMode);

    // LISTENER TOMBOL TUTUP PREVIEW
    if (btnClosePreviewMode) {
        btnClosePreviewMode.addEventListener("click", () => {
            // Sembunyikan mode preview
            if (viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
            // Stop loading PDF agar hemat memori
            if (fullscreenPdfViewer) fullscreenPdfViewer.src = ""; 
            // Kembali ke tabel
            showTableMode();
        });
    }

    // File Upload Preview (Form Edit/Tambah)
    if (inputFile) {
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

    if (btnCancelUpload) btnCancelUpload.addEventListener("click", resetFilePreview);

    // Simpan Data
    if (btnSave) btnSave.addEventListener("click", handleSaveData);

    // Filtering
    [elSearch, elStartDate, elEndDate, elFilterClass].forEach(el => {
        if (el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if (btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            elSearch.value = ""; elStartDate.value = ""; elEndDate.value = ""; elFilterClass.value = "";
            applyFilters();
        });
    }

    // --- FUNCTIONS ---

    async function initPage() {
        console.log("Memulai inisialisasi halaman...");
        await loadClassifications();
        await loadLetters();
    }

    async function loadClassifications() {
        try {
            const data = await api.classification.getAll();
            if (inputClassId) inputClassId.innerHTML = '<option value="">-- Pilih Klasifikasi --</option>';
            if (elFilterClass) elFilterClass.innerHTML = '<option value="">Semua Klasifikasi</option>';

            data.forEach(c => {
                if (inputClassId) inputClassId.add(new Option(`${c.code} - ${c.name}`, c.id));
                if (elFilterClass) elFilterClass.add(new Option(`${c.code} - ${c.name}`, c.code));
            });
        } catch (e) {
            console.error("Gagal load klasifikasi:", e);
        }
    }

    async function loadLetters() {
        const tbody = document.getElementById("table-body");
        if (!tbody) return;
        tbody.innerHTML = `<tr><td colspan="8" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;

        try {
            allLetters = await api.incomingLetter.getAll();
            allLetters.sort((a, b) => new Date(b.received_date) - new Date(a.received_date));
            renderTable(allLetters);
        } catch (e) {
            console.error("Gagal load surat:", e);
            tbody.innerHTML = `<tr><td colspan="8" style="color:red; text-align:center; padding:20px;">Gagal memuat data: ${e.message}</td></tr>`;
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
            const dateR = item.received_date ? new Date(item.received_date).toLocaleDateString("id-ID") : "-";
            const hasFile = !!item.file_path;

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600;">${item.number}</td>
                <td>${dateL}</td>
                <td style="color:var(--primary); font-weight:500;">${dateR}</td>
                <td>${item.sender}</td>
                <td>${item.subject}</td>
                <td><span class="code-badge">${item.classification_code || '-'}</span></td>
                <td style="font-size:12px;">👤 ${item.input_by || 'System'}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view" title="Lihat PDF" 
                            onclick="window.openFile(${item.id})" 
                            ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEdit(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDelete(${item.id})">🗑️</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // --- FORM LOGIC (CREATE & UPDATE) ---

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;

        // Reset Tampilan
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        
        if(viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");

        btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");

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

            for (let i = 0; i < inputClassId.options.length; i++) {
                if (data.classification_code && inputClassId.options[i].text.startsWith(data.classification_code)) {
                    inputClassId.selectedIndex = i;
                    break;
                }
            }

            // Preview File Lama (Di dalam Form Edit)
            // Menggunakan logika rekonstruksi URL manual yang sama
            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                const finalUrl = `/storage/documents/incoming_letters/${fileName}`;
                showPreview(finalUrl);
            }
        } else {
            currentEditId = null;
        }
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        
        if(viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
        
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

    // --- GLOBAL ACTIONS ---

    window.triggerEdit = (id) => {
        const item = allLetters.find(l => l.id === id);
        if (item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        if (confirm("Yakin ingin menghapus data ini?")) {
            try {
                await api.incomingLetter.delete(id);
                loadLetters();
            } catch (err) {
                alert("Gagal hapus: " + err.message);
            }
        }
    };

    // --- [PERBAIKAN UTAMA] ---
    // Menerima ID (angka), bukan path. Data path diambil aman dari memori.
    window.openFile = (id) => {
        // 1. Cari data surat berdasarkan ID
        const item = allLetters.find(l => l.id === id);
        
        if (!item || !item.file_path) {
            alert("File tidak tersedia atau data tidak ditemukan.");
            return;
        }

        // 2. Ambil nama file saja (Split backslash atau slash)
        // Data di 'item.file_path' masih utuh karena tidak lewat HTML attribute
        const fileName = item.file_path.split(/[\\/]/).pop();
        
        // 3. Rakit URL Manual (Menjamin path benar)
        const finalUrl = `/storage/documents/incoming_letters/${fileName}`;
        
        // 4. Tampilkan Preview Fullscreen
        viewTable.classList.add("hidden");
        viewForm.classList.add("hidden");
        btnAdd.classList.add("hidden");

        if(viewPdfFullscreen) {
            viewPdfFullscreen.classList.remove("hidden");
            viewPdfFullscreen.style.display = "flex";
            
            if(fullscreenPdfViewer) {
                console.log("Membuka Preview ID:", id, "URL:", finalUrl);
                fullscreenPdfViewer.src = finalUrl;
            }
        } else {
            console.error("Elemen view-pdf-fullscreen tidak ditemukan.");
        }
    };

    // --- FILTER LOGIC ---
    function applyFilters() {
        const term = elSearch.value.toLowerCase();
        const start = elStartDate.value ? new Date(elStartDate.value) : null;
        const end = elEndDate.value ? new Date(elEndDate.value) : null;
        if (end) end.setHours(23, 59, 59);
        const cls = elFilterClass.value;

        const filtered = allLetters.filter(item => {
            const txtMatch = (item.number || "").toLowerCase().includes(term) ||
                (item.sender || "").toLowerCase().includes(term) ||
                (item.subject || "").toLowerCase().includes(term);
            const clsMatch = cls === "" || item.classification_code === cls;

            let dateMatch = true;
            if (item.received_date) {
                const d = new Date(item.received_date);
                if (start && d < start) dateMatch = false;
                if (end && d > end) dateMatch = false;
            }
            return txtMatch && clsMatch && dateMatch;
        });
        renderTable(filtered);
    }
});