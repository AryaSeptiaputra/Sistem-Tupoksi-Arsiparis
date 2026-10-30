# Laporan Pengujian Fungsional Sistem Arsip Digital

Tanggal uji: 30 Oktober 2026
Versi aplikasi: branch `refactor/major-overhaul`, commit `a343805` (sebelum perbaikan apa pun)
Metode: pengujian black-box end-to-end dengan Selenium; operasi dijalankan lewat UI di Chrome, seperti yang dilakukan operator

## Ringkasan

Dari **180 skenario**, **146 lulus** dan **34 gagal** (81% lulus). Setiap kegagalan sudah diperiksa satu per satu. Semuanya bug aplikasi, bukan kesalahan test, dan penyebabnya dikelompokkan menjadi 10 temuan (T1–T10) di bawah. Satu run penuh memakan waktu sekitar 3,5 menit.

Fitur yang berjalan baik:
- Login, logout, dan perlindungan halaman.
- Navigasi 14 menu: tanpa error konsol dan tanpa request ke internet.
- Grafik dashboard.
- Semua fungsi Klasifikasi.
- Arsip Keuangan.
- Penyusutan arsip.
- Backup dan restore.
- Halaman Akun Saya.

Ada tiga masalah berat yang perlu diperbaiki sebelum aplikasi dipasang di klien:

1. **Surat Masuk dan Surat Keluar tidak bisa ditambah atau diedit**, begitu juga ijazah yang ditandai "sudah diambil". Semuanya gagal disimpan sejak database pindah ke SQLite (T1).
2. **Data bisa dibaca tanpa login.** Ini berlaku untuk data guru, surat, ijazah, arsip keuangan, dan arsip pegawai. Master Referensi bahkan bisa diubah tanpa login (T2).
3. **Teks yang diketik pengguna dijalankan sebagai HTML** di halaman daftar, sehingga terbuka celah XSS tersimpan (T3).

| Modul | Skenario | Lulus | Gagal | Temuan |
|---|---|---|---|---|
| Login & sesi | 22 | 21 | 1 | T2 |
| Hak akses API | 15 | 5 | 10 | T2 |
| Navigasi | 15 | 15 | 0 | - |
| Dashboard | 14 | 12 | 2 | T6 |
| Klasifikasi | 8 | 8 | 0 | - |
| Lokasi Simpan | 7 | 6 | 1 | T5 |
| Guru | 7 | 6 | 1 | T4 |
| Master Referensi | 7 | 5 | 2 | T7 |
| Surat Masuk | 16 | 12 | 4 | T1 |
| Surat Keluar | 8 | 6 | 2 | T1 |
| Data Ijazah | 11 | 8 | 3 | T1, T9, T10 |
| Arsip Keuangan | 8 | 8 | 0 | - |
| Arsip Pegawai | 10 | 9 | 1 | T9 |
| Penyusutan Arsip | 6 | 6 | 0 | - |
| Log Aktivitas | 6 | 5 | 1 | T8 |
| Backup Database | 5 | 4 | 1 | T9 |
| Input khusus | 6 | 1 | 5 | T3 |
| Akun Saya | 9 | 9 | 0 | - |
| **Total** | **180** | **146** | **34** | |

## Lingkungan uji

| Komponen | Versi / setelan |
|---|---|
| Sistem operasi penguji | Windows 11 |
| Browser | Chrome 156 headless, jendela 1366×768 (resolusi umum laptop Windows 7) |
| ChromeDriver / Selenium | 156.0.8078.76 / 4.27.1 |
| Server | `serve.py` (waitress, 4 thread) dengan Python 3.8.20, sama dengan target klien |
| Database | SQLite sementara, dibuat ulang setiap run |

**Isolasi.** Server uji berjalan dengan folder kerja sementara, sehingga:
- `.env` project tidak terbaca.
- Upload dan backup tersimpan di folder sementara.
- `database/arsip.db`, `storage/`, dan `database/backups/` milik project tidak berubah. Sudah dicek setelah run.

**Data awal (`e2e/seed.py`):**
- 35 referensi master.
- Satu akun operator sekali pakai; sandinya dibangkitkan acak dan tidak dicetak.
- 2 klasifikasi, 1 lokasi simpan, dan 2 guru.
- 10 surat, termasuk 1 surat tahun 2015 yang sudah lewat masa retensi.
- 2 arsip keuangan, 2 ijazah, dan 1 arsip pegawai.

Data surat dan arsip dimasukkan langsung ke database. Dengan begitu, uji edit, filter, hapus, dan dashboard tetap berjalan walaupun fitur tambah surat rusak.

**Cara uji.**
- Setiap skenario dijalankan lewat UI seperti operator: klik, isi form, lalu cek toast, modal, tabel, dan berkas.
- Data persiapan dibuat lewat API milik halaman.
- Seluruh suite dijalankan tiga kali penuh. Hasilnya sama persis setiap kali, tanpa skenario yang berubah status, jadi tidak ada test yang flaky.

**Pelengkap:**
- 50 test unit/API yang sudah ada (`pytest tests`) lulus di Python 3.8.
- Cek statis kompatibilitas Chrome 109 (lihat bagian tersendiri di bawah).

## Cara menjalankan ulang

Dari folder project:

```bash
.venv38\Scripts\python.exe -m pytest e2e -v
```

- Tabel hasil otomatis ditulis ke `e2e/hasil/hasil.md`.
- Screenshot setiap skenario yang gagal disimpan di `e2e/hasil/screenshot/`.
- Isi env `E2E_HEADED=1` untuk melihat browsernya.
- Di mesin ini, Selenium Manager membaca versi Chrome dari registry yang sudah usang (154, padahal yang terpasang 156) dan macet saat mengunduh driver. Karena itu ChromeDriver 156 diunduh manual dan ditunjuk lewat env:

```bash
set E2E_CHROMEDRIVER=%USERPROFILE%\.cache\selenium\chromedriver\win64\156.0.8078.76\chromedriver.exe
```

Kalau Chrome sudah diperbarui, ChromeDriver dengan versi yang sama perlu diunduh dari Chrome for Testing.

## Temuan

Temuan diurutkan dari yang paling berat. Setiap temuan berasal dari test yang gagal, lalu penyebabnya dicari di kode. Setiap temuan juga sudah dicatat sebagai issue GitHub (#22–#31), yang ditautkan di judulnya.

### T1 · Surat Masuk, Surat Keluar, dan ijazah "sudah diambil" gagal disimpan (Tinggi) · [#22](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/22)

**Test yang gagal:**
- Surat Masuk: tambah tanpa lampiran, tambah dengan PDF, dan edit.
- Surat Keluar: tambah dan edit.
- Ijazah: tambah dengan status sudah diambil.
- Uji nomor surat ganda juga terhalang bug ini.

**Hasil.** Setiap simpan memunculkan modal "Gagal Menyimpan: Gagal menyimpan data. Silakan periksa kembali data yang diisi." Log server mencatat `TypeError: SQLite DateTime type only accepts Python datetime and date objects as input`.

**Penyebab.** Tanggal dari form (misalnya `"2026-10-20"`) diteruskan apa adanya ke kolom `DateTime`:

| File | Baris | Jalur |
|---|---|---|
| `app/services/incoming_letter.py` | 29–30 | tambah |
| `app/services/incoming_letter.py` | 71 | edit |
| `app/services/outgoing_letter.py` | 28–29 | tambah |
| `app/services/outgoing_letter.py` | 69 | edit |
| `app/services/diploma.py` | 33 | tambah, `collected_at` |
| `app/services/diploma.py` | 77 | edit, `collected_at` |

MySQL dulu menerima tanggal berupa teks, sedangkan SQLite lewat SQLAlchemy tidak. Ini regresi dari migrasi #15. Test unit tidak menangkapnya karena semuanya mengirim objek `datetime`.

**Dampak.** Operator tidak bisa mencatat surat baru, padahal itu fungsi utama aplikasi.

**Usulan perbaikan:**
- Ubah teks tanggal menjadi `datetime` sebelum disimpan, misalnya `datetime.strptime(value, "%Y-%m-%d")`. Terapkan di jalur tambah dan edit.
- Tambah test API yang mengirim tanggal sebagai teks, seperti yang dikirim form.

### T2 · API data bisa diakses tanpa login (Tinggi) · [#23](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/23)

**Test yang gagal:**
- `Hak akses API`: 10 dari 15 endpoint menjawab permintaan tanpa token. Hasilnya 200, 201, atau 400, bukan 401.
- `Login & sesi`: skenario token rusak.

**Penyebab.** Endpoint berikut tidak memakai `@jwt_required()`:

| Data | Endpoint terbuka | Lokasi (baris) |
|---|---|---|
| Guru | `get_all`, `get_by_keys` | `app/routes/teacher.py:133, 154` |
| Klasifikasi | `get_all`, `get_by_keys` | `app/routes/classification.py:115, 136` |
| Surat Masuk | `get_all`, `get_by_keys` | `app/routes/incoming_letter.py:168, 188` |
| Surat Keluar | `get_all`, `get_by_keys` | `app/routes/outgoing_letter.py:209, 229` |
| Ijazah | `get_all`, `get_by_keys` | `app/routes/diploma.py:165, 185` |
| Arsip Keuangan | `get_all` | `app/routes/finance_archive.py:146` |
| Arsip Pegawai | `get_all` | `app/routes/employee_archive.py:138` |
| Master Referensi | Keempat endpoint, termasuk tambah, ubah, dan nonaktifkan | `app/routes/master_reference.py:12, 35, 58, 80` |

**Dampak.** Siapa pun di jaringan sekolah bisa:
- membaca NIP guru, isi surat, nominal keuangan, dan daftar arsip pegawai;
- mengubah daftar referensi tanpa login.

**Token rusak.** Ada dua masalah yang saling terkait:
- Dashboard tetap tampil berisi data, karena endpoint di atas terbuka.
- Untuk endpoint yang terlindungi, `flask_jwt_extended` membalas **422**, sementara `api.js:38` hanya mengenali 401. Akibatnya pesan "Sesi Berakhir" tidak pernah muncul dan halaman setengah kosong.

Token rusak terjadi misalnya setelah `JWT_SECRET_KEY` di server diganti.

**Usulan perbaikan:**
- Pasang `@jwt_required()` di endpoint-endpoint tersebut.
- Di `fetchAPI`, perlakukan 422 dari token yang tidak valid sama seperti 401.

### T3 · Teks dari pengguna dijalankan sebagai HTML / XSS tersimpan (Tinggi) · [#24](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/24)

**Test yang gagal.** Ada 5 dari 5 halaman yang diuji: Klasifikasi, Lokasi Simpan, Guru, Arsip Keuangan, dan Log Aktivitas. Nama `Nama <b>uji</b>` tampil sebagai kata **uji** bercetak tebal, bukan sebagai teks apa adanya.

Pembanding: kartu Aktivitas terakhir di Akun Saya sudah aman, karena memakai `textContent`.

**Penyebab.** Baris tabel disusun dengan template string lalu dimasukkan lewat `innerHTML`:

| File | Baris |
|---|---|
| `classification.js` | 144–166 |
| `storage_location.js` | 99–113 |
| `teacher.js` | 143–158 |
| `finance_archive.js` | 344–362 |
| `log.js` | 110–118 |

Halaman surat, ijazah, arsip pegawai, dan penyusutan memakai pola yang sama. Halaman-halaman itu tidak ikut diuji karena tambah surat rusak (T1).

**Dampak.** Uji ini sengaja hanya memakai tag `<b>`. Isian berisi `<img src=x onerror=...>` akan menjalankan script di browser operator, dan script itu bisa mengambil token login dari `localStorage`.

**Usulan perbaikan:**
- Escape teks sebelum disisipkan, misalnya dengan satu fungsi `escapeHtml` di `ui.js`.
- Atau isi sel dengan `textContent`, seperti di `user_profile.js`.

### T4 · Guru yang masih punya arsip bisa dihapus, dan arsipnya ikut terhapus (Sedang) · [#25](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/25)

**Test yang gagal.** Guru: hapus guru yang masih punya arsip pegawai.

**Penyebab:**
- Relasi `cascade="all, delete-orphan"` di `app/models/teacher.py:37`.
- `delete_teacher` (`app/services/teacher.py:87`) menghapus tanpa memeriksa arsip yang dimiliki.
- Dari kodenya, berkas lampiran arsip yang ikut terhapus tidak dibersihkan dari disk.

**Dampak.** Konfirmasi hapus hanya bertanya "Yakin ingin menghapus data ini?", jadi arsip pegawai hilang tanpa peringatan.

**Usulan perbaikan.** Tolak penghapusan selama guru masih punya arsip, seperti yang sudah dilakukan Klasifikasi. Arahkan operator mengubah status guru menjadi "Pensiun/Keluar"; saran ini sudah tertulis di panel info halaman Guru.

### T5 · Lokasi simpan yang masih dipakai bisa dihapus (Sedang) · [#26](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/26)

**Test yang gagal.** Lokasi Simpan: hapus lokasi yang masih dipakai arsip.

**Penyebab.** Saat lokasi dihapus (`app/services/storage_location.py:77`), SQLAlchemy mengosongkan `storage_location_id` di semua arsip yang memakai lokasi itu. Ini terjadi karena relasi backref tidak memakai `passive_deletes`.

**Dampak.** Arsip kehilangan informasi lokasi fisiknya tanpa peringatan. Pesan konfirmasi hanya meminta operator memastikan sendiri bahwa lemari itu kosong.

**Usulan perbaikan.** Hitung arsip yang memakai lokasi itu sebelum menghapus. Kalau masih ada, tolak dengan pesan yang jelas.

### T6 · Angka dashboard salah (Sedang) · [#27](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/27)

**Test yang gagal.** Dashboard: angka tab Data Guru dan total nominal keuangan.

**Jumlah guru PNS selalu 0.**
- `dashboard.js:106` dan `dashboard.js:235` membandingkan status kepegawaian dengan `'PNS'`.
- Padahal form Guru menyimpan nama referensinya, yaitu "Pegawai Negeri Sipil" (`teacher.js:87`).

**Total nominal keuangan selalu "Rp 0".**
- `dashboard.js:122` dan `dashboard.js:496` membaca `item.nominal`.
- API mengirim nominal dengan nama `amount`.

**Usulan perbaikan:**
- Simpan kode referensi (bukan nama) di form Guru. Alternatifnya, bandingkan dengan nama referensi.
- Ganti `nominal` menjadi `amount` di `dashboard.js`.

### T7 · Status Master Referensi tidak berpengaruh (Sedang) · [#28](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/28)

**Test yang gagal.** Master Referensi: referensi nonaktif masih muncul di dropdown, dan referensi baru berstatus Non-Aktif tersimpan sebagai Aktif.

**Penyebab:**
- `api.js:221` selalu meminta `?all=true`, termasuk dari form arsip.
- Fungsi tambah referensi memaksa `is_active=True` (`app/services/master_reference.py:63`).

**Dampak.** Konfirmasi "Data ini akan disembunyikan dari dropdown sistem" tidak terjadi.

**Usulan perbaikan:**
- Pakai `?all=true` hanya di halaman Master Referensi.
- Hormati nilai `is_active` dari form saat menambah referensi.

### T8 · Export CSV log terpotong pada karakter `#` (Rendah) · [#29](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/29)

**Test yang gagal.** Log Aktivitas: export CSV saat ada log yang memuat `#`.

**Hasil.** Berkas CSV berhenti tepat sebelum `#`, sehingga log berikutnya hilang dari berkas.

**Penyebab.** `log.js:179–190` membentuk data URI lalu menjalankan `encodeURI`. Karakter `#` tidak di-encode, sehingga browser membacanya sebagai fragmen URL.

**Usulan perbaikan:**
- Pakai `Blob` dan `URL.createObjectURL`, seperti unduh backup di `backup.js`.
- Bungkus kolom CSV dengan tanda kutip, alih-alih mengganti koma dengan spasi.

### T9 · Filter yang tidak berfungsi (Rendah) · [#30](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/30)

**Test yang gagal:**
- Arsip Pegawai: reset filter.
- Backup: filter status.
- Ijazah: pilihan tahun ajaran.

**Penyebab:**

| Masalah | Lokasi |
|---|---|
| Tombol Reset Arsip Pegawai diambil tetapi tidak diberi event | `employee_archive.js:22` |
| Dropdown Status dan Inisiator di halaman Backup tidak dipakai oleh `backup.js`, jadi tidak menyaring apa pun | `backup.html:147–156` |
| Pilihan filter Tahun ijazah ditulis tetap 2022/2023–2024/2025, sehingga data 2025/2026 tidak bisa disaring | `diploma.html:134–139` |

**Usulan perbaikan:**
- Pasang event pada tombol Reset Arsip Pegawai.
- Hubungkan dropdown Status dan Inisiator di halaman Backup, atau hapus.
- Isi tahun ajaran dari data, seperti `populateYearFilter` di `finance_archive.js:367`.

### T10 · Pesan validasi ijazah tanpa tahun ajaran (Rendah) · [#31](https://github.com/AryaSeptiaputra/Sistem-Tupoksi-Arsiparis/issues/31)

**Test yang gagal.** Ijazah: simpan tanpa tahun ajaran.

**Hasil.** Data memang ditolak, tetapi pesannya mentah dalam bahasa Inggris: "academic_year required".

**Penyebab:**
- Pesan tersebut berasal dari `app/routes/diploma.py:45–47`.
- Form tidak memeriksa tahun ajaran (`diploma.js:300`).

**Usulan perbaikan.** Tambahkan validasi tahun ajaran di form dengan pesan berbahasa Indonesia.

### Catatan tambahan

Catatan berikut tidak menggagalkan test:
- **Nama berkas backup.** Nama berkas memakai stempel waktu per detik (`app/services/backup.py:78`). Dua backup dalam detik yang sama menimpa berkas pertama, dan riwayatnya tercatat dua kali. Bagi operator peluangnya kecil, karena tombol dikunci selama proses.
- **Debug log.** `finance_archive.js` masih memuat 28 `console.log("[DEBUG] ...")`.

## Hasil per modul

Kolom "Catatan" berisi pesan kegagalan dari test.

### Login & sesi

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 1 | Login dengan username dan kata sandi yang benar. | Diarahkan ke dashboard, token tersimpan, dan sapaan memuat nama operator. | Lulus |  |
| 2 | Login dengan kata sandi yang salah. | Modal "Gagal Masuk" berisi pesan sandi salah, tetap di halaman login, tanpa token. | Lulus |  |
| 3 | Menekan tombol Login tanpa mengisi username dan kata sandi. | Form tidak terkirim (validasi isian wajib browser), tetap di halaman login. | Lulus |  |
| 4 | Membuka halaman aplikasi tanpa login. [Dashboard] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 5 | Membuka halaman aplikasi tanpa login. [Surat Masuk] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 6 | Membuka halaman aplikasi tanpa login. [Surat Keluar] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 7 | Membuka halaman aplikasi tanpa login. [Data Ijazah] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 8 | Membuka halaman aplikasi tanpa login. [Arsip Keuangan] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 9 | Membuka halaman aplikasi tanpa login. [Arsip Pegawai] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 10 | Membuka halaman aplikasi tanpa login. [Guru] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 11 | Membuka halaman aplikasi tanpa login. [Klasifikasi] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 12 | Membuka halaman aplikasi tanpa login. [Lokasi Simpan] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 13 | Membuka halaman aplikasi tanpa login. [Penyusutan] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 14 | Membuka halaman aplikasi tanpa login. [Log Aktivitas] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 15 | Membuka halaman aplikasi tanpa login. [Master Referensi] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 16 | Membuka halaman aplikasi tanpa login. [Backup] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 17 | Membuka halaman aplikasi tanpa login. [Akun Saya] | Diarahkan ke halaman login (boleh didahului pesan "Sesi Berakhir"). | Lulus |  |
| 18 | Membuka dashboard dengan token yang tidak valid. | Muncul modal "Sesi Berakhir", lalu diarahkan ke login dan token dihapus. | **Gagal** | T2: Modal 'Sesi Berakhir' tidak muncul |
| 19 | Menekan menu Keluar di sidebar, lalu membuka dashboard lagi. | Kembali ke halaman login, token dihapus, dan dashboard tidak bisa dibuka tanpa login ulang. | Lulus |  |
| 20 | Menekan ikon mata di kolom kata sandi halaman login dua kali. | Kata sandi tampil sebagai teks, lalu tersembunyi lagi. | Lulus |  |
| 21 | Membuka URL pendek tanpa awalan /page. [/] | Diarahkan ke halaman tujuan. | Lulus |  |
| 22 | Membuka URL pendek tanpa awalan /page. [/dashboard] | Diarahkan ke halaman tujuan. | Lulus |  |

### Hak akses API

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 23 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET guru] | Server menolak dengan status 401. | **Gagal** | T2: GET /teacher/get_all tanpa token dibalas 200, bukan 401 |
| 24 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET klasifikasi] | Server menolak dengan status 401. | **Gagal** | T2: GET /classification/get_all tanpa token dibalas 200, bukan 401 |
| 25 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET surat masuk] | Server menolak dengan status 401. | **Gagal** | T2: GET /incoming_letter/get_all tanpa token dibalas 200, bukan 401 |
| 26 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET surat keluar] | Server menolak dengan status 401. | **Gagal** | T2: GET /outgoing_letter/get_all tanpa token dibalas 200, bukan 401 |
| 27 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET ijazah] | Server menolak dengan status 401. | **Gagal** | T2: GET /diploma/get_all tanpa token dibalas 200, bukan 401 |
| 28 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET arsip keuangan] | Server menolak dengan status 401. | **Gagal** | T2: GET /finance_archive/get_all tanpa token dibalas 200, bukan 401 |
| 29 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET arsip pegawai] | Server menolak dengan status 401. | **Gagal** | T2: GET /employee_archive/get_all tanpa token dibalas 200, bukan 401 |
| 30 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET lokasi simpan] | Server menolak dengan status 401. | Lulus |  |
| 31 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET log] | Server menolak dengan status 401. | Lulus |  |
| 32 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET akun] | Server menolak dengan status 401. | Lulus |  |
| 33 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET referensi] | Server menolak dengan status 401. | **Gagal** | T2: GET /api/references/archive_status tanpa token dibalas 200, bukan 401 |
| 34 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [POST referensi] | Server menolak dengan status 401. | **Gagal** | T2: POST /api/references tanpa token dibalas 201, bukan 401 |
| 35 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [POST cari guru] | Server menolak dengan status 401. | **Gagal** | T2: POST /teacher/get_by_keys tanpa token dibalas 400, bukan 401 |
| 36 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET penyusutan] | Server menolak dengan status 401. | Lulus |  |
| 37 | Memanggil API data dari browser lain tanpa token login (tanpa header Authorization dan cookie). [GET riwayat backup] | Server menolak dengan status 401. | Lulus |  |

### Navigasi

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 38 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Dashboard] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 39 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Surat Masuk] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 40 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Surat Keluar] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 41 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Data Ijazah] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 42 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Arsip Keuangan] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 43 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Arsip Pegawai] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 44 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Guru] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 45 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Klasifikasi] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 46 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Lokasi Simpan] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 47 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Penyusutan Arsip] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 48 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Log Aktivitas] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 49 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Master Referensi] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 50 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Backup Database] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 51 | Membuka menu sidebar dari dashboard lalu menunggu halaman selesai memuat data. [Akun Saya] | URL dan judul halaman sesuai, menu yang aktif sesuai, tanpa error di konsol, dan tanpa request ke host di luar aplikasi. | Lulus |  |
| 52 | Menekan avatar inisial di kanan atas halaman Klasifikasi. | Avatar menampilkan huruf awal nama operator, lalu membuka halaman Akun Saya. | Lulus |  |

### Dashboard

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 53 | Membuka dashboard setelah login. | Sapaan memuat nama operator, kartu Total Guru Aktif dan Total Arsip Keuangan sesuai jumlah data. | Lulus |  |
| 54 | Membuka tab dashboard dan memeriksa grafiknya. [Ringkasan] | Setiap grafik di tab itu tergambar oleh Chart.js dan terlihat (lebar lebih dari 0). | Lulus |  |
| 55 | Membuka tab dashboard dan memeriksa grafiknya. [Surat Masuk] | Setiap grafik di tab itu tergambar oleh Chart.js dan terlihat (lebar lebih dari 0). | Lulus |  |
| 56 | Membuka tab dashboard dan memeriksa grafiknya. [Surat Keluar] | Setiap grafik di tab itu tergambar oleh Chart.js dan terlihat (lebar lebih dari 0). | Lulus |  |
| 57 | Membuka tab dashboard dan memeriksa grafiknya. [Keuangan] | Setiap grafik di tab itu tergambar oleh Chart.js dan terlihat (lebar lebih dari 0). | Lulus |  |
| 58 | Membuka tab dashboard dan memeriksa grafiknya. [Data Guru] | Setiap grafik di tab itu tergambar oleh Chart.js dan terlihat (lebar lebih dari 0). | Lulus |  |
| 59 | Membuka tab dashboard dan memeriksa grafiknya. [Data Ijazah] | Setiap grafik di tab itu tergambar oleh Chart.js dan terlihat (lebar lebih dari 0). | Lulus |  |
| 60 | Membuka tab dashboard dan memeriksa grafiknya. [Arsip Pegawai] | Setiap grafik di tab itu tergambar oleh Chart.js dan terlihat (lebar lebih dari 0). | Lulus |  |
| 61 | Membandingkan angka tab Surat Masuk dan Surat Keluar dengan data. | Total surat masuk, total surat keluar, dan jumlah surat menunggu/ditolak sama dengan data di API. | Lulus |  |
| 62 | Melihat widget surat keluar yang menunggu persetujuan, lalu menekannya. | Widget tampil dengan jumlah surat berstatus pending dan membuka halaman Surat Keluar. | Lulus |  |
| 63 | Membandingkan angka tab Data Guru dengan data guru aktif. | Total guru aktif, jumlah PNS, dan jumlah Non-ASN sesuai data (guru PNS disimpan form Guru sebagai "Pegawai Negeri Sipil"). | **Gagal** | T6: #tab-guru-pns menampilkan '0', seharusnya '1' |
| 64 | Membandingkan angka tab Data Ijazah dengan data ijazah. | Total, sudah diambil, dan belum diambil sesuai data. | Lulus |  |
| 65 | Membandingkan angka tab Arsip Pegawai dengan data. | Total arsip pegawai sama dengan jumlah data. | Lulus |  |
| 66 | Membandingkan total nominal di tab Keuangan dengan jumlah nominal arsip keuangan. | Jumlah arsip dan total nominal (format ringkas Rupiah, misalnya "Rp 1,5 jt") sesuai data. | **Gagal** | T6: #fin-nominal menampilkan 'Rp 0', seharusnya 'Rp 2,3 jt' |

### Klasifikasi

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 67 | Menambah klasifikasi dengan kode, nama, retensi, nasib akhir, dan deskripsi. | Toast "Data berhasil disimpan!" dan klasifikasi baru tampil di tabel. | Lulus |  |
| 68 | Mengetik kode dan nama di form tambah klasifikasi. | Pratinjau badge langsung menampilkan kode dan nama yang diketik. | Lulus |  |
| 69 | Menyimpan klasifikasi tanpa kode. | Modal "Data Belum Lengkap" dan data tidak tersimpan. | Lulus |  |
| 70 | Menambah klasifikasi dengan kode yang sudah dipakai klasifikasi lain. | Modal "Gagal Menyimpan" yang menyebut kode atau nama sudah ada. | Lulus |  |
| 71 | Mengubah nama klasifikasi lewat tombol Edit. | Toast "Data berhasil diperbarui!" dan tabel menampilkan nama baru. | Lulus |  |
| 72 | Mencari klasifikasi berdasarkan nama, lalu menekan Reset. | Hanya baris yang cocok yang tampil; setelah Reset semua baris tampil lagi. | Lulus |  |
| 73 | Menghapus klasifikasi yang belum dipakai arsip mana pun. | Muncul konfirmasi, lalu toast "Data dihapus" dan baris hilang dari tabel. | Lulus |  |
| 74 | Menghapus klasifikasi yang masih dipakai arsip keuangan. | Modal "Gagal Hapus" yang menyebut klasifikasi masih digunakan, dan baris tetap ada. | Lulus |  |

### Lokasi Simpan

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 75 | Menambah lokasi simpan dengan nama dan keterangan. | Toast "Berhasil disimpan!" dan lokasi baru tampil di tabel. | Lulus |  |
| 76 | Menyimpan lokasi tanpa nama. | Modal "Data Tidak Lengkap". | Lulus |  |
| 77 | Menambah lokasi dengan nama yang sudah ada. | Modal "Gagal Menyimpan" dan tidak ada baris ganda. | Lulus |  |
| 78 | Mengubah nama lokasi lewat tombol Edit. | Toast "Berhasil diperbarui!" dan tabel menampilkan nama baru. | Lulus |  |
| 79 | Mencari lokasi berdasarkan nama, lalu menekan Reset. | Hanya baris yang cocok yang tampil; setelah Reset semua baris tampil lagi. | Lulus |  |
| 80 | Menghapus lokasi yang belum dipakai arsip. | Toast "Lokasi dihapus" dan baris hilang dari tabel. | Lulus |  |
| 81 | Menghapus lokasi yang masih dipakai arsip keuangan. | Penghapusan ditolak (seperti klasifikasi yang masih dipakai) dan lokasi arsip tidak hilang. | **Gagal** | T5: Lokasi terhapus; lokasi arsip yang memakainya kini None |

### Guru

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 82 | Menambah guru dengan NIP, nama, jenis kelamin, pangkat, dan status kepegawaian. | Toast "Guru berhasil ditambahkan!" dan guru baru tampil di tabel dengan status Aktif. | Lulus |  |
| 83 | Menyimpan guru tanpa memilih jenis kelamin. | Modal "Data Belum Lengkap". | Lulus |  |
| 84 | Menambah guru dengan NIP yang sudah dipakai guru lain. | Modal "Gagal Menyimpan" dan tidak ada guru ganda. | Lulus |  |
| 85 | Mengubah nama guru lewat tombol Edit. | Kolom NIP terkunci, toast "Data guru berhasil diperbarui!", dan tabel menampilkan nama baru. | Lulus |  |
| 86 | Menyaring guru berdasarkan status kepegawaian "Guru Tidak Tetap". | Semua baris yang tampil berstatus Guru Tidak Tetap. | Lulus |  |
| 87 | Menghapus guru yang tidak punya arsip. | Toast "Data guru dihapus" dan baris hilang dari tabel. | Lulus |  |
| 88 | Menghapus guru yang masih memiliki arsip pegawai. | Penghapusan ditolak (seperti klasifikasi dan lokasi yang masih dipakai), dan arsip pegawainya tetap ada. | **Gagal** | T4: Guru terhapus beserta arsip pegawainya tanpa peringatan |

### Master Referensi

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 89 | Memilih kategori "Kategori Keuangan". | Tabel menampilkan referensi kategori itu, misalnya "BOS Reguler". | Lulus |  |
| 90 | Menambah referensi keuangan baru dengan mengetik namanya saja. | Kode terisi otomatis dari nama (huruf kecil, spasi menjadi garis bawah), toast "Data berhasil ditambahkan!", dan baris baru tampil. | Lulus |  |
| 91 | Menyimpan referensi tanpa nama dan kode. | Modal "Data Kurang". | Lulus |  |
| 92 | Menambah referensi dengan pilihan status Non-Aktif di form. | Referensi tersimpan dengan status Non-Aktif. | **Gagal** | T7: Referensi tersimpan sebagai Aktif |
| 93 | Mengubah nama referensi lewat tombol Edit. | Kolom kode terkunci, toast "Data berhasil diperbarui!", dan tabel menampilkan nama baru. | Lulus |  |
| 94 | Menonaktifkan referensi lewat tombol Non-aktifkan. | Konfirmasi, toast "Data dinonaktifkan", dan baris berlabel Non-Aktif. | Lulus |  |
| 95 | Menonaktifkan kategori keuangan, lalu membuka form tambah Arsip Keuangan. | Kategori yang nonaktif tidak muncul di dropdown Kategori (sesuai pesan "disembunyikan dari dropdown sistem"). | **Gagal** | T7: Kategori nonaktif masih muncul di dropdown form |

### Surat Masuk

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 96 | Menambah surat masuk lengkap tanpa lampiran. | Toast "Data berhasil disimpan!" dan surat tampil di tabel dengan tombol Lihat PDF nonaktif. | **Gagal** | T1: Muncul modal 'Gagal Menyimpan': Gagal menyimpan data. Silakan periksa kembali data yang diisi. |
| 97 | Menambah surat masuk dengan lampiran PDF. | Pratinjau berkas tampil sebelum disimpan, toast "Data berhasil disimpan!", dan lampiran bisa dibuka (HTTP 200). | **Gagal** | T1: Muncul modal 'Gagal Menyimpan': Gagal menyimpan data. Silakan periksa kembali data yang diisi. |
| 98 | Menyimpan surat masuk dengan satu isian wajib dikosongkan. [number] | Modal validasi yang menyebut isian tersebut, dan data tidak tersimpan. | Lulus |  |
| 99 | Menyimpan surat masuk dengan satu isian wajib dikosongkan. [sender] | Modal validasi yang menyebut isian tersebut, dan data tidak tersimpan. | Lulus |  |
| 100 | Menyimpan surat masuk dengan satu isian wajib dikosongkan. [letter_date] | Modal validasi yang menyebut isian tersebut, dan data tidak tersimpan. | Lulus |  |
| 101 | Menyimpan surat masuk dengan satu isian wajib dikosongkan. [received_date] | Modal validasi yang menyebut isian tersebut, dan data tidak tersimpan. | Lulus |  |
| 102 | Menyimpan surat masuk dengan satu isian wajib dikosongkan. [classification_id] | Modal validasi yang menyebut isian tersebut, dan data tidak tersimpan. | Lulus |  |
| 103 | Memilih berkas teks (.txt) sebagai lampiran surat masuk. | Modal "Format Salah" dan pilihan berkas dikosongkan. | Lulus |  |
| 104 | Membuka lampiran surat lama E2E/2015/001 lewat tombol Lihat PDF, lalu menutupnya. | Pratinjau layar penuh memuat berkas dari /storage (HTTP 200), dan tombol Tutup kembali ke tabel. | Lulus |  |
| 105 | Mengubah perihal surat E2E/MASUK/EDIT lewat tombol Edit. | Isian terisi data lama (termasuk tanggal), toast "Data berhasil diperbarui!", dan tabel menampilkan perihal baru. | **Gagal** | T1: Muncul modal 'Gagal Menyimpan': Gagal memperbarui data. Silakan periksa kembali data yang diisi. |
| 106 | Menambah surat masuk dengan nomor yang sudah terdaftar (E2E/MASUK/001). | Modal "Gagal Menyimpan" yang menyebut nomor surat sudah ada. | **Gagal** | T1: Pesan tidak menyebut nomor surat: Gagal menyimpan data. Silakan periksa kembali data yang diisi. |
| 107 | Mencari surat masuk dengan kata "Padjadjaran" (nama pengirim). | Hanya surat E2E/MASUK/002 yang tampil. | Lulus |  |
| 108 | Menyaring surat masuk dengan klasifikasi 000. | Semua baris berklasifikasi 000, termasuk E2E/MASUK/002, dan surat klasifikasi 421 tidak tampil. | Lulus |  |
| 109 | Menyaring surat masuk dengan status arsip Inaktif. | Hanya surat berstatus inaktif (E2E/2015/001) yang tampil. | Lulus |  |
| 110 | Menyaring surat masuk berdasarkan tanggal surat tahun 2015, lalu menekan Reset. | Hanya surat bertanggal 2015 yang tampil; setelah Reset muncul toast "Filter direset" dan semua surat tampil lagi. | Lulus |  |
| 111 | Menghapus surat E2E/MASUK/HAPUS. | Konfirmasi "Hapus Data?", toast "Data telah dihapus", dan baris hilang dari tabel. | Lulus |  |

### Surat Keluar

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 112 | Menambah surat keluar jenis SK yang sudah disetujui. | Toast "Data berhasil disimpan!" dan surat tampil di tabel dengan label SK dan status approved. | **Gagal** | T1: Muncul modal 'Gagal Menyimpan': Gagal menyimpan data. Silakan periksa kembali data yang diisi. |
| 113 | Menyimpan surat keluar tanpa tujuan. | Modal "Data Belum Lengkap". | Lulus |  |
| 114 | Menyimpan surat keluar tanpa tanggal surat dan tanggal kirim. | Ditolak dengan pesan yang menyebut tanggal wajib diisi. | Lulus |  |
| 115 | Melihat tombol Lihat PDF pada surat E2E/KELUAR/001 yang tidak punya lampiran. | Tombol Lihat PDF nonaktif. | Lulus |  |
| 116 | Menyaring surat keluar dengan status persetujuan "Disetujui". | Hanya surat yang disetujui (E2E/KELUAR/002) yang tampil. | Lulus |  |
| 117 | Mencari surat keluar dengan kata "Yayasan", lalu menekan Reset. | Hanya E2E/KELUAR/003 yang tampil; setelah Reset semua surat tampil lagi. | Lulus |  |
| 118 | Mengubah tujuan surat E2E/KELUAR/EDIT lewat tombol Edit. | Toast "Data berhasil diperbarui!" dan tabel menampilkan tujuan baru. | **Gagal** | T1: Muncul modal 'Gagal Menyimpan': Gagal memperbarui data. Silakan periksa kembali data yang diisi. |
| 119 | Menghapus surat E2E/KELUAR/HAPUS. | Konfirmasi "Hapus Surat?", toast "Data telah dihapus", dan baris hilang dari tabel. | Lulus |  |

### Data Ijazah

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 120 | Menambah data ijazah yang belum diambil siswa. | Toast "Data berhasil disimpan!" dan baris baru berstatus "Belum Diambil". | Lulus |  |
| 121 | Menambah ijazah dengan mencentang "Ijazah Sudah Diambil?". | Kolom tanggal pengambilan muncul terisi hari ini, toast "Data berhasil disimpan!", dan baris berstatus "Sudah Diambil". | **Gagal** | T1: Muncul modal 'Gagal Menyimpan': Gagal menyimpan data. Silakan periksa kembali data yang diisi. |
| 122 | Menyimpan ijazah tanpa memilih jurusan. | Modal "Data Belum Lengkap". | Lulus |  |
| 123 | Menyimpan ijazah tanpa tahun ajaran. | Ditolak dengan pesan yang menyebut tahun ajaran, dan data tidak tersimpan. | **Gagal** | T10: Pesan tidak menyebut tahun ajaran: academic_year required |
| 124 | Menambah ijazah dengan nomor seri yang sudah ada (DN-E2E-001). | Modal "Gagal Menyimpan" yang menyebut nomor sudah dipakai. | Lulus |  |
| 125 | Menambah ijazah dengan lampiran PDF, lalu membukanya. | Toast "Data berhasil disimpan!" dan lampiran bisa dibuka dari tombol Lihat File (HTTP 200). | Lulus |  |
| 126 | Menyaring ijazah dengan jurusan Farmasi. | Semua baris berjurusan Farmasi, termasuk Rina Lestari. | Lulus |  |
| 127 | Menyaring ijazah dengan status "Sudah Diambil". | Semua baris berstatus Sudah Diambil, termasuk Andi Pratama. | Lulus |  |
| 128 | Membuka pilihan filter Tahun saat ada ijazah tahun ajaran 2025/2026. | Tahun ajaran 2025/2026 tersedia di filter Tahun. | **Gagal** | T9: Pilihan filter tahun hanya ['Semua Tahun', '2024/2025', '2023/2024', '2022/2023'] |
| 129 | Mengubah nama siswa lewat tombol Edit. | Toast "Data berhasil diperbarui!" dan tabel menampilkan nama baru. | Lulus |  |
| 130 | Menghapus data ijazah. | Konfirmasi, toast "Data telah dihapus", dan baris hilang dari tabel. | Lulus |  |

### Arsip Keuangan

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 131 | Menambah arsip keuangan dengan judul, periode, kategori, nominal, dan klasifikasi. | Toast "Berhasil disimpan!" dan baris baru menampilkan nominal Rp 2.500.000. | Lulus |  |
| 132 | Menyimpan arsip keuangan tanpa nominal. | Modal "Data Belum Lengkap". | Lulus |  |
| 133 | Memilih berkas teks (.txt) sebagai lampiran arsip keuangan. | Modal "Format Salah". | Lulus |  |
| 134 | Menambah arsip keuangan dengan PDF, membukanya, lalu menghapus lampirannya lewat Edit. | Lampiran bisa dibuka (HTTP 200); setelah "Hapus File" dan simpan, tombol Lihat PDF nonaktif dan berkas lama tidak bisa diakses lagi (HTTP 404). | Lulus |  |
| 135 | Menyaring arsip keuangan dengan tahun 2025. | Hanya arsip tahun 2025 (Iuran Komite 2025) yang tampil. | Lulus |  |
| 136 | Menyaring arsip keuangan dengan kategori Komite / SPP Siswa. | Hanya arsip berkategori SPP yang tampil. | Lulus |  |
| 137 | Mengubah judul arsip keuangan lewat tombol Edit. | Pilihan Status Arsip muncul di mode edit, toast "Berhasil diperbarui!", dan tabel menampilkan judul baru. | Lulus |  |
| 138 | Menghapus arsip keuangan. | Konfirmasi, toast "Data telah dihapus", dan baris hilang dari tabel. | Lulus |  |

### Arsip Pegawai

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 139 | Menambah arsip pegawai milik Sari Wulandari. | Toast "Data disimpan" dan baris baru menampilkan nama dokumen dan pemiliknya. | Lulus |  |
| 140 | Menambah arsip pegawai tanpa memilih lokasi simpan (lokasi tidak wajib). | Toast "Data disimpan" dan baris baru tampil. | Lulus |  |
| 141 | Menyimpan arsip pegawai tanpa klasifikasi. | Modal "Data Belum Lengkap". | Lulus |  |
| 142 | Menyimpan arsip pegawai tanpa nama dokumen. | Ditolak dengan pesan validasi, dan tidak ada arsip tanpa nama yang tersimpan. | Lulus |  |
| 143 | Menyimpan arsip pegawai tanpa memilih pemilik (guru/pegawai). | Ditolak dengan pesan validasi yang menyebut pemilik, dan data tidak tersimpan. | Lulus |  |
| 144 | Menambah arsip pegawai dengan lampiran PDF, lalu membukanya. | Toast "Data disimpan" dan lampiran bisa dibuka dari tombol Lihat PDF (HTTP 200). | Lulus |  |
| 145 | Menyaring arsip pegawai milik Budi Santoso. | Semua baris milik Budi Santoso, termasuk "SK Pangkat Budi". | Lulus |  |
| 146 | Mengisi pencarian dan filter pegawai, lalu menekan Reset. | Kolom pencarian dan filter kosong lagi, dan semua arsip tampil. | **Gagal** | T9: Tombol Reset tidak mengosongkan filter |
| 147 | Mengubah nama dokumen lewat tombol Edit. | Toast "Data disimpan" dan tabel menampilkan nama baru. | Lulus |  |
| 148 | Menghapus arsip pegawai. | Konfirmasi, toast "Berhasil dihapus", dan baris hilang dari tabel. | Lulus |  |

### Penyusutan Arsip

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 149 | Membuka halaman Penyusutan saat ada surat masuk tahun 2015 berklasifikasi musnah (retensi 1+1 tahun). | Surat E2E/2015/001 tampil sebagai Surat Masuk dengan tahun kedaluwarsa 2017, dan penanda jumlah menyebut item kedaluwarsa. | Lulus |  |
| 150 | Mencentang lalu menghapus centang satu arsip kedaluwarsa. | Tombol Musnahkan aktif dengan jumlah "(1 Arsip)" saat dicentang, dan nonaktif lagi saat centang dihapus. | Lulus |  |
| 151 | Mencentang kotak "pilih semua" di kepala tabel. | Semua arsip tercentang dan tombol Musnahkan menyebut jumlah seluruh arsip. | Lulus |  |
| 152 | Menekan Musnahkan lalu mengetik "setuju" (huruf kecil) di kotak konfirmasi. | Toast "Konfirmasi salah. Pemusnahan dibatalkan." dan arsip tetap ada. | Lulus |  |
| 153 | Menekan Musnahkan lalu menekan Batal di kotak konfirmasi. | Modal tertutup dan arsip tetap ada di daftar. | Lulus |  |
| 154 | Memusnahkan surat E2E/2015/001 dengan mengetik "SETUJU". | Modal "Pemusnahan Berhasil" (1 arsip), arsip hilang dari daftar, statusnya "Musnah" di halaman Surat Masuk, dan lampirannya terhapus (HTTP 404). | Lulus |  |

### Log Aktivitas

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 155 | Menambah klasifikasi, lalu membuka Log Aktivitas. | Ada baris "Menambah Klasifikasi" dengan nama klasifikasi itu dan pelakunya nama operator. | Lulus |  |
| 156 | Mencari log dengan kata unik dari nama klasifikasi. | Hanya baris log yang memuat kata itu yang tampil. | Lulus |  |
| 157 | Menyaring log dengan pelaku Operator, lalu Sistem. | Filter Operator hanya menampilkan log akun operator; filter Sistem tidak menampilkan log akun operator. | Lulus |  |
| 158 | Menyaring log mulai besok, lalu menekan Reset. | Muncul "Tidak ada aktivitas tercatat."; setelah Reset muncul toast "Filter direset" dan semua log tampil lagi. | Lulus |  |
| 159 | Menekan Export CSV. | Toast "File CSV berhasil diunduh" dan berkas log_aktivitas_sistem.csv berisi header plus satu baris per log. | Lulus |  |
| 160 | Menambah klasifikasi bernama "Rak #2 ...", lalu menekan Export CSV. | CSV tetap memuat semua log, termasuk log klasifikasi bertanda # itu. | **Gagal** | T8: Isi CSV terpotong di tanda # |

### Backup Database

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 161 | Menekan "Backup Sekarang" dan mengonfirmasi. | Toast "Backup Berhasil Disimpan!", baris baru berisi nama berkas .db, dan berkasnya ada di folder backup server. | Lulus |  |
| 162 | Mencari riwayat backup dengan nama berkas, lalu dengan kata yang tidak ada. | Berkas yang dicari tampil; kata yang tidak ada menampilkan "Belum ada riwayat backup." | Lulus |  |
| 163 | Memilih filter Status "Failed (Gagal)" saat semua backup berhasil. | Backup yang berhasil tidak ditampilkan. | **Gagal** | T9: Filter status tidak menyaring riwayat backup |
| 164 | Menekan tombol unduh pada riwayat backup. | Toast "Mengunduh file..." dan berkas yang terunduh adalah database SQLite yang valid. | Lulus |  |
| 165 | Membuat backup, menambah klasifikasi, lalu me-restore backup tadi dengan dua kali konfirmasi. | Modal "Restore Sukses", klasifikasi yang dibuat setelah backup hilang, dan berkas pengaman pre_restore_*.db dibuat. | Lulus |  |

### Input khusus

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 166 | Menyimpan nama berisi teks "<b>uji</b>", lalu membuka halaman daftarnya. [Klasifikasi] | Tabel menampilkan teks "<b>uji</b>" apa adanya, bukan kata "uji" bercetak tebal. | **Gagal** | T3: Teks dari pengguna dirender sebagai HTML (tag <b> dijalankan) |
| 167 | Menyimpan nama berisi teks "<b>uji</b>", lalu membuka halaman daftarnya. [Lokasi Simpan] | Tabel menampilkan teks "<b>uji</b>" apa adanya, bukan kata "uji" bercetak tebal. | **Gagal** | T3: Teks dari pengguna dirender sebagai HTML (tag <b> dijalankan) |
| 168 | Menyimpan nama berisi teks "<b>uji</b>", lalu membuka halaman daftarnya. [Guru] | Tabel menampilkan teks "<b>uji</b>" apa adanya, bukan kata "uji" bercetak tebal. | **Gagal** | T3: Teks dari pengguna dirender sebagai HTML (tag <b> dijalankan) |
| 169 | Menyimpan nama berisi teks "<b>uji</b>", lalu membuka halaman daftarnya. [Arsip Keuangan] | Tabel menampilkan teks "<b>uji</b>" apa adanya, bukan kata "uji" bercetak tebal. | **Gagal** | T3: Teks dari pengguna dirender sebagai HTML (tag <b> dijalankan) |
| 170 | Menyimpan nama berisi teks "<b>uji</b>", lalu membuka halaman daftarnya. [Log Aktivitas] | Tabel menampilkan teks "<b>uji</b>" apa adanya, bukan kata "uji" bercetak tebal. | **Gagal** | T3: Teks dari pengguna dirender sebagai HTML (tag <b> dijalankan) |
| 171 | Menyimpan klasifikasi berisi "<b>uji</b>", lalu membuka Aktivitas terakhir di Akun Saya. | Aktivitas menampilkan teks "<b>uji</b>" apa adanya. | Lulus |  |

### Akun Saya

| No | Skenario | Hasil yang diharapkan | Status | Catatan |
|---|---|---|---|---|
| 172 | Membuka Akun Saya. | Banner menampilkan nama, @username, status Aktif, dan waktu login terakhir. | Lulus |  |
| 173 | Melihat kartu Aktivitas terakhir. | Tampil paling banyak 5 aktivitas, dan yang teratas adalah log terbaru. | Lulus |  |
| 174 | Mengubah nama tampilan, lalu menekan Batalkan. | Simpan dan Batalkan nonaktif sebelum ada perubahan, aktif setelah nama diubah, dan Batalkan mengembalikan nama semula. | Lulus |  |
| 175 | Mengosongkan nama tampilan. | Tombol Simpan nonaktif, Batalkan tetap aktif. | Lulus |  |
| 176 | Mengganti nama tampilan lalu menyimpan, kemudian mengembalikannya. | Toast "Informasi akun tersimpan" dan banner langsung menampilkan nama baru. | Lulus |  |
| 177 | Mengetik kata sandi baru yang lemah, lalu yang memenuhi syarat. | Checklist berubah langsung sesuai isian, dan tombol Ganti baru aktif setelah semua syarat terpenuhi dan sandi lama terisi. | Lulus |  |
| 178 | Menekan tombol mata pada kolom kata sandi baru dua kali. | Sandi tampil sebagai teks (aria-pressed true), lalu tersembunyi lagi; kolom lain tidak ikut berubah. | Lulus |  |
| 179 | Mengganti kata sandi dengan sandi lama yang salah. | Modal "Gagal mengganti" yang menyebut kata sandi lama salah, dan tetap login. | Lulus |  |
| 180 | Mengganti kata sandi dengan sandi lama yang benar, lalu login ulang. | Modal "Berhasil", diarahkan ke login, sandi lama ditolak, dan sandi baru diterima. | Lulus |  |

## Kompatibilitas Chrome 109 (cek statis)

Chrome 109 tidak bisa dijalankan di sini, karena Chrome for Testing baru tersedia mulai versi 113. Sebagai gantinya, `app/static/js`, `css`, dan `html` dicari untuk fitur yang baru ada setelah Chrome 109.

**JavaScript.** Tidak ditemukan fitur yang lebih baru dari Chrome 109. Yang dicari antara lain:
- `toSorted`, `toReversed`, `toSpliced`
- `Object.groupBy`, `Map.groupBy`
- `Promise.withResolvers`, `Array.fromAsync`
- method `Set` baru, `URL.canParse`, `AbortSignal.any`

**CSS dan HTML.** Satu-satunya temuan adalah `scrollbar-width: none` (didukung sejak Chrome 121) di empat tempat:
- `components.css:57`
- `layout.css:18`
- `pages.css:75`
- `pages.css:194`

Keempatnya sudah punya cadangan `::-webkit-scrollbar` yang berjalan di Chrome 109, jadi tampilannya tetap sama.

Yang juga dicari tetapi tidak ditemukan:
- nesting `&`, `color-mix(`, `text-wrap`, `light-dark(`
- `@starting-style`, `subgrid`, `@scope`
- atribut `popover`

**Pustaka.** Chart.js 4.5.0 dan boxicons disimpan lokal. Uji navigasi juga memastikan tidak ada request ke host luar.

## Keterbatasan

- Chrome 109 di Windows 7 tidak diuji langsung. Penggantinya hanya cek statis di atas. Uji di device klien tetap diperlukan.
- Hanya Chrome yang diuji. Edge dan Firefox tidak diuji.
- Beban dan kinerja tidak diuji. Aplikasi dirancang untuk satu operator.
- Uji input HTML (T3) tidak mencakup halaman surat, ijazah, arsip pegawai, dan penyusutan, karena tambah surat rusak (T1). Pola kodenya sama, jadi kemungkinan besar ikut terdampak.
- Data uji adalah data contoh, bukan data asli sekolah.
