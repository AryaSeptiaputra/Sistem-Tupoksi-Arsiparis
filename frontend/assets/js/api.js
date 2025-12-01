/**
 * KONFIGURASI API BACKEND
 * Pastikan port sesuai dengan 'main.py' (biasanya port 8000 atau 5000)
 */
const BASE_URL = "http://localhost:8000"; 

// --- HELPER FUNCTION (JANGAN DIUBAH) ---

/**
 * Fungsi utama untuk melakukan request ke Backend
 * @param {string} endpoint - Contoh: '/user/create'
 * @param {string} method - GET, POST, DELETE, dll
 * @param {object|FormData} body - Data yang dikirim (JSON object atau FormData untuk upload file)
 */
async function fetchAPI(endpoint, method = 'GET', body = null) {
    // 1. Ambil Token dari penyimpanan lokal (setelah login)
    const token = localStorage.getItem('access_token');

    // 2. Siapkan Headers
    const headers = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method: method,
        headers: headers
    };

    // 3. Cek tipe data body (JSON vs FormData)
    if (body) {
        if (body instanceof FormData) {
            // Jika upload file, jangan set Content-Type (biarkan browser mengaturnya otomatis)
            config.body = body;
        } else {
            // Jika data biasa, jadikan JSON
            headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(body);
        }
    }

    try {
        // 4. Tembak ke Server
        const response = await fetch(`${BASE_URL}${endpoint}`, config);
        const result = await response.json();

        // 5. Cek apakah sukses (Status 200-299)
        if (!response.ok) {
            // Jika token kadaluarsa (401), bisa redirect ke login (opsional)
            if (response.status === 401) {
                console.warn("Sesi habis, silakan login ulang.");
                // window.location.href = '/login.html'; 
            }
            throw new Error(result.message || result.error || 'Terjadi kesalahan pada server');
        }

        return result;
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        alert(error.message); // Tampilkan pesan error ke user
        throw error;
    }
}

// --- DAFTAR SERVICE (SESUAI FILE PYTHON KAMU) ---

const api = {
    // 1. AUTH (auth.py)
    auth: {
        login: (nuptk, password) => fetchAPI('/auth/login', 'POST', { nuptk, password }),
        logout: () => localStorage.removeItem('access_token') // Hapus token di client side
    },

    // 2. USER (user.py)
    user: {
        create: (data) => fetchAPI('/user/create', 'POST', data),
        update: (data) => fetchAPI('/user/update', 'POST', data),
        delete: (id) => fetchAPI('/user/delete', 'POST', { id }),
        getAll: () => fetchAPI('/user/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/user/get_by_keys', 'POST', { filters })
    },

    // 3. CLASSIFICATION (classification.py)
    classification: {
        create: (data) => fetchAPI('/classification/create', 'POST', data),
        update: (data) => fetchAPI('/classification/update', 'POST', data),
        delete: (id) => fetchAPI('/classification/delete', 'POST', { id }),
        getAll: () => fetchAPI('/classification/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/classification/get_by_keys', 'POST', { filters })
    },

    // 4. INCOMING LETTER / SURAT MASUK (incoming_letter.py)
    incomingLetter: {
        // PENTING: Gunakan FormData karena ada upload file
        create: (formData) => fetchAPI('/incoming_letter/create', 'POST', formData),
        update: (data) => fetchAPI('/incoming_letter/update', 'POST', data),
        delete: (id) => fetchAPI('/incoming_letter/delete', 'POST', { id }),
        getAll: () => fetchAPI('/incoming_letter/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/incoming_letter/get_by_keys', 'POST', { filters })
    },

    // 5. OUTGOING LETTER / SURAT KELUAR (outgoing_letter.py)
    outgoingLetter: {
        // PENTING: Gunakan FormData karena ada upload file
        create: (formData) => fetchAPI('/outgoing_letter/create', 'POST', formData),
        update: (data) => fetchAPI('/outgoing_letter/update', 'POST', data),
        delete: (id) => fetchAPI('/outgoing_letter/delete', 'POST', { id }),
        getAll: () => fetchAPI('/outgoing_letter/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/outgoing_letter/get_by_keys', 'POST', { filters })
    },

    // 6. REPORT CARD / RAPOT (report_card.py)
    reportCard: {
        // PENTING: Gunakan FormData karena ada upload file
        create: (formData) => fetchAPI('/report_card/create', 'POST', formData),
        update: (data) => fetchAPI('/report_card/update', 'POST', data),
        delete: (id) => fetchAPI('/report_card/delete', 'POST', { id }),
        getAll: () => fetchAPI('/report_card/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/report_card/get_by_keys', 'POST', { filters })
    },

    // 7. LOG ACTIVITY (log.py)
    log: {
        getAll: () => fetchAPI('/log/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/log/get_by_keys', 'POST', { filters })
    },

    // 8. BACKUP (backup.py)
    backup: {
        manual: () => fetchAPI('/backup/manual', 'POST'),
        getLogs: () => fetchAPI('/backup/logs', 'GET')
    }
};