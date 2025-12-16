document.addEventListener("DOMContentLoaded", async () => {
    
    // --- 0. NAVIGASI & AUTH ---
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => window.location.href = el.dataset.route);
    });

    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // --- CONFIGURATION ---
    const CATEGORY_MAP = {
        'school_major': '🎓 Jurusan Sekolah (Diploma)',
        'teacher_emp_status': '👨‍🏫 Status Kepegawaian Guru',
        'teacher_active_status': '🟢 Status Keaktifan Guru',
        'teacher_rank': '🥇 Pangkat / Golongan', // [BARU] Ditambahkan
        'finance_category': '💰 Kategori Keuangan',
        'emp_doc_type': '📄 Jenis Dokumen Pegawai',
        'letter_approval_status': '👍 Status Persetujuan Surat',
        'archive_status': '🗄️ Status Fisik Arsip',
        'final_action': '⚖️ Nasib Akhir Arsip (JRA)'
    };

    // --- STATE ---
    let allData = [];
    let currentCategory = 'school_major'; 
    let isEditMode = false;
    let currentEditId = null;

    // --- DOM REFERENCES ---
    const viewTable = document.getElementById("view-table");
    const viewForm = document.getElementById("view-form");
    const pageTitle = document.getElementById("page-title");

    const categoryFilter = document.getElementById("categoryFilter");
    const searchInput = document.getElementById("searchInput");
    
    const displayCategory = document.getElementById("displayCategory");
    const inputCode = document.getElementById("inputCode");
    const inputName = document.getElementById("inputName");
    const inputSort = document.getElementById("inputSort");
    const inputDesc = document.getElementById("inputDesc");
    const inputIsActive = document.getElementById("inputIsActive");

    const btnAdd = document.getElementById("btn-add-new");
    const btnBack = document.getElementById("btn-back-list");
    const btnSave = document.getElementById("btnSave");

    // --- INIT ---
    initPage();

    // --- LISTENERS ---
    if(categoryFilter) {
        categoryFilter.addEventListener("change", (e) => {
            currentCategory = e.target.value;
            loadData();
        });
    }

    if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
    if(btnBack) btnBack.addEventListener("click", showTableMode);
    if(btnSave) btnSave.addEventListener("click", handleSaveData);
    if(searchInput) searchInput.addEventListener("keyup", applyFilter);

    // [BARU] FITUR PENYEDERHANAAN INPUT
    // Saat Nama diketik, Kode otomatis terisi (Auto-Slug)
    // Contoh: "III/a Penata Muda" -> "iiia_penata_muda"
    if(inputName && inputCode) {
        inputName.addEventListener("input", (e) => {
            if(!isEditMode) { // Hanya aktif saat tambah baru agar tidak merusak data lama
                const val = e.target.value;
                const slug = val.toLowerCase()
                    .replace(/[^a-z0-9\s]/g, '') // Hapus simbol aneh seperti / atau .
                    .replace(/\s+/g, '_');       // Ganti spasi dengan underscore
                inputCode.value = slug;
            }
        });
    }

    // --- FUNCTIONS ---

    function initPage() {
        categoryFilter.innerHTML = "";
        Object.keys(CATEGORY_MAP).forEach(key => {
            categoryFilter.add(new Option(CATEGORY_MAP[key], key));
        });
        currentCategory = categoryFilter.value;
        loadData();
    }

    async function loadData() {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = `<tr><td colspan="5" class="loading-text" style="text-align:center; padding:20px;">Memuat data...</td></tr>`;
        
        try {
            const response = await api.reference.getByCategory(currentCategory);
            allData = response.data || [];
            renderTable(allData);
        } catch (e) {
            console.error(e);
            tbody.innerHTML = `<tr><td colspan="5" style="color:red; text-align:center;">Gagal: ${e.message}</td></tr>`;
        }
    }

    function renderTable(data) {
        const tbody = document.getElementById("table-body");
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px;">Data kosong untuk kategori ini.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement("tr");
            const activeBadge = item.is_active 
                ? '<span style="color:green; font-size:10px;">🟢 Aktif</span>' 
                : '<span style="color:red; font-size:10px;">🔴 Non-Aktif</span>';
            const trStyle = item.is_active ? '' : 'background:#f9fafb; opacity:0.7;';

            tr.style = trStyle;
            tr.innerHTML = `
                <td style="text-align:center; font-weight:600;">${item.sort_order}</td>
                <td><code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; color:#0f172a;">${item.code}</code></td>
                <td>
                    <div style="font-weight:600;">${item.name}</div>
                    <div>${activeBadge}</div>
                </td>
                <td style="color:var(--text-muted); font-size:13px;">${item.description || '-'}</td>
                <td style="text-align:center;">
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEdit(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Non-aktifkan" onclick="triggerDelete(${item.id})">🚫</button>
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

        document.getElementById("form-entry").reset();
        displayCategory.value = CATEGORY_MAP[currentCategory] || currentCategory;

        if (editMode && data) {
            pageTitle.textContent = "Edit Referensi";
            currentEditId = data.id;
            
            inputCode.value = data.code;
            inputName.value = data.name;
            inputSort.value = data.sort_order;
            inputDesc.value = data.description || "";
            inputIsActive.value = data.is_active ? "true" : "false";
            // Kunci input kode saat edit agar aman
            inputCode.readOnly = true; 
            inputCode.style.backgroundColor = "#e2e8f0";
        } else {
            pageTitle.textContent = "Tambah Referensi Baru";
            currentEditId = null;
            inputSort.value = 0;
            inputIsActive.value = "true";
            // Buka kunci input kode saat baru
            inputCode.readOnly = false;
            inputCode.style.backgroundColor = "";
        }
    }

    function showTableMode() {
        viewForm.classList.add("hidden");
        viewTable.classList.remove("hidden");
        btnAdd.classList.remove("hidden");
        btnBack.classList.add("hidden");
        pageTitle.textContent = "Master Data Referensi";
    }

    async function handleSaveData(e) {
        e.preventDefault();
        
        if (!inputCode.value.trim() || !inputName.value.trim()) {
            ui.alert("Data Kurang", "Kode dan Nama wajib diisi!", "warning");
            return;
        }

        const payload = {
            category: currentCategory,
            code: inputCode.value.trim(),
            name: inputName.value.trim(),
            sort_order: parseInt(inputSort.value) || 0,
            description: inputDesc.value.trim(),
            is_active: inputIsActive.value === "true"
        };

        const btn = e.target;
        const originalText = btn.textContent;
        btn.textContent = "Menyimpan...";
        btn.disabled = true;

        try {
            if (isEditMode) {
                await api.reference.update(currentEditId, payload);
                ui.toast("Data berhasil diperbarui!", "success");
            } else {
                await api.reference.create(payload);
                ui.toast("Data berhasil ditambahkan!", "success");
            }
            showTableMode();
            loadData();
        } catch (err) {
            console.error(err);
            ui.alert("Gagal Menyimpan", err.message, "error");
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }

    window.triggerEdit = (id) => {
        const item = allData.find(x => x.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDelete = async (id) => {
        const isConfirmed = await ui.confirm("Non-aktifkan?", "Data ini akan disembunyikan dari dropdown sistem.", true);
        if(isConfirmed) {
            try {
                await api.reference.delete(id);
                ui.toast("Data dinonaktifkan", "success");
                loadData();
            } catch (err) {
                ui.alert("Gagal", err.message, "error");
            }
        }
    };

    function applyFilter() {
        const term = searchInput.value.toLowerCase();
        const filtered = allData.filter(item => 
            item.code.toLowerCase().includes(term) || 
            item.name.toLowerCase().includes(term)
        );
        renderTable(filtered);
    }
});