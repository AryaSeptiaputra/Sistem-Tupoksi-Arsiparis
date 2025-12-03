// assets/js/dashboard.js

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "/page/login";
        return;
    }

    loadUserInfo();
    loadQuickAccess();
    loadUploadActivity();
});

/* ---------- USER INFO ---------- */
async function loadUserInfo() {
    const welcomeEl = document.getElementById("user-welcome");
    const nameEl = document.getElementById("profile-name");
    const roleEl = document.getElementById("profile-role");

    try {
        let user = null;

        try {
            user = await api.auth.me();
        } catch (_) {
            const saved = localStorage.getItem("auth_user");
            if (saved) user = JSON.parse(saved);
        }

        if (!user) {
            if (welcomeEl) welcomeEl.textContent = "Selamat Datang!";
            if (nameEl) nameEl.textContent = "Pengguna";
            if (roleEl) roleEl.textContent = "—";
            return;
        }

        const displayName = user.full_name || user.username || user.nuptk || "Pengguna";
        const displayRole = user.role || "Pengguna Sistem";

        if (welcomeEl) welcomeEl.textContent = `Selamat Datang, ${displayName}!`;
        if (nameEl) nameEl.textContent = displayName;
        if (roleEl) roleEl.textContent = displayRole;
    } catch (err) {
        console.error("Gagal load user info:", err);
    }
}

/* ---------- QUICK ACCESS ---------- */
async function loadQuickAccess() {
    const container = document.getElementById("quick-access");
    if (!container) return;
    container.innerHTML = `<p style="color:#6b7280;">Loading...</p>`;

    try {
        // PERBAIKAN: Menggunakan api.diploma bukan api.reportCard
        const [incoming, outgoing, diplomas] = await Promise.all([
            api.incomingLetter.getAll(),
            api.outgoingLetter.getAll(),
            api.diploma.getAll(), 
        ]);

        // Gabungkan semua data
        const allDocs = [
            ...(incoming || []).map(d => ({ 
                ...d, 
                _type: "Surat Masuk", 
                route: "/page/incoming_letter", 
                title: d.subject || d.number || "Tanpa Judul",
                date: d.created_at || d.received_date || new Date().toISOString()
            })),
            ...(outgoing || []).map(d => ({ 
                ...d, 
                _type: "Surat Keluar", 
                route: "/page/outgoing_letter", 
                title: d.subject || d.number || "Tanpa Judul",
                date: d.created_at || d.letter_date || new Date().toISOString()
            })),
            // Mapping Data Ijazah
            ...(diplomas || []).map(d => ({ 
                ...d, 
                _type: "Ijazah", 
                route: "/page/diploma", 
                title: d.student_name || d.number || "Tanpa Nama", // Sesuai diploma.py
                date: d.created_at || new Date().toISOString()
            })),
        ];

        if (!allDocs.length) {
            container.innerHTML = `<p style="color:#6b7280;">Belum ada dokumen terbaru.</p>`;
            return;
        }

        // Urutkan dari yang terbaru
        allDocs.sort((a, b) => new Date(b.date) - new Date(a.date));
        
        // Ambil 4 teratas
        const latest = allDocs.slice(0, 4);

        container.innerHTML = latest.map(doc => `
            <div class="doc-card" data-route="${doc.route}" style="cursor: pointer;">
                <div class="doc-icon">📄</div>
                <div>
                    <div class="doc-chip">${doc._type}</div>
                    <div class="doc-title">${doc.title}</div>
                </div>
            </div>
        `).join("");

        // Event listener klik
        container.querySelectorAll(".doc-card").forEach(el => {
            el.addEventListener("click", () => {
                const r = el.dataset.route;
                if (r) window.location.href = r;
            });
        });

    } catch (err) {
        console.error("Gagal load quick access:", err);
        container.innerHTML = `<p style="color:red; font-size:12px;">Gagal memuat data. Cek koneksi server.</p>`;
    }
}

/* ---------- UPLOAD ACTIVITY ---------- */
async function loadUploadActivity() {
    const countEl = document.getElementById("upload-count");
    const chart = document.getElementById("upload-chart");
    if (!countEl || !chart) return;

    try {
        // PERBAIKAN: Menggunakan api.diploma
        const [incoming, outgoing, diplomas] = await Promise.all([
            api.incomingLetter.getAll(),
            api.outgoingLetter.getAll(),
            api.diploma.getAll(),
        ]);

        const allDocs = [...(incoming || []), ...(outgoing || []), ...(diplomas || [])];
        
        // Hitung dokumen bulan ini
        const now = new Date();
        const monthDocs = allDocs.filter(doc => {
            const dateStr = doc.created_at || doc.letter_date || doc.received_date; 
            if(!dateStr) return false;
            
            const d = new Date(dateStr);
            return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
        });

        countEl.textContent = monthDocs.length;

        // Render Bar Chart (Visualisasi sederhana)
        chart.innerHTML = "";
        
        // Buat 6 bar random sebagai hiasan dashboard
        for (let i = 0; i < 6; i++) {
            const h = Math.floor(Math.random() * 50) + 20; 
            const div = document.createElement("div");
            div.className = "bar";
            div.style.height = `${h}%`;
            chart.appendChild(div);
        }
    } catch (err) {
        console.error("Gagal load activity:", err);
    }
}