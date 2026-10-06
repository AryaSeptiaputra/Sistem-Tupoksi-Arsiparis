from pathlib import Path

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

from evaluation.errors import SeedGuardError
from evaluation.report import Row
from evaluation.seed.spec import REQUIRED_REFERENCE_CATEGORIES, SEED_EMPTY_TABLES

# Nama host yang sama-sama menunjuk mesin lokal
LOCAL_HOSTS = frozenset({"", "localhost", "127.0.0.1", "::1"})
DEFAULT_PORTS = {"mysql": 3306}


def to_database_key(url: str, setting_name: str) -> tuple[str, str, int | None, str]:
    """Mengubah URL database menjadi kunci (backend, host, port, database) untuk dibandingkan.

    User dan kata sandi diabaikan. Host lokal disamakan, port kosong diisi port bawaan,
    dan nama database dibandingkan tanpa membedakan huruf besar (MySQL di Windows).
    Untuk SQLite, kuncinya path berkas yang sudah di-resolve.

    Args:
        url: URL SQLAlchemy.
        setting_name: Nama setting asal URL, untuk pesan error.

    Returns:
        Kunci pembanding.

    Raises:
        SeedGuardError: Kalau URL kosong atau tidak valid.
    """
    if not url:
        raise SeedGuardError(f"{setting_name} kosong; penjaga seed tidak bisa memeriksa target")
    try:
        parsed = make_url(url)
    except ArgumentError:
        raise SeedGuardError(f"{setting_name} bukan URL database yang valid") from None
    backend = parsed.get_backend_name()
    if backend == "sqlite":
        return backend, "", None, str(Path(parsed.database or "").resolve())
    host = (parsed.host or "").lower()
    host = "localhost" if host in LOCAL_HOSTS else host
    return backend, host, parsed.port or DEFAULT_PORTS.get(backend), (parsed.database or "").casefold()


def validate_seed_target(seed_url: str, old_url: str, app_url: str) -> None:
    """Memastikan seed hanya menulis ke D1 dan tidak ke database aplikasi (003a DS1).

    Args:
        seed_url: `EVAL_SEED_DB_URL`.
        old_url: `EVAL_OLD_DB_URL` (D1 yang dibaca baseline).
        app_url: `DATABASE_URL` aplikasi.

    Raises:
        SeedGuardError: Kalau salah satu URL kosong, target sama dengan database aplikasi
            (termasuk nama database yang sama di host mana pun), atau target bukan D1.
    """
    seed_key = to_database_key(seed_url, "EVAL_SEED_DB_URL")
    old_key = to_database_key(old_url, "EVAL_OLD_DB_URL")
    app_key = to_database_key(app_url, "DATABASE_URL")
    if seed_key == app_key or (seed_key[0] == app_key[0] and seed_key[3] == app_key[3]):
        raise SeedGuardError("EVAL_SEED_DB_URL menunjuk database aplikasi (DATABASE_URL); seed dihentikan")
    if seed_key != old_key:
        raise SeedGuardError("EVAL_SEED_DB_URL harus menunjuk database yang sama dengan EVAL_OLD_DB_URL (D1)")


def _is_same_or_nested(first: Path, second: Path) -> bool:
    return first == second or first in second.parents or second in first.parents


def validate_seed_storage_root(storage_root: str, app_storage_dirs: list[Path]) -> Path:
    """Memastikan folder lampiran seed diisi dan terpisah dari folder storage aplikasi (003a DS1).

    Args:
        storage_root: `EVAL_SEED_STORAGE_ROOT`.
        app_storage_dirs: Folder storage yang dipakai aplikasi lama.

    Returns:
        Folder lampiran seed yang sudah di-resolve.

    Raises:
        SeedGuardError: Kalau kosong, sama dengan, berada di dalam, atau memuat folder storage aplikasi.
    """
    if not storage_root.strip():
        raise SeedGuardError("EVAL_SEED_STORAGE_ROOT wajib diisi, misalnya data/evaluation/storage_d1")
    root = Path(storage_root).resolve()
    for app_dir in app_storage_dirs:
        if _is_same_or_nested(root, app_dir.resolve()):
            raise SeedGuardError(f"EVAL_SEED_STORAGE_ROOT bersinggungan dengan folder storage aplikasi {app_dir}")
    return root


def validate_target_state(archive_counts: dict[str, int], has_marked_rows: bool, references: list[Row]) -> None:
    """Memastikan isi D1 siap di-seed; semua masalah dilaporkan sekaligus (003a DS1).

    Args:
        archive_counts: Jumlah baris lima tabel arsip dan `storage_location`.
        has_marked_rows: Apakah sudah ada baris berpenanda DUMMY atau ANOMALI-.
        references: Baris `master_reference` dengan kunci `category`.

    Raises:
        SeedGuardError: Kalau ada tabel yang tidak kosong, sudah ada penanda, atau kategori
            referensi wajib kosong.
    """
    problems = [f"tabel {name} berisi {archive_counts.get(name, 0)} baris"
                for name in SEED_EMPTY_TABLES if archive_counts.get(name, 0) > 0]
    if has_marked_rows:
        problems.append("sudah ada baris berpenanda DUMMY/ANOMALI- (seed pernah dijalankan)")
    categories = {row["category"] for row in references}
    problems += [f"kategori master_reference {name} kosong"
                 for name in REQUIRED_REFERENCE_CATEGORIES if name not in categories]
    if problems:
        raise SeedGuardError("Seed dihentikan sebelum menulis: " + "; ".join(problems))


def validate_plan_columns(rows_by_table: dict[str, list[Row]], column_names: dict[str, set[str]],
                          column_lengths: dict[tuple[str, str], int]) -> None:
    """Memastikan setiap kolom plan ada di D1 dan setiap teks muat di kolomnya, sebelum menulis.

    Args:
        rows_by_table: Nilai kolom plan per tabel.
        column_names: Nama kolom D1 per tabel (hasil reflect).
        column_lengths: Panjang maksimal kolom teks D1 per (tabel, kolom).

    Raises:
        SeedGuardError: Kalau ada kolom yang tidak dikenal atau teks yang terlalu panjang;
            pesan menyebut tabel, kolom, dan panjangnya, tanpa isi nilai.
    """
    problems: list[str] = []
    for table, rows in rows_by_table.items():
        unknown = sorted({column for row in rows for column in row} - column_names.get(table, set()))
        problems += [f"kolom {table}.{column} tidak ada di D1" for column in unknown]
        for (length_table, column), limit in column_lengths.items():
            if length_table != table:
                continue
            longest = max((len(row[column]) for row in rows if isinstance(row.get(column), str)), default=0)
            if longest > limit:
                problems.append(f"{table}.{column} butuh {longest} karakter, kolom D1 hanya {limit}")
    if problems:
        raise SeedGuardError("Plan seed tidak cocok dengan skema D1: " + "; ".join(problems))
