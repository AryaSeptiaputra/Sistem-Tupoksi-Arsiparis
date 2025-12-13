// assets/js/user_profile.js
{
    // --- INIT ---
    const initUserProfile = () => {
        console.log("User Profile Loaded");

        // 1. Cek Token
        const token = localStorage.getItem("access_token");
        if (!token) {
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        // 2. Load Data User
        loadUserProfileData();

        // 3. Event Listener: Update Form
        const form = document.getElementById('form-profile');
        if (form) {
            form.addEventListener('submit', handleUpdateProfile);
        }

        // 4. Event Listener: Toggle Password
        const toggleBtn = document.getElementById('btn-toggle-pass');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', togglePassVisibility);
        }
    };

    // --- DATA LOGIC ---
    const loadUserProfileData = () => {
        const user = api.auth.getUserData();

        if (!user) {
            alert("Sesi tidak valid.");
            if(window.navigateTo) window.navigateTo("/login");
            return;
        }

        // --- A. Populate Kartu Kiri (Visual) ---
        const initial = user.username ? user.username.charAt(0).toUpperCase() : '?';
        
        const avatarBig = document.getElementById('profile-avatar-big');
        const headerAvatar = document.getElementById('header-avatar-page'); // Avatar spesifik halaman ini
        
        if(avatarBig) avatarBig.innerText = initial;
        if(headerAvatar) headerAvatar.innerText = initial;
        
        setText('display-username', user.username || 'User');
        setText('display-nuptk', `NUPTK: ${user.nuptk || '-'}`);
        
        // Note: created_at biasanya tidak ada di token standar, perlu fetch API detail user jika mau lengkap.
        // Di sini kita pakai data seadanya dari token atau placeholder.
        setText('display-joined', user.created_at || '-'); 
        setText('display-updated', '-');

        // Styling Role Badge
        const roleEl = document.getElementById('display-role');
        if (roleEl) {
            roleEl.innerText = user.role || 'User';
            roleEl.className = 'role-badge'; 
            
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
            const status = user.status || 'active'; // Asumsi active jika login berhasil
            statusText.innerText = status.toUpperCase();

            if (status === 'active') {
                statusDot.classList.add('status-active');
                statusText.classList.add('text-active');
            } else {
                statusDot.classList.add('status-inactive');
                statusText.classList.add('text-inactive');
            }
        }

        // --- B. Populate Form Input ---
        setValue('input-id', user.id);
        setValue('input-nuptk', user.nuptk || user.username); // Fallback
        setValue('input-username', user.username);
        setValue('input-role', user.role);
        setValue('input-status', user.status);
    };

    const handleUpdateProfile = async (event) => {
        event.preventDefault();

        // [PENTING] Ambil ID dari token atau hidden input
        // Jika token tidak memuat ID, pastikan backend endpoint '/user/update_profile' 
        // bisa mengambil ID dari token header secara otomatis.
        
        const username = document.getElementById('input-username').value;
        const password = document.getElementById('input-password').value;
        
        if (!username) {
            alert("Username tidak boleh kosong");
            return;
        }

        // Payload
        const payload = {
            username: username
        };

        if (password) {
            payload.password = password;
        }

        const btn = event.target.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = "Menyimpan...";
        btn.disabled = true;

        try {
            // Panggil API Update Profile
            // Kita gunakan api.user.update. Pastikan API ini mendukung update diri sendiri
            // atau buat endpoint khusus api.user.updateProfile(payload)
            await api.user.update(payload); 
            
            alert("Profil berhasil diperbarui! Silakan login ulang.");
            api.auth.logout(); 
        } catch (error) {
            alert("Gagal update profil: " + (error.message || "Error Server"));
            console.error(error);
            btn.innerText = originalText;
            btn.disabled = false;
        }
    };

    const togglePassVisibility = () => {
        const input = document.getElementById('input-password');
        const icon = document.getElementById('btn-toggle-pass');
        if (input) {
            const isPass = input.type === 'password';
            input.type = isPass ? 'text' : 'password';
            if(icon) icon.textContent = isPass ? '🙈' : '👁️';
        }
    };

    // Helper functions
    const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    };

    const setValue = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.value = val || '';
    };

    // Jalankan Init
    initUserProfile();
}