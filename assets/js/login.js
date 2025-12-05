// login.js

// Tunggu sampai halaman selesai dimuat
document.addEventListener('DOMContentLoaded', () => {
    
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // 1. Mencegah halaman refresh otomatis
            await handleLogin(); // 2. Jalankan logika login
        });
    }
});

async function handleLogin() {
    const nuptkInput = document.getElementById('nuptk').value; 
    const passInput = document.getElementById('password').value;
    const btnLogin = document.querySelector('.btn-login');

    try {
        // UI: Loading state
        btnLogin.textContent = "Loading...";
        btnLogin.disabled = true;

        // Panggil fungsi API
        // api.js akan otomatis menyimpan token jika login berhasil
        const result = await api.auth.login(nuptkInput, passInput);
        
        // FIX: Hapus localStorage.setItem manual di sini karena sudah dilakukan di api.js
        
        // Cek sukses
        if (result && result.access_token) {
            alert(result.message || "Login Berhasil!"); 
            window.location.href = '/dashboard'; 
        } else {
            // Jika api tidak return error tapi token kosong (edge case)
            throw new Error("Gagal mendapatkan token akses.");
        }
        
    } catch (error) {
        console.error("Login Error:", error);
        // Tampilkan pesan error
        const errorMsg = error.message || "Gagal login. Periksa NUPTK dan Password.";
        alert(errorMsg);
    } finally {
        // UI: Reset state
        btnLogin.textContent = "Login";
        btnLogin.disabled = false;
    }
}