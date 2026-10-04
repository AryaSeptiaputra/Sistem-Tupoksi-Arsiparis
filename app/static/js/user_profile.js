/**
 * static/js/user_profile.js
 * Versi waras: data murni dari model User
 */

document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();

    const form = document.getElementById('form-profile');
    if (form) {
        form.addEventListener('submit', handleUpdate);
    }

    const toggleBtn = document.getElementById('btn-toggle-pass');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', togglePassVisibility);
    }

    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            api.auth.logout();
        });
    }
});

/**
 * Load data user dari JWT (User model only)
 */
function loadUserProfile() {
    const user = api.auth.getUserData();

    if (!user) {
        alert("Sesi habis, silakan login kembali.");
        window.location.href = '/page/login';
        return;
    }

    // =====================
    // AVATAR & CARD KIRI
    // =====================
    const initial = user.full_name
        ? user.full_name.charAt(0).toUpperCase()
        : '?';

    setText('profile-avatar-big', initial);
    setText('header-avatar', initial);

    setText('display-username', user.full_name || 'Unknown');
    setText('display-nuptk', `NUPTK: ${user.identity_number || '-'}`);
    setText('display-joined', user.created_at || '-');

    // =====================
    // FORM KANAN (INI YANG KURANG)
    // =====================
    setValue('input-id', user.id);

    // NUPTK (readonly)
    setValue('input-nuptk', user.identity_number);

    // Username → Full Name (readonly / disabled)
    setValue('input-username', user.full_name);

    // Hidden
    setValue('input-role', user.role);
    setValue('input-status', user.status);

    // =====================
    // ROLE BADGE
    // =====================
    const roleEl = document.getElementById('display-role');
    if (roleEl) {
        roleEl.innerText = user.role;
        roleEl.className = 'role-badge';

        if (user.role === 'admin') roleEl.classList.add('role-admin');
        else if (user.role === 'headmaster') roleEl.classList.add('role-headmaster');
        else roleEl.classList.add('role-teacher');
    }

    // =====================
    // STATUS
    // =====================
    const statusDot = document.getElementById('status-indicator');
    const statusText = document.getElementById('display-status-text');

    if (statusDot && statusText) {
        statusDot.className = 'status-dot';
        statusText.className = 'status-text';
        statusText.innerText = user.status.toUpperCase();

        if (user.status === 'active') {
            statusDot.classList.add('status-active');
            statusText.classList.add('text-active');
        } else {
            statusDot.classList.add('status-inactive');
            statusText.classList.add('text-inactive');
        }
    }
}

/**
 * Update password user
 */
/**
 * Update data user (Nama & Password opsional)
 */
async function handleUpdate(event) {
    event.preventDefault();

    const id = document.getElementById('input-id').value;
    const fullName = document.getElementById('input-username').value; // Ambil nilai input
    const password = document.getElementById('input-password').value;

    // Payload wajib menyertakan full_name agar service di backend bisa menangkapnya
    let payload = {
        id: id,
        full_name: fullName 
    };

    // Password hanya dikirim jika diisi
    if (password) {
        payload.password = password;
    }

    try {
        await api.user.update(payload);

        if (password) {
            alert("Password berhasil diperbarui. Silakan login ulang.");
            api.auth.logout();
        } else {
            alert("Profil berhasil diperbarui.");
            loadUserProfile(); // Refresh data di layar
            document.getElementById('input-password').value = "";
        }
    } catch (error) {
        alert("Gagal update: " + (error.message || "Error Server"));
    }
}

function togglePassVisibility() {
    const input = document.getElementById('input-password');
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}

function setValue(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val || '';
}
