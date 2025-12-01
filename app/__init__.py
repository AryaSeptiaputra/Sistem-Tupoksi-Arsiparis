import os
from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager

from .core.config import settings
from .core.database import engine, Base
from .models import diploma, user, classification, log, incoming_letter, outgoing_letter, backup

from app.core import database as db

def create_app():
    # 1. Dapatkan lokasi folder 'app' (folder tempat __init__.py berada)
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 2. Tentukan lokasi folder HTML (Template)
    # Sesuai gambar: app -> frontend -> assets -> html
    template_dir = os.path.join(app_dir, 'frontend', 'assets', 'html')
    print(template_dir)

    # 3. Tentukan lokasi folder Static (CSS/JS)
    # Sesuai gambar: app -> frontend -> assets
    static_dir = os.path.join(app_dir, 'frontend', 'assets')

    # (Opsional) Print ini agar Anda bisa cek di terminal apakah path-nya sudah benar
    print(f"Lokasi Template: {template_dir}") 

    # Inisialisasi Flask dengan path custom
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
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

    # Redirect root '/' langsung ke halaman login
    @app.route('/')
    def index():
        return redirect(url_for('auth.login_page'))

    return app