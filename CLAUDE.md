# CLAUDE.md

## Rencana refactoring besar-besaran

Branch `refactor/major-overhaul` dipakai untuk merombak Sistem Tupoksi Arsiparis di tiga area:

1. **Desain tabel database** — merancang ulang skema tabel, relasi, constraint, dan migrasinya.
2. **Framework front-end** — mengganti front-end yang sekarang dengan framework baru.
3. **Optimisasi algoritma back-end** — memperbaiki performa dan struktur logika di `app/services` dan `app/routes`.

Pembagian kerja:

- **red-chan** merancang (skema database, arsitektur front-end, strategi optimisasi) ke `docs/keputusan-produk.md`. Tidak menulis kode.
- **pink-chan** mengeksekusi rancangan yang sudah disetujui Arya, mengikuti standar `writer-code`.

Definisi agent ada di `.claude/agents/`, skill yang mereka pakai ada di `.claude/skills/` (`product-design`, `writer-code`, `reader-code`).

## Agent pink-chan

Kalau perintah Arya diawali atau menyebut nama "pink-chan", serahkan pekerjaannya ke agent `pink-chan` — jangan dikerjakan sendiri di percakapan utama. Pink-chan melanjutkan pekerjaan bertahap lewat agent yang sama; saat Arya membalas persetujuan atau jawaban untuk pekerjaan pink-chan, teruskan balasan itu ke pink-chan.

## Agent red-chan

Kalau perintah Arya diawali atau menyebut nama "red-chan", serahkan pekerjaannya ke agent `red-chan` — jangan merancang sendiri di percakapan utama.

Red-chan bekerja per putaran. Saat laporannya berstatus `menunggu jawaban` atau `menunggu persetujuan`:

1. Tampilkan diagram gambaran sistem apa adanya di dalam blok kode (jangan digambar ulang), lalu keputusan, bentrokan, dan asumsi sebagai teks ringkas.
2. Ubah bagian "Pertanyaan / Titik periksa" menjadi `AskUserQuestion`: `[Judul]` menjadi `header`, tiap pilihan menjadi `option` dengan konsekuensinya sebagai `description`, dan pilihan (Usulan) tetap paling atas. Jangan menambah, mengurangi, atau mengubah isi pilihan.
3. Kalau statusnya `menunggu persetujuan`, tanyakan juga apakah rancangan disetujui atau ada koreksi lain.
4. Teruskan jawaban Arya ke red-chan yang sama lewat `SendMessage`, termasuk teks bebas kalau Arya memilih "Other".

Saat statusnya `selesai`, tampilkan perintah untuk pink-chan apa adanya. Jangan menjalankannya sebelum Arya sendiri mengirim perintah itu.

## red-chan dan pink-chan di mode plan

Kalau sesi sedang dalam mode plan, pekerjaan red-chan dan pink-chan tetap diserahkan ke agent-nya, dengan alur berikut:

1. Awali pesan ke agent dengan `MODE PLAN` lalu perintah Arya. Agent tidak menulis file dan mengembalikan laporan lengkap.
2. Titik periksa dari red-chan ditanyakan dulu dengan `AskUserQuestion` (aturan di atas). Teruskan jawabannya ke agent yang sama, juga diawali `MODE PLAN`, sampai tidak ada pertanyaan tersisa.
3. Salin laporan terakhir agent **apa adanya** ke file plan, termasuk diagram di dalam blok kode dan bagian "Akan ditulis/dikerjakan setelah disetujui", lalu panggil `ExitPlanMode`. Jangan meringkas atau menggambar ulang.
4. Setelah Arya menyetujui plan, kirim ke agent yang sama: `PLAN DISETUJUI`, beserta pilihan titik periksa dan koreksi Arya. Agent menulis semua file-nya.
5. Kalau Arya menolak atau mengoreksi plan, teruskan koreksinya ke agent dengan awalan `MODE PLAN`, lalu ulangi dari langkah 3.
