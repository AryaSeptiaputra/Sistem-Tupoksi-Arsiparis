// assets/js/report_card.js
// Pastikan api.js sudah di-load lebih dulu

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('report-card-form');
    const tbody = document.getElementById('report-card-tbody');

    if (!form || !tbody) return; // bukan halaman raport

    setupReportCardPage(form, tbody);
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

function setupReportCardPage(form, tbody) {
    loadReportCards(tbody);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const idField = document.getElementById('report-card-id');
        const isEdit = idField && idField.value;

        try {
            if (isEdit) {
                const payload = serializeFormToObject(form, ['file', 'report-card-id']);
                payload.id = parseInt(idField.value, 10);
                await api.reportCard.update(payload);
                alert('Raport berhasil diperbarui.');
            } else {
                const formData = new FormData(form);
                await api.reportCard.create(formData);
                alert('Raport berhasil ditambahkan.');
            }

            form.reset();
            if (idField) idField.value = '';
            await loadReportCards(tbody);
        } catch (err) {
            console.error(err);
            alert('Terjadi kesalahan saat menyimpan raport.');
        }
    });

    tbody.addEventListener('click', async (e) => {
        const btn = e.target;

        if (btn.matches('.btn-delete-report')) {
            const id = btn.dataset.id;
            await confirmDelete(async () => {
                await api.reportCard.delete(parseInt(id, 10));
                alert('Raport berhasil dihapus.');
                await loadReportCards(tbody);
            });
        }

        if (btn.matches('.btn-edit-report')) {
            const id = btn.dataset.id;
            const all = await api.reportCard.getAll();
            const report = all.find((r) => String(r.id) === String(id));
            if (!report) return;

            document.getElementById('report-card-id').value = report.id;
            form.number.value = report.number || '';
            form.student_name.value = report.student_name || '';
            form.class_name.value = report.class_name || '';
            form.academic_year.value = report.academic_year || '';
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
}

async function loadReportCards(tbody) {
    tbody.innerHTML = '<tr><td colspan="7">Loading...</td></tr>';

    try {
        const reports = await api.reportCard.getAll();

        if (!reports.length) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Belum ada data raport.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        reports.forEach((r, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${r.number || '-'}</td>
                <td>${r.student_name || '-'}</td>
                <td>${r.class_name || '-'}</td>
                <td>${r.academic_year || '-'}</td>
                <td>${r.attachment_path ? `<a href="${r.attachment_path}" target="_blank">Lihat File</a>` : '-'}</td>
                <td>
                    <button type="button" class="btn-edit-report" data-id="${r.id}">Edit</button>
                    <button type="button" class="btn-delete-report" data-id="${r.id}">Hapus</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
        tbody.innerHTML = '<tr><td colspan="7" style="color:red;">Gagal memuat data raport.</td></tr>';
    }
}
