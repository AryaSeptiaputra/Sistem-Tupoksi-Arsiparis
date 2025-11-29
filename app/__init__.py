from flask import Flask
from flask_jwt_extended import JWTManager

from .core.config import settings
from .core.database import engine, Base
from .core import database as db

from .models.user import User
from .models.classification import Classification
from .models.log import Log
from .models.incoming_letter import IncomingLetter
from .models.outgoing_letter import OutgoingLetter

def create_app():
    """
    Initializes and configures the Flask application instance.
    
    This function sets up the app configuration, JWT manager, database tables,
    and registers all application blueprints (routes).

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY

    jwt = JWTManager(app)
    
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating database tables: {e}")

    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.classification import classification_bp
    from .routes.incoming_letter import incoming_letter_bp
    from .routes.outgoing_letter import outgoing_letter_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(classification_bp, url_prefix='/classification')
    app.register_blueprint(incoming_letter_bp, url_prefix='/incoming-letter')
    app.register_blueprint(outgoing_letter_bp, url_prefix='/outgoing-letter')

    return app