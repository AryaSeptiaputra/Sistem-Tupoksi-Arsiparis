from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime

from evaluation.report import Row
from evaluation.seed.coverage import to_boundary_years
from evaluation.seed.plan import TABLE_ORDER, SeedParams
from evaluation.seed.repository import SeedTargetRepository
from evaluation.seed.spec import (
    ARCHIVE_STATUSES,
    CLASSIFIED_TABLES,
    DUMMY_CLASSIFICATIONS,
    IDENTITY_PREFIX,
    PRESETS,
    YEAR_SPAN,
)

# Kolom tahun dokumen per jenis ber-klasifikasi (sama dengan rumus lama dan DS4)
YEAR_COLUMNS = {
    "incoming_letter": "letter_date",
    "outgoing_letter": "letter_date",
    "finance_archive": "fiscal_year",
    "employee_archive": "document_year",
}
VOLUME_ATTRIBUTES = {
    "incoming_letter": "incoming_per_year",
    "outgoing_letter": "outgoing_per_year",
    "diploma": "diplomas_per_cohort",
    "finance_archive": "finance_per_year",
}


@dataclass(frozen=True)
class BeforeSeed:
    """Keadaan D1 sebelum seed, dipakai SY8."""

    max_ids: dict[str, int]
    row_counts: dict[str, int]
    old_row_hashes: dict[str, str]


def to_year(value: object) -> int | None:
    """Mengambil tahun dari tanggal, jejak waktu, atau angka tahun."""
    if isinstance(value, (date, datetime)):
        return value.year
    return int(value) if value is not None else None


def to_check(code: str, value: object, target: str, passed: bool) -> Row:
    """Membentuk satu baris ringkasan syarat data uji."""
    return {"syarat": code, "nilai": value, "target": target, "lulus": passed}


class SeedSummary:
    """Menilai SY1, SY6, SY8, dan SY9 dari isi D1 setelah seed (003a, syarat data uji)."""

    def __init__(self, repository: SeedTargetRepository, params: SeedParams) -> None:
        self._repository = repository
        self._params = params
        self._preset = PRESETS[params.scale]

    def _expected_volume(self, table: str) -> int:
        if table == "employee_archive":
            return self._preset.employees * self._preset.documents_per_employee
        return getattr(self._preset, VOLUME_ATTRIBUTES[table]) * YEAR_SPAN

    def _check_sy1(self, before: BeforeSeed) -> list[Row]:
        checks: list[Row] = []
        for table in CLASSIFIED_TABLES:
            rows = self._repository.fetch_rows_after(table, ["archive_status"], before.max_ids[table])
            statuses = {row["archive_status"] for row in rows}
            passed = statuses >= set(ARCHIVE_STATUSES) and len(rows) >= self._expected_volume(table)
            checks.append(to_check(f"SY1 {table}", f"{len(rows)} baris, {len(statuses & set(ARCHIVE_STATUSES))}/4 status",
                                   f"≥ {self._expected_volume(table)}, 4/4", passed))
        diplomas = self._repository.fetch_rows_after("diploma", ["academic_year", "is_collected"], before.max_ids["diploma"])
        cohorts: dict[str, set[bool]] = defaultdict(set)
        for row in diplomas:
            cohorts[str(row["academic_year"])].add(bool(row["is_collected"]))
        years = range(self._params.reference_year - YEAR_SPAN + 1, self._params.reference_year + 1)
        complete = sum(cohorts.get(f"{year - 1}/{year}") == {True, False} for year in years)
        checks.append(to_check("SY1 diploma", f"{len(diplomas)} baris, {complete}/{YEAR_SPAN} angkatan lengkap",
                               f"≥ {self._expected_volume('diploma')}, {YEAR_SPAN}/{YEAR_SPAN}",
                               len(diplomas) >= self._expected_volume("diploma") and complete == YEAR_SPAN))
        return checks

    def _check_sy6(self, before: BeforeSeed) -> Row:
        codes = {row["id"]: row["code"] for row in self._repository.fetch_rows_after(
            "classification", ["code"], before.max_ids["classification"])}
        found: set[tuple[str, str, int | None, str]] = set()
        for table, year_column in YEAR_COLUMNS.items():
            for row in self._repository.fetch_rows_after(table, ["classification_id", year_column, "archive_status"],
                                                         before.max_ids[table]):
                code = codes.get(row["classification_id"])
                found.add((table, str(code), to_year(row[year_column]), str(row["archive_status"])))
        cells = [(table, item) for table in CLASSIFIED_TABLES for item in DUMMY_CLASSIFICATIONS]
        complete = sum(
            all((table, item.code, year, status) in found
                for _, year, status in to_boundary_years(item, self._params.reference_year))
            for table, item in cells
        )
        return to_check("SY6 baris batas DS4", f"{complete}/{len(cells)}", f"{len(cells)}/{len(cells)}",
                        complete == len(cells))

    def _check_sy8(self, before: BeforeSeed, inserted: dict[str, int], old_hashes_after: dict[str, str]) -> list[Row]:
        counts_after = self._repository.count_rows()
        marked = self._repository.count_marked_rows()
        mismatched = [
            name for name in counts_after
            if counts_after[name] - before.row_counts[name] != inserted.get(name, 0)
            or (name in TABLE_ORDER and marked[name] != inserted.get(name, 0))
        ]
        return [
            to_check("SY8 baris berpenanda = baris ditambahkan", f"{len(mismatched)} tabel selisih",
                     "0 tabel selisih", not mismatched),
            to_check("SY8 hash baris lama", "sama" if old_hashes_after == before.old_row_hashes else "berbeda",
                     "sama", old_hashes_after == before.old_row_hashes),
        ]

    def _check_sy9(self, before: BeforeSeed) -> Row:
        teachers = self._repository.fetch_rows_after("teacher", ["full_name", "identity_number"], before.max_ids["teacher"])
        students = self._repository.fetch_rows_after("diploma", ["student_name"], before.max_ids["diploma"])
        violations = sum("Dummy" not in str(row["full_name"]) for row in teachers)
        violations += sum(not str(row["identity_number"]).startswith(IDENTITY_PREFIX) for row in teachers)
        violations += sum("Dummy" not in str(row["student_name"]) for row in students)
        return to_check("SY9 nama dan nomor induk", f"{violations} pelanggaran", "0 pelanggaran", violations == 0)

    def evaluate(self, before: BeforeSeed, inserted: dict[str, int], old_hashes_after: dict[str, str]) -> list[Row]:
        """Menilai SY1, SY6, SY8, dan SY9 setelah seed di-commit.

        Args:
            before: Keadaan D1 sebelum seed.
            inserted: Jumlah baris yang ditambahkan per tabel.
            old_hashes_after: Hash baris lama (id ≤ id terbesar sebelum seed) setelah seed.

        Returns:
            Baris `{syarat, nilai, target, lulus}`.

        Raises:
            DatabaseAccessError: Kalau D1 tidak bisa dibaca.
        """
        checks = self._check_sy1(before)
        checks.append(self._check_sy6(before))
        checks += self._check_sy8(before, inserted, old_hashes_after)
        checks.append(self._check_sy9(before))
        return checks
