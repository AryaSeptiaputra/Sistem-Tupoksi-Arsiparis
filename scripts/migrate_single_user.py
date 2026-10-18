"""
Migrasi sekali jalan dari tabel `user` (3 role, terhubung ke `teacher`)
ke tabel `app_user` (satu operator, tanpa role). Hanya untuk MySQL.

Pemakaian (dari folder project, setelah backup database):
    python scripts/migrate_single_user.py
    python scripts/migrate_single_user.py --keep <username>

Langkah, semuanya aman dijalankan ulang:
1. Membuat tabel `app_user` bila belum ada.
2. Bila `app_user` masih kosong, menyalin setiap baris `user` dengan id
   yang sama: username = NIP guru, display_name = nama guru,
   aktif = status 'active' dan role 'admin' (rancangan 001a, K1).
3. Memastikan hanya satu akun aktif. Bila lebih dari satu, skrip berhenti
   dan meminta `--keep <username>` untuk memilih akun yang dipertahankan.
4. Memindahkan foreign key `log.user_id` dan `backup.user_id` dari `user`
   ke `app_user` (ON DELETE SET NULL); `log.user_id` dibuat boleh kosong.

Tabel `user` lama tidak dihapus.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from app.core.database import engine
from app.models.user import User

LINKED_TABLES = ("log", "backup")

def _copy_old_users(conn: Connection) -> int:
    if conn.execute(text("SELECT COUNT(*) FROM app_user")).scalar():
        return 0
    result = conn.execute(text(
        "INSERT INTO app_user (id, username, password_hash, display_name, is_active, created_at, updated_at) "
        "SELECT u.id, t.identity_number, u.password, LEFT(t.full_name, 100), "
        "(u.status = 'active' AND u.role = 'admin'), u.created_at, u.updated_at "
        "FROM `user` u JOIN teacher t ON t.id = u.teacher_id"
    ))
    return result.rowcount

def _keep_single_active(conn: Connection, keep: str | None) -> bool:
    if keep:
        found = conn.execute(text("SELECT id FROM app_user WHERE username = :u"), {"u": keep}).first()
        if not found:
            print(f"Username '{keep}' tidak ada di app_user.", file=sys.stderr)
            return False
        conn.execute(text("UPDATE app_user SET is_active = (username = :u)"), {"u": keep})

    active = conn.execute(text("SELECT username, display_name FROM app_user WHERE is_active = 1")).all()
    if len(active) > 1:
        print("Ada lebih dari satu akun aktif. Jalankan ulang dengan --keep <username>:", file=sys.stderr)
        for username, display_name in active:
            print(f"  {username}  ({display_name})", file=sys.stderr)
        return False
    if not active:
        print("Belum ada akun aktif. Buat dengan: python scripts/akun.py buat --username ... --nama ...")
    else:
        print(f"Akun aktif: {active[0][0]}")
    return True

def _repoint_foreign_key(conn: Connection, table: str) -> None:
    for fk in inspect(conn).get_foreign_keys(table):
        if fk["referred_table"] == "user":
            conn.execute(text(f"ALTER TABLE `{table}` DROP FOREIGN KEY `{fk['name']}`"))

    if table == "log":
        conn.execute(text("ALTER TABLE `log` MODIFY user_id INT NULL"))
    conn.execute(text(
        f"UPDATE `{table}` SET user_id = NULL "
        f"WHERE user_id IS NOT NULL AND user_id NOT IN (SELECT id FROM app_user)"
    ))

    already_linked = any(fk["referred_table"] == "app_user" for fk in inspect(conn).get_foreign_keys(table))
    if not already_linked:
        conn.execute(text(
            f"ALTER TABLE `{table}` ADD CONSTRAINT `fk_{table}_user_id_app_user` "
            f"FOREIGN KEY (user_id) REFERENCES app_user (id) ON DELETE SET NULL"
        ))
    print(f"Foreign key {table}.user_id -> app_user.id siap.")

def migrate(keep: str | None) -> bool:
    """
    Menjalankan seluruh langkah migrasi.

    Args:
        keep (str | None): Username yang tetap aktif bila ada lebih dari satu akun aktif.

    Returns:
        bool: True bila selesai; False bila berhenti karena perlu tindakan operator.
    """
    User.__table__.create(bind=engine, checkfirst=True)

    with engine.begin() as conn:
        tables = inspect(conn).get_table_names()
        if "user" in tables:
            copied = _copy_old_users(conn)
            print(f"{copied} baris disalin dari `user` ke `app_user`.")
        if not _keep_single_active(conn, keep):
            return False
        for table in LINKED_TABLES:
            if table in tables:
                _repoint_foreign_key(conn, table)
    return True

def main() -> int:
    parser = argparse.ArgumentParser(description="Migrasi akun ke model satu pengguna.")
    parser.add_argument("--keep", help="Username yang dipertahankan aktif")
    args = parser.parse_args()

    if engine.dialect.name != "mysql":
        print(f"Skrip ini hanya untuk MySQL, bukan {engine.dialect.name}.", file=sys.stderr)
        return 1
    return 0 if migrate(args.keep) else 1

if __name__ == "__main__":
    sys.exit(main())
