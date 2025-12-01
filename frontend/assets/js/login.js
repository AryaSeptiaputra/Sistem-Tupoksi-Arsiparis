// Pastikan sudah load <script src="assets/js/api.js"></script> di HTML

async function handleLogin() {
    const nuptkInput = document.getElementById('nuptk').value;
    const passInput = document.getElementById('password').value;

    try {
        const result = await api.auth.login(nuptkInput, passInput);
        
        localStorage.setItem('access_token', result.access_token);
        
        alert(result.message); // "Selamat Datang..."
        window.location.href = 'dashboard.html'; // Pindah halaman
    } catch (error) {
        console.log("Gagal login");
    }
}