# Keputusan Produk

Produk: Sistem Tupoksi Arsiparis SMKN 7 Bandung
Jenis: Aplikasi bisnis (web, Flask + MySQL)
Fase: Dev — refactor area 1: desain ulang basis data (rancangan 001); data uji evaluasi (rancangan 003)
Data: tingkat 0 — belum ada data arsip sama sekali. Database aplikasi `arsiparis_smk7` hanya berisi data pengembangan: 1 akun, 1 pegawai, 203 log, 35 master_reference, 1 klasifikasi, dan 0 baris di kelima tabel arsip serta storage_location (hasil baseline dan information_schema Arya, 2026-10-05). Data uji Dev-A: salinan D1 `tupoksi_d1` + seed deterministik buatan pink-chan (keputusan Arya, 2026-10-05; rincian di docs/rencana-evaluasi.md DS1–DS7). Mode data rahasia tidak aktif
Status: siap dikerjakan
Diperbarui: 2026-10-05

## Ringkasan
Sistem pencatatan dan penyusutan arsip sekolah (surat masuk, surat keluar, ijazah, keuangan, dokumen kepegawaian, dan arsip lain yang ber-JRA) yang dipakai oleh satu operator, yaitu arsiparis. Rancangan ini mengganti 12 tabel lama dengan satu tabel induk `archive` beserta tabel rincian per jenis arsip. Retensi dihitung dari tahun berkas dinyatakan selesai, dan penyusutan mengikuti alur usulan → persetujuan → berita acara sesuai aturan kearsipan pemerintah daerah provinsi. Data lama dipindah sekali jalan ke database baru lewat skrip ETL, sedangkan skema baru dikelola Alembic.

## Titik periksa
1. [Struktur] Bagaimana kelima jenis arsip disimpan?
   a. Satu tabel induk `archive` + lima tabel rincian per jenis (Usulan) ✓ 2026-10-04
   b. Lima tabel terpisah seperti sekarang, kolomnya dirapikan
   c. Satu tabel untuk semua jenis, atribut khusus di kolom JSON
2. [Referensi] Bagaimana daftar pilihan yang bisa diubah operator disimpan?
   a. Satu tabel kecil per kategori (6 tabel) yang dirujuk lewat FK (Usulan) ✓ 2026-10-04
   b. Satu tabel referensi umum + FK `reference_id`
3. [Data lama] Bagaimana data lama dipindahkan?
   a. Database baru + skrip ETL sekali jalan yang hanya membaca database lama (Usulan) ✓ 2026-10-04
   b. Migrasi di tempat lewat revisi Alembic
   c. Mulai dari database kosong
4. [Evaluasi] Apakah evaluasi dirancang dulu sebelum pink-chan membangun?
   a. Jalankan "red-chan, rancang evaluasi" setelah rancangan ini disetujui (Usulan) ✓ 2026-10-04
   b. Langsung bangun; verifikasi cukup memakai metrik D4
5. [Dasar retensi] Dari kapan masa retensi dihitung?
   a. Dari tahun berkas dinyatakan selesai (`closed_year`, boleh kosong = berkas masih terbuka) (Usulan) ✓ 2026-10-04
   b. Dari tahun dokumen (`archive_year`)
6. [Penyusutan] Bagaimana alur pemusnahan dicatat?
   a. Usulan → persetujuan → berita acara, dengan tabel `disposal` + `disposal_item` (Usulan) ✓ 2026-10-04
   b. Hanya berita acara
7. [Jenis arsip] Apakah arsip di luar lima jenis bisa dicatat?
   a. Tambah jenis `other` yang hanya memakai atribut bersama, tanpa tabel rincian (Usulan) ✓ 2026-10-04
   b. Tetap lima jenis
8. [Ijazah] Apa tindakan akhir sementara untuk ijazah sampai kode JRA resmi dikonfirmasi?
   a. Dinilai kembali (`assess`); tidak pernah masuk daftar musnah otomatis (Usulan) ✓ 2026-10-04
   b. Musnah setelah 5 tahun (perilaku aplikasi sekarang)
   c. Permanen

## Bentrokan
| Bentrokan | Cara rancangan menghindarinya |
|---|---|
| Restore backup menimpa isi database, termasuk riwayat backup kalau disimpan di tabel | Riwayat backup tetap di file `backup_logs.json`; tabel `backup` dihapus (K8) |
| MySQL melarang CHECK pada kolom yang dipakai referential action FK [S1] | CHECK hanya dipasang pada kolom non-FK. Aturan lintas tabel (arsip destroyed harus punya item di disposal executed) dijaga service + test (K4) |
| DDL MySQL melakukan implicit commit sehingga migrasi tidak bisa di-rollback [S2] | Data dipindah ke database baru; database lama tidak diubah (K7) |
| Retensi dihitung saat query, jadi perubahan JRA berlaku surut | Asumsi A7; masuk Belum pasti |
| Hapus pegawai dulu cascade, sekarang RESTRICT | Pegawai yang punya dokumen dinonaktifkan lewat `active_status_id` |
| Nomor surat keluar UNIQUE vs nomor ganda di data lama | ETL berhenti dan melaporkan nomor ganda |
| Satu pengguna vs jejak audit | `activity_log.user_id` boleh kosong (= proses sistem) |
| Skema baru vs kode service/route lama | Aplikasi tetap memakai database lama sampai cutover di rancangan back-end (D2) |
| Sekolah tidak berwenang memusnahkan sendiri arsip pemda provinsi ber-retensi ≥ 10 tahun [S11] | Pemusnahan hanya bisa dieksekusi setelah persetujuan tercatat (`approval_reference`). Siapa yang berwenang tidak dikunci di skema (Belum pasti) |
| JRA Pergub Jabar sudah ditemukan tetapi isinya tidak terbaca [S9, S10] | Skema tidak memuat angka retensi apa pun. Operator mengisi `classification` dari dokumen resmi; placeholder IJZ memakai `assess` (TP8) |
| Retensi dihitung dari berkas selesai, tetapi data lama tidak punya informasi kapan berkas selesai | ETL mengisi `closed_year` = tahun dokumen (perilaku lama tetap), kecuali ijazah belum diambil = kosong |
| (Diubah 2026-10-05) ETL dirancang untuk data lama, padahal database lama belum berisi arsip | ETL tetap dibangun dan dievaluasi di D1 + seed deterministik (Dev-A, docs/rencana-evaluasi.md DS1–DS7). Dijalankan atau tidaknya saat cutover bergantung pada ada tidaknya data nyata; kalau tidak ada, cutover ke database baru kosong + data master (diputuskan di rancangan back-end). Klasifikasi seed `DMY-*` bukan JRA dan tidak boleh terbawa ke cutover |
| Seed data uji dan ETL ditulis agent yang sama (keputusan Arya, 2026-10-05; menyimpang dari aturan tanpa konten tiruan agent di product-design) | Dev-A hanya bukti mekanik; label D3 tetap manual Arya; isi seed struktural berpenanda DUMMY; angka Dev-A tidak pernah dipakai sebagai angka final |

## Asumsi
- A1. Aplikasi hanya dipakai satu operator (arsiparis), tanpa role.
- A2. `approval_status` surat keluar dipertahankan sebagai catatan status tanda tangan, tanpa penyetuju.
- A3. Arsip pegawai tidak difilter per pemilik.
- A4. MySQL 8.0.16 atau lebih baru [S1].
- A5. (Diubah 2026-10-05) Database lama belum berisi data arsip; isinya hanya akun, pegawai, log, referensi, dan satu klasifikasi dari masa pengembangan. Kalau sebelum cutover ada data arsip nyata di aplikasi lama, data itu harus dipertahankan dan dipindahkan lewat ETL.
- A6. Retensi dihitung per tahun dari `closed_year` (tahun berkas dinyatakan selesai), lewat setelah 31 Desember. `closed_year` kosong berarti berkas masih terbuka dan tidak diproses [S12].
- A7. Perubahan masa retensi di JRA berlaku surut.
- A8. Nomor surat keluar unik; surat masuk unik per (pengirim, nomor).
- A9. Waktu disimpan sebagai waktu lokal WIB.
- A10. Akun admin lama memakai username = NIP/NUPTK lama.
- A11. SMKN 7 Bandung adalah satuan pendidikan di bawah Pemerintah Provinsi Jawa Barat (pengetahuan umum: urusan SMA/SMK ada di provinsi). Karena itu kode klasifikasi mengikuti Permendagri 83/2022 [S8], JRA mengikuti Pergub Jabar 38/2019 dan 75/2020 [S9, S10], dan pemusnahan mengikuti PP 28/2012 untuk pemda provinsi [S11]. JRA Kemendikbud dan Permendikdasmen 7/2026 tidak dipakai karena hanya berlaku untuk unit kementerian [S13, S14].
- A12. Nilai awal `closed_year` = tahun dokumen untuk semua jenis, kecuali ijazah: tahun diambil, atau kosong bila belum diambil. Operator boleh mengosongkan atau mengubahnya, misalnya untuk berkas pegawai yang masih aktif.

## Belum pasti
- Ada tidaknya data arsip nyata (di server sekolah atau di tempat lain) sebelum cutover; kalau ada, apakah boleh dibaca atau dikirim ke AI.
- Profil data nyata (jumlah arsip per jenis per tahun, jumlah pegawai, jumlah lampiran) untuk target kinerja di rancangan back-end, dan untuk menyesuaikan preset volume seed.
- Versi MySQL di server sekolah (`SELECT VERSION()`).
- Isi baris JRA yang berlaku untuk sekolah dari Pergub Jabar 38/2019 (substantif) dan 75/2020 (fasilitatif keuangan, kepegawaian, umum): masa aktif, masa inaktif, dan keterangan untuk ijazah, buku induk, SPJ/BOS, berkas pegawai, dan persuratan. Teks resminya tidak bisa dibaca saat riset.
- Kode klasifikasi Permendagri 83/2022 yang dipakai sekolah untuk tiap jenis arsip (menggantikan placeholder `IJZ` dan `TANPA-KLAS`).
- Kepada siapa sekolah mengajukan usul musnah (misalnya lembaga kearsipan daerah Provinsi Jawa Barat atau Dinas Pendidikan), dan format berita acaranya.
- Tindakan akhir resmi untuk ijazah dan buku induk (ada indikasi vital/permanen, tetapi belum terkonfirmasi).
- Dasar `closed_year` untuk surat: tahun surat, atau tahun urusan surat itu selesai.
- Ada tidaknya nomor surat keluar ganda di data lama.
- Hak user MySQL untuk membuat database baru.
- (2026-10-05) Perlakuan ETL untuk arsip lama berstatus destroyed yang masih punya `attachment_path`. Pola ini tidak dicakup B4 maupun pra-cek K7; CHECK `ck_archive_destroyed_file` membuat ETL gagal dengan error database (terlihat, bukan diam-diam). Diputuskan kalau data nyata ada.

## Ditunda
| Topik | Ditunda sampai |
|---|---|
| Penyesuaian service/route ke skema baru, keamanan T1–T4, optimisasi query | Rancangan back-end (area 3) |
| Framework front-end dan delapan domain UI/UX | Rancangan front-end (area 2) |
| Role dan hak akses | Kalau pengguna lebih dari satu |
| Klasifikasi keamanan dan hak akses arsip (biasa/terbatas/rahasia), penanda arsip vital [S14] | Kalau diminta atau ada lebih dari satu pengguna |
| Hirarki kode klasifikasi (induk–anak sesuai Permendagri 83/2022) | Kalau diminta |
| Atribut tata naskah dinas surat (sifat, derajat kecepatan, nomor agenda, disposisi) [S15] | Kalau diminta |
| Hirarki lokasi, lebih dari satu lampiran, peminjaman arsip | Kalau diminta |
| Berita acara pemindahan arsip inaktif dan penyerahan arsip statis | Kalau diminta |
| Pencarian teks penuh (FULLTEXT) | Rancangan back-end, kalau pencarian terbukti lambat |

---
<!-- Bagian teknis — dibaca pink-chan -->

## Gambaran sistem
| Bagian | Tugasnya | Terhubung ke |
|---|---|---|
| Skema baru (19 tabel) ★ | Menyimpan arsip, JRA, lokasi, pegawai, akun, log, usulan dan berita acara pemusnahan | Model ORM, Alembic |
| Model ORM SQLAlchemy ✎ | Memetakan 19 tabel; konstanta status; fungsi domain transisi status (arsip dan disposal) dan rumus retensi | Skema baru; dipakai service pada rancangan back-end |
| Alembic ★ | Satu-satunya cara mengubah skema baru; `create_all` saat startup dihapus | Database baru |
| Skrip ETL sekali jalan ★ | Membaca database lama, memetakan nilai, menulis ke database baru, menulis laporan verifikasi | Database lama → database baru |
| Scheduler retensi ✎ | Satu `UPDATE ... JOIN` harian untuk active → inactive berdasarkan `closed_year` (K5) | `archive`, `classification`, `activity_log` |
| Penyusutan ✎ | Kandidat dari rumus K5 → usulan → persetujuan → berita acara → arsip destroyed (K4) | `archive`, `disposal`, `disposal_item`, `activity_log` |
| Backup/restore (tidak berubah) | mysqldump database aktif; riwayat di `backup_logs.json` | Database baru setelah cutover |
| Seed data uji Dev-A ★ (rancangan 003; alat evaluasi, bukan bagian aplikasi) | Mengisi salinan D1 dengan arsip dummy deterministik + baris anomali B4 | D1 `tupoksi_d1`, folder lampiran D1; rincian di docs/rencana-evaluasi.md |

## Keputusan
| # | Keputusan | Rancangan | Alasan | Label |
|---|---|---|---|---|
| D1 | Pengguna | Satu operator (arsiparis) dengan kemampuan teknis awam; tanpa role | Jawaban Arya | — |
| D2 | Cakupan | Dikerjakan: skema baru, migrasi Alembic, skrip ETL, model ORM baru, fungsi domain transisi status dan rumus retensi beserta testnya. Tidak dikerjakan: service/route, keamanan, front-end. Aplikasi tetap memakai database lama sampai cutover | Arya memilih desain database lebih dulu | — |
| D3 | Sumber data | Database MySQL lama (12 tabel), dibaca sekali oleh ETL. Saat ini belum berisi arsip (hanya akun, pegawai, log, referensi pengembangan); data arsip nyata belum pasti. Untuk evaluasi Dev-A, salinan D1 diisi seed deterministik (rancangan 003). File lampiran tetap di `storage/`; isi JRA dimasukkan operator dari Pergub Jabar | Kondisi sekarang + A5, A11 | — |
| D4 | Tanda berhasil | (1) Jumlah baris per jenis arsip, pegawai, klasifikasi, dan lokasi sama dengan database lama. (2) Laporan ETL tidak berisi nilai status tetap yang gagal dipetakan. (3) Setelah scheduler baru dijalankan sekali, kandidat musnah dari K5 identik 100% dengan `/disposal/check` lama untuk semua jenis kecuali ijazah (ijazah sengaja 0 kandidat, TP8). (4) Akun admin lama bisa login dengan username = NIP lama. Diukur di D1 Dev-A (salinan DB aplikasi + seed; bukti mekanik) dan diulang di dump data nyata kalau ada (docs/rencana-evaluasi.md) | Bisa dicek dengan query dan satu kali login | — |
| K1 | Akun operator | `app_user` tanpa role dan tanpa relasi ke pegawai | A1 | Umum |
| K2 | Struktur arsip | Class Table Inheritance: `archive` + 5 tabel rincian + jenis `other` tanpa rincian (TP1, TP7) | Satu tempat untuk siklus hidup arsip; semua arsip ber-JRA bisa dicatat | Umum |
| K3 | Nilai pilihan | 6 tabel lookup per kategori; status yang menggerakkan logika dikunci dengan CHECK (TP2) | Integritas di level database | Umum |
| K4 | Siklus status dan penyusutan | State machine arsip 4 status + alur disposal proposed → approved → executed / rejected dengan `disposal_item` (TP6) [S7, S11] | Pemusnahan wajib disertai daftar usul musnah, persetujuan, dan berita acara | Umum |
| K5 | Rumus retensi | Per tahun dari `closed_year`, dihitung saat query; kosong = tidak diproses (TP5) [S12] | Retensi berjalan sejak berkas selesai; satu rumus untuk scheduler dan penyusutan | Umum |
| K6 | Physical | MySQL ≥ 8.0.16 InnoDB utf8mb4; VARCHAR + CHECK; DECIMAL untuk uang; naming convention; indeks sesuai pola query [S1, S3, S6] | Portabel dan konsisten untuk Alembic | Umum |
| K7 | Migrasi | Alembic untuk skema baru + skrip ETL sekali jalan (TP3) [S2, S4, S5] | Database lama utuh sebagai jalan kembali | Umum |
| K8 | Log dan backup | `activity_log` terstruktur, `user_id` boleh kosong; tabel `backup` dihapus | T5–T8; restore tidak menghapus riwayat backup | Umum |

## Desain UI/UX
Tidak dirancang di rancangan ini (cakupan D2). Kedelapan domain tidak berubah dan akan diputuskan di rancangan framework front-end:
| Domain | Keputusan | Ringkasan |
|---|---|---|
| Design System | — | Ditunda ke rancangan front-end |
| Design Tokens | — | Ditunda ke rancangan front-end |
| Typography System | — | Ditunda; sekarang Poppins |
| Color System | — | Ditunda ke rancangan front-end |
| Spacing & Layout System | — | Ditunda ke rancangan front-end |
| Component Design | — | Ditunda ke rancangan front-end |
| Visual Hierarchy | — | Ditunda ke rancangan front-end |
| Gestalt Principles | — | Ditunda ke rancangan front-end |

## Model data

### Conceptual
- Satu **Arsip** punya tepat satu jenis (surat masuk, surat keluar, ijazah, keuangan, dokumen pegawai, lainnya), satu **Klasifikasi** JRA, dan paling banyak satu **Lokasi Simpan**.
- Satu **Usulan Pemusnahan** memuat banyak Arsip. Satu Arsip bisa masuk beberapa usulan dari waktu ke waktu (misalnya usulan pertama ditolak), tetapi paling banyak satu usulan yang masih berjalan dan paling banyak satu usulan yang dieksekusi.
- Satu **Pegawai** memiliki banyak Dokumen Pegawai.
- Satu **Akun** melakukan banyak **Aktivitas** dan membuat banyak Usulan Pemusnahan.
- Daftar pilihan (jurusan, kategori dana, jenis dokumen, status kepegawaian, golongan, status aktif) dirujuk oleh Ijazah, Keuangan, Dokumen Pegawai, dan Pegawai.

### Logical
Aturan umum: semua tabel punya `created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP`; tabel yang bisa diubah juga punya `updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`. Primary key memakai surrogate integer. FK tanpa keterangan berperilaku RESTRICT. Target normalisasi 3NF.

| Entitas | Isi | Kunci | Relasi | Aturan integritas |
|---|---|---|---|---|
| `archive` | `archive_type` VARCHAR(20), `title` VARCHAR(255), `description` TEXT NULL, `archive_year` SMALLINT (tahun dokumen), `closed_year` SMALLINT NULL (tahun berkas selesai = dasar retensi), `status` VARCHAR(20) DEFAULT 'active', `development_level` VARCHAR(10) NULL, `attachment_path` VARCHAR(255) NULL, `status_changed_at` DATETIME NULL | PK `id` BIGINT | `classification_id` NOT NULL → classification; `storage_location_id` NULL → storage_location; 1:N disposal_item | `archive_type` IN ('incoming_letter','outgoing_letter','diploma','finance_record','employee_document','other'); `status` IN ('active','inactive','destroyed','permanent'); `development_level` IN ('asli','salinan','tembusan'); `archive_year` BETWEEN 1900 AND 2100; `closed_year` IS NULL OR (`closed_year` BETWEEN 1900 AND 2100 AND `closed_year` ≥ `archive_year`); status='destroyed' ⇒ attachment_path IS NULL; jenis `other` tidak punya baris rincian |
| `incoming_letter` | `letter_number` VARCHAR(100), `letter_date` DATE, `received_date` DATE, `sender` VARCHAR(150) | PK = FK `archive_id` → archive ON DELETE CASCADE | 1:1 archive | UNIQUE (`sender`, `letter_number`); `archive_year` = YEAR(`letter_date`) (dijaga service) |
| `outgoing_letter` | `letter_number` VARCHAR(100), `letter_date` DATE, `sent_date` DATE NULL, `destination` VARCHAR(150), `is_decree` BOOLEAN DEFAULT 0, `approval_status` VARCHAR(10) DEFAULT 'pending' | PK = FK `archive_id` CASCADE | 1:1 archive | UNIQUE `letter_number`; `approval_status` IN ('draft','pending','approved','rejected'); `archive_year` = YEAR(`letter_date`) |
| `diploma` | `diploma_number` VARCHAR(100), `student_name` VARCHAR(150), `collected_at` DATE NULL | PK = FK `archive_id` CASCADE | `school_major_id` NOT NULL → school_major | UNIQUE `diploma_number`; sudah diambil ⇔ `collected_at` IS NOT NULL; tahun ajaran = `archive_year`/`archive_year`+1; `archive.title` diisi service: "Ijazah <student_name>"; `closed_year` diisi service = YEAR(`collected_at`), atau kosong bila belum diambil |
| `finance_record` | `period_month` TINYINT NULL, `amount` DECIMAL(15,2) NULL | PK = FK `archive_id` CASCADE | `finance_category_id` NOT NULL → finance_category | `period_month` BETWEEN 1 AND 12; `amount` ≥ 0; tahun anggaran = `archive_year` |
| `employee_document` | (hanya FK) | PK = FK `archive_id` CASCADE | `employee_id` NOT NULL → employee (RESTRICT); `document_type_id` NOT NULL → document_type | tahun dokumen = `archive_year` |
| `classification` | `code` VARCHAR(30), `name` VARCHAR(150), `description` TEXT NULL, `retention_active_years` SMALLINT, `retention_inactive_years` SMALLINT, `final_action` VARCHAR(10), `legal_basis` VARCHAR(255) NULL, `is_active` BOOLEAN DEFAULT 1 | PK `id` INT | 1:N archive | UNIQUE `code` (format kode Permendagri 83/2022, mis. "400.3.10"); kedua retensi ≥ 0; `final_action` IN ('destroy','permanent','assess'); `legal_basis` = rujukan baris JRA (mis. "Pergub Jabar 75/2020, no. …"); tidak bisa dihapus selama dipakai |
| `storage_location` | `name` VARCHAR(100), `description` TEXT NULL, `is_active` BOOLEAN DEFAULT 1 | PK `id` INT | 1:N archive | UNIQUE `name`; tidak bisa dihapus selama dipakai |
| `disposal` | `proposal_number` VARCHAR(100), `proposal_date` DATE, `status` VARCHAR(10) DEFAULT 'proposed', `approval_reference` VARCHAR(150) NULL, `approval_date` DATE NULL, `approver` VARCHAR(150) NULL, `minutes_number` VARCHAR(100) NULL, `executed_date` DATE NULL, `notes` TEXT NULL, `proposal_file_path` VARCHAR(255) NULL, `minutes_file_path` VARCHAR(255) NULL | PK `id` INT | 1:N disposal_item; `created_by_user_id` NULL → app_user ON DELETE SET NULL | UNIQUE `proposal_number`; UNIQUE `minutes_number`; `status` IN ('proposed','approved','rejected','executed'); status IN ('approved','executed') ⇒ approval_reference, approval_date NOT NULL; status='executed' ⇒ minutes_number, executed_date NOT NULL; approval_date ≥ proposal_date; executed_date ≥ approval_date |
| `disposal_item` | (hanya FK) | PK (`disposal_id`, `archive_id`) | `disposal_id` → disposal ON DELETE CASCADE; `archive_id` → archive (RESTRICT) | Satu arsip paling banyak di satu disposal berstatus proposed/approved, dan paling banyak di satu disposal executed (service + test) |
| `employee` | `identity_number` VARCHAR(30), `full_name` VARCHAR(150), `gender` CHAR(1), `address` TEXT NULL | PK `id` INT | `employment_status_id` NOT NULL, `employee_rank_id` NULL, `active_status_id` NOT NULL → lookup; 1:N employee_document | UNIQUE `identity_number`; `gender` IN ('L','P'); data pribadi hanya di tabel ini dan tidak ditulis ke log |
| `app_user` | `username` VARCHAR(50), `password_hash` VARCHAR(255), `display_name` VARCHAR(100), `is_active` BOOLEAN DEFAULT 1, `last_login_at` DATETIME NULL | PK `id` INT | 1:N activity_log, 1:N disposal | UNIQUE `username`; login ditolak bila `is_active`=0 |
| `activity_log` | `action` VARCHAR(30), `entity_type` VARCHAR(30) NULL, `entity_id` BIGINT NULL, `summary` TEXT | PK `id` BIGINT | `user_id` NULL → app_user ON DELETE SET NULL (kosong = sistem) | `entity_id` tanpa FK; `summary` tanpa NIP, alamat, atau nama pegawai; hanya insert |
| Lookup ×6: `school_major`, `employment_status`, `employee_rank`, `employee_active_status`, `finance_category`, `document_type` | `code` VARCHAR(30), `name` VARCHAR(150), `sort_order` SMALLINT DEFAULT 0, `is_active` BOOLEAN DEFAULT 1 | PK `id` INT | 1:N ke tabel perujuk | UNIQUE `code`; hapus = `is_active`=0 |

**Tabel lama yang dihapus setelah cutover:** `user` → `app_user`, `teacher` → `employee`, `log` → `activity_log`, `backup` (dihapus), `master_reference` → 6 lookup + CHECK, `incoming_letter`/`outgoing_letter`/`diploma`/`finance_archive`/`employee_archive` → `archive` + rincian. Semuanya tetap ada di database lama.

**Transisi status `archive.status`:**
| Dari → Ke | Pemicu | Syarat |
|---|---|---|
| (baru) → active | Input arsip | — |
| active → inactive | Scheduler harian atau manual | Scheduler: `closed_year` terisi dan `closed_year + retention_active_years < YEAR(today)`; manual: kapan saja |
| inactive → active | Manual (dinilai kembali / masih dipakai) | Tidak sedang berada di disposal proposed/approved |
| inactive → destroyed | Hanya saat disposal-nya dieksekusi | Arsip ada di disposal yang berubah approved → executed |
| inactive → permanent | Manual (penetapan permanen) | `final_action` ∈ {permanent, assess} |
| destroyed, permanent | — | Status akhir |
Aturan tambahan: data arsip hanya bisa diedit saat status active atau inactive. Baris arsip hanya bisa dihapus fisik saat status active dan belum pernah masuk disposal. Status tidak boleh diubah lewat endpoint update umum.

**Transisi status `disposal.status`:**
| Dari → Ke | Syarat |
|---|---|
| (baru) → proposed | Semua item: arsip inactive, lewat masa inaktif (K5), `final_action` ∈ {destroy, assess}, tidak ada di disposal lain yang proposed/approved |
| proposed → approved | `approval_reference` dan `approval_date` diisi |
| proposed → rejected | — (item tetap tersimpan sebagai riwayat; arsip tetap inactive) |
| approved → executed | `minutes_number` dan `executed_date` diisi; dalam satu transaksi semua arsip item → destroyed, lalu file lampiran dihapus setelah commit |
| rejected, executed | Status akhir; tidak bisa diubah atau dihapus |
Item hanya bisa ditambah atau dihapus saat status proposed. Disposal hanya bisa dihapus saat proposed.

## Rincian engineering

### K1 · Single-operator account model
Pendekatan: `app_user` (id, username, password_hash, display_name, is_active, last_login_at, timestamps), tanpa role dan tanpa FK ke `employee`.
Parameter: Hash lama dipindah apa adanya (argon2 atas prehash SHA-256, `app/utils/hash.py`). Setiap `user` lama → `app_user` dengan id yang sama; `username` = `teacher.identity_number`; `display_name` = `teacher.full_name`; `is_active` = (status='active' AND role='admin').
Metrik: D4 butir 4.
Alternatif ditolak:
| Pendekatan | Ditolak karena |
|---|---|
| Role + relasi ke teacher | Pengguna hanya satu (A1) |
| Kredensial di variabel lingkungan | Sandi tidak bisa diganti dari aplikasi; tidak ada baris yang dirujuk log |

### K2 · Class Table Inheritance (supertype `archive` + subtype per jenis)
Pendekatan: Atribut bersama ada di `archive`; atribut khusus ada di 5 tabel rincian (PK = FK `archive_id`, ON DELETE CASCADE). Jenis `other` hanya memakai atribut bersama, untuk arsip tupoksi lain yang ber-JRA (buku induk, leger, SK kepala sekolah, inventaris, dan sejenisnya).
Parameter: Pemetaan `archive_year`: surat = YEAR(letter_date); ijazah = tahun awal tahun ajaran; keuangan = tahun anggaran; pegawai dan `other` = tahun dokumen (diisi operator). Klasifikasi wajib untuk semua jenis. Service menulis induk dan rincian dalam satu transaksi.
Placeholder klasifikasi dari ETL (is_active 0, tidak bisa dipilih untuk arsip baru):
  IJZ        "Ijazah (sementara — ganti dengan kode JRA resmi)"   aktif 5, inaktif 0, assess (TP8 a)
  TANPA-KLAS "Belum diklasifikasi"                                aktif 0, inaktif 0, assess
Metrik: D4 butir 1.
Alternatif ditolak:
| Pendekatan | Ditolak karena |
|---|---|
| Lima tabel terpisah | Logika ditulis lima kali (T12–T13) |
| Single table + JSON | Atribut khusus kehilangan constraint |
| Tabel rincian baru untuk setiap jenis arsip tupoksi | Belum ada atribut khusus yang diminta; `other` cukup sampai ada kebutuhan |

### K3 · Per-category lookup tables + fixed-domain CHECK
Pendekatan: 6 tabel lookup (code, name, sort_order, is_active), dirujuk lewat FK id. Status arsip, status disposal, tindakan akhir, status persetujuan, jenis arsip, gender, dan tingkat perkembangan memakai domain tetap dengan CHECK; labelnya diatur di aplikasi.
Parameter: school_major → `school_major`; teacher_emp_status → `employment_status`; teacher_rank → `employee_rank`; teacher_active_status → `employee_active_status`; finance_category → `finance_category`; emp_doc_type → `document_type`; archive_status, letter_approval_status, final_action → CHECK.
Metrik: tidak ada kolom string bebas yang menyimpan nilai referensi.
Alternatif ditolak:
| Pendekatan | Ditolak karena |
|---|---|
| Satu tabel referensi umum | Kategori FK tidak dijamin database |
| ENUM native | ALTER untuk nilai baru; tidak portabel |

### K4 · Lifecycle state machines + disposal proposal/approval/minutes
Pendekatan: Dua state machine (arsip dan disposal) mengikuti tabel transisi di atas. Pemusnahan mengikuti alur: daftar arsip usul musnah (`disposal` proposed + `disposal_item`) → persetujuan pihak berwenang (`approval_reference`, `approval_date`, `approver`) → pelaksanaan dengan berita acara (`minutes_number`, `executed_date`, scan opsional) [S7, S11]. Daftar arsip usul musnah = item disposal X, berisi nomor/judul, klasifikasi, `archive_year`, `development_level` [S7].
Parameter:
  Eksekusi = satu transaksi: disposal → executed; semua arsip item → destroyed, status_changed_at = NOW(), attachment_path = NULL; satu activity_log ('disposal_execute'). File dihapus setelah commit.
  CHECK di `disposal` (kolom non-FK): `ck_disposal_status`, `ck_disposal_approved_fields`, `ck_disposal_executed_fields`, `ck_disposal_dates` (lihat tabel Logical).
  CHECK di `archive`: `ck_archive_destroyed_file`: status <> 'destroyed' OR attachment_path IS NULL.
  Aturan lintas tabel (destroyed ⇔ ada item di disposal executed; paling banyak satu disposal terbuka per arsip) dijaga fungsi domain + test, karena CHECK MySQL tidak bisa merujuk tabel lain [S1].
  Arsip destroyed dari data lama → satu disposal executed: proposal_number = minutes_number = 'PRA-MIGRASI', approval_reference = 'TIDAK-TERCATAT', ketiga tanggal = tanggal ETL, notes = "Dimusnahkan sebelum migrasi; usulan, persetujuan, dan berita acara tidak tercatat di sistem".
  Ambang persetujuan PP 28/2012 (retensi ≥ 10 tahun butuh persetujuan Kepala ANRI untuk pemda provinsi [S11]) tidak dikunci di skema; pihak penyetuju dicatat sebagai teks di `approver`.
Metrik: test mencakup setiap pasangan transisi arsip dan disposal (sah diterima, tidak sah ditolak).
Alternatif ditolak:
| Pendekatan | Ditolak karena |
|---|---|
| Status bebas lewat update (sekarang) | Arsip bisa langsung destroyed tanpa jejak |
| Hanya berita acara, `archive.disposal_id` | Usulan dan persetujuan tidak tercatat; usulan yang ditolak hilang |
| Mengunci ambang 10 tahun di database | Pihak berwenang untuk sekolah belum pasti |

### K5 · Year-based retention from `closed_year`, computed at query time
Pendekatan: Retensi berjalan sejak tahun berkas dinyatakan selesai [S12]. `closed_year` kosong berarti berkas masih terbuka dan tidak diproses.
Rumus:
  y = YEAR(tanggal hari ini)
  jatuh_inaktif(a)  ⇔  a.closed_year IS NOT NULL ∧ a.closed_year + c.retention_active_years < y
  jatuh_akhir(a)    ⇔  a.closed_year IS NOT NULL ∧ a.closed_year + c.retention_active_years + c.retention_inactive_years < y
  kandidat_musnah   =  status='inactive' ∧ jatuh_akhir ∧ c.final_action='destroy' ∧ tidak di disposal proposed/approved
  perlu_dinilai     =  status='inactive' ∧ jatuh_akhir ∧ c.final_action='assess'
  kandidat_permanen =  status='inactive' ∧ jatuh_akhir ∧ c.final_action='permanent'
Scheduler (harian 00:01): `UPDATE archive a JOIN classification c ON c.id = a.classification_id SET a.status='inactive', a.status_changed_at=NOW() WHERE a.status='active' AND a.closed_year IS NOT NULL AND a.closed_year + c.retention_active_years < YEAR(CURDATE())`, lalu satu activity_log (user_id NULL, 'retention_run', jumlah baris).
Parameter: Nilai awal `closed_year` (A12): = archive_year untuk semua jenis; ijazah = YEAR(collected_at) atau kosong bila belum diambil. Operator boleh mengosongkan atau mengubahnya.
Kenapa: Kondisi `x + n < y` setara dengan "lewat 31 Desember tahun x + n" (sama dengan `/disposal/check` lama bila x = tahun dokumen).
Metrik: D4 butir 3.
Alternatif ditolak:
| Pendekatan | Ditolak karena |
|---|---|
| Dari `archive_year` | Berkas yang masih berjalan menjadi inaktif terlalu cepat |
| Menyimpan active_until/inactive_until | Butuh sinkronisasi saat JRA berubah |
| Per tanggal (relativedelta) | Tidak konsisten dengan penyusutan dan keuangan lama |

### K6 · Physical design (MySQL 8 InnoDB)
Pendekatan: InnoDB; `utf8mb4` / `utf8mb4_unicode_ci`; MySQL ≥ 8.0.16 [S1]. Domain tetap memakai `sqlalchemy.Enum(..., native_enum=False, create_constraint=True, length=n)` → VARCHAR + CHECK [S6]. Uang memakai `Numeric(15, 2)` [S6]. Tanggal bisnis DATE, jejak waktu DATETIME.
Naming convention di `MetaData` [S3]:
  ix: "ix_%(column_0_label)s"
  uq: "uq_%(table_name)s_%(column_0_name)s"
  ck: "ck_%(table_name)s_%(constraint_name)s"
  fk: "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
  pk: "pk_%(table_name)s"
Indeks (selain PK, UNIQUE, dan indeks FK otomatis InnoDB):
  archive (archive_type, created_at)    — daftar per jenis, terbaru dulu
  archive (status, closed_year)         — scheduler, kandidat penyusutan
  archive (archive_year)                — filter tahun dokumen
  disposal (status)                     — daftar usulan berjalan
  activity_log (created_at)             — log terbaru
  activity_log (entity_type, entity_id) — riwayat satu entitas
Aturan CHECK: hanya pada kolom non-FK [S1].
Path lampiran: relatif terhadap folder `storage/` (tanpa awalan "storage/"); unggahan baru memakai `documents/<archive_type>/<uuid>.<ext>`; scan usulan dan berita acara memakai `documents/disposal/<uuid>.<ext>`; path lama dipertahankan setelah awalan dibuang. Ini memperbaiki path upload dan hapus yang berbeda (`utils/file_helper.py:40` vs `:88`).
Metrik: `SHOW CREATE TABLE` memuat semua CHECK, UNIQUE, dan FK di tabel Logical.
Alternatif ditolak:
| Pendekatan | Ditolak karena |
|---|---|
| ENUM native | ALTER untuk nilai baru |
| BIGINT rupiah, DATETIME untuk tanggal surat | Bukan desimal; jam tidak bermakna |

### K7 · Alembic for new schema + one-off ETL cutover
Pendekatan: Database baru; revisi Alembic `0001_initial` membuat 19 tabel; `create_all` saat startup dihapus [S4]. Alembic dipakai langsung (aplikasi memakai SQLAlchemy murni, bukan Flask-SQLAlchemy); 1.17.1 sudah ada di requirements, rilis 2025-10-28, MIT [S5].
Skrip ETL sekali jalan [S4]:
  1. Pra-cek, berhenti bila gagal: versi MySQL ≥ 8.0.16; database baru kosong dan sudah di head; nomor surat keluar ganda; nilai archive_status/final_action/approval_status di luar domain; academic_year ijazah bukan `YYYY/YYYY`.
  2. Salin dengan id dipertahankan: classification (+ placeholder IJZ, TANPA-KLAS; `legal_basis` kosong), storage_location, 6 lookup dari master_reference, teacher → employee, user → app_user (K1).
  3. String → FK: cocokkan dengan `code` atau `name` (trim, tidak peka huruf besar/kecil); yang tidak cocok dibuat sebagai baris lookup baru dan dicatat. Gender: 'L'/'Laki-laki' → L, 'P'/'Perempuan' → P; nilai lain menghentikan ETL.
  4. Arsip: setiap baris 5 tabel lama → `archive` + rincian; pemetaan id lama → id baru dicatat. title: surat = subject (kosong → "(Tanpa perihal)"), keuangan = title, pegawai = document_name, ijazah = "Ijazah <student_name>". `closed_year` = archive_year, kecuali ijazah: YEAR(collected_at) bila diambil, kosong bila belum. collected_at = DATE(collected_at) bila is_collected; bila is_collected tetapi tanggal kosong → DATE(updated_at) dan dicatat. Ijazah memakai klasifikasi IJZ. Pegawai tanpa klasifikasi → TANPA-KLAS. Arsip destroyed → disposal 'PRA-MIGRASI' + item (K4). Tidak ada arsip `other` dari data lama.
  5. log → activity_log: user_id NULL, action 'legacy', summary = teks lama, created_at = timestamp lama.
  6. Lampiran: buang awalan "storage/"; file yang hilang dicatat.
  7. Laporan verifikasi: D4 butir 1–2, pemetaan, file hilang.
Cutover (di rancangan back-end): backup database lama → ETL → verifikasi D4 → ganti DATABASE_URL. Jalan kembali: DATABASE_URL lama [S2]. Kalau saat cutover database lama belum berisi data arsip nyata, cutover memakai database baru kosong + data master (keputusan di rancangan back-end). Baris seed Dev-A (penanda DUMMY, klasifikasi `DMY-*`) hanya ada di D1 dan tidak pernah ikut cutover.
Metrik: D4 butir 1–3; ETL ulang di database kosong memberi hasil yang sama.
Alternatif ditolak:
| Pendekatan | Ditolak karena |
|---|---|
| Revisi Alembic di tempat | DDL MySQL implicit commit [S2] |
| Mulai kosong | Arsip yang sudah tercatat hilang (kalau data nyata ada) |

### K8 · Structured activity log; drop backup table
Pendekatan: `activity_log` (user_id NULL = sistem, action, entity_type, entity_id, summary, created_at), hanya insert. Nilai action: login, create, update, delete, status_change, disposal_propose, disposal_approve, disposal_reject, disposal_execute, retention_run, backup, restore, legacy. Tabel `backup` dihapus; riwayat tetap di `database/backups/backup_logs.json`.
Metrik: user_id valid atau NULL (FK); tidak ada NIP atau alamat di summary (test).
Alternatif ditolak:
| Pendekatan | Ditolak karena |
|---|---|
| Log teks bebas + user_id NOT NULL (sekarang) | Proses sistem tidak bisa dicatat; pelaku salah (T5–T6) |
| Riwayat backup di tabel | Restore menimpa riwayatnya sendiri |

## Sumber
| # | Sumber | Tingkat | Tanggal | Dipakai untuk |
|---|---|---|---|---|
| S1 | MySQL 8.0 Reference Manual — CHECK Constraints, https://dev.mysql.com/doc/refman/8.0/en/create-table-check-constraints.html | 1 | dibaca 2026-10-04 | CHECK sejak 8.0.16; larangan CHECK pada kolom FK dengan referential action; CHECK tidak bisa merujuk tabel lain |
| S2 | MySQL 8.0 Reference Manual — Implicit Commit, https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html | 1 | dibaca 2026-10-04 | DDL tidak bisa di-rollback |
| S3 | Alembic docs — Naming Conventions, https://alembic.sqlalchemy.org/en/latest/naming.html | 1 | dibaca 2026-10-04 | Naming convention |
| S4 | Alembic docs — Cookbook, https://alembic.sqlalchemy.org/en/latest/cookbook.html | 1 | dibaca 2026-10-04 | create_all + stamp; migrasi data terpisah |
| S5 | Alembic changelog / PyPI, https://alembic.sqlalchemy.org/en/latest/changelog.html, https://pypi.org/project/alembic/ | 1 | 1.17.1 rilis 2025-10-28 | Usia rilis, lisensi |
| S6 | SQLAlchemy 2.0 — Type Basics, https://docs.sqlalchemy.org/en/20/core/type_basics.html | 1 | dibaca 2026-10-04 | Enum non-native + CHECK; Numeric |
| S7 | Perka ANRI No. 37 Tahun 2016 (Pedoman Penyusutan Arsip), https://peraturan.bpk.go.id/Download/298800/Perka_37_2016.pdf | 1 | 2016 | Tahap penyusutan; pemusnahan disertai daftar arsip usul musnah dan berita acara |
| S8 | Permendagri No. 83 Tahun 2022 — Kode Klasifikasi Arsip di Lingkungan Kemendagri dan Pemerintah Daerah, https://peraturan.bpk.go.id/Details/247841/permendagri-no-83-tahun-2022 | 1 | berlaku 2022-09-23 | Kode klasifikasi pemda (mis. 400.3 Pendidikan, menurut cuplikan pencarian); format `classification.code` |
| S9 | Pergub Jawa Barat No. 75 Tahun 2020 — JRA Fasilitatif Keuangan, Kepegawaian, dan Non Keuangan dan Kepegawaian, https://peraturan.bpk.go.id/Home/Details/173795/pergub-prov-jawa-barat-no-75-tahun-2020 | 1 | berlaku 2020-10-19 | JRA fasilitatif yang berlaku (isi PDF tidak terbaca) |
| S10 | Pergub Jawa Barat No. 38 Tahun 2019 — JRA Substantif Pemda Provinsi Jawa Barat, https://peraturan.bpk.go.id/Details/228374/pergub-prov-jawa-barat-no-38-tahun-2019 | 1 | 2019 | JRA substantif yang berlaku (isi tidak terbaca) |
| S11 | PP No. 28 Tahun 2012 — Pelaksanaan UU 43/2009 tentang Kearsipan, https://peraturan.go.id/files/pp28-2012bt.pdf | 1 | 2012 | Pemusnahan pemda provinsi retensi ≥ 10 tahun: ditetapkan gubernur setelah pertimbangan panitia penilai dan persetujuan Kepala ANRI (dari cuplikan pencarian; PDF tidak terbaca) |
| S12 | ANRI — pedoman retensi arsip sektor kesejahteraan rakyat urusan pendidikan dan kebudayaan (jdih.anri.go.id, cuplikan hasil pencarian) | 1 (cuplikan) | — | Retensi dihitung sejak kegiatan atau berkas dinyatakan selesai; belum dikonfirmasi teks lengkap |
| S13 | Permendikbud No. 45 Tahun 2016 — JRA Substantif dan Fasilitatif Kemendikbud, https://peraturan.bpk.go.id/Details/224352/permendikbud-no-45-tahun-2016 | 1 | dicabut Permendikbudristek 20/2022 | Hanya unit kementerian; tidak dipakai untuk SMK provinsi |
| S14 | Kemendikdasmen — Permendikdasmen No. 7 Tahun 2026 tentang Penyelenggaraan Kearsipan, https://www.kemendikdasmen.go.id/berita/14755-kemendikdasmen-tetapkan-permendikdasmen-nomor-7-tahun-2026-t | 1 | 2026-02-15 | Lingkup unit kerja kementerian; arsip vital, klasifikasi keamanan dan akses (masuk Ditunda) |
| S15 | Permendagri No. 1 Tahun 2023 — Tata Naskah Dinas di Lingkungan Pemerintah Daerah, https://peraturan.bpk.go.id/Details/245536/permendagri-no-1-tahun-2023 | 1 | berlaku 2023-02-15 | Atribut naskah dinas (masuk Ditunda) |

## Riwayat
| Tanggal | Perubahan | Alasan |
|---|---|---|
| 2026-10-04 | Usulan pertama rancangan 001 (desain ulang basis data) | Arya memilih area database lebih dulu; aplikasi dipakai satu orang |
| 2026-10-04 | TP1–TP4 dijawab Arya (semua a). Revisi setelah riset aturan kearsipan sekolah: `closed_year` sebagai dasar retensi; alur disposal usulan → persetujuan → berita acara dengan `disposal_item` (ganti `archive.disposal_id`); jenis `other`; `classification.code` VARCHAR(30) + `legal_basis`; placeholder IJZ dari destroy menjadi assess; D4 butir 3 mengecualikan ijazah; TP5–TP8 baru | Koreksi Arya: cek aturan tupoksi arsiparis SMK di Indonesia sebelum skema dikunci |
| 2026-10-04 | Rancangan 001 disetujui Arya; TP5–TP8 dijawab (semua a). Status → siap dikerjakan. Arsip: docs/rancangan/001a_2026-10-04_dev-desain-ulang-basis-data.md | Persetujuan Arya |
| 2026-10-04 | Koreksi status data setelah disetujui: baris Data (tingkat 3 produksi → tingkat 0 data asli, database lama berisi dummy, aman dibaca AI); A5 diubah; D3 dan D4 diberi keterangan dummy/nyata; satu bentrokan baru (ETL vs data dummy); dua butir Belum pasti baru; catatan cutover di K7. Struktur skema, keputusan K1–K8, dan pilihan titik periksa tidak berubah. Kepala file 001a (Data: tingkat 3) sudah usang; yang berlaku adalah dokumen ini | Informasi Arya: seluruh data di database saat ini adalah dummy |
| 2026-10-05 | Rancangan 003 disetujui (data uji Dev-A dari seed). Baris Data, A5, D3, D4 diperbarui: database lama belum berisi arsip; data uji Dev-A = D1 + seed deterministik. Bentrokan "ETL vs dummy" diubah; bentrokan baru seed dan ETL ditulis agent yang sama; Belum pasti: profil data untuk preset volume, ETL untuk arsip destroyed berlampiran; Gambaran sistem + baris seed; catatan K7 tentang baris seed. Skema, K1–K8, dan titik periksa 001 tidak berubah. Arsip: docs/rancangan/003a_2026-10-05_dev-rancang-evaluasi-data-seed.md | Hasil baseline dan information_schema Arya: database hampir kosong; keputusan Arya: data uji dibuat lewat script seed pink-chan |
