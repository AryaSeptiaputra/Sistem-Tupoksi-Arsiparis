import csv
import io
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from evaluation.errors import OutputError
from evaluation.logger import setup_logger

logger = setup_logger(__name__)

SOURCES = ("dummy", "nyata")

Row = dict[str, object]


def validate_source(source: str) -> None:
    """Memastikan sumber data hanya `dummy` atau `nyata` (Gate 5).

    Args:
        source: Sumber data putaran ini.

    Raises:
        ValueError: Kalau nilainya di luar `dummy` dan `nyata`.
    """
    if source not in SOURCES:
        raise ValueError(f"Sumber data harus salah satu dari {SOURCES}, bukan {source!r}")


def is_id_column(name: str) -> bool:
    """Menjawab apakah nama kolom menandakan id.

    Args:
        name: Nama kolom.

    Returns:
        `True` untuk `id`, `<x>_id`, atau `id_<x>`.
    """
    return name == "id" or name.endswith("_id") or name.startswith("id_")


def _is_numeric_column(rows: list[Row], name: str) -> bool:
    values = [row.get(name) for row in rows if row.get(name) is not None]
    return all(isinstance(value, (int, float, Decimal)) for value in values)


def to_columns(rows: list[Row]) -> list[str]:
    """Mengumpulkan nama kolom dari semua baris, urut sesuai kemunculan pertama.

    Args:
        rows: Baris hasil pengukuran.

    Returns:
        Nama kolom tanpa duplikat.
    """
    return list(dict.fromkeys(name for row in rows for name in row))


def to_safe_rows(rows: list[Row], label_columns: set[str] | None = None) -> list[Row]:
    """Menyisakan kolom angka, id, dan kolom label yang dinyatakan aman (Gate 4, data nyata).

    Args:
        rows: Baris lengkap.
        label_columns: Kolom berisi nama tabel, status, atau butir yang bukan data
            pribadi, ditetapkan oleh pemanggil.

    Returns:
        Baris yang hanya memuat kolom aman.
    """
    labels = label_columns or set()
    kept = [
        name
        for name in to_columns(rows)
        if name in labels or is_id_column(name) or _is_numeric_column(rows, name)
    ]
    return [{name: row.get(name) for name in kept} for row in rows]


def _to_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def format_table(rows: list[Row], columns: list[str] | None = None) -> str:
    """Menyusun baris menjadi tabel teks rata kiri untuk terminal.

    Args:
        rows: Baris yang ditampilkan.
        columns: Urutan kolom; default semua kolom sesuai kemunculan.

    Returns:
        Tabel teks, atau `(kosong)` kalau tidak ada baris.
    """
    if not rows:
        return "(kosong)"
    names = columns or to_columns(rows)
    cells = [[_to_cell(row.get(name)) for name in names] for row in rows]
    widths = [max(len(name), *(len(line[i]) for line in cells)) for i, name in enumerate(names)]
    header = "  ".join(name.ljust(width) for name, width in zip(names, widths))
    divider = "  ".join("-" * width for width in widths)
    body = ["  ".join(cell.ljust(width) for cell, width in zip(line, widths)) for line in cells]
    return "\n".join([header, divider, *body])


class ResultWriter:
    """Menyimpan hasil satu putaran ke `<output_root>/<tanggal jalan>/<dummy|nyata>/`."""

    def __init__(self, output_root: Path, run_date: date, source: str) -> None:
        validate_source(source)
        self._source = source
        self.directory = output_root / run_date.isoformat() / source

    def _write_text(self, file_name: str, content: str) -> Path:
        path = self.directory / file_name
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="")
        except OSError as e:
            logger.error(f"Gagal menulis {path}: {e}", exc_info=True)
            raise OutputError(f"Hasil tidak bisa disimpan ke {path}") from e
        return path

    def save_table(self, name: str, rows: list[Row], label_columns: set[str] | None = None) -> Path:
        """Menyimpan satu tabel hasil sebagai CSV.

        Untuk sumber `nyata`, hanya kolom angka, id, dan `label_columns` yang disimpan.

        Args:
            name: Nama berkas tanpa ekstensi.
            rows: Baris hasil.
            label_columns: Kolom label yang aman disimpan untuk data nyata.

        Returns:
            Path berkas CSV.

        Raises:
            OutputError: Kalau berkas tidak bisa ditulis.
        """
        stored = to_safe_rows(rows, label_columns) if self._source == "nyata" else rows
        columns = to_columns(stored)
        buffer = io.StringIO()
        if columns:
            writer = csv.writer(buffer, lineterminator="\n")
            writer.writerow(columns)
            writer.writerows([[_to_cell(row.get(name)) for name in columns] for row in stored])
        return self._write_text(f"{name}.csv", buffer.getvalue())

    def save_meta(self, meta: Row, name: str = "meta") -> Path:
        """Menyimpan keterangan putaran sebagai `<name>.json`.

        Args:
            meta: Keterangan putaran; URL database harus sudah tanpa kata sandi.
            name: Nama berkas tanpa ekstensi; default `meta` (baseline).

        Returns:
            Path berkas JSON.

        Raises:
            OutputError: Kalau berkas tidak bisa ditulis.
        """
        content = json.dumps({**meta, "sumber": self._source}, ensure_ascii=False, indent=2, default=_to_cell)
        return self._write_text(f"{name}.json", content + "\n")

