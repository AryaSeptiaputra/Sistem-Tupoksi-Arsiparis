from flask import Flask
from flask_jwt_extended import JWTManager

from .core.config import settings
from .core.database import engine, Base
from .models import diploma, user, classification, log, incoming_letter, outgoing_letter, backup

from app.core import database as db

def create_app():
    """
    Initialize and configure the Flask application.

    This function sets up the application instance, configures JWT handling,
    initializes the database schema if not already created, and registers
    all route blueprints used throughout the system.

    Returns:
        Flask: The fully configured Flask application instance.
    """
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY

    JWTManager(app)
    Base.metadata.create_all(bind=engine)

    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.classification import classification_bp
    from .routes.incoming_letter import incoming_letter_bp
    from .routes.outgoing_letter import outgoing_letter_bp
    from .routes.diploma import diploma_bp
    from .routes.log import log_bp
    from .routes.backup import backup_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(classification_bp, url_prefix="/classification")
    app.register_blueprint(incoming_letter_bp, url_prefix="/incoming-letter")
    app.register_blueprint(outgoing_letter_bp, url_prefix="/outgoing-letter")
    app.register_blueprint(diploma_bp, url_prefix="/diploma")
    app.register_blueprint(log_bp, url_prefix="/log")   
    app.register_blueprint(backup_bp, url_prefix="/backup")

    return app
