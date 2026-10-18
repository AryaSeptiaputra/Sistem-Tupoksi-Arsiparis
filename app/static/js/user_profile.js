/**
 * static/js/user_profile.js
 * Halaman Akun Saya: satu akun operator, tanpa role.
 */

// Nilai yang tersimpan di server; dipakai untuk mendeteksi perubahan dan tombol Batalkan
let savedAccount = null;

const RECENT_ACTIVITY_LIMIT = 5;

// Syarat kata sandi baru, sama dengan check_password di backend
const PASSWORD_RULES = {
    length: (pw) => pw.length >= 8,
    upper: (pw) => /[A-Z]/.test(pw),
    lower: (pw) => /[a-z]/.test(pw),
    digit: (pw) => /[0-9]/.test(pw),
};

document.addEventListener('DOMContentLoaded', () => {
    loadAccount();
    loadRecentActivity();
    setupProfileForm();
    setupPasswordForm();

    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => api.auth.logout());
    }
});

/* --- Akun --- */

async function loadAccount() {
    try {
        const account = await api.user.getMe();
        if (account) renderAccount(account);
    } catch (error) {
        ui.toast("Gagal memuat akun: " + error.message, "error");
    }
}

function renderAccount(account) {
    savedAccount = account;
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
    updateProfileButtons();

    const badge = document.getElementById('status-badge');
    const statusDot = document.getElementById('status-indicator');
    if (badge && statusDot) {
        badge.classList.toggle('is-inactive', !account.is_active);
        statusDot.className = 'status-dot ' + (account.is_active ? 'status-active' : 'status-inactive');
        setText('display-status-text', account.is_active ? 'Aktif' : 'Nonaktif');
    }
}

/* --- Form informasi akun --- */

function setupProfileForm() {
    const form = document.getElementById('form-profile');
    if (!form) return;

    ['input-display-name', 'input-username'].forEach(id => {
        document.getElementById(id).addEventListener('input', updateProfileButtons);
    });
    document.getElementById('btn-profile-reset').addEventListener('click', () => {
        if (savedAccount) renderAccount(savedAccount);
    });
    form.addEventListener('submit', handleProfileUpdate);
}

function readProfileInputs() {
    return {
        display_name: document.getElementById('input-display-name').value.trim(),
        username: document.getElementById('input-username').value.trim()
    };
}

function updateProfileButtons() {
    if (!savedAccount) return;
    const current = readProfileInputs();
    const changed = current.display_name !== (savedAccount.display_name || '')
        || current.username !== (savedAccount.username || '');
    const filled = current.display_name !== '' && current.username !== '';

    document.getElementById('btn-profile-reset').disabled = !changed;
    document.getElementById('btn-profile-save').disabled = !(changed && filled);
}

async function handleProfileUpdate(event) {
    event.preventDefault();
    const saveBtn = document.getElementById('btn-profile-save');
    saveBtn.disabled = true;

    try {
        const result = await api.user.update(readProfileInputs());
        renderAccount(result.data);
        ui.toast("Informasi akun tersimpan. Login ulang untuk memperbarui nama di semua halaman.", "success");
    } catch (error) {
        updateProfileButtons();
        ui.alert("Gagal menyimpan", error.message || "Error Server", "error");
    }
}

/* --- Form kata sandi --- */

function setupPasswordForm() {
    const form = document.getElementById('form-password');
    if (!form) return;

    document.querySelectorAll('.ak-eye').forEach(btn => {
        btn.addEventListener('click', () => togglePasswordVisibility(btn));
    });
    ['input-old-password', 'input-new-password', 'input-confirm-password'].forEach(id => {
        document.getElementById(id).addEventListener('input', updatePasswordChecklist);
    });
    form.addEventListener('submit', handlePasswordChange);
}

function togglePasswordVisibility(button) {
    const input = document.getElementById(button.dataset.target);
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    button.setAttribute('aria-pressed', String(show));
    button.setAttribute('aria-label', button.getAttribute('aria-label').replace(show ? 'Tampilkan' : 'Sembunyikan', show ? 'Sembunyikan' : 'Tampilkan'));
    button.querySelector('i').className = show ? 'bx bx-hide' : 'bx bx-show';
}

function updatePasswordChecklist() {
    const oldPw = document.getElementById('input-old-password').value;
    const newPw = document.getElementById('input-new-password').value;
    const confirmPw = document.getElementById('input-confirm-password').value;

    const results = Object.fromEntries(
        Object.entries(PASSWORD_RULES).map(([rule, check]) => [rule, check(newPw)])
    );
    results.match = newPw !== '' && newPw === confirmPw;

    Object.entries(results).forEach(([rule, met]) => {
        const item = document.querySelector(`#password-rules [data-rule="${rule}"]`);
        if (!item) return;
        item.classList.toggle('is-met', met);
        item.querySelector('i').className = met ? 'bx bxs-check-circle' : 'bx bx-circle';
    });

    const allMet = Object.values(results).every(Boolean);
    document.getElementById('btn-password-save').disabled = !(allMet && oldPw !== '');
}

async function handlePasswordChange(event) {
    event.preventDefault();
    const oldPassword = document.getElementById('input-old-password').value;
    const newPassword = document.getElementById('input-new-password').value;

    try {
        await api.user.changePassword(oldPassword, newPassword);
        await ui.alert("Berhasil", "Kata sandi diganti. Silakan login ulang.", "success");
        api.auth.logout();
    } catch (error) {
        ui.alert("Gagal mengganti", error.message || "Error Server", "error");
    }
}

/* --- Aktivitas terakhir --- */

async function loadRecentActivity() {
    const list = document.getElementById('activity-list');
    if (!list) return;

    try {
        const logs = await api.log.getRecent(RECENT_ACTIVITY_LIMIT);
        list.innerHTML = '';
        if (logs.length === 0) {
            list.appendChild(createEmptyItem('Belum ada aktivitas tercatat.'));
            return;
        }
        logs.forEach(log => list.appendChild(createActivityItem(log)));
    } catch (error) {
        list.innerHTML = '';
        list.appendChild(createEmptyItem('Aktivitas gagal dimuat: ' + error.message));
    }
}

function createActivityItem(log) {
    const item = document.createElement('li');

    const icon = document.createElement('span');
    icon.className = 'ak-activity-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.innerHTML = `<i class='bx ${log.user_id ? 'bx-user' : 'bx-cog'}'></i>`;

    const text = document.createElement('div');
    text.className = 'ak-activity-text';
    const action = document.createElement('span');
    // textContent, bukan innerHTML: isi log berasal dari input pengguna
    action.textContent = log.action;
    const time = document.createElement('time');
    time.dateTime = log.timestamp;
    time.textContent = `${formatDateTime(log.timestamp)} · ${log.username}`;
    text.append(action, time);

    item.append(icon, text);
    return item;
}

function createEmptyItem(message) {
    const item = document.createElement('li');
    item.className = 'ak-activity-empty';
    item.textContent = message;
    return item;
}

/* --- Helper --- */

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
