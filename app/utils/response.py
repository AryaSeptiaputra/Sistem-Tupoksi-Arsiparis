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
