document.addEventListener("DOMContentLoaded", async () => {
    console.log("[DEBUG] DOMContentLoaded event fired - finance_archive.js starting");

    // --- 0. SETUP NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    console.log("[DEBUG] Token check:", token ? "Found" : "Not found");
    if (!token) { 
        console.log("[DEBUG] Redirecting to login");
        window.location.href = "/page/login"; 
        return; 
    }

    // --- STATE VARIABLES ---
    let allArchives = [];
    let isEditMode = false;
    let currentEditId = null;
    let removeAttachmentFlag = false;  // Track if user wants to remove attachment
    const monthNames = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"];

    console.log("[DEBUG] State variables initialized");

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
    const inputTitle = document.getElementById("title");
    const inputFiscalYear = document.getElementById("fiscal_year");
    const inputMonth = document.getElementById("period_month");
    const inputCategory = document.getElementById("category"); // Dynamic
    const inputAmount = document.getElementById("amount");
    const inputDesc = document.getElementById("description");
    const inputClassId = document.getElementById("classification_id");
    const inputStorageId = document.getElementById("storage_location_id");
    
    // Status Input
    const groupStatus = document.getElementById("group-archive-status");
    const inputArchiveStatus = document.getElementById("archive_status"); // Dynamic
    
    // File Upload Elements
    const inputFile = document.getElementById("fileInput");
    const uploadBox = document.getElementById("upload-box");
    const previewBox = document.getElementById("preview-box");
    const pdfViewer = document.getElementById("pdf-viewer");
    const btnCancelUpload = document.getElementById("btn-cancel-upload");
    const btnRemoveFile = document.getElementById("btn-remove-file");

    // Filters
    const elSearch = document.getElementById("searchInput");
    const elFilterYear = document.getElementById("filterYear");
    const elFilterMonth = document.getElementById("filterMonth");
    const elFilterCat = document.getElementById("filterCategory"); // Dynamic
    const elFilterStatus = document.getElementById("filterStatus"); // Dynamic

    // Check critical elements
    console.log("[DEBUG] DOM element check:");
    console.log("  - viewTable:", !!viewTable);
    console.log("  - btnAdd:", !!btnAdd);
    console.log("  - elSearch:", !!elSearch);
    console.log("  - elFilterYear:", !!elFilterYear);
    console.log("  - elFilterMonth:", !!elFilterMonth);
    console.log("  - elFilterCat:", !!elFilterCat);
    console.log("  - elFilterStatus:", !!elFilterStatus);
    console.log("  - inputCategory:", !!inputCategory);
    console.log("  - inputArchiveStatus:", !!inputArchiveStatus);

    // --- INITIALIZATION ---
    console.log("[DEBUG] Calling initPage()");
    await initPage();
    console.log("[DEBUG] initPage() completed");

    // --- EVENT LISTENERS ---
    
    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    
    if(btnClosePreviewMode) {
        btnClosePreviewMode.addEventListener("click", () => {
            viewPdfFullscreen.classList.add("hidden");
            fullscreenPdfViewer.src = "";
            showTableMode();
        });
    }

    if(btnSave) btnSave.addEventListener("click", handleSaveData);
    if(btnCancelUpload) btnCancelUpload.addEventListener("click", resetFilePreview);
    if(btnRemoveFile) btnRemoveFile.addEventListener("click", () => {
        removeAttachmentFlag = true;
        resetFilePreview();
    });

    if(inputFile) {
        inputFile.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if(file) {
                if (file.type !== "application/pdf") {
                    ui.alert("Format Salah", "Hanya file PDF yang diperbolehkan!", "warning");
                    inputFile.value = "";
                    return;
                }
                showPreview(URL.createObjectURL(file));
            }
        });
    }

    [elSearch, elFilterYear, elFilterMonth, elFilterCat, elFilterStatus].forEach(el => {
        if(el) {
            el.addEventListener("change", applyFilters);
            el.addEventListener("keyup", applyFilters);
        }
    });

    if(btnResetFilter) {
        btnResetFilter.addEventListener("click", () => {
            elSearch.value = ""; 
            elFilterYear.value = ""; 
            elFilterMonth.value = ""; 
            elFilterCat.value = "";
            elFilterStatus.value = "";
            applyFilters();
            ui.toast("Filter direset", "info");
        });
    }

    // --- FUNCTIONS ---

    async function initPage() {
        console.log("[DEBUG] initPage started");
        const tbody = document.getElementById("table-body");
        if (!tbody) {
            console.error("[ERROR] table-body not found on page!");
            alert("CRITICAL ERROR: Elemen table-body tidak ditemukan!");
            return;
        }
        tbody.innerHTML = `<tr><td colspan="7" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;

        // [BARU] Load References untuk Kategori & Status
        try {
            const results = await Promise.allSettled([
                loadReferences(),
                loadClassifications(),
                loadStorageLocations(),
                loadArchives()
            ]);
            
            console.log("[DEBUG] All async operations completed");
            let hasError = false;
            results.forEach((result, index) => {
                const names = ['loadReferences', 'loadClassifications', 'loadStorageLocations', 'loadArchives'];
                if (result.status === 'rejected') {
                    console.error(`[ERROR] ${names[index]} failed:`, result.reason);
                    hasError = true;
                } else {
                    console.log(`[DEBUG] ${names[index]} completed`);
                }
            });
            
            // If loading archives failed, show error message in table
            if (hasError && allArchives.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px; color:red;">Gagal memuat data. Silakan refresh halaman atau cek console.</td></tr>`;
            }
        } catch (e) {
            console.error("[ERROR] initPage failed:", e);
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px; color:red;">Error: ${e.message}</td></tr>`;
        }
    }

    // [BARU] Load Master References (Category & Status)
    async function loadReferences() {
        try {
            console.log("[DEBUG] loadReferences() called");
            // Helper pengisi dropdown
            const populate = (element, data, placeholder) => {
                if(!element) {
                    console.warn("[WARN] Element not found for populate");
                    return;
                }
                element.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '';
                data.forEach(item => {
                    element.add(new Option(item.name, item.code));
                });
            };

            // 1. Finance Category
            console.log("[DEBUG] Fetching finance_category references");
            const respCat = await api.reference.getByCategory('finance_category');
            console.log("[DEBUG] Finance category response:", respCat);
            if(respCat && respCat.data) {
                console.log("[DEBUG] Populating category filter with", respCat.data.length, "items");
                populate(elFilterCat, respCat.data, "Semua Kategori");
                populate(inputCategory, respCat.data, null); // Required form input
            } else {
                console.warn("[WARN] No finance_category data in response");
            }

            // 2. Archive Status
            console.log("[DEBUG] Fetching archive_status references");
            const respStat = await api.reference.getByCategory('archive_status');
            console.log("[DEBUG] Archive status response:", respStat);
            if(respStat && respStat.data) {
                console.log("[DEBUG] Populating status filter with", respStat.data.length, "items");
                populate(elFilterStatus, respStat.data, "Semua Status");
                populate(inputArchiveStatus, respStat.data, null);
            } else {
                console.warn("[WARN] No archive_status data in response");
            }
            console.log("[DEBUG] loadReferences completed");
        } catch (e) {
            console.error("[ERROR] loadReferences failed:", e);
        }
    }

    async function loadClassifications() {
        try {
            console.log("[DEBUG] loadClassifications() called");
            const response = await api.classification.getAll();
            let data = response;
            if (response && response.data && Array.isArray(response.data)) {
                data = response.data;
            } else if (!Array.isArray(response)) {
                console.warn("[WARN] Classification response format:", response);
                data = [];
            }
            console.log("[DEBUG] Loaded", data.length, "classifications");
            if (!inputClassId) {
                console.error("[ERROR] inputClassId element not found");
                return;
            }
            inputClassId.innerHTML = '<option value="">-- Pilih Klasifikasi --</option>';
            if (Array.isArray(data)) {
                data.forEach(c => inputClassId.add(new Option(`${c.code} - ${c.name}`, c.id)));
            }
            console.log("[DEBUG] loadClassifications completed");
        } catch (e) { 
            console.error("[ERROR] loadClassifications failed:", e);
        }
    }

    async function loadStorageLocations() {
        try {
            console.log("[DEBUG] loadStorageLocations() called");
            const response = await api.storageLocation.getAll();
            let data = response;
            if (response && response.data && Array.isArray(response.data)) {
                data = response.data;
            } else if (!Array.isArray(response)) {
                console.warn("[WARN] StorageLocation response format:", response);
                data = [];
            }
            console.log("[DEBUG] Loaded", data.length, "storage locations");
            if (!inputStorageId) {
                console.error("[ERROR] inputStorageId element not found");
                return;
            }
            inputStorageId.innerHTML = '<option value="">-- Pilih Lokasi --</option>';
            if (Array.isArray(data)) {
                data.forEach(l => inputStorageId.add(new Option(l.name, l.id)));
            }
            console.log("[DEBUG] loadStorageLocations completed");
        } catch (e) { 
            console.error("[ERROR] loadStorageLocations failed:", e);
        }
    }

    async function loadArchives() {
        try {
            console.log("[DEBUG] loadArchives() called");
            allArchives = await api.financeArchive.getAll();
            console.log("[DEBUG] API returned:", allArchives);
            console.log("[DEBUG] Data type:", typeof allArchives, "Is array:", Array.isArray(allArchives));
            
            if (!Array.isArray(allArchives)) {
                console.error("[ERROR] allArchives is not an array:", allArchives);
                allArchives = [];
            }
            
            // Sorting: Tahun Descending, lalu Bulan Descending
            allArchives.sort((a, b) => {
                if (b.fiscal_year !== a.fiscal_year) return b.fiscal_year - a.fiscal_year;
                return (b.period_month || 0) - (a.period_month || 0);
            });
            
            console.log("[DEBUG] After sorting:", allArchives.length, "items");
            populateYearFilter();
            renderTable(allArchives);
        } catch (e) {
            console.error("[ERROR] loadArchives exception:", e);
            document.getElementById("table-body").innerHTML = `<tr><td colspan="7" style="color:red; text-align:center;">Error: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        console.log("[DEBUG] renderTable called with data:", data);
        const tbody = document.getElementById("table-body");
        
        if (!tbody) {
            console.error("[ERROR] table-body element not found!");
            return;
        }
        
        tbody.innerHTML = "";
        
        if(!data || data.length === 0) {
            console.log("[DEBUG] No data to render");
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        console.log("[DEBUG] Rendering", data.length, "items");
        const user = api.auth.getUserData();
        const isAdmin = user && user.role === 'admin';
        const fmt = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 });

        data.forEach(item => {
            const tr = document.createElement("tr");
            const hasFile = !!item.file_path;
            
            // Badge Kategori (Gunakan Code untuk styling, Name jika tersedia dari backend/reference)
            // Default styling jika code tidak cocok
            let catClass = 'cat-lain';
            // Simple mapping untuk style lama (jika code di MasterReference sama)
            if(item.category === 'bos_reguler') catClass = 'cat-bos-reg';
            else if(item.category === 'bos_kinerja') catClass = 'cat-bos-kin';
            else if(item.category === 'komite') catClass = 'cat-komite';
            else if(item.category === 'bop') catClass = 'cat-bop';
            
            // Text: Gunakan category name jika backend kirim (misal lewat join), fallback ke code
            // (Disini kita pakai code/raw value karena backend mungkin belum join name)
            const catLabel = item.category.replace(/_/g, ' ').toUpperCase(); 

            // Badge Status
            let statusBadgeClass = 'st-active';
            if(item.archive_status === 'inactive') statusBadgeClass = 'st-inactive';
            else if(item.archive_status === 'destroyed') statusBadgeClass = 'st-destroyed';
            
            // Fallback Text untuk Status
            const statusText = item.archive_status || '-'; 

            const monthName = item.period_month ? monthNames[item.period_month] : "";
            const periodText = monthName ? `${monthName} ${item.fiscal_year}` : item.fiscal_year;
            const desc = item.description || "-";
            const locationName = item.storage_location_name || '<span style="color:#aaa; font-style:italic;">-</span>';

            let actionButtons = `
                <button class="btn-action-view" title="Lihat PDF" onclick="window.openFile(${item.id})" 
                    ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
            `;

            if (isAdmin) {
                actionButtons += `
                    <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEdit(${item.id})">✏️</button>
                    <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDelete(${item.id})">🗑️</button>
                `;
            }

            tr.innerHTML = `
                <td style="font-weight:600;">${periodText}</td>
                <td>
                    <div style="font-weight:600; font-size:13px;">${item.title}</div>
                    <div class="desc-text" title="${desc}">${desc}</div>
                </td>
                <td><span class="badge-cat ${catClass}">${catLabel}</span></td>
                <td class="money-text">${fmt.format(item.amount || 0)}</td>
                <td><span class="code-badge">${item.classification_code || '-'}</span></td>
                <td>
                    <div style="font-size:12px; margin-bottom:4px;">📍 ${locationName}</div>
                    <span class="status-pill ${statusBadgeClass}">${statusText}</span>
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

    function populateYearFilter() {
        const years = [...new Set(allArchives.map(item => item.fiscal_year))].sort().reverse();
        elFilterYear.innerHTML = '<option value="">Semua Tahun</option>';
        years.forEach(y => elFilterYear.add(new Option(y, y)));
    }

    // --- FORM ACTIONS ---

    function showFormMode(editMode = false, data = null) {
        isEditMode = editMode;
        viewTable.classList.add("hidden");
        viewForm.classList.remove("hidden");
        if(viewPdfFullscreen) viewPdfFullscreen.classList.add("hidden");
        
        if(btnAdd) btnAdd.classList.add("hidden");
        if(btnBack) btnBack.classList.remove("hidden");

        document.getElementById("form-title").textContent = editMode ? "✏️ Edit Arsip Keuangan" : "📝 Tambah Arsip Keuangan";
        document.getElementById("form-entry").reset();
        resetFilePreview();

        inputFiscalYear.value = new Date().getFullYear();

        if (editMode && data) {
            currentEditId = data.id;
            inputId.value = data.id;
            inputTitle.value = data.title;
            inputFiscalYear.value = data.fiscal_year;
            inputMonth.value = data.period_month || "";
            inputCategory.value = data.category;
            inputAmount.value = data.amount;
            inputDesc.value = data.description || "";
            
            if (data.classification_id) inputClassId.value = data.classification_id; 
            if (data.storage_location_id) inputStorageId.value = data.storage_location_id;
            
            if(groupStatus) groupStatus.classList.remove("hidden");
            if(inputArchiveStatus && data.archive_status) inputArchiveStatus.value = data.archive_status;

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                showPreview(`/storage/documents/finance_archives/${fileName}`);
            }
        } else {
            currentEditId = null;
            if(groupStatus) groupStatus.classList.add("hidden");
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
        
        if (!inputTitle.value || !inputFiscalYear.value || !inputAmount.value || !inputClassId.value || !inputCategory.value) {
            ui.alert("Data Belum Lengkap", "Harap lengkapi Judul, Tahun, Kategori, Nominal, dan Klasifikasi!", "warning");
            return;
        }

        const formData = new FormData();
        formData.append('title', inputTitle.value);
        formData.append('fiscal_year', inputFiscalYear.value);
        if(inputMonth.value) formData.append('period_month', inputMonth.value);
        formData.append('category', inputCategory.value);
        formData.append('amount', inputAmount.value);
        formData.append('description', inputDesc.value);
        formData.append('classification_id', inputClassId.value);
        
        if(inputStorageId.value) formData.append('storage_location_id', inputStorageId.value);
        
        if(isEditMode && inputArchiveStatus) {
            formData.append('archive_status', inputArchiveStatus.value);
        }

        if (inputFile.files[0]) formData.append('file', inputFile.files[0]);
        
        // Send remove_attachment flag jika user klik hapus file
        if (removeAttachmentFlag) formData.append('remove_attachment', 'true');

        const btn = e.target;
        const originalText = btn.textContent;
        btn.textContent = "Menyimpan...";
        btn.disabled = true;

        try {
            if (isEditMode) {
                formData.append('id', currentEditId);
                await api.financeArchive.update(formData);
                ui.toast("Berhasil diperbarui!", "success");
            } else {
                await api.financeArchive.create(formData);
                ui.toast("Berhasil disimpan!", "success");
            }
            showTableMode();
            loadArchives();
        } catch (err) {
            console.error(err);
            ui.alert("Gagal Menyimpan", err.message || "Error Server", "error");
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
            removeAttachmentFlag = false;  // Reset flag setelah submit
        }
    }

    // --- GLOBAL ACTIONS ---

    window.triggerEdit = (id) => {
        const item = allArchives.find(x => x.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Hapus Data?", "Yakin ingin menghapus arsip keuangan ini secara permanen?", true);
        if(isConfirmed) {
            try { 
                await api.financeArchive.delete(id); 
                ui.toast("Data telah dihapus", "success");
                loadArchives(); 
            } 
            catch(e) { 
                ui.alert("Gagal Hapus", e.message, "error"); 
            }
        }
    };

    window.openFile = (id) => {
        const item = allArchives.find(x => x.id === id);
        if(!item || !item.file_path) { 
            ui.toast("File tidak tersedia", "error"); 
            return; 
        }
        
        const fileName = item.file_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/finance_archives/${fileName}`;
        
        viewTable.classList.add("hidden");
        viewForm.classList.add("hidden");
        if(btnAdd) btnAdd.classList.add("hidden");
        
        viewPdfFullscreen.classList.remove("hidden");
        viewPdfFullscreen.style.display = "flex";
        fullscreenPdfViewer.src = finalUrl;
    };

    // --- FILTER LOGIC ---
    function applyFilters() {
        const term = elSearch.value.toLowerCase();
        const year = elFilterYear.value;
        const month = elFilterMonth.value;
        const cat = elFilterCat.value;
        const status = elFilterStatus.value;

        const filtered = allArchives.filter(item => {
            const txtMatch = (item.title||"").toLowerCase().includes(term) || (item.description||"").toLowerCase().includes(term);
            const yearMatch = year === "" || item.fiscal_year == year;
            const monthMatch = month === "" || item.period_month == month;
            const catMatch = cat === "" || item.category === cat;
            const statusMatch = status === "" || item.archive_status === status;

            return txtMatch && yearMatch && monthMatch && catMatch && statusMatch;
        });
        renderTable(filtered);
    }
});