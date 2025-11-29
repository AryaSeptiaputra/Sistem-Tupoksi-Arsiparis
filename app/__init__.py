from flask import Flask
from flask_jwt_extended import JWTManager

from .models.user import user
from .models.classification import classification
from .models.log import log

from .core.database import engine, Base
from .core import database as db

from .core.config import Settings

def create_app():
    """Membuat dan mengkonfigurasi instance aplikasi Flask."""
    
    app = Flask(__name__)


    app.config["JWT_SECRET_KEY"] = Settings().JWT_SECRET_KEY

    jwt = JWTManager(app)
    
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created.")
    except Exception as e:
        print(f"Error creating database tables: {e}")

    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.classification import classification_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(classification_bp, url_prefix='/classification')

    return app