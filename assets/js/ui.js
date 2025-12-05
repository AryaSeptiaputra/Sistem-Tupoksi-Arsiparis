const ui = {
    // Inisialisasi HTML Modal ke dalam Body
    init: () => {
        if (document.getElementById('customModal')) return;

        const html = `
        <div id="customModal" class="custom-modal-overlay">
            <div class="custom-modal-box">
                <span id="modalIcon" class="modal-icon">⚠️</span>
                <h3 id="modalTitle" class="modal-title">Judul</h3>
                <p id="modalMessage" class="modal-message">Pesan...</p>
                <div class="modal-actions" id="modalActions">
                    </div>
            </div>
        </div>
        <div id="toastContainer" class="custom-toast-container"></div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    },

    // 1. PENGGANTI ALERT
    alert: (title, message, type = 'info') => {
        ui.init();
        return new Promise((resolve) => {
            const modal = document.getElementById('customModal');
            const icon = document.getElementById('modalIcon');
            const actions = document.getElementById('modalActions');

            // Set Content
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalMessage').textContent = message;
            
            // Set Icon
            if(type === 'success') icon.textContent = '✅';
            else if(type === 'error') icon.textContent = '❌';
            else icon.textContent = 'ℹ️';

            // Set Button (Hanya OK)
            actions.innerHTML = `<button class="btn-modal-confirm" id="btnModalOk">Oke, Mengerti</button>`;

            // Show
            modal.classList.add('active');

            // Handle Click
            document.getElementById('btnModalOk').onclick = () => {
                modal.classList.remove('active');
                resolve(true);
            };
        });
    },

    // 2. PENGGANTI CONFIRM (Mengembalikan Promise true/false)
    confirm: (title, message, isDanger = false) => {
        ui.init();
        return new Promise((resolve) => {
            const modal = document.getElementById('customModal');
            const icon = document.getElementById('modalIcon');
            const actions = document.getElementById('modalActions');

            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalMessage').textContent = message;
            icon.textContent = '❓';

            const confirmBtnClass = isDanger ? 'btn-modal-confirm danger' : 'btn-modal-confirm';

            actions.innerHTML = `
                <button class="btn-modal-cancel" id="btnModalCancel">Batal</button>
                <button class="${confirmBtnClass}" id="btnModalYes">Ya, Lanjutkan</button>
            `;

            modal.classList.add('active');

            // Handle Yes
            document.getElementById('btnModalYes').onclick = () => {
                modal.classList.remove('active');
                resolve(true);
            };

            // Handle Cancel
            document.getElementById('btnModalCancel').onclick = () => {
                modal.classList.remove('active');
                resolve(false);
            };
        });
    },

    // 3. TOAST NOTIFICATION (Muncul sebentar lalu hilang)
    toast: (message, type = 'success') => {
        ui.init();
        const container = document.getElementById('toastContainer');
        const el = document.createElement('div');
        el.className = `toast-box ${type}`;
        
        let icon = '✅';
        if(type === 'error') icon = '❌';
        
        el.innerHTML = `
            <span style="font-size:20px;">${icon}</span>
            <span style="font-size:14px; font-weight:500; color:#374151;">${message}</span>
        `;

        container.appendChild(el);

        // Hapus otomatis setelah 3 detik
        setTimeout(() => {
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 300);
        }, 3000);
    }
};