"""
Health check endpoint untuk monitoring aplikasi
"""
from flask import Blueprint, jsonify
from app.core.database import SessionLocal
from sqlalchemy import text
import psutil
import os
from datetime import datetime, timezone

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Comprehensive health check endpoint
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "services": {}
    }

    # Database check
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["services"]["database"] = {"status": "healthy", "message": "Database connection OK"}
    except Exception as e:
        health_status["services"]["database"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "unhealthy"

    # System resources check
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)

        health_status["system"] = {
            "memory_usage_percent": memory.percent,
            "cpu_usage_percent": cpu_percent,
            "memory_available_mb": memory.available / 1024 / 1024
        }

        # Mark unhealthy if resources are critically low
        if memory.percent > 90 or cpu_percent > 95:
            health_status["status"] = "warning"
            health_status["system"]["warning"] = "High resource usage detected"

    except Exception as e:
        health_status["system"] = {"error": str(e)}

    # Application info
    health_status["application"] = {
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "platform": os.sys.platform,
        "uptime": "N/A"  # Could be enhanced with app start time tracking
    }

    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code

@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    Basic metrics endpoint untuk monitoring
    """
    try:
        db = SessionLocal()

        # Get some basic counts (you can expand this)
        teacher_count = db.execute(text("SELECT COUNT(*) FROM teacher")).scalar()
        user_count = db.execute(text("SELECT COUNT(*) FROM user")).scalar()
        log_count = db.execute(text("SELECT COUNT(*) FROM log")).scalar()

        db.close()

        return jsonify({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "total_teachers": teacher_count,
                "total_users": user_count,
                "total_logs": log_count
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500