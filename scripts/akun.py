"""
Kelola akun operator tunggal dari server.

Pemakaian (dari folder project, virtual environment aktif):
    python scripts/akun.py buat --username arsiparis --nama "Operator Arsip"
    python scripts/akun.py reset-sandi --username arsiparis

Kata sandi selalu diminta lewat prompt, tidak lewat argumen, agar tidak
tersimpan di riwayat terminal.
"""
import argparse
import getpass
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, engine
from app.models.user import User
from app.services.user import create_user, reset_password

def _ask_new_password() -> str:
    first = getpass.getpass("Kata sandi baru: ")
    second = getpass.getpass("Ulangi kata sandi baru: ")
    if first != second:
        raise ValueError("Kata sandi tidak sama.")
    return first

def create(username: str, display_name: str) -> None:
    """
    Membuat akun operator. Gagal bila sudah ada akun aktif.

    Args:
        username (str): Username login.
        display_name (str): Nama tampilan.

    Raises:
        ValueError: Dari `create_user`, atau kata sandi tidak sama.
    """
    User.__table__.create(bind=engine, checkfirst=True)
    password = _ask_new_password()
    db = SessionLocal()
    try:
        user = create_user(db, username, display_name, password)
        print(f"Akun '{user.username}' dibuat.")
    finally:
        db.close()

def reset(username: str) -> None:
    """
    Mengganti kata sandi akun tanpa kata sandi lama.

    Args:
        username (str): Username akun.

    Raises:
        ValueError: Dari `reset_password`, atau kata sandi tidak sama.
    """
    password = _ask_new_password()
    db = SessionLocal()
    try:
        user = reset_password(db, username, password)
        print(f"Kata sandi akun '{user.username}' diganti.")
    finally:
        db.close()

def main() -> int:
    parser = argparse.ArgumentParser(description="Kelola akun operator Sistem Arsip.")
    commands = parser.add_subparsers(dest="command", required=True)

    create_parser = commands.add_parser("buat", help="Buat akun operator (hanya bila belum ada akun aktif)")
    create_parser.add_argument("--username", required=True)
    create_parser.add_argument("--nama", required=True, help="Nama tampilan")

    reset_parser = commands.add_parser("reset-sandi", help="Ganti kata sandi tanpa kata sandi lama")
    reset_parser.add_argument("--username", required=True)

    args = parser.parse_args()
    try:
        if args.command == "buat":
            create(args.username, args.nama)
        else:
            reset(args.username)
    except ValueError as e:
        print(f"Gagal: {e}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
