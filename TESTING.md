# Dokumentasi Pengujian — Sistem Tupoksi Arsiparis

Dokumen ini merangkum seluruh pengujian (testing) yang dilakukan pada project **Sistem Tupoksi Arsiparis**. Pengujian terbagi menjadi dua kelompok besar:

1. **Automated Test (pytest)** — terstruktur, berada di folder `tests/`.
2. **Manual / Integration Test Script** — skrip pengujian API & verifikasi yang dijalankan langsung, berada di root project.

---

## Tools Pengujian

| Tool | Versi | Kegunaan |
|------|-------|----------|
| **pytest** | 8.3.3 | Framework unit & integration testing |
| **pytest-cov** / **coverage** | 5.0.0 / 7.13.0 | Mengukur code coverage |
| **requests** | 2.32.5 | HTTP client untuk pengujian API endpoint |
| **Flask test_client** | (bawaan Flask) | Simulasi request tanpa menjalankan server |
| **SQLite in-memory** | — | Database sementara untuk isolasi test |

---

## 1. Automated Test (pytest) — folder `tests/`

### 1.1 `tests/test_app.py` — Smoke Test Aplikasi
Memastikan aplikasi dapat dibuat (application factory) dan berjalan.

| Test | Yang Diuji | Ekspektasi |
|------|-----------|------------|
| `test_home_page` | Akses halaman utama `/` | HTTP 302 (redirect ke halaman login) |

- Menggunakan **SQLite in-memory** (`sqlite:///:memory:`) dan environment variabel test (JWT, secret key).
- Menggunakan fixture `app` dan `client` (Flask `test_client`).

### 1.2 `tests/test_pagination.py` — Unit & Integration Test Backend
Pengujian paling lengkap, mencakup logika pagination, format response, dan performa.

**A. Pengujian Parameter Pagination (`PaginationParams`)**

| Test | Yang Diuji |
|------|-----------|
| `test_pagination_params_default` | Nilai default (page=1, per_page=20, sort=id asc) |
| `test_pagination_params_custom` | Parameter custom + perhitungan `offset` |
| `test_pagination_params_max_per_page` | Batas maksimum `per_page` di-cap ke 100 |
| `test_pagination_params_min_page` | Page minimum default ke 1 |
| `test_pagination_params_invalid_sort_order` | Sort order tidak valid default ke `asc` |
| `test_pagination_params_to_dict` | Konversi parameter ke dictionary |

**B. Pengujian Query Pagination (`paginate_query`)**

| Test | Yang Diuji |
|------|-----------|
| `test_paginate_query_first_page` | Halaman pertama (has_next=True, has_prev=False) |
| `test_paginate_query_last_page` | Halaman terakhir (has_next=False, has_prev=True) |
| `test_paginate_query_middle_page` | Halaman tengah (has_next & has_prev True) |
| `test_paginate_query_to_dict` | Struktur hasil (`data` + `pagination`) |

> Menggunakan fixture `sample_data` yang membuat **150 record** `IncomingLetter`.

**C. Pengujian Format Response (`response.py`)**

| Test | Yang Diuji |
|------|-----------|
| `test_success_response` | Format response sukses (success, message, data) |
| `test_error_response` | Format response error (HTTP 404) |
| `test_error_response_with_details` | Response error dengan detail validasi (HTTP 422) |

**D. Pengujian Ekstraksi Parameter dari Request**

| Test | Yang Diuji |
|------|-----------|
| `test_get_pagination_params_from_request` | Ambil parameter dari query string |
| `test_get_pagination_params_defaults` | Nilai default saat parameter tidak ada |

**E. Integration Test Endpoint API**

| Test | Yang Diuji |
|------|-----------|
| `test_get_all_endpoint_with_pagination` | Endpoint `/incoming_letter/get_all` dengan pagination |
| `test_get_all_endpoint_default_page` | Default ke page 1 |
| `test_get_by_keys_with_filter` | Endpoint `/incoming_letter/get_by_keys` dengan filter |

**F. Performance Test**

| Test | Yang Diuji | Ekspektasi |
|------|-----------|------------|
| `test_pagination_large_dataset` | Pagination dengan **1000 record** | Waktu query < 100ms |

---

## 2. Manual / Integration Test Script (root project)

Skrip-skrip ini dijalankan manual (`python <nama_file>.py`) terhadap server yang berjalan di `http://127.0.0.1:8000`, terutama saat debugging modul **Finance Archive**.

### 2.1 Pengujian Koneksi Database

| File | Yang Diuji |
|------|-----------|
| `test_finance.py` | Menghitung & menampilkan record `FinanceArchive` langsung dari database |
| `test_finance_json.py` | Serialisasi data `FinanceArchive` ke JSON (`to_dict()`) |
| `test_references.py` | Verifikasi data master reference (`finance_category`, `archive_status`) di database |

### 2.2 Pengujian API Endpoint

| File | Yang Diuji |
|------|-----------|
| `test_api_response.py` | Response mentah endpoint `/finance_archive/get_all` (status, content-type, JSON) |
| `test_api_consistency.py` | Konsistensi format response antara Finance Archive (array) vs Incoming Letter (object + pagination) |
| `test_simple_api.py` | Konektivitas server & response API tanpa autentikasi (cek 401, struktur data) |

### 2.3 Pengujian Autentikasi & Alur Lengkap

| File | Yang Diuji |
|------|-----------|
| `test_auth_and_api.py` | Membuat test user → login → akses Finance Archive & Reference API dengan token JWT |
| `test_with_auth.py` | Login (NUPTK + password) → uji Finance Archive & Master Reference API ber-token |
| `test_complete_flow.py` | Alur penuh: login → ambil data finance, references, classification, storage location → uji logika filter (kategori, status, tahun, pencarian teks) |
| `test_js_flow.py` | Simulasi persis alur JavaScript frontend (`loadReferences`, `loadClassifications`, `loadStorageLocations`, `loadArchives`) |
| `test_final_verification.py` | Verifikasi render halaman HTML (elemen `view-table`, tombol, dropdown), urutan loading script JS, dan pengecekan seluruh API yang dibutuhkan halaman |

---

## Cara Menjalankan Pengujian

### Automated Test (pytest)
```bash
# Jalankan seluruh test
pytest -v

# Jalankan test tertentu
pytest tests/test_pagination.py -v

# Jalankan dengan coverage report
pytest --cov=app --cov-report=html
```

### Manual Test Script
```bash
# Pastikan server berjalan lebih dahulu (python serve.py / main.py)
# Lalu jalankan skrip yang diinginkan
python test_complete_flow.py
python test_with_auth.py
```

---

## Cakupan Pengujian (Coverage)

| Aspek | Status | Keterangan |
|-------|--------|------------|
| Application bootstrap | ✅ | `test_app.py` |
| Pagination logic | ✅ | Unit test lengkap |
| Response formatting | ✅ | Success & error response |
| Performance | ✅ | Dataset besar (1000 record) |
| Autentikasi (JWT) | ✅ | Via integration script |
| API CRUD endpoint | ⚠️ | Sebagian (fokus Finance Archive & read endpoint) |
| Database query | ✅ | Via script langsung |
| Frontend rendering | ⚠️ | Verifikasi HTML statis (bukan automated browser test) |

> **Catatan:** Skrip pada bagian 2 bersifat manual/debugging dan bukan automated test pytest. Untuk pengujian CI/CD yang andal, disarankan memindahkan logika verifikasinya ke dalam struktur pytest dengan mock autentikasi.
