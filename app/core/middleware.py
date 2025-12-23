"""
Global error handlers dan middleware untuk sustainability
"""
from flask import jsonify, request, current_app
from werkzeug.exceptions import HTTPException
import logging
import time
from functools import wraps

# Setup logging
logger = logging.getLogger(__name__)

# Simple in-memory rate limiting (untuk production, gunakan Redis)
rate_limit_store = {}

def rate_limit(max_requests=100, window_seconds=60):
    """
    Rate limiting decorator
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get client identifier (IP address)
            client_id = request.remote_addr or "unknown"

            # Create key for this client and endpoint
            key = f"{client_id}:{request.endpoint}"

            # Get current time
            now = time.time()

            # Clean old entries
            if key in rate_limit_store:
                rate_limit_store[key] = [
                    req_time for req_time in rate_limit_store[key]
                    if now - req_time < window_seconds
                ]

            # Check if under limit
            if key not in rate_limit_store:
                rate_limit_store[key] = []

            if len(rate_limit_store[key]) >= max_requests:
                logger.warning(f"Rate limit exceeded for {client_id} on {request.endpoint}")
                return jsonify({
                    "error": "Too many requests",
                    "message": f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                }), 429

            # Add current request
            rate_limit_store[key].append(now)

            return f(*args, **kwargs)
        return wrapper
    return decorator

def register_error_handlers(app):
    """
    Register global error handlers untuk aplikasi
    """

    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"400 Bad Request: {request.url} - {str(error)}")
        return jsonify({
            "error": "Bad Request",
            "message": "The request could not be understood by the server.",
            "status_code": 400
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"401 Unauthorized: {request.url}")
        return jsonify({
            "error": "Unauthorized",
            "message": "Authentication is required to access this resource.",
            "status_code": 401
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"403 Forbidden: {request.url}")
        return jsonify({
            "error": "Forbidden",
            "message": "You don't have permission to access this resource.",
            "status_code": 403
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"404 Not Found: {request.url}")
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found.",
            "status_code": 404
        }), 404

    @app.errorhandler(429)
    def too_many_requests(error):
        logger.warning(f"429 Too Many Requests: {request.url}")
        return jsonify({
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please try again later.",
            "status_code": 429
        }), 429

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"500 Internal Server Error: {request.url} - {str(error)}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.error(f"Unexpected error: {request.url} - {str(error)}", exc_info=True)

        # Don't expose internal errors in production
        if isinstance(error, HTTPException):
            return error

        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "status_code": 500
        }), 500

def add_security_headers(app):
    """
    Add security headers ke semua responses
    """

    @app.after_request
    def add_security_headers(response):
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"

        # API information
        response.headers['X-API-Version'] = '2.0.0'
        response.headers['X-Powered-By'] = 'Flask/Sistem Tupoksi Arsiparis'

        return response

def add_request_logging(app):
    """
    Add request logging middleware
    """

    @app.before_request
    def log_request_info():
        logger.info(f"{request.method} {request.url} - IP: {request.remote_addr} - User-Agent: {request.headers.get('User-Agent', 'Unknown')}")

    @app.after_request
    def log_response_info(response):
        logger.info(f"Response: {response.status_code} - {request.method} {request.url}")
        return response