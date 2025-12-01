// assets/js/dashboard.js

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
        window.location.href = "login.html";
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
        const [incoming, outgoing, report] = await Promise.all([
            api.incomingLetter.getAll(),
            api.outgoingLetter.getAll(),
            api.reportCard.getAll(),
        ]);

        const allDocs = [
            ...(incoming || []).map(d => ({ ...d, _type: "Surat Masuk", route: "incoming_letter.html", title: d.subject || d.number })),
            ...(outgoing || []).map(d => ({ ...d, _type: "Surat Keluar", route: "outgoing_letter.html", title: d.subject || d.number })),
            ...(report || []).map(d => ({ ...d, _type: "Ijazah", route: "report_card.html", title: d.student_name || d.number })),
        ];

        if (!allDocs.length) {
            container.innerHTML = `<p style="color:#6b7280;">Belum ada dokumen.</p>`;
            return;
        }

        allDocs.sort((a, b) => new Date(b.created_at || b.letter_date || 0) - new Date(a.created_at || a.letter_date || 0));
        const latest = allDocs.slice(0, 4);

        container.innerHTML = latest.map(doc => `
            <div class="doc-card" data-route="${doc.route}">
                <div class="doc-icon">📄</div>
                <div>
                    <div class="doc-chip">${doc._type}</div>
                    <div class="doc-title">${doc.title}</div>
                </div>
            </div>
        `).join("");

        container.querySelectorAll(".doc-card").forEach(el => {
            el.addEventListener("click", () => {
                const r = el.dataset.route;
                if (r) window.location.href = r;
            });
        });

    } catch (err) {
        console.error("Gagal load quick access:", err);
        container.innerHTML = `<p style="color:red;">Gagal memuat data.</p>`;
    }
}

/* ---------- UPLOAD ACTIVITY ---------- */
async function loadUploadActivity() {
    const countEl = document.getElementById("upload-count");
    const growthEl = document.getElementById("upload-growth");
    const chart = document.getElementById("upload-chart");
    if (!countEl || !chart) return;

    try {
        const [incoming, outgoing, report] = await Promise.all([
            api.incomingLetter.getAll(),
            api.outgoingLetter.getAll(),
            api.reportCard.getAll(),
        ]);

        const allDocs = [...(incoming || []), ...(outgoing || []), ...(report || [])];
        if (!allDocs.length) {
            countEl.textContent = 0;
            if (growthEl) growthEl.textContent = "0%";
            chart.innerHTML = "";
            return;
        }

        const now = new Date();
        const monthDocs = allDocs.filter(doc => {
            const d = new Date(doc.created_at || doc.letter_date || Date.now());
            return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
        });

        countEl.textContent = monthDocs.length;
        if (growthEl) growthEl.textContent = monthDocs.length ? "+100%" : "0%";

        chart.innerHTML = "";
        for (let i = 0; i < 6; i++) {
            const h = Math.random() * 80 + 10;
            const div = document.createElement("div");
            div.className = "bar";
            div.style.height = `${h}%`;
            chart.appendChild(div);
        }
    } catch (err) {
        console.error("Gagal load upload activity:", err);
    }
}
