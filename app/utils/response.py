"""
Standard response formatting untuk consistency across all endpoints.
"""

from typing import Any, Dict, Optional, List
from flask import jsonify
from http import HTTPStatus


def success_response(data: Any = None, message: str = "Success", 
                    status_code: int = 200) -> tuple:
    """
    Standard success response format
    
    Args:
        data: Response data (can be dict, list, or paginated result)
        message: Success message
        status_code: HTTP status code
    
    Returns:
        Tuple of (jsonified response, status_code)
    """
    response = {
        "success": True,
        "message": message
    }
    
    # If data has to_dict() method (PaginatedResult), use it
    if hasattr(data, 'to_dict'):
        response.update(data.to_dict())
    elif data is not None:
        response["data"] = data
    
    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400,
                   errors: Optional[Dict] = None) -> tuple:
    """
    Standard error response format
    
    Args:
        message: Error message
        status_code: HTTP status code
        errors: Additional error details
    
    Returns:
        Tuple of (jsonified response, status_code)
    """
    response = {
        "success": False,
        "message": message
    }
    
    if errors:
        response["errors"] = errors
    
    return jsonify(response), status_code


def validation_error_response(errors: Dict[str, List[str]]) -> tuple:
    """Handle validation errors"""
    return error_response(
        message="Validation failed",
        status_code=422,
        errors=errors
    )


def not_found_response(resource: str = "Resource") -> tuple:
    """Handle not found errors"""
    return error_response(
        message=f"{resource} not found",
        status_code=404
    )


def unauthorized_response(message: str = "Unauthorized") -> tuple:
    """Handle unauthorized errors"""
    return error_response(
        message=message,
        status_code=401
    )


def server_error_response(message: str = "Internal server error",
                         exception: Optional[Exception] = None) -> tuple:
    """Handle server errors with optional exception logging"""
    if exception:
        message = f"{message}: {str(exception)}"
    
    return error_response(
        message=message,
        status_code=500
    )


def handle_database_error(exception: Exception, operation: str = "menyimpan") -> tuple:
    """
    Handle database errors dengan pesan user-friendly
    
    Args:
        exception: Exception yang ditangkap
        operation: Operasi yang sedang dilakukan (menyimpan, memperbarui, menghapus)
    
    Returns:
        Tuple of (jsonified response, status_code)
    """
    error_msg = str(exception)
    
    # Handle duplicate entry
    if "Duplicate entry" in error_msg or "1062" in error_msg:
        if "number" in error_msg or "nomor" in error_msg.lower():
            return error_response("Nomor dokumen sudah ada. Harap gunakan nomor yang berbeda.", 400)
        elif "nuptk" in error_msg.lower():
            return error_response("NUPTK sudah terdaftar dalam sistem.", 400)
        elif "email" in error_msg.lower():
            return error_response("Email sudah terdaftar dalam sistem.", 400)
        else:
            return error_response("Data yang Anda masukkan sudah ada dalam sistem.", 400)
    
    # Handle foreign key constraint
    if "foreign key constraint" in error_msg.lower() or "1451" in error_msg or "1452" in error_msg:
        if "1451" in error_msg:  # Cannot delete or update a parent row
            return error_response("Data tidak dapat dihapus karena masih digunakan oleh data lain.", 400)
        else:  # Cannot add or update a child row
            return error_response("Data terkait tidak ditemukan. Pastikan semua data referensi valid.", 400)
    
    # Handle data too long
    if "Data too long" in error_msg or "1406" in error_msg:
        return error_response("Data yang dimasukkan terlalu panjang. Harap kurangi jumlah karakter.", 400)
    
    # Handle null constraint
    if "cannot be null" in error_msg.lower() or "1048" in error_msg:
        return error_response("Ada field wajib yang belum diisi. Harap lengkapi semua data.", 400)
    
    # Generic database error
    return error_response(
        f"Gagal {operation} data. Silakan periksa kembali data yang diisi.",
        500
    )
