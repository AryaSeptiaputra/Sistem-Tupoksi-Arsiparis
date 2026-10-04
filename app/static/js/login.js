// static/js/login.js

document.addEventListener('DOMContentLoaded', () => {
    
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            await handleLogin(); 
        });
    }
});

async function handleLogin() {
    const nuptkInput = document.getElementById('nuptk').value; 
    const passInput = document.getElementById('password').value;
    const btnLogin = document.querySelector('.btn-login');
    const originalText = btnLogin.textContent;

    try {
        // 1. Ubah tombol jadi Loading
        btnLogin.textContent = "Memproses...";
        btnLogin.disabled = true;

        // 2. Panggil API Login
        const result = await api.auth.login(nuptkInput, passInput);
        
        // 3. JIKA SUKSES:
        if (result && result.access_token) {
            // Gunakan TOAST (Hijau) agar mulus
            ui.toast("Login Berhasil! Mengalihkan...", "success"); 
            
            // Beri jeda sedikit agar user sempat baca toast sebelum pindah
            setTimeout(() => {
                window.location.href = '/page/dashboard'; 
            }, 1000);
        } else {
            throw new Error("Gagal mendapatkan token akses.");
        }
        
    } catch (error) {
        console.error("Login Error:", error);
        
        // 4. JIKA GAGAL: Gunakan CUSTOM MODAL (Merah)
        // Menggantikan alert() biasa
        await ui.alert(
            "Gagal Masuk", 
            error.message || "Periksa kembali NUPTK dan Password Anda.", 
            "error"
        );

    } finally {
        // 5. Reset Tombol
        btnLogin.textContent = originalText;
        btnLogin.disabled = false;
    }
}