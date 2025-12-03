// static/js/outgoing_letter.js

let allLetters = [];
let classifications = [];

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Cek Login
    const token = localStorage.getItem("access_token");
    if (!token) { window.location.href = "/page/login"; return; }

    // 2. Setup Navigasi
    setupNavigation();

    // 3. Load Data
    await Promise.all([loadClassifications(), loadOutgoingLetters()]);

    // 4. Event Listeners Filter
    document.getElementById('searchInput').addEventListener('keyup', applyFilters);
    document.getElementById('startDate').addEventListener('change', applyFilters);
    document.getElementById('endDate').addEventListener('change', applyFilters);
    document.getElementById('classificationFilter').addEventListener('change', applyFilters);
    document.getElementById('btnResetFilter').addEventListener('click', resetFilters);

    // 5. Tombol Tambah
    document.getElementById('btnAddLetter').addEventListener('click', () => {
        alert("Fitur Tambah Surat Keluar akan segera hadir!");
    });
});

/* ---------- DATA LOADING ---------- */

async function loadClassifications() {
    const select = document.getElementById("classificationFilter");
    try {
        const data = await api.classification.getAll();
        classifications = data || [];
        classifications.forEach(cls => {
            const option = document.createElement("option");
            option.value = cls.id; 
            option.textContent = `${cls.code} - ${cls.name}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Gagal memuat klasifikasi:", error);
    }
}

async function loadOutgoingLetters() {
    const tableBody = document.getElementById("table-body");
    tableBody.innerHTML = `<tr><td colspan="6" class="loading-text">Sedang memuat data...</td></tr>`;

    try {
        // Panggil API outgoingLetter
        const data = await api.outgoingLetter.getAll();

        if (!data || data.length === 0) {
            allLetters = [];
            renderTable([]);
            return;
        }

        allLetters = data;
        
        // Urutkan berdasarkan tanggal surat (terbaru di atas)
        allLetters.sort((a, b) => new Date(b.letter_date) - new Date(a.letter_date));

        renderTable(allLetters);

    } catch (error) {
        console.error(error);
        tableBody.innerHTML = `<tr><td colspan="6" class="loading-text" style="color:red;">Gagal memuat data surat keluar.</td></tr>`;
    }
}

/* ---------- RENDERING ---------- */

function renderTable(data) {
    const tableBody = document.getElementById("table-body");
    tableBody.innerHTML = "";

    if (data.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="6" class="loading-text">Data tidak ditemukan.</td></tr>`;
        return;
    }

    data.forEach(item => {
        const row = document.createElement("tr");

        // Format Tanggal
        const options = { day: 'numeric', month: 'short', year: 'numeric' };
        const dateLetter = item.letter_date ? new Date(item.letter_date).toLocaleDateString('id-ID', options) : '-';

        // Handling path file
        // Menggunakan attachment_path sesuai schema DB yang umum, fallback ke file_path
        const filePath = item.attachment_path || item.file_path;
        const fileAction = filePath ? `viewFile('${filePath}')` : '';
        const fileIcon = filePath ? '📄' : '-';
        
        // Klasifikasi
        const classCode = item.classification ? item.classification.code : '-';
        
        // Penerima / Tujuan
        // Asumsi field di database adalah 'recipient' atau 'destination'
        // Jika di schema Anda masih menggunakan 'sender' untuk tujuan (jarang), sesuaikan di sini.
        const recipientDisplay = item.recipient || item.destination || item.tujuan || '-';

        row.innerHTML = `
            <td style="font-weight: 500; font-family: 'Courier New';">${item.number || '-'}</td>
            <td>${dateLetter}</td>
            <td style="font-weight: 500;">${recipientDisplay}</td>
            <td>${item.subject || '-'}</td>
            <td><span class="code-badge">${classCode}</span></td>
            <td style="text-align: center;">
                <div class="btn-action-group">
                    <button class="btn-action-view" onclick="${fileAction}" title="Lihat File" ${!filePath ? 'disabled' : ''}>${fileIcon}</button>
                    <button class="btn-action-view btn-edit" onclick="editLetter('${item.id}')">✏️</button>
                    <button class="btn-action-view btn-delete" onclick="deleteLetter('${item.id}')">🗑️</button>
                </div>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

/* ---------- FILTER LOGIC ---------- */

function applyFilters() {
    const searchVal = document.getElementById('searchInput').value.toLowerCase();
    const startDateVal = document.getElementById('startDate').value;
    const endDateVal = document.getElementById('endDate').value;
    const classVal = document.getElementById('classificationFilter').value;

    const filtered = allLetters.filter(item => {
        // Asumsi field penerima adalah 'recipient'
        const recipient = item.recipient || item.destination || "";
        
        // 1. Search (Nomor, Subjek, Penerima)
        const textMatch = (
            (item.number || "").toLowerCase().includes(searchVal) ||
            (item.subject || "").toLowerCase().includes(searchVal) ||
            recipient.toLowerCase().includes(searchVal)
        );

        // 2. Klasifikasi
        const classMatch = classVal === "" || (item.classification_id && String(item.classification_id) === String(classVal));

        // 3. Tanggal (Berdasarkan letter_date)
        let dateMatch = true;
        if (startDateVal && endDateVal) {
            const itemDate = new Date(item.letter_date);
            const start = new Date(startDateVal);
            const end = new Date(endDateVal);
            end.setHours(23, 59, 59);
            dateMatch = itemDate >= start && itemDate <= end;
        }

        return textMatch && classMatch && dateMatch;
    });

    renderTable(filtered);
}

function resetFilters() {
    document.getElementById('searchInput').value = "";
    document.getElementById('startDate').value = "";
    document.getElementById('endDate').value = "";
    document.getElementById('classificationFilter').value = "";
    renderTable(allLetters);
}

/* ---------- UTILS ---------- */

function setupNavigation() {
    document.querySelectorAll("[data-route]").forEach(el => {
        el.addEventListener("click", () => { if (el.dataset.route) window.location.href = el.dataset.route; });
    });
    document.getElementById("btn-logout").addEventListener("click", () => {
        localStorage.removeItem("access_token"); window.location.href = "/page/login";
    });
}

window.viewFile = function(path) { alert("Membuka file: " + path); };
window.editLetter = function(id) { console.log("Edit ID: " + id); };
window.deleteLetter = async function(id) {
    if (confirm("Hapus surat keluar ini?")) {
        try { 
            await api.outgoingLetter.delete(id); 
            allLetters = allLetters.filter(l => l.id != id);
            applyFilters();
            alert("Data berhasil dihapus");
        } catch (e) { alert("Gagal hapus: " + e.message); }
    }
};