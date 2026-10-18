class BackupError(Exception):
    """Pembuatan backup database gagal."""


class RestoreError(Exception):
    """Pemulihan database dari file backup gagal."""


class FileStorageError(Exception):
    """Penyimpanan file lampiran ke disk gagal."""
