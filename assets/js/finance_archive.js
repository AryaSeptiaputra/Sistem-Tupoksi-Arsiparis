// assets/js/finance_archive.js
{
    let allArchives = [];
    let isEditMode = false;
    let currentEditId = null;
    const monthNames = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"];

    // --- INIT ---
    const initFinancePage = async () => {
        console.log("Finance Page Loaded");

        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        await Promise.all([
            loadClassifications(),
            loadStorageLocations(),
            loadArchives()
        ]);

        setupEventListeners();
    };

    // --- DATA ---
    const loadClassifications = async () => {
        try {
            const data = await api.classification.getAll();
            const inputClass = document.getElementById("classification_id");
            if(inputClass) {
                inputClass.innerHTML = '<option value="">-- Pilih Klasifikasi --</option>';
                data.forEach(c => inputClass.add(new Option(`${c.code} - ${c.name}`, c.id)));
            }
        } catch (e) { console.error("Gagal load klasifikasi", e); }
    };

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

    const loadArchives = async () => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="7" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;
        try {
            allArchives = await api.financeArchive.getAll();
            
            // Sorting: Tahun Descending, lalu Bulan Descending
            allArchives.sort((a, b) => {
                if (b.fiscal_year !== a.fiscal_year) return b.fiscal_year - a.fiscal_year;
                return (b.period_month || 0) - (a.period_month || 0);
            });
            
            populateYearFilter();
            renderTable(allArchives);
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="7" style="color:red; text-align:center;">Error: ${e.message}</td></tr>`;
        }
    };

    const populateYearFilter = () => {
        const elFilterYear = document.getElementById("filterYear");
        if(!elFilterYear) return;
        
        const years = [...new Set(allArchives.map(item => item.fiscal_year))].sort().reverse();
        elFilterYear.innerHTML = '<option value="">Semua Tahun</option>';
        years.forEach(y => elFilterYear.add(new Option(y, y)));
    };

    const renderTable = (data) => {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";
        
        if(!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        const user = api.auth.getUserData();
        const isAdmin = user && user.role === 'admin';
        
        // Hide button add if not admin
        const btnAdd = document.getElementById("btn-add-new");
        if(btnAdd && !isAdmin) btnAdd.style.display = 'none';

        const fmt = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 });

        data.forEach(item => {
            const tr = document.createElement("tr");
            const hasFile = !!item.file_path;
            
            let catClass = 'cat-lain';
            let catLabel = item.category;
            switch(item.category) {
                case 'bos_reguler': catClass = 'cat-bos-reg'; catLabel = 'BOS Reguler'; break;
                case 'bos_kinerja': catClass = 'cat-bos-kin'; catLabel = 'BOS Kinerja'; break;
                case 'komite': catClass = 'cat-komite'; catLabel = 'Komite'; break;
                case 'bop': catClass = 'cat-bop'; catLabel = 'BOP'; break;
                default: catClass = 'cat-lain'; catLabel = 'Lainnya';
            }

            let statusBadge = `<span class="status-pill" style="background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Aktif</span>`;
            if(item.archive_status === 'inactive') statusBadge = `<span class="status-pill" style="background:#fef9c3; color:#a16207; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Inaktif</span>`;
            else if(item.archive_status === 'destroyed') statusBadge = `<span class="status-pill" style="background:#fee2e2; color:#b91c1c; padding:2px 8px; border-radius:99px; font-size:11px; font-weight:600;">Musnah</span>`;

            const monthName = item.period_month ? monthNames[item.period_month] : "";
            const periodText = monthName ? `${monthName} ${item.fiscal_year}` : item.fiscal_year;
            const desc = item.description || "-";
            const locationName = item.storage_location_name || '<span style="color:#aaa; font-style:italic;">-</span>';

            let actionButtons = `
                <button class="btn-action-view" title="Lihat PDF" onclick="openFileFinance(${item.id})" 
                    ${!hasFile ? 'disabled style="background:#eee; cursor:default;"' : ''}>📄</button>
            `;

            if (isAdmin) {
                actionButtons += `
                    <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditFinance(${item.id})">✏️</button>
                    <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteFinance(${item.id})">🗑️</button>
                `;
            }

            tr.innerHTML = `
                <td style="font-weight:600;">${periodText}</td>
                <td>
                    <div style="font-weight:600; font-size:13px;">${item.title}</div>
                    <div class="desc-text" title="${desc}" style="font-size:11px; color:#6b7280; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:200px;">${desc}</div>
                </td>
                <td><span style="font-size:10px; font-weight:700; padding:2px 8px; border-radius:4px; text-transform:uppercase; border:1px solid transparent;" class="badge-cat ${catClass}">${catLabel}</span></td>
                <td class="money-text" style="font-family:monospace; font-weight:600;">${fmt.format(item.amount || 0)}</td>
                <td><span class="code-badge">${item.classification_code || '-'}</span></td>
                <td>
                    <div style="font-size:12px; margin-bottom:4px;">📍 ${locationName}</div>
                    ${statusBadge}
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
        if(title) title.textContent = editMode ? "✏️ Edit Arsip Keuangan" : "📝 Tambah Arsip Keuangan";
        
        document.getElementById("form-entry").reset();
        resetFilePreview();

        document.getElementById("fiscal_year").value = new Date().getFullYear();
        
        const groupStatus = document.getElementById("group-archive-status");

        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("entry-id").value = data.id;
            document.getElementById("title").value = data.title;
            document.getElementById("fiscal_year").value = data.fiscal_year;
            document.getElementById("period_month").value = data.period_month || "";
            document.getElementById("category").value = data.category;
            document.getElementById("amount").value = data.amount;
            document.getElementById("description").value = data.description || "";
            
            if (data.classification_id) document.getElementById("classification_id").value = data.classification_id; 
            if (data.storage_location_id) document.getElementById("storage_location_id").value = data.storage_location_id;
            
            if(groupStatus) {
                groupStatus.classList.remove("hidden");
                if(data.archive_status) document.getElementById("archive_status").value = data.archive_status;
            }

            if (data.file_path) {
                const fileName = data.file_path.split(/[\\/]/).pop();
                showPreview(`/storage/documents/finance_archives/${fileName}`);
            }
        } else {
            currentEditId = null;
            if(groupStatus) groupStatus.classList.add("hidden");
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

    // --- EVENT LISTENERS ---
    const setupEventListeners = () => {
        const btnAdd = document.getElementById("btn-add-new");
        const btnBack = document.getElementById("btn-back-list");
        const btnSave = document.getElementById("btn-save-data");
        const btnCloseFull = document.getElementById("btn-close-preview-mode");
        const btnCancelUpload = document.getElementById("btn-cancel-upload");
        const btnReset = document.getElementById("btnResetFilter");
        const inputFile = document.getElementById("fileInput");

        if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
        if(btnBack) btnBack.addEventListener("click", showTableMode);
        
        if (btnCloseFull) {
            btnCloseFull.addEventListener("click", () => {
                const viewPdf = document.getElementById("view-pdf-fullscreen");
                const fullPdf = document.getElementById("fullscreen-pdf-viewer");
                if(viewPdf) viewPdf.classList.add("hidden");
                if(fullPdf) fullPdf.src = "";
                showTableMode();
            });
        }

        if(btnSave) {
            btnSave.addEventListener("click", async (e) => {
                e.preventDefault();
                
                const title = document.getElementById("title").value;
                const year = document.getElementById("fiscal_year").value;
                const amount = document.getElementById("amount").value;
                const classId = document.getElementById("classification_id").value;
                
                if (!title || !year || !amount || !classId) {
                    alert("Harap lengkapi Judul, Tahun, Nominal, dan Klasifikasi!");
                    return;
                }

                const formData = new FormData();
                formData.append('title', title);
                formData.append('fiscal_year', year);
                const month = document.getElementById("period_month").value;
                if(month) formData.append('period_month', month);
                formData.append('category', document.getElementById("category").value);
                formData.append('amount', amount);
                formData.append('description', document.getElementById("description").value);
                formData.append('classification_id', classId);
                
                const storageId = document.getElementById("storage_location_id").value;
                if(storageId) formData.append('storage_location_id', storageId);
                
                if(isEditMode) {
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
                        await api.financeArchive.update(formData);
                        alert("Berhasil diperbarui!");
                    } else {
                        await api.financeArchive.create(formData);
                        alert("Berhasil disimpan!");
                    }
                    showTableMode();
                    loadArchives();
                } catch (err) {
                    console.error(err);
                    alert("Gagal: " + (err.message || "Error Server"));
                } finally {
                    btn.textContent = originalText;
                    btn.disabled = false;
                }
            });
        }

        if (inputFile) {
            inputFile.addEventListener("change", (e) => {
                const file = e.target.files[0];
                if(file) {
                    if (file.type !== "application/pdf") {
                        alert("Hanya file PDF yang diperbolehkan!");
                        inputFile.value = "";
                        return;
                    }
                    showPreview(URL.createObjectURL(file));
                }
            });
        }
        if(btnCancelUpload) btnCancelUpload.addEventListener("click", resetFilePreview);

        // Filter Logic
        const elSearch = document.getElementById("searchInput");
        const elYear = document.getElementById("filterYear");
        const elMonth = document.getElementById("filterMonth");
        const elCat = document.getElementById("filterCategory");
        const elStatus = document.getElementById("filterStatus");

        const runFilter = () => {
            const term = elSearch.value.toLowerCase();
            const year = elYear.value;
            const month = elMonth.value;
            const cat = elCat.value;
            const status = elStatus.value;

            const filtered = allArchives.filter(item => {
                const txtMatch = (item.title||"").toLowerCase().includes(term) || (item.description||"").toLowerCase().includes(term);
                const yearMatch = year === "" || item.fiscal_year == year;
                const monthMatch = month === "" || item.period_month == month;
                const catMatch = cat === "" || item.category === cat;
                const statusMatch = status === "" || item.archive_status === status;

                return txtMatch && yearMatch && monthMatch && catMatch && statusMatch;
            });
            renderTable(filtered);
        };

        if(elSearch) elSearch.addEventListener("keyup", runFilter);
        if(elYear) elYear.addEventListener("change", runFilter);
        if(elMonth) elMonth.addEventListener("change", runFilter);
        if(elCat) elCat.addEventListener("change", runFilter);
        if(elStatus) elStatus.addEventListener("change", runFilter);

        if(btnReset) {
            btnReset.addEventListener("click", () => {
                elSearch.value = ""; elYear.value = ""; elMonth.value = ""; 
                elCat.value = ""; elStatus.value = "";
                runFilter();
            });
        }
    };

    // --- GLOBAL ACTIONS ---
    window.triggerEditFinance = (id) => {
        const item = allArchives.find(x => x.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDeleteFinance = async (id) => {
        if(confirm("Yakin ingin menghapus arsip keuangan ini?")) {
            try { await api.financeArchive.delete(id); loadArchives(); } 
            catch(e) { alert("Gagal hapus: " + e.message); }
        }
    };

    window.openFileFinance = (id) => {
        const item = allArchives.find(x => x.id === id);
        if(!item || !item.file_path) { alert("File tidak tersedia."); return; }
        
        const fileName = item.file_path.split(/[\\/]/).pop();
        const finalUrl = `/storage/documents/finance_archives/${fileName}`;
        
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
    initFinancePage();
}   