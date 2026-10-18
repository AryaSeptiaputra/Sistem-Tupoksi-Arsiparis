"""Bentuk respons JSON standar untuk endpoint.

`data` pada `success_response` bisa berupa dict, list, atau `PaginatedResult`,
jadi diberi tipe `Any`.
"""

from typing import Any
from flask import Response, jsonify

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def success_response(data: Any = None, message: str = "Success",
                    status_code: int = 200) -> tuple[Response, int]:
    """Membentuk respons sukses.

    Args:
        data: Isi respons. Object yang punya `to_dict()` (misalnya
            `PaginatedResult`) digabung ke akar respons; selain itu
            diletakkan di kunci `data`.
        message: Pesan sukses.
        status_code: Status HTTP.

    Returns:
        Pasangan (respons JSON, status HTTP).
    """
    response = {
        "success": True,
        "message": message
    }

    if hasattr(data, 'to_dict'):
        response.update(data.to_dict())
    elif data is not None:
        response["data"] = data

    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400,
                   errors: dict[str, Any] | None = None) -> tuple[Response, int]:
    """Membentuk respons gagal.

    Args:
        message: Pesan error.
        status_code: Status HTTP.
        errors: Rincian error tambahan.

    Returns:
        Pasangan (respons JSON, status HTTP).
    """
    response = {
        "success": False,
        "message": message
    }

    if errors:
        response["errors"] = errors

    return jsonify(response), status_code










def handle_database_error(exception: Exception, operation: str = "menyimpan") -> tuple[Response, int]:
    """Mencatat error database dan mengubahnya menjadi pesan untuk pengguna.

    Pesan dipilih dari kode error MySQL: 1062 duplikat, 1451/1452 foreign
    key, 1406 data terlalu panjang, 1048 kolom wajib kosong.

    Args:
        exception: Exception yang ditangkap di route.
        operation: Kata kerja operasi untuk pesan, misalnya `menyimpan`.

    Returns:
        Pasangan (respons JSON, status HTTP): 400 untuk kesalahan data,
        500 untuk selainnya.
    """
    logger.error(f"Gagal {operation} data: {exception}", exc_info=exception)
    error_msg = str(exception)

    if "Duplicate entry" in error_msg or "1062" in error_msg:
        if "number" in error_msg or "nomor" in error_msg.lower():
            return error_response("Nomor dokumen sudah ada. Harap gunakan nomor yang berbeda.", 400)
        elif "nuptk" in error_msg.lower():
            return error_response("NUPTK sudah terdaftar dalam sistem.", 400)
        elif "email" in error_msg.lower():
            return error_response("Email sudah terdaftar dalam sistem.", 400)
        else:
            return error_response("Data yang Anda masukkan sudah ada dalam sistem.", 400)

    if "foreign key constraint" in error_msg.lower() or "1451" in error_msg or "1452" in error_msg:
        # 1451: baris induk masih dirujuk; 1452: baris rujukan tidak ada
        if "1451" in error_msg:
            return error_response("Data tidak dapat dihapus karena masih digunakan oleh data lain.", 400)
        else:
            return error_response("Data terkait tidak ditemukan. Pastikan semua data referensi valid.", 400)

    if "Data too long" in error_msg or "1406" in error_msg:
        return error_response("Data yang dimasukkan terlalu panjang. Harap kurangi jumlah karakter.", 400)

    if "cannot be null" in error_msg.lower() or "1048" in error_msg:
        return error_response("Ada field wajib yang belum diisi. Harap lengkapi semua data.", 400)

    return error_response(
        f"Gagal {operation} data. Silakan periksa kembali data yang diisi.",
        500
    )
