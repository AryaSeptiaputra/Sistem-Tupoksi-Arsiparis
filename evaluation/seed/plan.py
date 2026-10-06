import random
from dataclasses import dataclass

from evaluation.baseline.rules import strip_storage_prefix
from evaluation.report import Row
from evaluation.seed.anomalies import build_anomaly_rows
from evaluation.seed.coverage import build_boundary_rows, build_coverage_rows, build_people_rows
from evaluation.seed.fill import assign_attachments, build_fill_rows
from evaluation.seed.rows import Ref, RowFactory, SeedRow
from evaluation.seed.spec import DEFAULT_REFERENCE_YEAR, DEFAULT_SEED, PRESETS

# Urutan insert tabel: induk sebelum anak (FK)
TABLE_ORDER = (
    "classification",
    "storage_location",
    "teacher",
    "user",
    "incoming_letter",
    "outgoing_letter",
    "diploma",
    "finance_archive",
    "employee_archive",
)
# Kunci simbolik yang dirujuk tabel lain
KEYED_TABLES = ("classification", "storage_location", "teacher")


@dataclass(frozen=True)
class SeedParams:
    """Parameter satu jalan seed (003a DS2)."""

    scale: str
    anomalies: bool = False
    seed: int = DEFAULT_SEED
    reference_year: int = DEFAULT_REFERENCE_YEAR


@dataclass(frozen=True)
class AttachmentFile:
    """Berkas lampiran yang ditulis setelah commit, relatif ke `EVAL_SEED_STORAGE_ROOT`."""

    relative_path: str
    content: str


@dataclass
class SeedPlan:
    """Semua baris (id dan FK sudah berupa angka) dan berkas lampiran satu jalan seed."""

    rows: list[SeedRow]
    files: list[AttachmentFile]

    def rows_for(self, table: str) -> list[Row]:
        """Mengambil nilai kolom baris satu tabel, urut sesuai insert.

        Args:
            table: Nama tabel lama.

        Returns:
            Nilai kolom per baris, termasuk `id`.
        """
        return [row.values for row in self.rows if row.table == table]


def to_reference_map(references: list[Row]) -> dict[str, list[tuple[str, str]]]:
    """Mengelompokkan baris `master_reference` per kategori, urut sesuai id.

    Args:
        references: Baris `{id, category, code, name}`.

    Returns:
        Pasangan (code, name) per kategori.
    """
    grouped: dict[str, list[tuple[str, str]]] = {}
    for row in sorted(references, key=lambda item: int(item["id"])):
        grouped.setdefault(str(row["category"]), []).append((str(row["code"] or ""), str(row["name"] or "")))
    return grouped


def _assign_ids(rows: list[SeedRow], max_ids: dict[str, int]) -> None:
    next_ids = {table: max_ids.get(table, 0) + 1 for table in TABLE_ORDER}
    keys: dict[Ref, int] = {}
    for table in TABLE_ORDER:
        for row in (item for item in rows if item.table == table):
            row.values["id"] = next_ids[table]
            next_ids[table] += 1
            if table in KEYED_TABLES and row.key is not None:
                keys[Ref(table, row.key)] = int(row.values["id"])
    for row in rows:
        for column, value in row.values.items():
            if isinstance(value, Ref):
                row.values[column] = keys[value]


def _to_files(rows: list[SeedRow]) -> list[AttachmentFile]:
    return [
        AttachmentFile(strip_storage_prefix(str(row.values["attachment_path"])),
                       f"DUMMY lampiran {row.table} {row.values['id']}\n")
        for row in rows
        if row.values.get("attachment_path") and not row.meta.get("attachment_missing")
    ]


def _order(rows: list[SeedRow]) -> list[SeedRow]:
    position = {table: index for index, table in enumerate(TABLE_ORDER)}
    return sorted(rows, key=lambda row: position[row.table])


def build_seed_plan(params: SeedParams, references: list[Row], max_ids: dict[str, int]) -> SeedPlan:
    """Merakit plan seed lengkap dari satu generator acak (003a DS2–DS7).

    Urutan: klasifikasi, lokasi, pegawai, akun → baris batas DS4 → cakupan C1–C7 →
    isian → lampiran → anomali (opsional) → id dan FK. Anomali diundi paling akhir,
    sehingga baris non-anomali sama persis dengan atau tanpa `--anomali`.

    Args:
        params: Parameter seed.
        references: Baris `master_reference` D1.
        max_ids: id terbesar per tabel lama sebelum seed (0 kalau kosong).

    Returns:
        Plan berurutan sesuai `TABLE_ORDER`.

    Raises:
        KeyError: Kalau `params.scale` bukan nama preset.
    """
    preset = PRESETS[params.scale]
    rng = random.Random(params.seed)
    factory = RowFactory(rng, to_reference_map(references), params.reference_year)
    owners = list(range(1, preset.employees + 1))

    rows = factory.build_classification_rows() + factory.build_location_rows()
    rows += build_people_rows(factory, preset.employees)
    rows += build_boundary_rows(factory, params.reference_year, owners)
    rows += build_coverage_rows(factory, params.reference_year, owners)
    rows += build_fill_rows(factory, rng, preset, params.reference_year)
    assign_attachments(rng, rows)
    if params.anomalies:
        rows += build_anomaly_rows(factory, params.reference_year, preset.employees + 1)

    ordered = _order(rows)
    _assign_ids(ordered, max_ids)
    return SeedPlan(rows=ordered, files=_to_files(ordered))
