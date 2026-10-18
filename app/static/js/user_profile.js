/**
 * static/js/user_profile.js
 * Halaman Akun Saya: satu akun operator, tanpa role.
 */

document.addEventListener('DOMContentLoaded', () => {
    loadAccount();

    const profileForm = document.getElementById('form-profile');
    if (profileForm) profileForm.addEventListener('submit', handleProfileUpdate);

    const passwordForm = document.getElementById('form-password');
    if (passwordForm) passwordForm.addEventListener('submit', handlePasswordChange);

    const toggle = document.getElementById('toggle-password');
    if (toggle) {
        toggle.addEventListener('change', () => {
            document.querySelectorAll('.pw-field').forEach(input => {
                input.type = toggle.checked ? 'text' : 'password';
            });
        });
    }

    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => api.auth.logout());
    }
});

async function loadAccount() {
    try {
        const account = await api.user.getMe();
        if (account) renderAccount(account);
    } catch (error) {
        ui.toast("Gagal memuat akun: " + error.message, "error");
    }
}

function renderAccount(account) {
    const name = account.display_name || account.username || '?';
    const initial = name.charAt(0).toUpperCase();

    setText('profile-avatar-big', initial);
    setText('header-avatar', initial);
    setText('display-name', name);
    setText('display-username', '@' + account.username);
    setText('display-last-login', formatDateTime(account.last_login_at));
    setText('display-updated', formatDateTime(account.updated_at));
    setText('display-joined', formatDateTime(account.created_at));

    setValue('input-display-name', account.display_name);
    setValue('input-username', account.username);

    const statusDot = document.getElementById('status-indicator');
    const statusText = document.getElementById('display-status-text');
    if (statusDot && statusText) {
        statusDot.className = 'status-dot ' + (account.is_active ? 'status-active' : 'status-inactive');
        statusText.className = 'status-text ' + (account.is_active ? 'text-active' : 'text-inactive');
        statusText.innerText = account.is_active ? 'Aktif' : 'Nonaktif';
    }
}

async function handleProfileUpdate(event) {
    event.preventDefault();

    const payload = {
        display_name: document.getElementById('input-display-name').value.trim(),
        username: document.getElementById('input-username').value.trim()
    };

    try {
        const result = await api.user.update(payload);
        renderAccount(result.data);
        ui.toast("Informasi akun tersimpan. Login ulang untuk memperbarui nama di semua halaman.", "success");
    } catch (error) {
        ui.alert("Gagal menyimpan", error.message || "Error Server", "error");
    }
}

async function handlePasswordChange(event) {
    event.preventDefault();

    const oldPassword = document.getElementById('input-old-password').value;
    const newPassword = document.getElementById('input-new-password').value;
    const confirmPassword = document.getElementById('input-confirm-password').value;

    if (newPassword !== confirmPassword) {
        ui.alert("Gagal mengganti", "Kata sandi baru tidak sama.", "error");
        return;
    }

    try {
        await api.user.changePassword(oldPassword, newPassword);
        await ui.alert("Berhasil", "Kata sandi diganti. Silakan login ulang.", "success");
        api.auth.logout();
    } catch (error) {
        ui.alert("Gagal mengganti", error.message || "Error Server", "error");
    }
}

function formatDateTime(value) {
    if (!value) return '-';
    // Contoh hasil: 18 Okt 2026, 07.52
    return new Date(value).toLocaleString('id-ID', {
        day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}

function setValue(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val || '';
}
