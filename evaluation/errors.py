class EvaluationError(Exception):
    """Induk semua error alat evaluasi."""


class DatabaseAccessError(EvaluationError):
    """Database evaluasi tidak bisa dibuka atau dibaca."""


class LegacyCodeError(EvaluationError):
    """Kode aplikasi lama gagal di-import atau gagal dijalankan."""


class OutputError(EvaluationError):
    """Hasil evaluasi tidak bisa disimpan."""
