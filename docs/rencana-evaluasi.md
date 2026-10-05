# Rencana Evaluasi

Produk: Sistem Tupoksi Arsiparis SMKN 7 Bandung
Fase: Dev — evaluasi untuk rancangan 001 (desain ulang basis data); rancangan evaluasi bernomor 002, data uji Dev-A bernomor 003
Dasar: docs/keputusan-produk.md (2026-10-05, siap dikerjakan) · docs/rancangan/001a_2026-10-04_dev-desain-ulang-basis-data.md · docs/rancangan/003a_2026-10-05_dev-rancang-evaluasi-data-seed.md
Data: tingkat 0 — belum ada data arsip. Database aplikasi `arsiparis_smk7` dan salinan D1 `tupoksi_d1` hanya berisi data pengembangan (1 akun, 1 pegawai, 203 log, 35 master_reference, klasifikasi 1 di aplikasi / 0 di D1, 0 arsip, 0 lokasi). Data uji Dev-A: D1 + seed deterministik buatan pink-chan (DS1–DS7, keputusan Arya 2026-10-05) + baris anomali B4 yang nilainya diisi agent atas permintaan Arya (DS6). Bukan data publik. Mode data rahasia tidak aktif.
Status: siap dikerjakan
Diperbarui: 2026-10-05

## Ringkasan
Produk ini bukan sistem LLM/RAG. Semua modul di rancangan 001 bersifat deterministik, jadi metriknya berupa pemeriksaan kebenaran dengan target persis (100% atau selisih 0), bukan skor kualitas.

Karena data asli belum ada, evaluasi dibagi dua tahap [data.md]:
- **Dev-A (sekarang, D1 + seed):** membuktikan mekanik — skema, aturan, ETL, scheduler, dan alat evaluasi berjalan benar.
- **Dev-B (hanya kalau data nyata ada sebelum cutover):** mengulang metrik yang bergantung pada isi data di dump data nyata.

| Modul | Metrik utama | Target awal | Cara menilai | Berlaku final di |
|---|---|---|---|---|
| M1 Skema (Alembic 0001, K6) | Kesesuaian skema; penolakan pelanggaran constraint | 1,00; 100% | Otomatis | Dev-A (tidak bergantung data) |
| M2 ETL (K7) | Kelengkapan per entitas; fidelitas sampel manual; nilai gagal dipetakan; idempotensi; integritas pasca-ETL | 1,00 per entitas; 100%; 0; checksum sama; 0 pelanggaran | Otomatis + golden sampel migrasi | Dev-A = mekanik; Dev-B = final bila data nyata ada |
| M3 Retensi (K5) | Akurasi golden retensi per kelompok; ekuivalensi dengan `/disposal/check` lama | 100%; selisih simetris 0 (di luar ijazah) | Golden retensi + otomatis | Golden: Dev-A. Ekuivalensi: Dev-A = mekanik; Dev-B = final |
| M4 State machine (K4) | Cakupan dan kebenaran matriks transisi | 100% | Otomatis, kunci = tabel transisi 001a | Dev-A |
| M5 Scheduler (K5) | Baris diubah = predikat; jalan kedua = 0 | sama persis; 0 | Otomatis | Dev-A |
| M6 Akun (K1) | Admin aktif lama bisa login; non-admin nonaktif | 100%; 100% | Otomatis + 1 login manual Arya | Dev-A = mekanik; Dev-B = final |
| M7 Log (K8) | FK valid; data pribadi di summary | 100%; 0 | Otomatis | Dev-A |
| E2E Gladi cutover (D4) | D4 butir 1–4 lulus dalam satu kali jalan | 4 dari 4 | Otomatis + manual Arya | Dump yang benar-benar akan dimigrasikan (lihat Gate 6) |

## Titik periksa
1. [Sampel] a. 5 per jenis arsip + 5 pegawai + 2 akun = 32 record (Usulan) ✓ 2026-10-04
2. [Tempat uji] a. Dump di-restore ke MySQL terpisah; database asal tidak disentuh (Usulan) ✓ 2026-10-04
3. [Kasus] a. 30 kasus dalam 6 kelompok, 10 uji akhir (Usulan) ✓ 2026-10-04
4. [Kinerja] a. Diukur sebagai informasi saja; target ditetapkan di rancangan back-end (Usulan) ✓ 2026-10-04
5. [Data asli] Apakah sudah ada, atau akan ada, data arsip nyata di aplikasi lama sebelum cutover?
   a. Belum pasti — ETL tetap dibangun dan dievaluasi di dummy (Dev-A); Dev-B bila data nyata muncul; tanpa data nyata, cutover ke database baru kosong + data master (Usulan) ✓ 2026-10-04
   b. Pasti tidak ada data nyata — ETL dikeluarkan dari 001
   c. Sudah ada data nyata di server sekolah — Dev-B wajib sebelum cutover
6. [Anomali] Apakah jalur anomali ETL diuji dengan data?
   a. Arya menambah ±10 baris anomali ke database dummy sebelum baseline, mengikuti daftar B4 (Usulan) ✓ 2026-10-04 — diganti 2026-10-05 oleh c
   b. Pakai dummy apa adanya
   c. Nilai anomali diisi agent atas permintaan Arya (semula `scripts/evaluation/b4_anomali_dev_a.sql`), dijalankan lewat seed opsi `--anomali` (DS6) ✓ 2026-10-05
7. [Data uji] Dari mana data uji Dev-A? (rancangan 003)
   a. Script seed deterministik buatan pink-chan ke D1 (keputusan Arya) ✓ 2026-10-05
8. [Volume] (003) a. Dua preset, Gate 1 memakai `penuh` (±22.000 arsip, 11 tahun) (Usulan) ✓ 2026-10-05
   b. Hanya `kecil` · c. Menunggu profil data dari Arya
9. [Tempat seed] (003) a. Hanya ke D1 `tupoksi_d1` + folder lampiran terpisah; DB aplikasi tidak disentuh (Usulan) ✓ 2026-10-05
   b. Ke DB aplikasi lalu di-dump ke D1
10. [Anomali B4] (003) a. Digabung ke seed sebagai opsi `--anomali`, tanggal dari tahun acuan; file SQL ditandai usang (Usulan) ✓ 2026-10-05
    b. File SQL tetap, dijalankan Arya setelah seed
11. [Penanda] (003) a. Penanda "DUMMY" di setiap kolom teks utama, NIP 18 digit berawalan 9900, tanpa nama orang (Usulan) ✓ 2026-10-05
    b. Nama dan teks realistis, penanda di satu kolom

## Dataset uji

Kelompok wajib golden set di `references/evaluasi.md` (`ada_di_dokumen`, `tidak_ada_di_dokumen`, `di_luar_cakupan`, `sulit`) ditulis untuk sistem tanya-jawab dan **tidak berlaku** di sini. Penggantinya adalah kelompok per aturan di bawah. Aturan lain tetap berlaku: golden set ditulis manual oleh Arya, ±⅓ disisihkan sebagai uji akhir, dan setiap baris diverifikasi.

### D1 · Salinan database lama
- **Dev-A:** salinan DB aplikasi di server MySQL terpisah (`tupoksi_d1`), diisi seed DS1–DS7 dengan preset `penuh` dan opsi `--anomali`. Seed hanya menambah baris; baris yang sudah ada (akun admin, pegawai, log, master_reference) tidak diubah. Setelah seed dan sebelum baseline, Arya mengambil dump D1 sebagai salinan acuan putaran. Isinya dummy, jadi AI (red-chan dan pink-chan) boleh membaca isi dan hasilnya. D1 tidak boleh dipakai aplikasi lama: `create_app()` menyalakan scheduler yang mengubah status.
- **Dev-B:** dump data nyata, kalau ada (TP5). Status kerahasiaannya diputuskan Arya saat data itu ada. Sampai ada keputusan, berlaku aturan keluaran terbatas (Gate 4).
- Tanggal uji (`tanggal_uji`) ditetapkan sebagai parameter dan sama untuk semua pengukuran satu putaran. Di Dev-A, tahun `tanggal_uji` harus sama dengan tahun acuan seed Y₀.

### D1-S · Seed data uji Dev-A (rancangan 003)
Seed adalah alat evaluasi, bukan bagian aplikasi. Isinya struktural dan berpenanda DUMMY; seed tidak membuat label golden apa pun.

```
DS1 · Write-guarded seed target — Umum (pengetahuan umum)
Pendekatan   Seed hanya MENAMBAH baris ke skema lama (12 tabel) di D1;
             tanpa DDL, tanpa UPDATE/DELETE baris yang sudah ada
Parameter    EVAL_SEED_DB_URL (baru): harus menunjuk database yang sama
             dengan EVAL_OLD_DB_URL dan berbeda dari DATABASE_URL aplikasi
             EVAL_SEED_STORAGE_ROOT (baru): wajib diisi, bukan folder
             storage/ aplikasi; usulan data/evaluation/storage_d1/
Penjaga      Berhenti sebelum menulis apa pun bila: target = DB aplikasi;
             salah satu dari 5 tabel arsip atau storage_location tidak
             kosong; sudah ada baris berpenanda DUMMY; kategori wajib
             master_reference (school_major, teacher_emp_status,
             teacher_active_status, finance_category, emp_doc_type) kosong
             (teacher_rank opsional → rank NULL semua)
Transaksi    Semua baris DB dalam satu transaksi; berkas lampiran ditulis
             setelah commit. Gagal di tengah → restore D1 lalu ulang
             (tidak ada jalan ulang parsial)
Metrik       SY8
```
Alternatif ditolak: seed ke DB aplikasi lalu dump (scheduler lama mengubah status dan merusak sebaran; TP9).

```
DS2 · Deterministic generation — Umum
Pendekatan   random.Random(seed); semua nilai dari generator ini; urutan
             insert tetap (per tabel, lalu per tahun, lalu nomor urut)
Parameter    --seed (default 20261005) · --tahun-acuan Y₀ (default 2026)
             · --skala kecil|penuh (Gate 1: penuh) · --anomali
             Semua DATE/DATETIME, termasuk created_at dan updated_at,
             diisi eksplisit dari tahun dokumen (tidak ada NOW()/CURDATE()).
             Nama file lampiran = hex 32 karakter dari generator (bukan uuid4)
Syarat pakai tanggal_uji baseline harus berada di tahun Y₀
Metrik       SY7: dua jalan dengan parameter sama ke dua salinan D1 yang
             sama → hash berurutan semua baris identik (memakai fungsi hash
             M2); seed berbeda → hash berbeda
```
Alternatif ditolak: tanggal relatif terhadap hari dijalankan (D1 berbeda tiap hari; kode lama memakai `datetime.now()` dan `created_at.year`, sehingga B2 tidak bisa diulang).

```
DS3 · Stratified coverage + seeded random fill — Umum
Pendekatan   (1) baris cakupan wajib (DS4, C1–C8), lalu
             (2) baris isian acak sampai volume preset tercapai
Klasifikasi  7 baris dummy (code ≤ 10 karakter, name ≤ 50, unik):
             code     a   i   final_action
             DMY-D11  1   1   destroy
             DMY-D23  2   3   destroy
             DMY-D55  5   5   destroy
             DMY-D10  1   0   destroy
             DMY-DXX  10  10  destroy      (tidak pernah jatuh di rentang isian)
             DMY-P55  5   5   permanent
             DMY-A25  2   5   assess
             Bukan kode JRA; tidak boleh dipakai sebagai acuan retensi nyata
Volume       preset penuh (per tahun Y₀−10 … Y₀, 11 tahun):
               incoming 800/th · outgoing 500/th · diploma 450/angkatan ·
               finance 150/th · pegawai 120 × ±10 dokumen
               ≈ 22.000 arsip (asumsi perkiraan satu SMK, sementara)
             preset kecil = penuh ÷ 10 (≈ 2.200 arsip, 12 pegawai)
             Baris cakupan ditambahkan di atas volume preset
Sebaran isian
             tahun dokumen  seragam Y₀−10 … Y₀
             klasifikasi    seragam dari 7 (4 jenis ber-klasifikasi)
             status         active 60% · inactive 25% · destroyed 10% ·
                            permanent 5%; destroyed hanya dengan final_action
                            destroy dan sudah lewat masa akhir;
                            permanent hanya dengan permanent/assess
             referensi      70% code persis · 20% name persis · 10% varian
                            huruf besar/kecil atau spasi (semua tetap cocok)
             gender         L 40% · P 40% · Laki-laki 10% · Perempuan 10%
             rank           70% terisi bila teacher_rank ada, sisanya NULL
             period_month   NULL 20%, sisanya 1–12
             amount         NULL 10%, sisanya kelipatan 1.000 di
                            100.000–500.000.000
             document_year  NULL 5% (memicu fallback created_at.year lama)
             ijazah         is_collected 70%; collected_at di tahun ajaran
                            akhir s.d. +3 tahun
Cakupan wajib (minimal 1 baris per sel, sebelum isian)
  C1 tiap jenis ber-klasifikasi × tiap klasifikasi × status
     {active, inactive}
  C2 tiap jenis ber-klasifikasi × status {destroyed, permanent}: ≥ 3
  C3 surat masuk letter_date Desember x, received_date Januari x+1: ≥ 5;
     surat keluar sent_date beda tahun dari letter_date: ≥ 5
  C4 surat masuk/keluar active di tahun Y₀−a, bulan Januari dan Desember
     (memperlihatkan beda per-tanggal lama vs per-tahun K5): ≥ 1 per
     klasifikasi
  C5 ijazah: tiap angkatan punya diambil dan belum diambil; ≥ 5 diambil
     dengan tahun awal < Y₀−5 (L ijazah lama > 0)
  C6 dokumen pegawai dengan document_year NULL: ≥ 5, created_at
     tersebar di beberapa tahun
  C7 tiap kategori referensi: bentuk code, name, dan varian masing-masing ≥ 1
  C8 user: admin-inactive, teacher-active, teacher-inactive,
     headmaster-active (admin aktif = akun lama yang sudah ada)
Larangan     Seed tidak membuat satu pun pola B4 (anomali hanya dari DS6)
Metrik       SY1, SY4
```
Alternatif ditolak: murni acak tanpa baris cakupan (L, B3, dan baris batas bisa kebetulan kosong); data pengganti publik (tidak ada dataset publik berskema arsip sekolah ini).

```
DS4 · Retention boundary rows — Umum
Rumus        Untuk tiap jenis ber-klasifikasi dan tiap klasifikasi (a, i):
             x_akhir_batas = Y₀ − (a+i)        → tidak masuk L lama
             x_akhir_lewat = Y₀ − (a+i) − 1    → masuk L lama (bila destroy)
             x_aktif_batas = Y₀ − a            → tidak jatuh inaktif (K5)
             x_aktif_lewat = Y₀ − a − 1        → jatuh inaktif (K5)
             x = tahun dokumen (letter_date.year, fiscal_year,
             document_year). Status baris akhir = inactive, baris aktif =
             active. Baris batas boleh lebih tua dari Y₀−10
             (DMY-DXX → x = Y₀−21)
Kenapa       Kondisi lama current_year > x+n dan K5 x+n < y bertemu tepat di
             batas; baris di dua sisi batas menguji ekuivalensi M3 dan
             scheduler M5 di titik yang paling mungkin salah
Metrik       SY6
```

```
DS5 · Attachment fixtures (B5) — Umum
Pendekatan   Path ditulis dalam format lama:
             storage/documents/<subfolder route lama>/<hex32>.txt
Parameter    40% baris non-destroyed punya path; dari baris itu, 10% sengaja
             tanpa berkas (hilang); destroyed selalu NULL (perilaku
             execute_disposal lama). Isi berkas: satu baris
             "DUMMY lampiran <tabel> <id>". Berkas dibuat di
             EVAL_SEED_STORAGE_ROOT; saat baseline,
             EVAL_STORAGE_ROOT diarahkan ke folder yang sama
Metrik       SY5
```

```
DS6 · B4 anomaly rows (opsi --anomali) — Umum
Pendekatan   Opsi --anomali menambah baris dengan nilai yang sama dengan
             b4_anomali_dev_a.sql (7 butir; B4-1 = satu pasang nomor ganda),
             tetapi tanggal dari Y₀ (1 Juli Y₀), bukan CURDATE(). Induk tetap
             klasifikasi permanent supaya tidak masuk L atau B3. Penanda
             ANOMALI- tetap dipakai. File b4_anomali_dev_a.sql dan
             b4_anomali_template.sql ditandai usang dan tidak dijalankan
Catatan      Nilai diisi agent atas permintaan Arya → B4 Dev-A hanya bukti
             mekanik (E6)
Metrik       SY4
```
Alternatif ditolak: file SQL tetap dan dijalankan terpisah (dua langkah manual; `CURDATE()` membuat D1 bergantung hari; TP10).

```
DS7 · Dummy marker, no realistic PII — Umum
Pendekatan   Setiap baris baru bisa dikenali dari penanda:
             subject/title/document_name/name diawali "DUMMY "; nomor surat
             "DMY/IN|OUT/<tahun>/<nnnn>"; ijazah "DMY-IJZ-<tahun>-<nnnn>";
             student_name "Siswa Dummy <tahun>-<nnnn>"; full_name
             "Pegawai Dummy <nnn>"; address "Alamat Dummy <nnn>";
             identity_number 18 digit berawalan "9900" (bulan 00 → bukan NIP
             sah, tetapi tetap tertangkap pola PII M7); storage_location
             "DUMMY Lemari <nn>"
             password_hash akun seed = satu konstanta hash argon2 dari sandi
             acak yang tidak disimpan → akun seed tidak bisa dipakai login
             (login manual M6 tetap memakai akun admin lama)
             Seed tidak menulis log
Metrik       SY8, SY9
```
Alternatif ditolak: nama dan teks realistis (bisa tertukar atau terbawa ke produksi; lebih jauh dari aturan tanpa konten tiruan; TP11).

**Syarat data uji (dipakai Gate 1).** SY1, SY6, SY8, SY9 dicetak ringkasan seed; SY2–SY5 dibaca dari keluaran baseline; SY7 dari test.
| # | Syarat | Target |
|---|---|---|
| SY1 | B1: tiap jenis arsip punya baris di keempat status; volume ≥ preset | ya |
| SY2 | B2: \|L\| > 0 untuk tiap jenis non-ijazah, dan L ijazah > 0 | ya |
| SY3 | B3 > 0 untuk incoming, outgoing, dan finance | ya |
| SY4 | B4 = 0 setelah seed tanpa anomali; tepat 1 per butir dengan `--anomali` | ya |
| SY5 | B5: ada dan hilang masing-masing > 0 untuk tiap jenis | ya |
| SY6 | Tiap (jenis, klasifikasi) punya keempat baris batas DS4 | 100% |
| SY7 | Hash identik untuk parameter sama, berbeda untuk seed berbeda | ya |
| SY8 | Baris berpenanda = baris yang ditambahkan; hash baris lama sebelum = sesudah | ya |
| SY9 | Tidak ada nama tanpa "Dummy"; semua identity_number baru berawalan 9900 | 0 pelanggaran |

### D2 · Golden retensi (ditulis Arya)
Kasus buatan tangan yang menguji rumus K5. Kasus ini tidak bergantung pada isi database, jadi hasilnya berlaku final sejak Dev-A. Jawabannya dihitung manual oleh Arya dari aturan di 001a.

| Kelompok | Jumlah | Menguji |
|---|---|---|
| `normal_musnah` | 6 | Arsip biasa lewat masa inaktif, final_action destroy, untuk tiap jenis arsip |
| `batas_tahun` | 6 | y = x + n (belum lewat) vs y = x + n + 1 (lewat), untuk masa aktif dan masa akhir |
| `berkas_terbuka` | 4 | `closed_year` kosong, tidak pernah jatuh inaktif atau masuk daftar |
| `ijazah` | 4 | Diambil vs belum; klasifikasi IJZ (assess) tidak pernah masuk kandidat musnah |
| `assess_permanen` | 4 | Masuk `perlu_dinilai` atau `kandidat_permanen`, bukan kandidat musnah |
| `status_lain` | 6 | Arsip active yang belum jatuh tempo, sudah destroyed/permanent, atau sedang di disposal proposed/approved |
| **Total** | **30** | 10 baris (±⅓, tersebar di semua kelompok) = `uji_akhir` |

Kolom spreadsheet, dikonversi pink-chan ke `data/evaluation/golden_retensi.jsonl`:
| Kolom | Isi | Wajib |
|---|---|---|
| `id` | `R001`, `R002`, … | Ya |
| `kelompok` | Salah satu kelompok di atas | Ya |
| `archive_type` | incoming_letter · outgoing_letter · diploma · finance_record · employee_document · other | Ya |
| `archive_year` | Tahun dokumen | Ya |
| `closed_year` | Tahun berkas selesai, boleh kosong | Ya (boleh kosong) |
| `retention_active_years`, `retention_inactive_years` | Angka ≥ 0 | Ya |
| `final_action` | destroy · permanent · assess | Ya |
| `status_awal` | active · inactive · destroyed · permanent | Ya |
| `disposal_terbuka` | ya · tidak | Ya |
| `tanggal_uji` | `YYYY-MM-DD` | Ya |
| `label_jatuh_inaktif` | ya · tidak | Ya |
| `label_daftar` | kandidat_musnah · perlu_dinilai · kandidat_permanen · tidak_ada | Ya |
| `bagian` | perbaikan · uji_akhir | Ya |
| `diverifikasi` | Nama pemeriksa; kosong bila belum | Ya |
| `catatan` | Alasan label untuk kasus batas | Tidak |

### D3 · Golden sampel migrasi (ditulis Arya)
Arya memilih record dari database lama (Dev-A: D1 setelah seed) lalu menulis nilai yang seharusnya muncul di skema baru, berdasarkan database lama dan aturan pemetaan di 001a K7. Label ditulis manual supaya pemeriksaan tidak berputar pada kode ETL yang sama — ini makin penting karena seed dan ETL ditulis agent yang sama (E6). Kalau data nyata datang (Dev-B), Arya menulis sampel baru dengan bentuk yang sama dari data nyata; sampel dummy tidak dipakai untuk gate Dev-B.

| Kelompok | Jumlah record | Kolom yang diberi label |
|---|---|---|
| `incoming_letter` | 5 | archive: archive_type, title, archive_year, closed_year, status, kode klasifikasi, nama lokasi, attachment_path · rincian: letter_number, letter_date, received_date, sender |
| `outgoing_letter` | 5 | archive (sama) · letter_number, letter_date, sent_date, destination, is_decree, approval_status |
| `diploma` | 5 (minimal 1 belum diambil) | archive (sama) · diploma_number, student_name, nama jurusan, collected_at |
| `finance_record` | 5 | archive (sama) · kode kategori, period_month, amount |
| `employee_document` | 5 (minimal 1 tanpa klasifikasi lama) | archive (sama) · id pegawai lama, kode jenis dokumen |
| `employee` | 5 | gender, nama status kepegawaian, nama status aktif, nama golongan |
| `app_user` | 2 (1 admin, 1 non-admin bila ada) | username, is_active |
| **Total** | **32 record** | ±⅓ record = `uji_akhir` |

Bentuk: satu baris per (record, kolom), dikonversi pink-chan ke `data/evaluation/golden_sampel_migrasi.jsonl`:
| Kolom | Isi | Wajib |
|---|---|---|
| `id` | `S001`, … | Ya |
| `sumber_data` | dummy · nyata | Ya |
| `kelompok` | Nama entitas di atas | Ya |
| `id_lama` | id baris di tabel lama | Ya |
| `kolom_baru` | Mis. `archive.closed_year`, `diploma.collected_at`, `school_major.name` | Ya |
| `nilai_harapan` | Dinormalisasi: tanggal `YYYY-MM-DD`, angka tanpa titik/Rp, kosong = `NULL` | Ya |
| `bagian` | perbaikan · uji_akhir (sama untuk semua kolom satu record) | Ya |
| `diverifikasi` | Nama pemeriksa | Ya |
| `catatan` | Hal khusus, mis. data lama tidak konsisten | Tidak |

### D4 · Kunci dari spesifikasi
M1 (daftar tabel, kolom, constraint, indeks) dan M4 (tabel transisi) memakai spesifikasi 001a yang sudah disetujui Arya sebagai kunci.

### Alat bantu dari pink-chan
- Konversi dan pemeriksaan spreadsheet. Baris ditolak (beserta alasannya) bila: `id` kosong atau ganda; nilai di luar domain; `label_daftar` tidak konsisten dengan `label_jatuh_inaktif` (`tidak` hanya boleh dengan `tidak_ada`); `diverifikasi` kosong pada baris yang masuk gate; `kolom_baru` tidak ada di skema.
- Pemilih record acak per kelompok untuk D3: menampilkan id lama saja, Arya yang memilih.
- Seed data uji Dev-A (D1-S) beserta ringkasan SY1, SY6, SY8, SY9.
- Fixture kecil buatan test untuk menguji alat evaluasi itu sendiri dan jalur anomali ETL. Fixture bukan golden set dan angkanya tidak dipakai untuk gate.
- Semua skrip menerima parameter koneksi database dan `tanggal_uji`, supaya alat yang sama bisa dijalankan ulang di dump data nyata (Dev-B) tanpa diubah.

## Metrik per modul

### M1 · Skema (Alembic 0001, K6)
```
Keluaran     Database baru setelah `alembic upgrade head`
Rumus        E = himpunan item skema yang diharapkan dari 001a: tabel;
             (tabel, kolom, tipe, nullable, default); PK; (FK, tabel
             rujukan, ON DELETE); UNIQUE; CHECK (berdasarkan nama
             convention); indeks
             A = himpunan item yang sama dibaca dari information_schema
             Kesesuaian_skema = |E ∩ A| / |E ∪ A|
             Penolakan = Σ kasus pelanggaran yang ditolak DB /
                         Σ kasus pelanggaran
             (satu kasus negatif untuk setiap CHECK, UNIQUE, FK, NOT NULL)
Target       Kesesuaian_skema = 1,00 · Penolakan = 100%
Cara         Otomatis; laporan menampilkan E \ A dan A \ E
```

### M2 · ETL (K7)
```
Keluaran     Database baru setelah ETL + laporan ETL
Rumus        Kelengkapan(e) = n_baru(e) / n_lama(e) untuk tiap entitas e:
               5 jenis arsip, employee, app_user, storage_location,
               activity_log (= log), classification (n_lama + 2 placeholder)
             Lookup: n_baru(kategori) ≥ n_master_reference(kategori); baris
               tambahan dari nilai tak cocok dilaporkan untuk diperiksa Arya
             Fidelitas_sampel = Σ kolom benar / Σ kolom di D3 (setelah
               normalisasi; per kelompok dan per bagian)
             Gagal_peta = jumlah nilai status tetap (archive_status,
               final_action, approval_status, gender) yang tidak terpetakan
             Lampiran: Δ_file = |path lama dengan file ada| −
               |path baru dengan file ada|
             Idempotensi: hash berurutan semua baris semua tabel pada ETL
               ke-1 = ETL ke-2 (masing-masing ke DB kosong, tanggal ETL sama)
             Integritas = pelanggaran aturan lintas tabel: archive tanpa
               rincian sesuai archive_type; rincian ganda; other dengan
               rincian; destroyed tanpa item di disposal executed; arsip di
               > 1 disposal proposed/approved
Target       Kelengkapan = 1,00 · Fidelitas_sampel = 100% (uji_akhir) ·
             Gagal_peta = 0 · Δ_file = 0 · hash sama · Integritas = 0
Cara         Otomatis + D3. Baris anomali B4 (DS6) harus tertangkap pra-cek
             atau dilaporkan sesuai aturan K7 (tidak hilang diam-diam).
             Hasil Dev-A membuktikan mekanik; angka final hanya dari Dev-B
             kalau data nyata ada
```

### M3 · Retensi (fungsi domain dan query K5)
```
Keluaran     jatuh_inaktif dan daftar per arsip pada tanggal_uji
Rumus        Akurasi_golden(k) = Σ benar(k) / Σ kasus(k), per kelompok k
             di D2; benar = label_jatuh_inaktif dan label_daftar sama
             Ekuivalensi (di D1, tanggal_uji sama):
               L = {(jenis, id_lama)} hasil /disposal/check lama, tanpa
                   jenis ijazah
               N = {(jenis, id_lama)} kandidat_musnah baru setelah scheduler
                   baru dijalankan sekali, dipetakan balik ke id lama
               Selisih = |L △ N| ;  J = |L ∩ N| / |L ∪ N|
               Kandidat ijazah baru = |N_ijazah|
             Cakupan_kandidat = |L| (dijamin > 0 oleh seed, SY2)
Target       Akurasi_golden = 100% per kelompok (uji_akhir) · Selisih = 0 ·
             Kandidat ijazah = 0 · Cakupan_kandidat > 0
Cara         D2 otomatis terhadap label Arya; ekuivalensi otomatis; bila
             Selisih > 0, laporan menampilkan id di L \ N dan N \ L
```

### M4 · State machine (K4)
```
Keluaran     Hasil percobaan setiap transisi lewat fungsi domain
Rumus        P_arsip = {(baru), active, inactive, destroyed, permanent} ×
             {active, inactive, destroyed, permanent}
             P_disposal = {(baru), proposed, approved, rejected, executed} ×
             {proposed, approved, rejected, executed}
             Cakupan = pasangan diuji / |P_arsip ∪ P_disposal|
             Kebenaran = pasangan yang sesuai tabel transisi 001a / diuji
             + aturan tambahan: edit hanya saat active/inactive; hapus fisik
             hanya active dan belum pernah di disposal; item hanya diubah
             saat proposed; eksekusi atomik
Target       Cakupan = 100% · Kebenaran = 100%
Cara         Otomatis (test)
```

### M5 · Scheduler retensi (K5)
```
Rumus        n_update = |{a : status='active' ∧ closed_year IS NOT NULL ∧
             closed_year + retention_active_years < y}| (SELECT terpisah
             sebelum UPDATE)
             Idempotensi: n_update jalan kedua = 0
             Log: 1 baris 'retention_run' per jalan, angkanya = n_update
             Waktu_jalan (ms) — informasi (sementara: volume seed adalah
             perkiraan, bukan data nyata)
Target       sama persis · 0 · 1 baris sesuai
Cara         Otomatis
```

### M6 · Akun (K1)
```
Rumus        Admin_aktif = |app_user aktif| / |user lama role=admin ∧
             status=active| ; Non_admin_nonaktif = |akun non-admin lama
             dengan is_active=0| / |akun non-admin lama|
             Verifikasi hash: password_hash identik dengan kolom lama
Target       1,00 · 1,00 · 100% identik; + Arya berhasil login 1× dengan
             NIP dan sandi lamanya di DB salinan
Cara         Otomatis + manual Arya (akun admin lama; akun seed tidak bisa
             dipakai login, DS7)
```

### M7 · Log aktivitas (K8)
```
Rumus        FK_valid = baris dengan user_id NULL atau ada di app_user /
             semua baris
             PII = baris non-'legacy' yang summary-nya memuat deretan 16–18
             digit (pola NIP/NUPTK) atau nilai employee.address
Target       FK_valid = 100% · PII = 0
Cara         Otomatis. Tetap diperiksa walaupun data dummy, karena yang
             diuji adalah perilaku kode untuk data nyata nanti
```

### E2E · Gladi cutover (D4 rancangan 001)
```
Keluaran     Satu kali jalan penuh: alembic upgrade → ETL → scheduler 1× →
             M1–M7
Rumus        Lulus = D4-1 ∧ D4-2 ∧ D4-3 ∧ D4-4
             Waktu_ETL (menit) — informasi
Target       4 dari 4
Cara         Otomatis + login manual Arya; dijalankan di dump yang akan
             benar-benar dimigrasikan (Gate 6)
```

## Membaca hasil
Baca dari hulu ke hilir: SY (data uji) → M1 → M2 → M5 → M3 → M4/M6/M7 → E2E. Modul pertama yang gagal adalah tersangka utama.

| Pola hasil | Kesalahan ada di |
|---|---|
| Salah satu SY1–SY9 gagal | Seed (DS1–DS7); baseline belum sah, jangan lanjut ke 001b |
| SY2 gagal hanya untuk satu jenis | Baris batas DS4 atau sebaran status DS3 untuk jenis itu |
| SY7 gagal | Seed memakai NOW()/uuid4 atau urutan insert tidak tetap |
| Kesesuaian_skema < 1 | Revisi Alembic 0001 atau model ORM; periksa E \ A dan A \ E |
| Penolakan < 100% hanya pada CHECK | Versi MySQL < 8.0.16 atau Enum tanpa `create_constraint=True` |
| Kelengkapan < 1 untuk satu jenis | ETL langkah 4 (join/filter) atau pra-cek yang melewatkan baris |
| Baris anomali B4 hilang tanpa laporan | ETL langkah 1 (pra-cek) atau langkah 3 (pemetaan nilai) |
| Fidelitas_sampel rendah di kolom lookup | ETL langkah 3 (pencocokan code/name) |
| Fidelitas_sampel rendah di closed_year/archive_year | ETL langkah 4 (aturan tahun), terutama ijazah dan pegawai |
| Fidelitas_sampel rendah hanya di uji_akhir | ETL disesuaikan berlebihan ke baris perbaikan |
| Idempotensi gagal | ETL memakai NOW() atau urutan tak tetap |
| Akurasi_golden < 100% | Rumus K5 di fungsi domain |
| Akurasi_golden 100%, Selisih M3 > 0 | Data hasil ETL atau scheduler belum dijalankan; cek M2 dan M5 dulu |
| Selisih M3 hanya di dokumen pegawai | document_year/created_at atau TANPA-KLAS di ETL |
| Kandidat ijazah > 0 | Ijazah tidak memakai IJZ (assess) atau closed_year salah |
| Lulus di Dev-A, gagal di Dev-B | Data nyata punya pola yang tidak ada di seed; tambahkan anomalinya ke B4 dan perbaiki pemetaan ETL |
| n_update ≠ predikat | SQL scheduler K5 |
| Kebenaran M4 < 100% | Fungsi domain transisi |
| PII > 0 | Pembentuk summary log |

## Gate dan baseline

**Baseline (Dev-A: diukur di D1 setelah seed `penuh` + `--anomali`, sebelum ETL dan sebelum perubahan apa pun; Dev-B: diukur ulang di dump data nyata saat ada):**
| # | Yang diukur di database lama | Dipakai untuk |
|---|---|---|
| B1 | Jumlah baris per tabel lama, per archive_status, per jenis arsip | Kelengkapan M2; SY1 |
| B2 | Himpunan L: hasil `/disposal/check` lama pada tanggal_uji | Ekuivalensi M3; SY2 |
| B3 | Himpunan yang akan diubah scheduler lama pada tanggal_uji | Informasi perbedaan scheduler lama vs baru; SY3 |
| B4 | Anomali data: nomor surat keluar ganda, status di luar domain, academic_year tidak berformat, nilai gender, string referensi yang tidak cocok dengan master_reference, ijazah diambil tanpa tanggal, pegawai tanpa klasifikasi. Di Dev-A, setiap butir diwakili tepat satu baris (B4-1: satu pasang) dari seed `--anomali` (DS6); nilainya diisi agent atas permintaan Arya | Pra-cek ETL; diselesaikan bersama Arya sebelum gladi; SY4 |
| B5 | Lampiran dengan file ada dan file hilang | Δ_file M2; SY5 |
| B6 | Waktu `/disposal/check` lama dan get_all per modul (ms) + jumlah baris | Informasi (sementara) untuk rancangan back-end; volume preset `penuh` adalah perkiraan, bukan data nyata |

**Aturan gate:**
1. Baseline B1–B6 diukur dan disimpan sebelum langkah pembangunan 001 dimulai, dan baru sah kalau SY1–SY9 lulus (Gate 1). Hasil baseline yang diukur di D1 kosong (2026-10-05) disimpan tetapi ditandai **tidak dipakai**.
2. Setiap langkah di rencana pembangunan 001 (file `001b`) wajib mencapai target modul yang ditargetkannya, di Dev-A.
3. Target bersifat persis. Metrik yang sudah lulus lalu turun di langkah berikutnya (berapa pun penurunannya) membuat langkah itu di-rollback atau diperbaiki sebelum lanjut.
4. Hasil tiap putaran disimpan di `outputs/evaluation/<tanggal>/<dummy|nyata>/`. Untuk data dummy, keluaran boleh memuat isi baris lengkap supaya mudah diperiksa. Untuk data nyata, keluaran hanya angka dan id (tanpa nama, NIP, alamat, atau isi lampiran) sampai Arya menyatakan data itu boleh dibaca AI.
5. Angka dari dummy dan dari data nyata tidak pernah digabung atau dirata-rata. Metrik yang bergantung pada isi data (M2, ekuivalensi M3, M6, E2E) hanya dinyatakan final dari data nyata kalau data nyata ada. Metrik yang tidak bergantung data (M1, golden M3, M4, M5, M7) final di Dev-A.
6. Cutover (rancangan back-end) mensyaratkan E2E lulus 4/4 di dump yang benar-benar akan dimigrasikan. Kalau ada data nyata, itu dump data nyata yang paling baru (Dev-B). Kalau tidak ada data nyata, cutover ke database baru kosong + data master, dan E2E di D1 + seed cukup sebagai bukti mekanik (TP5). Baris seed tidak pernah ikut cutover.
7. Kalau data nyata tidak pernah datang sampai serah terima, dokumen ini mencatat: **ETL belum diuji pada data nyata.**

## Asumsi
- E1. Arya bisa membuat dump database dan me-restore-nya ke MySQL ≥ 8.0.16 yang terpisah.
- E2. Kode lama (`app/services/disposal.py`) bisa dijalankan terhadap salinan dengan tanggal uji yang ditetapkan, untuk B2 dan B3.
- E3. Target 100% / selisih 0 tepat untuk modul deterministik. Satu-satunya pengecualian yang direncanakan adalah ijazah (TP8 rancangan 001).
- E4. 30 kasus retensi dan 32 record sampel cukup untuk menangkap kesalahan aturan. Pengukuran lengkap tetap dijalankan atas semua baris.
- E5. (Diubah 2026-10-05) Seed menjamin kelima jenis arsip ada, |L| > 0, B3 > 0, dan B5 punya file ada dan hilang (SY1–SY5). Memajukan `tanggal_uji` khusus untuk ekuivalensi tidak diperlukan lagi.
- E6. (Diubah 2026-10-05) Data uji Dev-A dibuat oleh seed pink-chan (keputusan Arya), dan nilai baris anomali B4 diisi agent atas permintaan Arya (semula `scripts/evaluation/b4_anomali_dev_a.sql`, kini DS6). Ini menyimpang dari aturan `references/data.md` (tanpa konten tiruan buatan agent) atas keputusan Arya. Akibatnya: Dev-A hanya membuktikan mekanik; B4 tidak menguji detektor secara independen; seed dan ETL ditulis agent yang sama sehingga salah paham yang sama bisa lolos. Penyeimbangnya: label D2/D3 tetap manual Arya, dan uji independen atas pola data sungguhan hanya ada di Dev-B.
- E7. Volume preset `penuh` (±22.000 arsip, 120 pegawai, 11 tahun) dan sebaran DS3 adalah perkiraan umum satu SMK, bukan profil nyata (sementara).
- E8. master_reference D1 (35 baris) memuat lima kategori wajib DS1.

## Belum pasti
- Ada tidaknya data arsip nyata (di server sekolah atau di tempat lain) sebelum cutover.
- Kalau data nyata ada: apakah boleh dibaca atau dikirim ke AI.
- Profil data nyata (jumlah arsip per jenis per tahun, jumlah pegawai, jumlah lampiran) untuk target kinerja di rancangan back-end dan untuk menyesuaikan preset volume seed [data.md: tingkat 1].
- Versi MySQL tempat salinan di-restore.
- Keputusan Arya untuk tiap anomali B4 sebelum gladi (misalnya nomor surat keluar ganda).
- Perlakuan ETL untuk arsip destroyed yang masih punya lampiran (tidak dicakup B4 maupun seed; lihat keputusan-produk Belum pasti).

## Sumber
Tidak ada riset web. Metrik berupa pemeriksaan kebenaran dan himpunan (pengetahuan umum). Kunci diambil dari docs/rancangan/001a_2026-10-04_dev-desain-ulang-basis-data.md. Pembagian Dev-A/Dev-B dan aturan data mengikuti `references/data.md` (product-design). Spesifikasi seed diturunkan dari kode lama (`app/services/disposal.py`, `app/services/retention_scheduler.py`, `app/models/*`, `app/utils/file_helper.py`) dan docs/rancangan/003a_2026-10-05_dev-rancang-evaluasi-data-seed.md.

## Riwayat
| Tanggal | Perubahan | Alasan |
|---|---|---|
| 2026-10-04 | Usulan pertama rencana evaluasi (rancangan 002) untuk rancangan 001 | TP4 rancangan 001: evaluasi dirancang sebelum pink-chan membangun |
| 2026-10-04 | TP1–TP4 dijawab (semua a). Data diubah dari tingkat 3 (produksi) menjadi tingkat 0 data asli + dump dummy sebagai data uji; pembagian Dev-A/Dev-B; kolom "berlaku final di"; keluaran boleh lengkap untuk dummy, angka + id untuk data nyata; Gate 4–7 diperbarui; M3 + Cakupan_kandidat; E5, E6; TP5 dan TP6 baru | Arya: data di DB saat ini semuanya dummy dan aman dikirim ke AI |
| 2026-10-04 | Rancangan 002 disetujui Arya; TP5–TP6 dijawab (semua a). Status → siap dikerjakan. Baris anomali Arya dimasukkan ke D1, B4, M2, dan tabel Membaca hasil. Arsip: docs/rancangan/002a_2026-10-04_dev-rancang-evaluasi-basis-data.md | Persetujuan Arya |
| 2026-10-05 | Rancangan 003 disetujui (TP8–TP11 semua a). Data: DB lama belum berisi arsip; data uji Dev-A = D1 + seed deterministik pink-chan. Baru: D1-S (DS1–DS7, SY1–SY9), TP6 c, TP7–TP11, E7, E8. Diubah: D1, D3, B4, B6, M2, M3 (Cakupan_kandidat dijamin seed), M5, M6, Membaca hasil (baris SY), Gate 1 (SY lulus; baseline D1 kosong tidak dipakai), Gate 6, E5, E6, Belum pasti. Nilai anomali B4 dicatat sebagai isian agent atas permintaan Arya; `b4_anomali_dev_a.sql` usang. Arsip: docs/rancangan/003a_2026-10-05_dev-rancang-evaluasi-data-seed.md | Hasil baseline dan information_schema Arya: database hampir kosong, B2–B5 = 0; keputusan Arya: data uji dibuat lewat script seed pink-chan |
