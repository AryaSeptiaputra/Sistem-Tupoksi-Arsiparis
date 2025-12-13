// assets/js/router.js

const router = async () => {
    // 1. Daftar Rute URL -> File HTML -> File JS
    const routes = [
        { path: "/", view: "dashboard", script: "dashboard.js" },
        { path: "/dashboard", view: "dashboard", script: "dashboard.js" },
        { path: "/login", view: "login", script: "login.js" },
        { path: "/teacher", view: "teacher", script: "teacher.js" },
        { path: "/incoming_letter", view: "incoming_letter", script: "incoming_letter.js" },
        { path: "/outgoing_letter", view: "outgoing_letter", script: "outgoing_letter.js" },
        { path: "/storage_location", view: "storage_location", script: "storage_location.js" },
        { path: "/user", view: "user", script: "user.js" },
        { path: "/user_profile", view: "user_profile", script: "user_profile.js" },
        { path: "/classification", view: "classification", script: "classification.js" },
        { path: "/diploma", view: "diploma", script: "diploma.js" },
        { path: "/finance_archive", view: "finance_archive", script: "finance_archive.js" },
        { path: "/employee_archive", view: "employee_archive", script: "employee_archive.js" },
        { path: "/disposal", view: "disposal", script: "disposal.js" },
        { path: "/log", view: "log", script: "log.js" },
        { path: "/backup", view: "backup", script: "backup.js" }
    ];

    // 2. Cek URL saat ini
    const currentPath = location.pathname;
    let match = routes.find(r => r.path === currentPath);

    if (!match) {
        match = routes[0]; // Default ke dashboard jika 404
    }

    // 3. Atur Tampilan Sidebar (Sembunyikan jika Login)
    const sidebar = document.getElementById('main-sidebar');
    const appContent = document.getElementById('app-content');
    
    if (match.view === 'login') {
        sidebar.style.display = 'none';
        appContent.style.marginLeft = '0'; // Reset margin agar full width
        document.body.className = 'login-page'; // Tambah class khusus login body
    } else {
        sidebar.style.display = 'flex';
        appContent.style.marginLeft = ''; // Gunakan default CSS (250px)
        document.body.className = ''; 
    }

    // 4. Update Active Menu di Sidebar
    document.querySelectorAll('.nav-item').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === match.path) {
            link.classList.add('active');
        }
    });

    // 5. Muat Konten HTML
    await loadPage(match.view, match.script);
};

// Fungsi Navigasi (Dipanggil saat klik link)
const navigateTo = url => {
    history.pushState(null, null, url);
    router();
};

// Fungsi Memuat Halaman
async function loadPage(viewName, scriptName) {
    const contentDiv = document.getElementById('app-content');
    contentDiv.innerHTML = '<div style="padding:20px;">Memuat halaman...</div>';

    try {
        // Fetch HTML Fragment
        const response = await fetch(`assets/html/${viewName}.html`);
        if (!response.ok) throw new Error("Gagal memuat halaman");
        
        const html = await response.text();
        contentDiv.innerHTML = html;

        // Fetch & Execute Script JS terkait
        if (scriptName) {
            loadScript(`assets/js/${scriptName}`);
        }

    } catch (error) {
        contentDiv.innerHTML = `<h1>Error</h1><p>${error.message}</p>`;
    }
}

// Helper: Load Script Dinamis
function loadScript(src) {
    // Hapus script lama dengan nama yang sama agar bisa dieksekusi ulang
    const oldScript = document.querySelector(`script[src="${src}"]`);
    if (oldScript) oldScript.remove();

    const script = document.createElement("script");
    script.src = src;
    script.async = false; // Penting agar urutan eksekusi benar
    document.body.appendChild(script);
}

// Event Listeners
window.addEventListener("popstate", router); // Handle tombol Back browser

document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", e => {
        // Cek jika yang diklik adalah link SPA (data-link) atau anak elemennya
        const link = e.target.closest("[data-link]");
        if (link) {
            e.preventDefault();
            navigateTo(link.href);
        }
    });
    router(); // Jalankan router saat pertama load
});