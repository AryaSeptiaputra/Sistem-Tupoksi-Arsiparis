from pathlib import Path

from evaluation.errors import OutputError
from evaluation.logger import setup_logger
from evaluation.seed.plan import AttachmentFile

logger = setup_logger(__name__)


class AttachmentWriter:
    """Menulis berkas lampiran seed ke `EVAL_SEED_STORAGE_ROOT` (003a DS5)."""

    def __init__(self, storage_root: Path) -> None:
        self._root = storage_root.resolve()

    def _to_target(self, relative_path: str) -> Path:
        target = (self._root / relative_path).resolve()
        if self._root not in target.parents:
            raise OutputError(f"Path lampiran keluar dari folder seed: {relative_path}")
        return target

    def save(self, files: list[AttachmentFile]) -> int:
        """Menulis semua berkas lampiran; dipanggil hanya setelah transaksi DB di-commit.

        Args:
            files: Berkas dengan path relatif ke folder seed.

        Returns:
            Jumlah berkas yang ditulis.

        Raises:
            OutputError: Kalau path keluar dari folder seed atau berkas tidak bisa ditulis.
        """
        for file in files:
            target = self._to_target(file.relative_path)
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(file.content, encoding="utf-8", newline="")
            except OSError as e:
                logger.error(f"Gagal menulis lampiran {target}: {e}", exc_info=True)
                raise OutputError(f"Lampiran tidak bisa ditulis ke {target}") from e
        return len(files)
