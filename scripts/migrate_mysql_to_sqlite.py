"""
Migrasi sekali jalan: menyalin seluruh data dari database MySQL lama ke file
SQLite yang ditunjuk `DATABASE_URL` di `.env`. Database MySQL tidak diubah.

Pemakaian (dari folder project, setelah `DATABASE_URL` di `.env` diganti ke
SQLite, misalnya `sqlite:///database/arsip.db`):
    pip install PyMySQL
    python scripts/migrate_mysql_to_sqlite.py --source "mysql+pymysql://user:sandi@localhost/nama_db"

URL sumber juga bisa diberikan lewat env `MYSQL_SOURCE_URL` agar kata sandi
tidak tersimpan di riwayat terminal. Kalau database lama masih memakai tabel
`user` (sebelum model satu pengguna), jalankan dulu
`scripts/migrate_single_user.py` terhadap MySQL tersebut.

Langkah:
1. Menolak berjalan bila database SQLite tujuan sudah berisi data.
2. Membuat semua tabel model di SQLite.
3. Menyalin tiap tabel sesuai urutan foreign key, hanya kolom yang ada di
   sumber dan tujuan, per 500 baris.
4. Memeriksa keutuhan foreign key dengan `PRAGMA foreign_key_check`.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import Table, create_engine, func, inspect, select, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
# Meng-import paket `app` mendaftarkan semua model ke Base.metadata
from app.core.database import Base, engine

BATCH_SIZE = 500

def _target_has_data(target: Connection) -> bool:
    existing = set(inspect(target).get_table_names())
    for table in Base.metadata.sorted_tables:
        if table.name in existing and target.execute(select(func.count()).select_from(table)).scalar():
            return True
    return False

def _copy_table(source: Connection, target: Connection, table: Table) -> int | None:
    source_tables = inspect(source).get_table_names()
    if table.name not in source_tables:
        return None

    source_columns = {column["name"] for column in inspect(source).get_columns(table.name)}
    columns = [column for column in table.columns if column.name in source_columns]
    result = source.execution_options(stream_results=True).execute(select(*columns))

    copied = 0
    for chunk in result.mappings().partitions(BATCH_SIZE):
        target.execute(table.insert(), [dict(row) for row in chunk])
        copied += len(chunk)
    return copied

def _check_foreign_keys(target: Connection) -> list[tuple]:
    # Tiap baris: (tabel, rowid, tabel induk, indeks foreign key)
    return target.execute(text("PRAGMA foreign_key_check")).all()

def migrate(source_url: str) -> bool:
    """Menyalin seluruh tabel model dari MySQL ke SQLite.

    Args:
        source_url: URL SQLAlchemy database MySQL sumber.

    Returns:
        True bila selesai tanpa pelanggaran foreign key; False bila dibatalkan.
    """
    source_engine = create_engine(source_url)
    Base.metadata.create_all(bind=engine)

    with engine.connect() as target:
        if _target_has_data(target):
            print(f"Database tujuan {engine.url.database} sudah berisi data. Migrasi dibatalkan.", file=sys.stderr)
            return False

        # Foreign key dimatikan selama penyalinan; PRAGMA ini diabaikan SQLite
        # di dalam transaksi, jadi transaksi pengecekan di atas ditutup dulu.
        target.commit()
        target.execute(text("PRAGMA foreign_keys=OFF"))
        with source_engine.connect() as source:
            for table in Base.metadata.sorted_tables:
                copied = _copy_table(source, target, table)
                status = "tidak ada di sumber, dilewati" if copied is None else f"{copied} baris"
                print(f"  {table.name}: {status}")
        target.commit()
        target.execute(text("PRAGMA foreign_keys=ON"))

        violations = _check_foreign_keys(target)
    source_engine.dispose()

    if violations:
        print(f"Ada {len(violations)} baris yang merujuk data induk yang tidak ada:", file=sys.stderr)
        for row in violations[:20]:
            print(f"  {row}", file=sys.stderr)
        return False
    return True

def main() -> int:
    """Menjalankan migrasi dari terminal.

    Returns:
        Kode keluar proses: 0 berhasil, 1 bila URL sumber kosong, migrasi
        dibatalkan, atau koneksi database gagal.
    """
    parser = argparse.ArgumentParser(description="Pindahkan data MySQL lama ke SQLite.")
    parser.add_argument("--source", default=os.environ.get("MYSQL_SOURCE_URL"),
                        help="URL MySQL sumber, misalnya mysql+pymysql://user:sandi@localhost/nama_db")
    args = parser.parse_args()

    if not args.source:
        print("URL MySQL sumber wajib diisi lewat --source atau env MYSQL_SOURCE_URL.", file=sys.stderr)
        return 1

    print(f"Menyalin data ke {engine.url.database}")
    try:
        ok = migrate(args.source)
    except SQLAlchemyError as e:
        print(f"Migrasi gagal: {e}", file=sys.stderr)
        return 1
    print("Migrasi selesai." if ok else "Migrasi belum selesai, periksa pesan di atas.")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
