// assets/js/dashboard.js

// Cache data global
let allDocumentsCache = [];

document.addEventListener("DOMContentLoaded", () => {
    // 1. Cek Token Login
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "/page/login";
        return;
    }

    // 2. Load Data User & Dokumen
    loadUserInfo();
    loadDocuments(); 
    loadUploadActivity();
    setupSearch(); 

    // 3. Setup Event Listeners (Logout & Navigasi)
    setupEventListeners();
});

/* ---------- USER INFO ---------- */
function loadUserInfo() {
    const welcomeEl = document.getElementById("user-welcome");
    const nameEl = document.getElementById("profile-name");
    const roleEl = document.getElementById("profile-role");

    // Ambil data langsung dari token (fungsi ini ada di api.js)
    const user = api.auth.getUserData();

    if (!user) {
        // Jika gagal decode token atau token rusak
        if (welcomeEl) welcomeEl.textContent = "Selamat Datang!";
        if (nameEl) nameEl.textContent = "Pengguna";
        if (roleEl) roleEl.textContent = "—";
        return;
    }

    // Ambil data dari claim token (sesuai auth.py)
    const displayName = user.username || "Pengguna";
    const displayRole = user.role || "Staf";

    // Update UI
    if (welcomeEl) welcomeEl.textContent = `Selamat Datang, ${displayName}!`;
    if (nameEl) nameEl.textContent = displayName;
    if (roleEl) roleEl.textContent = displayRole;
}

/* ---------- EVENT LISTENERS (LOGOUT & NAV) ---------- */
function setupEventListeners() {
    // Tombol Logout
    const btnLogout = document.getElementById("btn-logout");
    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            api.auth.logout(); // Panggil fungsi logout dari api.js
        });
    }

    // Navigasi Sidebar (data-route)
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => {
            if(el.dataset.route) window.location.href = el.dataset.route;
        });
    });
}

/* ---------- LOAD DOCUMENTS ---------- */
async function loadDocuments() {
    const container = document.getElementById("quick-access");
    if (!container) return;
    container.innerHTML = `<p style="color:#6b7280;">Memuat dokumen...</p>`;

    try {
        // Fetch semua data secara paralel
        const [incoming, outgoing, diplomas] = await Promise.all([
            api.incomingLetter.getAll(),
            api.outgoingLetter.getAll(),
            api.diploma.getAll(), 
        ]);

        // Gabungkan dan format data
        allDocumentsCache = [
            ...(incoming || []).map(d => ({ 
                ...d, 
                _type: "Surat Masuk", 
                _route: "/page/incoming_letter", 
                _title: d.subject || d.number || "Surat Masuk Tanpa Judul",
                _date: d.created_at || new Date().toISOString() 
            })),
            ...(outgoing || []).map(d => ({ 
                ...d, 
                _type: "Surat Keluar", 
                _route: "/page/outgoing_letter", 
                _title: d.subject || d.number || "Surat Keluar Tanpa Judul",
                _date: d.created_at || new Date().toISOString()
            })),
            ...(diplomas || []).map(d => ({ 
                ...d, 
                _type: "Ijazah", 
                _route: "/page/diploma", 
                _title: d.student_name || d.number || "Ijazah Tanpa Nama",
                _date: d.created_at || new Date().toISOString()
            })),
        ];

        // Sorting: Terbaru (Desc)
        allDocumentsCache.sort((a, b) => new Date(b._date) - new Date(a._date));

        renderDocs(allDocumentsCache);

    } catch (err) {
        console.error("Gagal load documents:", err);
        container.innerHTML = `<p style="color:red; font-size:12px;">Gagal memuat data (API Error).</p>`;
    }
}

function renderDocs(data) {
    const container = document.getElementById("quick-access");
    
    if (!data || data.length === 0) {
        container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; color:#9ca3af; padding:20px;">Tidak ada dokumen ditemukan.</div>`;
        return;
    }

    container.innerHTML = data.map(doc => {
        const dateObj = new Date(doc._date);
        const dateStr = dateObj.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });

        return `
            <div class="doc-card" onclick="window.location.href='${doc._route}'" style="cursor: pointer;">
                <div class="doc-icon">
                    ${doc._type === 'Ijazah' ? '🎓' : doc._type === 'Surat Keluar' ? '📤' : '📄'}
                </div>
                <div style="width:100%;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="doc-chip">${doc._type}</span>
                        <span style="font-size:11px; color:#9ca3af;">${dateStr}</span>
                    </div>
                    <div class="doc-title" style="margin-top:6px;">${doc._title}</div>
                    <div style="font-size:12px; color:#6b7280; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        ${doc.number || '-'}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

/* ---------- FILTER LOGIC ---------- */
window.filterDocs = function(type, btnElement) {
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    btnElement.classList.add('active');

    let filteredData = [];
    if (type === 'all') {
        filteredData = allDocumentsCache;
        document.getElementById("list-title").textContent = "Dokumen Terkini";
    } else {
        filteredData = allDocumentsCache.filter(doc => doc._type === type);
        document.getElementById("list-title").textContent = `Daftar ${type} Terbaru`;
    }
    renderDocs(filteredData);
};

/* ---------- SEARCH LOGIC ---------- */
function setupSearch() {
    const searchInput = document.getElementById("searchInput");
    if(!searchInput) return;

    searchInput.addEventListener("keyup", (e) => {
        const keyword = e.target.value.toLowerCase();
        
        const searchResults = allDocumentsCache.filter(doc => {
            const titleMatch = (doc._title || "").toLowerCase().includes(keyword);
            const numMatch = (doc.number || "").toLowerCase().includes(keyword);
            return titleMatch || numMatch;
        });

        if(keyword.length > 0) {
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById("list-title").textContent = `Hasil Pencarian: "${keyword}"`;
        } else {
             document.getElementById("list-title").textContent = "Dokumen Terkini";
             // Reset filter ke 'Semua' jika search kosong
             const allBtn = document.querySelector('.filter-btn'); 
             if(allBtn) allBtn.classList.add('active');
        }
        renderDocs(searchResults);
    });
}

/* ---------- UPLOAD ACTIVITY (SIMPLE) ---------- */
async function loadUploadActivity() {
    const countEl = document.getElementById("upload-count");
    const chart = document.getElementById("upload-chart");
    if (!countEl || !chart) return;

    try {
        // Reuse data jika sudah ada di cache, atau fetch ulang jika perlu
        // Di sini kita fetch ulang agar data fresh khusus statistik
        const [incoming, outgoing, diplomas] = await Promise.all([
            api.incomingLetter.getAll(),
            api.outgoingLetter.getAll(),
            api.diploma.getAll(),
        ]);
        const allDocs = [...(incoming||[]), ...(outgoing||[]), ...(diplomas||[])];

        const now = new Date();
        const monthDocs = allDocs.filter(doc => {
            const dateStr = doc.created_at || doc.letter_date || doc.received_date; 
            if(!dateStr) return false;
            const d = new Date(dateStr);
            return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
        });

        countEl.textContent = monthDocs.length;

        // Render Simple Chart Bars
        chart.innerHTML = "";
        for (let i = 0; i < 6; i++) {
            const h = Math.floor(Math.random() * 50) + 20; 
            const div = document.createElement("div");
            div.className = "bar";
            div.style.height = `${h}%`;
            chart.appendChild(div);
        }
    } catch (e) { console.log("Chart Error:", e); }
}