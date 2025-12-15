/**
 * api.js - Service Wrapper untuk komunikasi dengan Backend Flask
 */
// Kosongkan agar otomatis mengikuti domain tempat aplikasi dibuka
const BASE_URL = "";

// --- HELPER FUNCTION ---

async function fetchAPI(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('access_token');
    const headers = {};
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method: method,
        headers: headers,
        credentials: 'include'
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
        
        // --- BLOK PENANGANAN ERROR ---
        if (!response.ok) {
            // JIKA ERROR 401 (UNAUTHORIZED) - Sesi Habis
            if (response.status === 401 && endpoint !== '/auth/login') {
                console.warn("Sesi habis atau Token invalid.");
                localStorage.removeItem('access_token');

                // [UPDATE] Tampilkan Notifikasi sebelum redirect
                if (typeof ui !== 'undefined' && ui.alert) {
                    await ui.alert(
                        "Sesi Berakhir", 
                        "Masa berlaku login Anda telah habis.<br>Silakan login kembali untuk melanjutkan.", 
                        "warning"
                    );
                } else {
                    // Fallback jika ui.js belum terload
                    alert("Sesi Anda telah habis. Silakan login kembali.");
                }

                window.location.href = '/page/login'; 
                return; 
            }

            // Jika error lain (500, 404, atau 401 saat login)
            const result = await response.json().catch(() => ({}));
            throw new Error(result.message || result.error || `Server Error (${response.status})`);
        }
        // -----------------------------

        // Jika Sukses
        return await response.json();

    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
    }
}

// --- DAFTAR SERVICE ---

const api = {
    // 1. AUTH
    auth: {
        login: async (nuptk, password) => {
            const result = await fetchAPI('/auth/login', 'POST', { nuptk, password });
            
            if (result && result.access_token) {
                localStorage.setItem('access_token', result.access_token);
            }
            return result;
        },
        logout: () => {
            // Logout manual tidak perlu notifikasi "Sesi Habis", langsung redirect
            localStorage.removeItem('access_token');
            window.location.href = '/page/login'; 
        },
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

    teacher: {
        create: (data) => fetchAPI('/teacher/create', 'POST', data),
        update: (data) => fetchAPI('/teacher/update', 'POST', data),
        delete: (id) => fetchAPI('/teacher/delete', 'POST', { id }),
        getAll: () => fetchAPI('/teacher/get_all', 'GET'),
        getByKeys: (filters) => fetchAPI('/teacher/get_by_keys', 'POST', { filters })
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
        getLogs: () => fetchAPI('/backup/logs', 'GET'),
        restore: (filename) => fetchAPI('/backup/restore', 'POST', { filename })
    },

    // 9. STORAGE LOCATION
    storageLocation: {
        create: (data) => fetchAPI('/storage_location/create', 'POST', data),
        update: (data) => fetchAPI('/storage_location/update', 'POST', data),
        delete: (id) => fetchAPI('/storage_location/delete', 'POST', { id }),
        getAll: () => fetchAPI('/storage_location/get_all', 'GET')
    },

    financeArchive: {
        create: (formData) => fetchAPI('/finance_archive/create', 'POST', formData),
        update: (data) => fetchAPI('/finance_archive/update', 'POST', data),
        delete: (id) => fetchAPI('/finance_archive/delete', 'POST', { id }),
        getAll: () => fetchAPI('/finance_archive/get_all', 'GET')
    },

    employeeArchive: {
        create: (formData) => fetchAPI('/employee_archive/create', 'POST', formData),
        update: (data) => fetchAPI('/employee_archive/update', 'POST', data),
        delete: (id) => fetchAPI('/employee_archive/delete', 'POST', { id }),
        getAll: () => fetchAPI('/employee_archive/get_all', 'GET')
    },

    disposal: {
        check: () => fetchAPI('/disposal/check', 'GET'),
        execute: (items) => fetchAPI('/disposal/execute', 'POST', { items }) 
    },

    reference: {
        // [UPDATE] Tambahkan method CRUD lengkap
        getByCategory: (category) => fetchAPI(`/api/references/${category}?all=true`, 'GET'), // Tambah all=true agar admin bisa lihat yang non-aktif
        create: (data) => fetchAPI('/api/references', 'POST', data),
        update: (id, data) => fetchAPI(`/api/references/${id}`, 'PUT', data),
        delete: (id) => fetchAPI(`/api/references/${id}`, 'DELETE')
    }
};

// --- GLOBAL EVENT LISTENERS ---
document.addEventListener("DOMContentLoaded", () => {
    // 1. Setup Header Avatar
    const headerAvatar = document.getElementById("header-avatar");
    if (headerAvatar) {
        const user = api.auth.getUserData();
        if (user && user.username) {
            headerAvatar.textContent = user.username.charAt(0).toUpperCase();
            headerAvatar.style.cursor = "pointer";
            headerAvatar.title = "Klik untuk lihat profil";
            headerAvatar.onclick = () => {
                window.location.href = "/page/user_profile";
            };
        }
    }

    // 2. Setup Logout Button
    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault(); 
            api.auth.logout();
        });
    }
});