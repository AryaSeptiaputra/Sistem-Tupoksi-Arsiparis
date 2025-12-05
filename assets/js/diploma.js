document.addEventListener("DOMContentLoaded", async () => {
    
    // --- 0. SETUP NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    // Cek Token Login
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- STATE VARIABLES ---
    let allDiplomas = []; 
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    
    // Buttons
    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    const btnSave = document.getElementById("btn-save-data");
    const btnResetFilter = document.getElementById("btnResetFilter");

    // Form Inputs
    const inputId = document.getElementById("entry-id");
    const inputName = document.getElementById("student_name");
    const inputSerial = document.getElementById("serial_number"); // ID HTML tetap 'serial_number'
    const inputMajor = document.getElementById("major");
    const inputYear = document.getElementById("academic_year");
    
    // Status Logic Inputs
    const inputIsTaken = document.getElementById("is_taken_checkbox");
    const wrapperDateTaken = document.getElementById("date-taken-wrapper");
    const inputDateTaken = document.getElementById("date_taken");

    // File Upload Inputs
    const inputFile = document.getElementById("fileInput");
    const uploadBox = document.getElementById("upload-box");
    const previewBox = document.getElementById("preview-box");
    const pdfViewer = document.getElementById("pdf-viewer");
    const btnCancelUpload = document.getElementById("btn-cancel-upload");

    // Filters Inputs
    const elSearch = document.getElementById("searchInput");
    const elFilterMajor = document.getElementById("filterMajor");
    const elFilterYear = document.getElementById("filterYear");
    const elFilterStatus = document.getElementById("filterStatus");

    // --- INITIALIZATION ---
    await loadData();

    // --- EVENT LISTENERS ---
    
    // 1. Navigasi Mode
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);

    // 2. Logic Checkbox "Sudah Diambil"
    if(inputIsTaken) {
        inputIsTaken.addEventListener("change", (e) => {
            if(e.target.checked) {
                wrapperDateTaken.classList.remove("hidden");
                // Default ke hari ini jika tanggal kosong
                if(!inputDateTaken.value) inputDateTaken.valueAsDate = new Date();
            } else {
                wrapperDateTaken.classList.add("hidden");
                inputDateTaken.value = "";
            }
        });
    }

    // 3. File Preview
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

    // 4. Save Action
    if(btnSave) btnSave.addEventListener("click", handleSaveData);

    // 5. Filters
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
        });
    }

    // --- CORE FUNCTIONS ---

    async function loadData() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="7" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;
        
        try {
            allDiplomas = await api.diploma.getAll();
            renderTable(allDiplomas);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="7" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");
            
            // --- [ADAPTASI PYTHON MODEL] ---
            // 1. Status ada di dalam object 'status' (nested)
            const statusObj = item.status || {}; 
            const isCollected = statusObj.is_collected === true;
            
            // 2. Ambil tanggal dari dalam statusObj
            const rawDate = statusObj.collected_at;
            const dateTaken = rawDate ? new Date(rawDate).toLocaleDateString("id-ID") : "-";
            
            // 3. Badge Logic
            const badgeClass = isCollected ? 'badge-success' : 'badge-warning';
            const statusText = statusObj.status_text || (isCollected ? 'Sudah Diambil' : 'Belum Diambil');

            // 4. File Path key dari backend adalah 'attachment_path'
            const hasFile = !!item.attachment_path; 

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600;">${item.number || '-'}</td>
                <td>${item.student_name}</td>
                <td>${item.major || '-'}</td>
                <td>${item.academic_year || '-'}</td>
                <td><span class="badge ${badgeClass}">${statusText}</span></td>
                <td style="font-size:13px; color:var(--text-muted);">${dateTaken}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view" title="Lihat File" 
                            onclick="window.openFile('${item.attachment_path || ''}')" 
                            ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEdit(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDelete(${item.id})">🗑️</button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // --- FORM MANAGEMENT ---

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;
        
        // Toggle UI
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        btnAdd.classList.add("hidden");
        btnBack.classList.remove("hidden");

        // Set Title & Reset
        document.getElementById("form-title").textContent = editMode ? "✏️ Edit Data Ijazah" : "🎓 Input Data Baru";
        document.getElementById("form-entry").reset();
        resetFilePreview();
        wrapperDateTaken.classList.add("hidden");

        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            
            // Isi Form standar
            inputName.value = data.student_name;
            inputSerial.value = data.number; // Backend key: number
            inputMajor.value = data.major;
            inputYear.value = data.academic_year;

            // --- [ADAPTASI PYTHON MODEL] ---
            // Baca status dari nested object 'status'
            const statusObj = data.status || {};
            
            if (statusObj.is_collected === true) {
                inputIsTaken.checked = true;
                wrapperDateTaken.classList.remove("hidden");
                
                if(statusObj.collected_at) {
                    // Format tanggal ISO ke YYYY-MM-DD untuk input type=date
                    inputDateTaken.value = statusObj.collected_at.split('T')[0];
                }
            }

            // Preview File (attachment_path)
            if (data.attachment_path) {
                const cleanPath = data.attachment_path.replace(/\\/g, "/");
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

    // --- SAVE DATA (CREATE/UPDATE) ---

    async function handleSaveData(e) {
        e.preventDefault();
        
        // Validasi Sederhana
        if (!inputName.value || !inputSerial.value || !inputMajor.value) {
            alert("Harap lengkapi Nama, No. Seri, dan Jurusan!");
            return;
        }

        const formData = new FormData();
        
        // --- KEY YANG DIKIRIM KE BACKEND ---
        formData.append('number', inputSerial.value); // Backend minta 'number'
        formData.append('student_name', inputName.value);
        formData.append('major', inputMajor.value);
        formData.append('academic_year', inputYear.value);
        
        // Kirim status sebagai string 'true'/'false' agar aman dibaca Backend
        formData.append('is_collected', inputIsTaken.checked ? 'true' : 'false');
        
        // Kirim tanggal jika dicentang
        if(inputIsTaken.checked && inputDateTaken.value) {
            formData.append('collected_at', inputDateTaken.value); // Backend model pakai 'collected_at'
        }
        
        // Kirim File fisik
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
    }

    // --- GLOBAL ACTIONS ---

    window.triggerEdit = (id) => {
        // Cari data di array lokal
        const item = allDiplomas.find(d => d.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        if(confirm("Yakin ingin menghapus data ijazah ini?")) {
            try {
                await api.diploma.delete(id);
                loadData();
            } catch (e) {
                alert("Gagal hapus: " + e.message);
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
        const mjr = elFilterMajor.value;
        const yr = elFilterYear.value;
        const sts = elFilterStatus.value; // 'taken', 'pending', ''

        const filtered = allDiplomas.filter(item => {
            // Text Search
            const txtMatch = (item.student_name || "").toLowerCase().includes(term) || 
                           (item.number || "").toLowerCase().includes(term);
            
            // Dropdown Filters
            const mjrMatch = mjr === "" || item.major === mjr;
            const yrMatch = yr === "" || item.academic_year === yr;
            
            // --- [ADAPTASI PYTHON MODEL] ---
            // Cek status dari nested object
            const statusObj = item.status || {};
            const isCollected = statusObj.is_collected === true;

            let stsMatch = true;
            if (sts === "taken") stsMatch = isCollected;
            if (sts === "pending") stsMatch = !isCollected;

            return txtMatch && mjrMatch && yrMatch && stsMatch;
        });

        renderTable(filtered);
    }
});