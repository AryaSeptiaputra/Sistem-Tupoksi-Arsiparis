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
    // Pastikan ID ini sudah sama dengan di HTML (sekarang sudah 'nuptk')
    const nuptkInput = document.getElementById('nuptk').value; 
    const passInput = document.getElementById('password').value;
    const btnLogin = document.querySelector('.btn-login');

    try {
        // (Opsional) Ubah teks tombol biar user tahu sedang loading
        btnLogin.textContent = "Loading...";
        btnLogin.disabled = true;

        // Panggil fungsi API (Pastikan api.js strukturnya benar menerima ini)
        const result = await api.auth.login(nuptkInput, passInput);
        
        // Simpan token
        localStorage.setItem('access_token', result.access_token);
        
        // Feedback sukses
        alert(result.message); 
        
        // Redirect
        // Saran: Gunakan window.location.origin untuk path absolut jika perlu
        window.location.href = '/dashboard'; // Sesuaikan dengan route dashboard Flask Anda
        
    } catch (error) {
        console.error("Login Error:", error);
        // Tampilkan pesan error dari server jika ada, atau pesan default
        const errorMsg = error.message || "Gagal login. Periksa NUPTK dan Password.";
        alert(errorMsg);
    } finally {
        // Kembalikan tombol seperti semula
        btnLogin.textContent = "Login";
        btnLogin.disabled = false;
    }
}   