/**
 * static/js/user_profile.js
 * Mengatur logika tampilan dan update profil pengguna
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Load Data User saat halaman siap
    loadUserProfile();

    // 2. Event Listener: Update Form
    const form = document.getElementById('form-profile');
    if (form) {
        form.addEventListener('submit', handleUpdate);
    }

    // 3. Event Listener: Toggle Password Visibility
    const toggleBtn = document.getElementById('btn-toggle-pass');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', togglePassVisibility);
    }

    // 4. Event Listener: Navigasi Sidebar
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => {
            window.location.href = el.dataset.route;
        });
    });

    // 5. Event Listener: Logout
    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            api.auth.logout();
        });
    }
});

/**
 * Mengambil data dari Token JWT via api.js dan menampilkannya ke UI
 */
function loadUserProfile() {
    // Menggunakan fungsi helper dari api.js
    const user = api.auth.getUserData();

    if (!user) {
        alert("Sesi habis, silakan login kembali.");
        window.location.href = '/page/login';
        return;
    }

    // --- A. Populate Kartu Kiri (Visual) ---
    const initial = user.username ? user.username.charAt(0).toUpperCase() : '?';
    
    const avatarBig = document.getElementById('profile-avatar-big');
    const headerAvatar = document.getElementById('header-avatar');
    if(avatarBig) avatarBig.innerText = initial;
    if(headerAvatar) headerAvatar.innerText = initial;
    
    setText('display-username', user.username || 'User');
    setText('display-nuptk', `NUPTK: ${user.nuptk || '-'}`);
    setText('display-joined', user.created_at || '-');
    setText('display-updated', user.updated_at || '-');

    // Styling Role Badge
    const roleEl = document.getElementById('display-role');
    if (roleEl) {
        roleEl.innerText = user.role || 'User';
        roleEl.className = 'role-badge'; // Reset class
        
        if (user.role === 'admin') roleEl.classList.add('role-admin');
        else if (user.role === 'headmaster') roleEl.classList.add('role-headmaster');
        else roleEl.classList.add('role-teacher');
    }

    // Styling Status Dot
    const statusDot = document.getElementById('status-indicator');
    const statusText = document.getElementById('display-status-text');
    
    if (statusDot && statusText) {
        statusDot.className = 'status-dot';
        statusText.className = 'status-text';
        statusText.innerText = (user.status || 'inactive').toUpperCase();

        if (user.status === 'active') {
            statusDot.classList.add('status-active');
            statusText.classList.add('text-active');
        } else {
            statusDot.classList.add('status-inactive');
            statusText.classList.add('text-inactive');
        }
    }

    // --- B. Populate Form Input (Hidden & Visible) ---
    setValue('input-id', user.id);
    setValue('input-nuptk', user.nuptk);
    setValue('input-username', user.username);
    setValue('input-role', user.role);
    setValue('input-status', user.status);
}

/**
 * Menangani submit form update profil
 */
async function handleUpdate(event) {
    event.preventDefault();

    const id = document.getElementById('input-id').value;
    const username = document.getElementById('input-username').value;
    const password = document.getElementById('input-password').value;
    
    // Role & Status dikirim ulang nilai lamanya (karena user biasa tidak bisa ubah role sendiri)
    const role = document.getElementById('input-role').value;
    const status = document.getElementById('input-status').value;

    if (!username) {
        alert("Username tidak boleh kosong");
        return;
    }

    // Siapkan Payload
    const payload = {
        id: id,
        username: username,
        role: role,
        status: status
    };

    // Hanya kirim password jika user mengisinya
    if (password) {
        payload.password = password;
    }

    try {
        // Panggil API Update (asumsi api.user.update ada di api.js)
        await api.user.update(payload);
        
        alert("Profil berhasil diperbarui! Silakan login ulang untuk melihat perubahan.");
        api.auth.logout(); // Logout paksa agar token diperbarui
    } catch (error) {
        alert("Gagal update profil: " + error.message);
        console.error(error);
    }
}

/**
 * Ubah tipe input password menjadi text dan sebaliknya
 */
function togglePassVisibility() {
    const input = document.getElementById('input-password');
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}

/**
 * Helper sederhana untuk set innerText elemen
 */
function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}

/**
 * Helper sederhana untuk set value input
 */
function setValue(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val || '';
}   