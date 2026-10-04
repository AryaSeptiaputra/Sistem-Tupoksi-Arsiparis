# Template: Riset & Training Model (notebook-only)

Dipakai untuk project yang tujuannya mencari jawaban, bukan melayani pengguna: melatih model, fine-tune, atau membandingkan beberapa pendekatan untuk memilih yang terbaik.

Seluruh kode hidup di notebook. Tidak ada `app/`, `src/`, `tests/`, `scripts/`, `configs/`, `config.py`, atau `.env`. Pembaca, misalnya penguji skripsi atau reviewer paper, membuka satu notebook dan melihat seluruh langkahnya dari atas ke bawah tanpa melompat ke file lain. Contoh rujukannya adalah `C:\Penelitian\IndoBERT-with-RAC`.

**File lain untuk pekerjaan lain:**
- Menyajikan model yang sudah jadi: `structure-api-model.md`
- Chatbot yang melayani pengguna: `structure-ai-app.md`
- Menyiapkan data sebagai pekerjaan utama: `structure-pipeline.md`

---

## Bentuk foldernya

```
project-name/
├── notebooks/                    # seluruh kode; dijalankan dari folder ini
│   ├── 01_eda.ipynb              # melihat data, mengunci keputusan preprocessing
│   ├── 02_preprocessing.ipynb    # membangun split siap latih
│   ├── 03a_<skenario_a>.ipynb    # satu notebook per skenario atau pendekatan
│   ├── 03b_<skenario_b>.ipynb
│   ├── 05_final_benchmark.ipynb  # satu-satunya notebook yang membuka split test
│   ├── 06_artifacts.ipynb        # gambar dan data tabel untuk laporan
│   └── 07_archive.ipynb          # membungkus outputs/ sebelum mesin dimatikan
├── tuning_grids/                 # rancangan percobaan
│   ├── <SKENARIO>_TUNING_GRID.md     # penalaran rentang yang dicoba
│   └── <SKENARIO>_TUNING_GRID.csv    # satu baris per konfigurasi, kolom `catatan`
├── data/
│   ├── raw/                      # data asli, jangan pernah diubah
│   ├── interim/
│   └── processed/                # train.csv, val.csv, test.csv, metadata.json
├── outputs/                      # di-gitignore, kecuali README dan figur EDA
│   ├── tuning/                   # runs_*.csv, best.json, history/, checkpoints/, features/, hardware.json
│   ├── metrics/                  # hasil benchmark final
│   ├── artifacts/                # gambar dan data tabel laporan
│   └── notebooks_eksekusi/       # salinan notebook beserta keluarannya, untuk bukti
├── models/
├── docs/
├── CLAUDE.md                     # tabel fungsi tersalin dan kontrak berkas
├── PROGRESS.md                   # status kampanye dan ringkasan angka
├── requirements.txt / requirements-dev.txt
└── README.md
```

Nomor notebook menunjukkan urutan menjalankan. Huruf (`03a`, `03b`) dipakai untuk skenario yang setingkat. Nomor yang belum dipakai boleh dibiarkan kosong supaya urutan lama tidak bergeser.

---

## Empat aturan wajib

1. **Notebook terhubung hanya lewat berkas.** Tidak ada import antar-notebook. Notebook membaca keluaran notebook sebelumnya dari `data/` dan `outputs/`. Kolom CSV, kunci JSON, dan isi checkpoint adalah kontrak; mengubahnya berarti mengubah seluruh pembacanya.
2. **Angka percobaan disimpan, bukan diingat.** Setiap run menambah satu baris di `outputs/tuning/runs_<skenario>.csv` beserta `run_id`, seluruh hyperparameter, seed, metrik, waktu, dan kolom `catatan` (alasan konfigurasi dicoba). Berkas ini menumpuk lintas sesi dan tidak pernah ditimpa.
3. **Split test hanya dibuka di notebook benchmark final.** Seleksi hyperparameter memakai validation. Kandidat juara dikunci ke berkas (cap waktu dan hash isi) sebelum test dibuka, dan notebook final berhenti kalau hash-nya tidak cocok.
4. **Catat seed dan lingkungan.** Seed ada di sel konstanta dan di setiap baris run. Versi Python, library, GPU, dan driver dicatat ke `hardware.json`. Angka efisiensi (waktu latih, latency, memori) hanya sah dari satu hardware dan satu sesi, jadi notebook final memeriksa bahwa lingkungannya sama dengan saat tuning.

---

## Cara menulis notebook

### Sel pembuka

1. **Sel markdown pertama:** judul `# NN - Nama: tujuan`, alur tahap dalam satu kalimat, daftar berkas keluaran, dan prasyarat (notebook mana yang harus sudah dijalankan).
2. **Sel kode pertama berisi seluruh konstanta:** path relatif `../`, nama kolom, nama model, seed, ambang, konfigurasi bawaan (`DEFAULT_CONFIG`). Huruf besar semua, masing-masing dengan komentar satu baris. Tidak ada angka atau path yang ditulis langsung di sel lain.

```python
from pathlib import Path

# Split siap latih dan metadata.json (class weight) dari 02_preprocessing
PROCESSED_DIR = Path("../data/processed")
# Folder keluaran kampanye, sama untuk seluruh notebook skenario
OUT_DIR = Path("../outputs/tuning")

RANDOM_SEED = 42
# Selisih F1 di bawah ambang ini dihitung seri, konfigurasi yang lebih murah menang
TIE_THRESHOLD_PP = 0.15
```

### Sel tahap

Setiap tahap adalah pasangan sel:

1. **Markdown** `## n. Judul tahap`, diikuti alasan keputusan di tahap itu bila ada. Bukan narasi langkah yang sudah terbaca dari kodenya.
2. **Kode** dengan urutan: import yang baru dibutuhkan di sel itu, konstanta yang hanya dipakai sel itu (misalnya regex beserta komentarnya), definisi fungsi, lalu pemanggilan langsung di bawahnya. Keluaran untuk pembaca memakai `print` atau `display`.

```python
import pandas as pd


def load_splits(processed_dir: Path) -> dict[str, pd.DataFrame]:
    """Baca split train, val, dan test hasil 02_preprocessing."""
    return {name: pd.read_csv(processed_dir / f"{name}.csv") for name in ["train", "val", "test"]}


splits = load_splits(PROCESSED_DIR)
print({name: len(frame) for name, frame in splits.items()})
```

Fungsi ditulis di sel yang pertama kali memakainya. Sel berikutnya boleh memanggil fungsi dari sel sebelumnya di notebook yang sama.

### Fungsi

Bagian 2 `SKILL.md` tetap berlaku untuk fungsi di notebook: peran dan awalan nama (`load_`, `save_`, `build_`, `to_`, `compute_`, `is_`), docstring Google style, komentar wajib di regex dan format waktu, type hint di semua parameter dan nilai kembalian, badan maksimal 50 baris. Yang berbeda:

| Aturan umum | Di notebook-only |
|---|---|
| Class untuk proses dan pengakses luar | Fungsi biasa. Class hanya untuk `nn.Module` atau state yang benar-benar perlu disimpan |
| Error milik project di `errors.py` | Exception bawaan yang spesifik (`ValueError`, `FileNotFoundError`) dengan pesan yang menyebut nilai penyebabnya |
| `logging` lewat `setup_logger` | `print` dan `display` |
| Setting dari `config.py` dan `.env` | Sel konstanta |
| Test di `tests/` | Notebook dijalankan ulang dari atas sampai bawah tanpa error |

### Fungsi yang dipakai beberapa notebook

Fungsi **disalin**, tidak di-import. Setiap salinan harus identik. Daftarnya dicatat di `CLAUDE.md` project:

```markdown
| Fungsi | Ada di |
|---|---|
| `load_tokenizer` | 01, 02, 03a, 03b, 05 |
| `compute_metrics` | 03a, 03b, 03c, 05, 06 |
```

Saat mengubah salah satu salinan, ubah semua salinannya dalam pekerjaan yang sama, lalu perbarui tabel itu kalau ada notebook yang mulai atau berhenti memakai fungsinya.

### Menulis berkas

- JSON: UTF-8, `ensure_ascii=False`, indentasi 2.
- CSV: UTF-8, tanpa index, ujung baris LF (`lineterminator="\n"`). Hash dan checksum dihitung dari isi kanonik, bukan dari byte berkas, karena ujung baris berbeda antar OS.
- Data siap latih tidak boleh ditimpa tanpa gate checksum: notebook preprocessing membandingkan isi split baru dengan yang lama dan berhenti kalau berbeda. Split yang berubah membuat seluruh riwayat run kehilangan pasangannya.

---

## Rancangan percobaan di `tuning_grids/`

- Yang diubah antar percobaan ada di CSV grid, bukan di kode. Notebook membaca grid dan menjalankan setiap barisnya; kolom yang kosong memakai nilai `DEFAULT_CONFIG`.
- Setiap CSV punya `.md` pasangannya yang menjelaskan kenapa rentang itu dipilih.
- Grid bertahap (`_STAGE2`, `_STAGE3`) diisi setelah tahap sebelumnya selesai dan dibaca hasilnya. Satu sel notebook menjalankan satu tahap.
- Tidak ada resume otomatis. Kalau terputus, jalankan ulang hanya baris yang belum tercatat di `runs_*.csv`.
- Pemenang di tepi rentang grid adalah tanda untuk melebarkan rentang, bukan untuk mengunci.

---

## Saat fase MVP

Mulai dari tiga notebook:

1. `01_eda.ipynb`: lihat data, tentukan kunci dedup, panjang maksimum, dan ketimpangan kelas
2. `02_preprocessing.ipynb`: bangun split train/val/test, simpan dengan `metadata.json`
3. `03a_<skenario>.ipynb`: satu skenario dengan `DEFAULT_CONFIG`, hasilnya dicatat ke `runs_<skenario>.csv`

Belum perlu `tuning_grids/`, benchmark final, atau tabel fungsi tersalin.

---

## Saat fase Dev, aturan pertumbuhan

1. **Pendekatan baru jadi notebook baru atau baris grid baru**, bukan cabang `if` di notebook lama. Skenario setingkat mendapat huruf berikutnya (`03b`, `03c`).
2. **Percobaan mulai banyak, buat `tuning_grids/`.** Pindahkan konfigurasi dari sel ke CSV grid.
3. **Fungsi dipakai notebook kedua, salin dan catat** di tabel `CLAUDE.md`.
4. **Hasil mulai dilaporkan, tambah notebook final, artefak, dan arsip** (`05`, `06`, `07`). Notebook final memeriksa lingkungan dan hash kandidat sebelum membuka test.

---

## Saat fase Production

Model hasil riset yang akan dipakai sistem lain tidak dijalankan dari project ini. Simpan model beserta catatan versinya, lalu sajikan lewat project terpisah memakai `structure-api-model.md`. Fungsi yang dibutuhkan saat inferensi (misalnya pembersihan teks dan pembentukan model) disalin ke project itu dan ditulis ulang mengikuti aturan `app/`, termasuk test-nya.
