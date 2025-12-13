// assets/js/teacher.js
{
    // Variabel state lokal (aman di dalam kurung kurawal)
    let allTeachers = [];
    let isEditMode = false;
    let currentEditId = null;

    // --- FUNGSI UTAMA (INIT) ---
    const initTeacherPage = async () => {
        console.log("Teacher Page Loaded");

        // 1. Cek Login
        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        // 2. Load Data
        await loadTeachers();

        // 3. Setup Listener Tombol (Add, Back, Save, Filter)
        setupEventListeners();
    };

    // --- LOGIKA DATA ---
    const loadTeachers = async () => {
        const tbody = document.getElementById("table-body");
        if(!tbody) return;
        
        tbody.innerHTML = `<tr><td colspan="6" class="loading-text" style="text-align:center;">Memuat data...</td></tr>`;

        try {
            allTeachers = await api.teacher.getAll();
            renderTable(allTeachers);
        } catch (e) {
            tbody.innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Error: ${e.message}</td></tr>`;
        }
    };

    const renderTable = (data) => {
        const tbody = document.getElementById("table-body");
        if(!tbody) return;
        
        tbody.innerHTML = "";

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:20px;">Data tidak ditemukan.</td></tr>`;
            return;
        }

        const user = api.auth.getUserData();
        const isAdmin = user && user.role === 'admin';

        data.forEach(item => {
            const tr = document.createElement("tr");

            // Badge Status
            let statusBadge = `<span class="badge-active">Aktif</span>`;
            if (item.status === 'Pensiun') statusBadge = `<span class="badge-inactive" style="background:#f3f4f6; color:#4b5563;">Pensiun</span>`;
            else if (item.status === 'Keluar') statusBadge = `<span class="badge-inactive">Keluar</span>`;
            else if (item.status === 'Cuti') statusBadge = `<span class="badge-other" style="background:#fff7ed; color:#c2410c;">Cuti</span>`;

            // Badge Kepegawaian
            let empBadge = `<span class="badge-other">${item.employment_status}</span>`;
            if (item.employment_status === 'PNS') empBadge = `<span class="badge-active" style="background:#dbeafe; color:#1e40af;">PNS</span>`;
            else if (item.employment_status === 'PPPK') empBadge = `<span class="badge-active" style="background:#fae8ff; color:#6b21a8;">PPPK</span>`;

            // Tombol Aksi (Hanya Admin)
            let actionButtons = '-';
            if (isAdmin) {
                actionButtons = `
                    <div class="btn-action-group">
                        <button class="btn-action-view btn-edit" title="Edit" onclick="triggerEditTeacher(${item.id})">✏️</button>
                        <button class="btn-action-view btn-delete" title="Hapus" onclick="triggerDeleteTeacher(${item.id})">🗑️</button>
                    </div>
                `;
            }

            tr.innerHTML = `
                <td style="font-family:monospace; font-weight:600;">${item.identity_number}</td>
                <td>
                    <div style="font-weight:600; color:#374151;">${item.full_name}</div>
                    <div style="font-size:11px; color:#6b7280;">Gol: ${item.rank || '-'}</div>
                </td>
                <td>${item.gender}</td>
                <td>${empBadge}</td>
                <td>${statusBadge}</td>
                <td style="text-align:center;">${actionButtons}</td>
            `;
            tbody.appendChild(tr);
        });
    };

    // --- MODE VIEW (TABLE vs FORM) ---
    const showFormMode = (editMode = false, data = null) => {
        isEditMode = editMode;
        
        document.getElementById("view-table").classList.add("hidden");
        document.getElementById("view-form").classList.remove("hidden");
        document.getElementById("btn-add-new").classList.add("hidden");
        document.getElementById("btn-back-list").classList.remove("hidden");

        const formTitle = document.getElementById("form-title"); // Ambil elemen judul
        if(formTitle) {
            formTitle.textContent = editMode ? "✏️ Edit Biodata Guru" : "📝 Tambah Guru Baru";
        }
        
        document.getElementById("form-entry").reset();

        if (editMode && data) {
            currentEditId = data.id;
            document.getElementById("entry-id").value = data.id;
            document.getElementById("inputIdentity").value = data.identity_number;
            document.getElementById("inputName").value = data.full_name;
            document.getElementById("inputGender").value = data.gender;
            document.getElementById("inputRank").value = data.rank || "";
            document.getElementById("inputEmpStatus").value = data.employment_status;
            document.getElementById("inputStatus").value = data.status;
            document.getElementById("inputAddress").value = data.address || "";
            
            // Disable NIP saat edit agar konsisten
            document.getElementById("inputIdentity").disabled = true;
            document.getElementById("inputIdentity").style.backgroundColor = "#f3f4f6";
        } else {
            currentEditId = null;
            document.getElementById("inputIdentity").disabled = false;
            document.getElementById("inputIdentity").style.backgroundColor = "";
            document.getElementById("inputStatus").value = "Aktif";
        }
    };

    const showTableMode = () => {
        document.getElementById("view-form").classList.add("hidden");
        document.getElementById("view-table").classList.remove("hidden");
        document.getElementById("btn-add-new").classList.remove("hidden");
        document.getElementById("btn-back-list").classList.add("hidden");
    };

    // --- EVENT LISTENERS ---
    const setupEventListeners = () => {
        // Tombol Tambah & Kembali
        const btnAdd = document.getElementById("btn-add-new");
        const btnBack = document.getElementById("btn-back-list");
        const btnCancel = document.getElementById("btnCancel");
        const btnSave = document.getElementById("btnSave");
        const btnReset = document.getElementById("btnResetFilter");

        if(btnAdd) btnAdd.addEventListener("click", () => showFormMode(false));
        if(btnBack) btnBack.addEventListener("click", showTableMode);
        if(btnCancel) btnCancel.addEventListener("click", showTableMode);

        // Filter
        const searchInput = document.getElementById("searchInput");
        const filterStatus = document.getElementById("filterStatus");
        const filterEmp = document.getElementById("filterEmpStatus");

        const runFilter = () => {
            const term = searchInput.value.toLowerCase();
            const stat = filterStatus.value;
            const emp = filterEmp.value;

            const filtered = allTeachers.filter(item => {
                const txtMatch = item.full_name.toLowerCase().includes(term) || item.identity_number.includes(term);
                const statMatch = stat === "" || item.status === stat;
                const empMatch = emp === "" || item.employment_status === emp;
                return txtMatch && statMatch && empMatch;
            });
            renderTable(filtered);
        };

        if(searchInput) searchInput.addEventListener("keyup", runFilter);
        if(filterStatus) filterStatus.addEventListener("change", runFilter);
        if(filterEmp) filterEmp.addEventListener("change", runFilter);
        
        if(btnReset) {
            btnReset.addEventListener("click", () => {
                searchInput.value = ""; filterStatus.value = ""; filterEmp.value = "";
                runFilter();
            });
        }

        // Save Data
        if(btnSave) {
            btnSave.addEventListener("click", async (e) => {
                e.preventDefault();
                
                // Ambil Value
                const identity = document.getElementById("inputIdentity").value;
                const name = document.getElementById("inputName").value;
                const gender = document.getElementById("inputGender").value;
                const empStatus = document.getElementById("inputEmpStatus").value;
                
                if (!identity || !name || !gender || !empStatus) {
                    alert("Harap lengkapi NIP, Nama, Jenis Kelamin, dan Status Kepegawaian!");
                    return;
                }

                const payload = {
                    identity_number: identity,
                    full_name: name,
                    gender: gender,
                    rank: document.getElementById("inputRank").value,
                    employment_status: empStatus,
                    status: document.getElementById("inputStatus").value,
                    address: document.getElementById("inputAddress").value
                };

                const originalText = btnSave.textContent;
                btnSave.textContent = "Menyimpan...";
                btnSave.disabled = true;

                try {
                    if (isEditMode) {
                        payload.id = currentEditId;
                        await api.teacher.update(payload);
                        alert("Data berhasil diperbarui!");
                    } else {
                        await api.teacher.create(payload);
                        alert("Data berhasil disimpan!");
                    }
                    showTableMode();
                    loadTeachers(); // Refresh Data
                } catch (err) {
                    console.error(err);
                    alert("Gagal: " + (err.message || "Error Server"));
                } finally {
                    btnSave.textContent = originalText;
                    btnSave.disabled = false;
                }
            });
        }
    };

    // --- GLOBAL ACTIONS (Agar bisa dipanggil via onclick di HTML string) ---
    // Kita tempelkan ke window, tapi beri nama unik agar tidak bentrok
    window.triggerEditTeacher = (id) => {
        const item = allTeachers.find(t => t.id === id);
        if(item) showFormMode(true, item);
    };

    window.triggerDeleteTeacher = async (id) => {
        if(confirm("Yakin ingin menghapus data guru ini?")) {
            try {
                await api.teacher.delete(id);
                loadTeachers();
            } catch (err) {
                alert("Gagal menghapus: " + err.message);
            }
        }
    };

    // Jalankan Init
    initTeacherPage();
}