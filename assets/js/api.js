/**
 * api.js - Service Wrapper untuk komunikasi dengan Backend Flask
 */
const BASE_URL = "http://127.0.0.1:5000"; 

// --- HELPER FUNCTION (JANGAN DIUBAH) ---
async function fetchAPI(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('access_token');
    const headers = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method: method,
        headers: headers
    };

    if (body) {
        if (body instanceof FormData) {
            config.body = body;
        } else {
            headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(body);
        }
    }

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, config);
        
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            throw new Error("Server Error: Respon bukan JSON");
        }

        const result = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                console.warn("Sesi habis.");
                // Opsional: Redirect ke login jika token expired saat request
                // window.location.href = '/page/login'; 
            }
            throw new Error(result.message || result.error || 'Terjadi kesalahan pada server');
        }

        return result;
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
    }
}

// --- DAFTAR SERVICE ---

const api = {
    // 1. AUTH
    auth: {
        // UPDATE: Login kini async dan menyimpan token otomatis
        login: async (nuptk, password) => {
            const result = await fetchAPI('/auth/login', 'POST', { nuptk, password });
            if (result.access_token) {
                localStorage.setItem('access_token', result.access_token);
            }
            return result;
        },
        logout: () => {
            localStorage.removeItem('access_token');
            window.location.href = '/page/login'; // Redirect setelah logout
        },
        // BARU: Ambil data user dari token yang tersimpan
        getUserData: () => {
            const token = localStorage.getItem('access_token');
            if (!token) return null;
            try {
                const base64Url = token.split('.')[1];
                const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                }).join(''));
                return JSON.parse(jsonPayload);
            } catch (e) {
                console.error("Error parsing JWT:", e);
                return null;
            }
        }
    },

    // 2. USER
    user: {
        create: (data) => fetchAPI('/user/create', 'POST', data),
        update: (data) => fetchAPI('/user/update', 'POST', data),
        delete: (id) => fetchAPI('/user/delete', 'POST', { id }),
        getAll: () => fetchAPI('/user/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/user/get_by_keys', 'POST', { filters })
    },

    // 3. CLASSIFICATION
    classification: {
        create: (data) => fetchAPI('/classification/create', 'POST', data),
        update: (data) => fetchAPI('/classification/update', 'POST', data),
        delete: (id) => fetchAPI('/classification/delete', 'POST', { id }),
        getAll: () => fetchAPI('/classification/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/classification/get_by_keys', 'POST', { filters })
    },

    // 4. INCOMING LETTER
    incomingLetter: {
        create: (formData) => fetchAPI('/incoming_letter/create', 'POST', formData),
        update: (data) => fetchAPI('/incoming_letter/update', 'POST', data),
        delete: (id) => fetchAPI('/incoming_letter/delete', 'POST', { id }),
        getAll: () => fetchAPI('/incoming_letter/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/incoming_letter/get_by_keys', 'POST', { filters })
    },

    // 5. OUTGOING LETTER
    outgoingLetter: {
        create: (formData) => fetchAPI('/outgoing_letter/create', 'POST', formData),
        update: (data) => fetchAPI('/outgoing_letter/update', 'POST', data),
        delete: (id) => fetchAPI('/outgoing_letter/delete', 'POST', { id }),
        getAll: () => fetchAPI('/outgoing_letter/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/outgoing_letter/get_by_keys', 'POST', { filters })
    },

    // 6. DIPLOMA / IJAZAH
    diploma: {
        create: (formData) => fetchAPI('/diploma/create', 'POST', formData),
        update: (data) => fetchAPI('/diploma/update', 'POST', data),
        delete: (id) => fetchAPI('/diploma/delete', 'POST', { id }),
        getAll: () => fetchAPI('/diploma/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/diploma/get_by_keys', 'POST', { filters })
    },

    // 7. LOG ACTIVITY
    log: {
        getAll: () => fetchAPI('/log/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/log/get_by_keys', 'POST', { filters })
    },

    // 8. BACKUP
    backup: {
        manual: () => fetchAPI('/backup/manual', 'POST'),
        getLogs: () => fetchAPI('/backup/logs', 'GET')
    }
};

// ... (kode api.js sebelumnya) ...

// --- TAMBAHAN: UPDATE HEADER AVATAR GLOBAL ---
document.addEventListener("DOMContentLoaded", () => {
    // Cari elemen avatar di header
    const headerAvatar = document.getElementById("header-avatar");
    
    if (headerAvatar) {
        const user = api.auth.getUserData();
        if (user && user.username) {
            // Set inisial nama
            headerAvatar.textContent = user.username.charAt(0).toUpperCase();
            
            // Tambahkan link ke profil saat diklik
            headerAvatar.style.cursor = "pointer";
            headerAvatar.title = "Klik untuk lihat profil";
            headerAvatar.onclick = () => {
                window.location.href = "/page/user_profile";
            };
        }
    }
});