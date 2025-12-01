// assets/js/outgoing.js
// Pastikan api.js sudah di-load lebih dulu

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('outgoing-form');
    const tbody = document.getElementById('outgoing-tbody');

    if (!form || !tbody) return; // bukan halaman surat keluar

    setupOutgoingLetterPage(form, tbody);
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

function setupOutgoingLetterPage(form, tbody) {
    loadOutgoingLetters(tbody);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const idField = document.getElementById('outgoing-id');
        const isEdit = idField && idField.value;

        try {
            if (isEdit) {
                const payload = serializeFormToObject(form, ['file', 'outgoing-id']);
                payload.id = parseInt(idField.value, 10);

                if (payload.is_decree !== undefined) {
                    payload.is_decree = payload.is_decree === 'true' || payload.is_decree === true;
                }

                await api.outgoingLetter.update(payload);
                alert('Surat keluar berhasil diperbarui.');
            } else {
                const formData = new FormData(form);
                await api.outgoingLetter.create(formData);
                alert('Surat keluar berhasil ditambahkan.');
            }

            form.reset();
            if (idField) idField.value = '';
            await loadOutgoingLetters(tbody);
        } catch (err) {
            console.error(err);
            alert('Terjadi kesalahan saat menyimpan surat keluar.');
        }
    });

    tbody.addEventListener('click', async (e) => {
        const btn = e.target;

        if (btn.matches('.btn-delete-outgoing')) {
            const id = btn.dataset.id;
            await confirmDelete(async () => {
                await api.outgoingLetter.delete(parseInt(id, 10));
                alert('Surat keluar berhasil dihapus.');
                await loadOutgoingLetters(tbody);
            });
        }

        if (btn.matches('.btn-edit-outgoing')) {
            const id = btn.dataset.id;
            const all = await api.outgoingLetter.getAll();
            const letter = all.find((l) => String(l.id) === String(id));
            if (!letter) return;

            document.getElementById('outgoing-id').value = letter.id;
            form.number.value = letter.number || '';
            form.letter_date.value = letter.letter_date || '';
            form.sent_date.value = letter.sent_date || '';
            form.destination.value = letter.destination || '';
            if (form.is_decree) {
                if (form.is_decree.type === 'checkbox') {
                    form.is_decree.checked = !!letter.is_decree;
                } else {
                    form.is_decree.value = String(letter.is_decree);
                }
            }
            form.classification_id.value = letter.classification_id || '';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
}

async function loadOutgoingLetters(tbody) {
    tbody.innerHTML = '<tr><td colspan="9">Loading...</td></tr>';

    try {
        const letters = await api.outgoingLetter.getAll();

        if (!letters.length) {
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;">Belum ada data surat keluar.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        letters.forEach((l, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${l.number || '-'}</td>
                <td>${l.letter_date || '-'}</td>
                <td>${l.sent_date || '-'}</td>
                <td>${l.destination || '-'}</td>
                <td>${l.is_decree ? 'Ya' : 'Tidak'}</td>
                <td>${l.classification_name || l.classification_id || '-'}</td>
                <td>${l.attachment_path ? `<a href="${l.attachment_path}" target="_blank">Lihat File</a>` : '-'}</td>
                <td>
                    <button type="button" class="btn-edit-outgoing" data-id="${l.id}">Edit</button>
                    <button type="button" class="btn-delete-outgoing" data-id="${l.id}">Hapus</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        tbody.innerHTML = '<tr><td colspan="9" style="color:red;">Gagal memuat data surat keluar.</td></tr>';
    }
}
