const ui = {
    // Inisialisasi HTML Modal ke dalam Body
    init: () => {
        if (document.getElementById('customModal')) return;

        const html = `
        <div id="customModal" class="custom-modal-overlay">
            <div class="custom-modal-box">
                <span id="modalIcon" class="modal-icon">⚠️</span>
                <h3 id="modalTitle" class="modal-title">Judul</h3>
                <div id="modalBody">
                    <p id="modalMessage" class="modal-message">Pesan...</p>
                    <div id="modalInputContainer" style="display:none; margin-top:10px;">
                        <input type="text" id="modalInput" style="width:100%; padding:10px; border:1px solid #d1d5db; border-radius:6px; font-family:inherit; outline:none;">
                    </div>
                </div>
                <div class="modal-actions" id="modalActions">
                </div>
            </div>
        </div>
        <div id="toastContainer" class="custom-toast-container"></div>
        `;
        document.body.insertAdjacentHTML('beforeend', html);
    },

    // 1. ALERT (Hanya tombol OK)
    alert: (title, message, type = 'info') => {
        ui.init();
        return new Promise((resolve) => {
            const modal = document.getElementById('customModal');
            const icon = document.getElementById('modalIcon');
            const actions = document.getElementById('modalActions');
            const inputContainer = document.getElementById('modalInputContainer');

            // Reset
            inputContainer.style.display = 'none';

            // Set Content (Gunakan innerHTML agar support <b> dan <br>)
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalMessage').innerHTML = message;
            
            // Set Icon
            if(type === 'success') icon.textContent = '✅';
            else if(type === 'error') icon.textContent = '❌';
            else if(type === 'warning') icon.textContent = '⚠️';
            else icon.textContent = 'ℹ️';

            // Set Button
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

    // 2. CONFIRM (Tombol Batal & Ya)
    confirm: (title, message, isDanger = false) => {
        ui.init();
        return new Promise((resolve) => {
            const modal = document.getElementById('customModal');
            const icon = document.getElementById('modalIcon');
            const actions = document.getElementById('modalActions');
            const inputContainer = document.getElementById('modalInputContainer');

            // Reset
            inputContainer.style.display = 'none';

            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalMessage').innerHTML = message;
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

    // 3. PROMPT (Input Text + Tombol) - [BARU DITAMBAHKAN]
    prompt: (title, message, placeholder = '') => {
        ui.init();
        return new Promise((resolve) => {
            const modal = document.getElementById('customModal');
            const icon = document.getElementById('modalIcon');
            const actions = document.getElementById('modalActions');
            const inputContainer = document.getElementById('modalInputContainer');
            const inputField = document.getElementById('modalInput');

            // Setup Content
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalMessage').innerHTML = message;
            icon.textContent = '📝';

            // Show Input
            inputContainer.style.display = 'block';
            inputField.value = '';
            inputField.placeholder = placeholder;

            actions.innerHTML = `
                <button class="btn-modal-cancel" id="btnModalCancel">Batal</button>
                <button class="btn-modal-confirm" id="btnModalSubmit">Kirim</button>
            `;

            modal.classList.add('active');
            inputField.focus();

            // Handle Submit
            document.getElementById('btnModalSubmit').onclick = () => {
                const val = inputField.value;
                modal.classList.remove('active');
                resolve(val); // Return string input
            };

            // Handle Cancel
            document.getElementById('btnModalCancel').onclick = () => {
                modal.classList.remove('active');
                resolve(null); // Return null jika batal
            };
            
            // Handle Enter Key di Input
            inputField.onkeyup = (e) => {
                if (e.key === 'Enter') {
                    document.getElementById('btnModalSubmit').click();
                }
            };
        });
    },

    // 4. TOAST NOTIFICATION
    toast: (message, type = 'success') => {
        ui.init();
        const container = document.getElementById('toastContainer');
        const el = document.createElement('div');
        el.className = `toast-box ${type}`;
        
        let icon = '✅';
        if(type === 'error') icon = '❌';
        if(type === 'warning') icon = '⚠️';
        if(type === 'info') icon = 'ℹ️';
        
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