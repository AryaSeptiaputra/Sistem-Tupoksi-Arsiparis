// assets/js/incoming.js
// Pastikan api.js sudah di-load lebih dulu

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('incoming-form');
    const tbody = document.getElementById('incoming-tbody');

    if (!form || !tbody) return; // bukan halaman surat masuk

    setupIncomingLetterPage(form, tbody);
});

function serializeFormToObject(form, excludeNames = []) {
    const data = {};
    const formData = new FormData(form);

    for (const [key, value] of formData.entries()) {
        if (excludeNames.includes(key)) continue;
        if (data[key] !== undefined) {
            if (!Array.isArray(data[key])) data[key] = [data[key]];
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }
    return data;
}

async function confirmDelete(callback) {
    if (confirm('Yakin ingin menghapus data ini?')) {
        await callback();
    }
}

function setupIncomingLetterPage(form, tbody) {
    loadIncomingLetters(tbody);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const idField = document.getElementById('incoming-id');
        const isEdit = idField && idField.value;

        try {
            if (isEdit) {
                const payload = serializeFormToObject(form, ['file', 'incoming-id']);
                payload.id = parseInt(idField.value, 10);
                await api.incomingLetter.update(payload);
                alert('Surat masuk berhasil diperbarui.');
            } else {
                const formData = new FormData(form);
                await api.incomingLetter.create(formData);
                alert('Surat masuk berhasil ditambahkan.');
            }

            form.reset();
            if (idField) idField.value = '';
            await loadIncomingLetters(tbody);
        } catch (err) {
            console.error(err);
            alert('Terjadi kesalahan saat menyimpan surat masuk.');
        }
    });

    tbody.addEventListener('click', async (e) => {
        const btn = e.target;

        if (btn.matches('.btn-delete-incoming')) {
            const id = btn.dataset.id;
            await confirmDelete(async () => {
                await api.incomingLetter.delete(parseInt(id, 10));
                alert('Surat masuk berhasil dihapus.');
                await loadIncomingLetters(tbody);
            });
        }

        if (btn.matches('.btn-edit-incoming')) {
            const id = btn.dataset.id;
            const all = await api.incomingLetter.getAll();
            const letter = all.find((l) => String(l.id) === String(id));
            if (!letter) return;

            document.getElementById('incoming-id').value = letter.id;
            form.number.value = letter.number || '';
            form.letter_date.value = letter.letter_date || '';
            form.received_date.value = letter.received_date || '';
            form.sender.value = letter.sender || '';
            form.subject.value = letter.subject || '';
            form.classification_id.value = letter.classification_id || '';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
}

async function loadIncomingLetters(tbody) {
    tbody.innerHTML = '<tr><td colspan="9">Loading...</td></tr>';

    try {
        const letters = await api.incomingLetter.getAll();

        if (!letters.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;">Belum ada data surat masuk.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        letters.forEach((l, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${l.number || '-'}</td>
                <td>${l.letter_date || '-'}</td>
                <td>${l.received_date || '-'}</td>
                <td>${l.sender || '-'}</td>
                <td>${l.subject || '-'}</td>
                <td>${l.classification_name || l.classification_id || '-'}</td>
                <td>${l.attachment_path ? `<a href="${l.attachment_path}" target="_blank">Lihat File</a>` : '-'}</td>
                <td>
                    <button type="button" class="btn-edit-incoming" data-id="${l.id}">Edit</button>
                    <button type="button" class="btn-delete-incoming" data-id="${l.id}">Hapus</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        tbody.innerHTML = '<tr><td colspan="9" style="color:red;">Gagal memuat data surat masuk.</td></tr>';
    }
}
