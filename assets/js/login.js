// assets/js/login.js
{
    const initLoginPage = () => {
        // --- 1. DOM REFERENCES ---
        const loginForm = document.getElementById('login-form');
        const pwdInput = document.getElementById('password');
        const toggleBtn = document.getElementById('toggle-password');
        const btnSubmit = document.getElementById('btn-login-submit');

        // --- 2. EVENT LISTENER: TOGGLE PASSWORD ---
        if (toggleBtn && pwdInput) {
            toggleBtn.addEventListener('click', () => {
                const isPwd = pwdInput.type === 'password';
                pwdInput.type = isPwd ? 'text' : 'password';
                toggleBtn.textContent = isPwd ? '🙈' : '👁️'; // Ubah icon
            });
        }

        // --- 3. EVENT LISTENER: SUBMIT ---
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                // Ambil value
                const nuptk = document.getElementById('nuptk').value;
                const password = pwdInput.value;

                // UI Loading
                const originalText = btnSubmit.textContent;
                btnSubmit.textContent = "Memproses...";
                btnSubmit.disabled = true;

                try {
                    // Panggil API (api.js global)
                    const result = await api.auth.login(nuptk, password);
                    
                    if (result && result.access_token) {
                        // Login Sukses -> Pindah ke Dashboard
                        // Gunakan window.navigateTo dari router.js
                        if(window.navigateTo) {
                            window.navigateTo('/dashboard');
                        } else {
                            // Fallback jika router belum load
                            window.location.href = '/'; 
                        }
                    } else {
                        alert("Login gagal: Token tidak diterima.");
                    }
                } catch (error) {
                    console.error(error);
                    // Tampilkan pesan error (bisa pakai ui.alert jika mau lebih bagus)
                    alert("Login Gagal: " + (error.message || "Periksa NIP dan Password Anda"));
                } finally {
                    // Reset UI
                    btnSubmit.textContent = originalText;
                    btnSubmit.disabled = false;
                }
            });
        }
    };

    // Jalankan inisialisasi
    initLoginPage();
}