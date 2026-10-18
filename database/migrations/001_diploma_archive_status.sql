-- Menambah status arsip ke tabel diploma agar ijazah yang dimusnahkan
-- tidak muncul lagi di daftar kedaluwarsa. Jalankan sekali pada database
-- yang dibuat sebelum kolom ini ada; database baru sudah dibuat oleh create_all.
ALTER TABLE diploma ADD COLUMN archive_status VARCHAR(20) NOT NULL DEFAULT 'active';
