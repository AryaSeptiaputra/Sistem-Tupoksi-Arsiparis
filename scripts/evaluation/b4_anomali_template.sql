-- =====================================================================
-- USANG (rancangan 003a DS6, 2026-10-05) — JANGAN DIJALANKAN.
-- Baris anomali B4 sekarang dibuat oleh seed:
--   python -m scripts.evaluation.seed_d1 --skala penuh --anomali
-- File ini disimpan hanya sebagai riwayat. Penjaga di bawah langsung
-- menghentikan mysql dengan ERROR 1242 sebelum perintah lain dijalankan.
-- =====================================================================
SET @usang_003a_ds6 = (SELECT 1 FROM DUAL UNION ALL SELECT 2 FROM DUAL);

-- =====================================================================
-- Kerangka baris anomali B4 untuk salinan D1 (rencana evaluasi 002, TP6 / E6)
--
-- Kerangka ini dibuat agent. Nilai yang melanggar aturan diisi Arya di
-- BAGIAN 1 (placeholder <<ISI_ARYA>>), supaya detektor B4 diuji dengan kasus
-- yang tidak dirancang oleh penulis detektornya.
--
-- Dijalankan sekali, di salinan D1 saja, SEBELUM dump Dev-A diambil:
--   mysql -u root -p tupoksi_d1 < scripts\evaluation\b4_anomali_template.sql
-- Jangan memakai --force: client harus berhenti di error pertama, supaya
-- transaksi yang belum di-COMMIT dibatalkan saat koneksi ditutup.
--
-- Tidak boleh dijalankan dua kali. Penjaga G4 menghentikan jalan kedua.
-- Untuk mengulang dari awal, restore ulang dump dummy ke tupoksi_d1.
--
-- Script ini tidak mengubah atau menghapus baris dummy yang sudah ada; ia
-- hanya menambah baris baru. Setiap baris baru membawa penanda 'ANOMALI-'
-- di kolom teksnya (nomor, nama, judul, atau perihal), dan baris induk
-- pendukung membawa penanda 'ANOMALI-INDUK'.
-- =====================================================================


-- ---------------------------------------------------------------------
-- BAGIAN 1 · Diisi Arya
-- Ganti setiap '<<ISI_ARYA>>' dengan nilai yang MELANGGAR aturan di
-- komentarnya. Panjang maksimal mengikuti kolom skema lama; nilai yang lebih
-- panjang ditolak penjaga G3.
-- ---------------------------------------------------------------------

-- Nama database tujuan; script berhenti kalau dijalankan di database lain (G1)
SET @db_tujuan = 'tupoksi_d1';

-- B4-1 · Nomor surat keluar ganda (002a K7 pra-cek; 001a: UNIQUE letter_number)
-- Nomor yang dipakai dua baris surat keluar baru di bawah. Boleh nomor baru,
-- atau nomor surat keluar dummy yang sudah ada (maks 50 karakter).
SET @b4_1_nomor_surat_keluar = '<<ISI_ARYA>>';

-- B4-2a · archive_status di luar domain {active, inactive, destroyed, permanent}
-- Dipasang pada satu surat masuk baru (maks 20 karakter).
SET @b4_2_archive_status = '<<ISI_ARYA>>';

-- B4-2b · final_action di luar domain {destroy, permanent, assess}
-- Dipasang pada satu klasifikasi baru (maks 50 karakter).
SET @b4_2_final_action = '<<ISI_ARYA>>';

-- B4-2c · approval_status di luar domain {draft, pending, approved, rejected}
-- Dipasang pada satu surat keluar baru (maks 20 karakter).
SET @b4_2_approval_status = '<<ISI_ARYA>>';

-- B4-3 · academic_year ijazah yang bukan berformat YYYY/YYYY
-- Dipasang pada satu ijazah baru yang belum diambil (maks 9 karakter).
SET @b4_3_tahun_ajaran = '<<ISI_ARYA>>';

-- B4-4 · gender pegawai yang bukan L/Laki-laki atau P/Perempuan
-- Dipasang pada satu pegawai baru (maks 20 karakter).
SET @b4_4_gender = '<<ISI_ARYA>>';

-- B4-5 · string referensi yang tidak cocok dengan code maupun name master_reference
-- Dipasang sebagai kategori satu arsip keuangan baru (kategori finance_category, maks 50 karakter).
SET @b4_5_kategori_keuangan = '<<ISI_ARYA>>';

-- B4-6 (ijazah diambil tanpa tanggal) dan B4-7 (dokumen pegawai tanpa
-- klasifikasi) tidak butuh nilai: anomalinya adalah kolom yang kosong.


-- ---------------------------------------------------------------------
-- BAGIAN 2 · Penjaga (jangan diubah)
-- Pola: SET @cek = (SELECT 1 ... WHERE <syarat gagal> UNION ALL SELECT 2 ... WHERE <syarat gagal>);
-- Kalau syarat gagal terpenuhi, subquery mengembalikan dua baris dan MySQL
-- berhenti dengan "ERROR 1242 ... Subquery returns more than 1 row at line N".
-- Baca komentar penjaga di sekitar baris N untuk tahu penyebabnya.
-- ---------------------------------------------------------------------

-- Mode ketat hanya untuk sesi ini: nilai yang terlalu panjang atau NULL di kolom wajib menjadi error, bukan peringatan
SET SESSION sql_mode = 'STRICT_ALL_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- G1 · Database aktif bukan @db_tujuan
SET @cek = (SELECT 1 FROM DUAL WHERE DATABASE() IS NULL OR DATABASE() <> @db_tujuan
            UNION ALL SELECT 2 FROM DUAL WHERE DATABASE() IS NULL OR DATABASE() <> @db_tujuan);

-- G2 · Masih ada placeholder <<ISI_ARYA>> atau nilai NULL di BAGIAN 1
SET @cek = (SELECT 1 FROM DUAL WHERE '<<ISI_ARYA>>' IN (@b4_1_nomor_surat_keluar, @b4_2_archive_status,
                @b4_2_final_action, @b4_2_approval_status, @b4_3_tahun_ajaran, @b4_4_gender, @b4_5_kategori_keuangan)
              OR @b4_1_nomor_surat_keluar IS NULL OR @b4_2_archive_status IS NULL OR @b4_2_final_action IS NULL
              OR @b4_2_approval_status IS NULL OR @b4_3_tahun_ajaran IS NULL OR @b4_4_gender IS NULL
              OR @b4_5_kategori_keuangan IS NULL
            UNION ALL SELECT 2 FROM DUAL WHERE '<<ISI_ARYA>>' IN (@b4_1_nomor_surat_keluar, @b4_2_archive_status,
                @b4_2_final_action, @b4_2_approval_status, @b4_3_tahun_ajaran, @b4_4_gender, @b4_5_kategori_keuangan)
              OR @b4_1_nomor_surat_keluar IS NULL OR @b4_2_archive_status IS NULL OR @b4_2_final_action IS NULL
              OR @b4_2_approval_status IS NULL OR @b4_3_tahun_ajaran IS NULL OR @b4_4_gender IS NULL
              OR @b4_5_kategori_keuangan IS NULL);

-- G3 · Nilai lebih panjang dari kolom skema lama
SET @terlalu_panjang = CHAR_LENGTH(@b4_1_nomor_surat_keluar) > 50 OR CHAR_LENGTH(@b4_2_archive_status) > 20
    OR CHAR_LENGTH(@b4_2_final_action) > 50 OR CHAR_LENGTH(@b4_2_approval_status) > 20
    OR CHAR_LENGTH(@b4_3_tahun_ajaran) > 9 OR CHAR_LENGTH(@b4_4_gender) > 20 OR CHAR_LENGTH(@b4_5_kategori_keuangan) > 50;
SET @cek = (SELECT 1 FROM DUAL WHERE @terlalu_panjang UNION ALL SELECT 2 FROM DUAL WHERE @terlalu_panjang);

-- G4 · Script ini sudah pernah dijalankan (baris induk ANM-INDUK sudah ada)
SET @sudah_jalan = EXISTS (SELECT 1 FROM classification WHERE code = 'ANM-INDUK');
SET @cek = (SELECT 1 FROM DUAL WHERE @sudah_jalan UNION ALL SELECT 2 FROM DUAL WHERE @sudah_jalan);

-- Referensi sah dari master_reference dummy, supaya baris induk dan baris anomali
-- lain tidak ikut tertangkap sebagai B4-5
SET @ref_jurusan = (SELECT code FROM master_reference WHERE category = 'school_major' ORDER BY id LIMIT 1);
SET @ref_status_kepegawaian = (SELECT code FROM master_reference WHERE category = 'teacher_emp_status' ORDER BY id LIMIT 1);
SET @ref_status_aktif = (SELECT code FROM master_reference WHERE category = 'teacher_active_status' ORDER BY id LIMIT 1);
SET @ref_jenis_dokumen = (SELECT code FROM master_reference WHERE category = 'emp_doc_type' ORDER BY id LIMIT 1);

-- G5 · master_reference dummy tidak punya salah satu kategori di atas
SET @referensi_kurang = @ref_jurusan IS NULL OR @ref_status_kepegawaian IS NULL
    OR @ref_status_aktif IS NULL OR @ref_jenis_dokumen IS NULL;
SET @cek = (SELECT 1 FROM DUAL WHERE @referensi_kurang UNION ALL SELECT 2 FROM DUAL WHERE @referensi_kurang);


-- ---------------------------------------------------------------------
-- BAGIAN 3 · Baris anomali (satu transaksi)
-- Tanggal memakai hari ini dan klasifikasi induk ber-final_action 'permanent',
-- supaya baris anomali tidak masuk /disposal/check (B2) dan tidak diubah
-- scheduler lama (B3) pada tanggal_uji sekitar hari ini.
-- ---------------------------------------------------------------------

START TRANSACTION;

-- Induk · klasifikasi sah untuk baris arsip anomali
INSERT INTO classification (code, name, description, retention_active_period, retention_inactive_period, final_action)
VALUES ('ANM-INDUK', 'ANOMALI-INDUK klasifikasi',
        'Induk baris anomali B4; permanent supaya tidak masuk /disposal/check', 1, 1, 'permanent');
SET @kls_induk = LAST_INSERT_ID();

-- Induk · pegawai sah sebagai pemilik dokumen B4-7
INSERT INTO teacher (identity_number, full_name, gender, employment_status, `rank`, status, address)
VALUES ('ANOMALI-INDUK-PEGAWAI', 'ANOMALI-INDUK pegawai', 'L', @ref_status_kepegawaian, NULL, @ref_status_aktif, NULL);
SET @pegawai_induk = LAST_INSERT_ID();

-- B4-1 · dua surat keluar dengan nomor yang sama
INSERT INTO outgoing_letter (number, letter_date, sent_date, destination, subject, is_decree,
                             approval_status, classification_id, archive_status)
VALUES (@b4_1_nomor_surat_keluar, CURDATE(), CURDATE(), 'ANOMALI-B4-1', 'ANOMALI-B4-1 nomor ganda (1 dari 2)',
        0, 'pending', @kls_induk, 'active'),
       (@b4_1_nomor_surat_keluar, CURDATE(), CURDATE(), 'ANOMALI-B4-1', 'ANOMALI-B4-1 nomor ganda (2 dari 2)',
        0, 'pending', @kls_induk, 'active');

-- B4-2a · surat masuk dengan archive_status di luar domain
INSERT INTO incoming_letter (number, letter_date, received_date, sender, subject, classification_id, archive_status)
VALUES ('ANOMALI-B4-2A', CURDATE(), CURDATE(), 'ANOMALI-B4-2A', 'ANOMALI-B4-2A archive_status di luar domain',
        @kls_induk, @b4_2_archive_status);

-- B4-2b · klasifikasi dengan final_action di luar domain
INSERT INTO classification (code, name, description, retention_active_period, retention_inactive_period, final_action)
VALUES ('ANM-B4-2B', 'ANOMALI-B4-2B final_action', 'Baris anomali B4-2b', 1, 1, @b4_2_final_action);

-- B4-2c · surat keluar dengan approval_status di luar domain
INSERT INTO outgoing_letter (number, letter_date, sent_date, destination, subject, is_decree,
                             approval_status, classification_id, archive_status)
VALUES ('ANOMALI-B4-2C', CURDATE(), CURDATE(), 'ANOMALI-B4-2C', 'ANOMALI-B4-2C approval_status di luar domain',
        0, @b4_2_approval_status, @kls_induk, 'active');

-- B4-3 · ijazah dengan academic_year tidak berformat (belum diambil)
INSERT INTO diploma (number, student_name, major, academic_year, is_collected, collected_at)
VALUES ('ANOMALI-B4-3', 'ANOMALI-B4-3 tahun ajaran', @ref_jurusan, @b4_3_tahun_ajaran, 0, NULL);

-- B4-4 · pegawai dengan gender yang tidak bisa dipetakan
INSERT INTO teacher (identity_number, full_name, gender, employment_status, `rank`, status, address)
VALUES ('ANOMALI-B4-4', 'ANOMALI-B4-4 gender', @b4_4_gender, @ref_status_kepegawaian, NULL, @ref_status_aktif, NULL);

-- B4-5 · arsip keuangan dengan kategori yang tidak ada di master_reference
INSERT INTO finance_archive (title, fiscal_year, period_month, category, amount, description,
                             classification_id, archive_status)
VALUES ('ANOMALI-B4-5 kategori tidak cocok', YEAR(CURDATE()), NULL, @b4_5_kategori_keuangan, NULL,
        'Baris anomali B4-5', @kls_induk, 'active');

-- B4-6 · ijazah tercatat sudah diambil tetapi tanpa tanggal (tahun ajaran sah: tahun lalu/tahun ini)
INSERT INTO diploma (number, student_name, major, academic_year, is_collected, collected_at)
VALUES ('ANOMALI-B4-6', 'ANOMALI-B4-6 diambil tanpa tanggal', @ref_jurusan,
        CONCAT(YEAR(CURDATE()) - 1, '/', YEAR(CURDATE())), 1, NULL);

-- B4-7 · dokumen pegawai tanpa klasifikasi
INSERT INTO employee_archive (document_name, document_type, archive_status, document_year, description,
                              owner_id, classification_id)
VALUES ('ANOMALI-B4-7 tanpa klasifikasi', @ref_jenis_dokumen, 'active', YEAR(CURDATE()), 'Baris anomali B4-7',
        @pegawai_induk, NULL);

COMMIT;


-- ---------------------------------------------------------------------
-- Ringkasan baris yang ditambahkan (hanya dibaca)
-- ---------------------------------------------------------------------
SELECT 'classification' AS tabel, COUNT(*) AS baris_anomali FROM classification WHERE name LIKE 'ANOMALI-%'
UNION ALL SELECT 'teacher', COUNT(*) FROM teacher WHERE full_name LIKE 'ANOMALI-%'
UNION ALL SELECT 'incoming_letter', COUNT(*) FROM incoming_letter WHERE subject LIKE 'ANOMALI-%'
UNION ALL SELECT 'outgoing_letter', COUNT(*) FROM outgoing_letter WHERE subject LIKE 'ANOMALI-%'
UNION ALL SELECT 'diploma', COUNT(*) FROM diploma WHERE student_name LIKE 'ANOMALI-%'
UNION ALL SELECT 'finance_archive', COUNT(*) FROM finance_archive WHERE title LIKE 'ANOMALI-%'
UNION ALL SELECT 'employee_archive', COUNT(*) FROM employee_archive WHERE document_name LIKE 'ANOMALI-%';
