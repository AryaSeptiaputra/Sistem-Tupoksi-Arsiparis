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
            // Upload file: biarkan browser atur Content-Type
            config.body = body;
        } else {
            // Data JSON biasa
            headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(body);
        }
    }

    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, config);
        
        // Cek jika response bukan JSON (misal HTML Error 404/500)
        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            throw new Error("Server Error: Respon bukan JSON (Mungkin URL salah atau Error 500)");
        }

        const result = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                console.warn("Sesi habis.");
            }
            throw new Error(result.message || result.error || 'Terjadi kesalahan pada server');
        }

        return result;
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        // Jangan alert setiap kali error agar tidak mengganggu UI, cukup throw
        throw error;
    }
}

// --- DAFTAR SERVICE ---

const api = {
    // 1. AUTH
    auth: {
        login: (nuptk, password) => fetchAPI('/auth/login', 'POST', { nuptk, password }),
        logout: () => localStorage.removeItem('access_token')
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

    // 6. DIPLOMA / IJAZAH (MENGGANTIKAN REPORT CARD)
    diploma: {
        // Create butuh FormData karena ada upload file scan ijazah
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