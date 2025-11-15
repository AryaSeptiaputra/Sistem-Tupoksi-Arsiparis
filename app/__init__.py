from flask import Flask

from .models.user import user

from .core.database import engine, Base
from .core import database as db

def create_app():
    """Membuat dan mengkonfigurasi instance aplikasi Flask."""
    
    app = Flask(__name__)
    
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables checked/created.")
    except Exception as e:
        print(f"Error creating database tables: {e}")

    from .routes.auth import auth_bp
    from .routes.user import user_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app