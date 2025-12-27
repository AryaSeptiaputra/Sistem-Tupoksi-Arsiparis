import os
import atexit # Untuk mematikan scheduler saat app stop
import logging
from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_compress import Compress  # <--- [BARU] Import Compression
from apscheduler.schedulers.background import BackgroundScheduler # <--- [BARU 1] Import Scheduler

from .core.config import settings
from .core.database import engine, Base
# Import logic scheduler yang baru dibuat
from .services.retention_scheduler import check_and_deactivate_archives # <--- [BARU 2] Import Fungsi Logic

from .models import (diploma, user, classification,
                     log, incoming_letter, outgoing_letter,
                     backup, storage_location, finance_archive,
                     employee_archive, teacher, master_reference)

from app.core import database as db

def create_app():
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Setup folder template & static
    template_dir = os.path.join(app_dir, 'assets', 'html')
    static_dir = os.path.join(app_dir, 'assets')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # ==========================================================================
    # 🔧 PERFORMANCE OPTIMIZATION
    # ==========================================================================
    # Enable gzip compression untuk response besar
    Compress(app)
    app.config['COMPRESS_LEVEL'] = 6  # Compression level 1-9 (higher = better, slower)
    app.config['COMPRESS_MIN_SIZE'] = 1024  # Minimum size untuk compress (1KB)

    # ==========================================================================
    # 🔥 KONFIGURASI KEAMANAN (PRODUCTION)
    # ==========================================================================
    app.secret_key = 'kunci_rahasia_smkn7_bandung_super_secure' 
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False # Ubah True jika nanti pakai HTTPS (SSL)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400

    CORS(app, supports_credentials=True)

    # Konfigurasi JWT
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    JWTManager(app)

    # ==========================================================================
    # 📝 KONFIGURASI LOGGING
    # ==========================================================================
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if settings.LOG_FILE_PATH:
        os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)
        handler = logging.FileHandler(settings.LOG_FILE_PATH)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
    app.logger.info("Application started")

    # ==========================================================================
    # ❌ ERROR HANDLERS
    # ==========================================================================
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        return {"error": "Internal server error"}, 500

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"Page not found: {error}")
        return {"error": "Not found"}, 404

    # Create Database Tables
    Base.metadata.create_all(bind=engine)

    # ==========================================================================
    # 🕒 KONFIGURASI SCHEDULER (MODE DEPLOY: HARIAN)
    # ==========================================================================
    # Cek environment agar tidak jalan double
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        
        # 🟢 MODE PRODUKSI: Jalan setiap hari jam 00:01 WIB
        # Ini ringan dan tidak membebani server sekolah
        scheduler.add_job(func=check_and_deactivate_archives, trigger="cron", hour=0, minute=1)
        
        # 🔴 MODE TESTING (Hanya nyalakan ini jika sedang demo ke dosen)
        # scheduler.add_job(func=check_and_deactivate_archives, trigger="interval", seconds=10)
        
        scheduler.start()
        print("✅ Scheduler Retensi Arsip Berjalan (Mode Harian)...")
        
        # Matikan scheduler saat app berhenti
        atexit.register(lambda: scheduler.shutdown())

    # ==========================================================================
    # 🔌 REGISTER BLUEPRINTS
    # ==========================================================================
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.classification import classification_bp
    from .routes.incoming_letter import incoming_letter_bp
    from .routes.outgoing_letter import outgoing_letter_bp
    from .routes.diploma import diploma_bp
    from .routes.log import log_bp
    from .routes.backup import backup_bp
    from .routes.views import view_bp
    from .routes.storage import storage_bp
    from .routes.storage_location import storage_location_bp
    from .routes.finance_archive import finance_bp
    from .routes.employee_archive import employee_archive_bp
    from .routes.disposal import disposal_bp 
    from .routes.teacher import teacher_bp
    from .routes.master_reference import reference_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(classification_bp, url_prefix="/classification")
    app.register_blueprint(incoming_letter_bp, url_prefix="/incoming_letter")
    app.register_blueprint(outgoing_letter_bp, url_prefix="/outgoing_letter")
    app.register_blueprint(diploma_bp, url_prefix="/diploma")
    app.register_blueprint(log_bp, url_prefix="/log")
    app.register_blueprint(backup_bp, url_prefix="/backup")
    app.register_blueprint(view_bp, url_prefix="/page")
    app.register_blueprint(storage_bp, url_prefix='/storage')
    app.register_blueprint(storage_location_bp, url_prefix="/storage_location")
    app.register_blueprint(finance_bp, url_prefix=('/finance_archive'))
    app.register_blueprint(employee_archive_bp, url_prefix="/employee_archive")
    app.register_blueprint(disposal_bp, url_prefix="/disposal")
    app.register_blueprint(teacher_bp, url_prefix="/teacher")
    app.register_blueprint(reference_bp)

    # ==========================================================================
    # 🔗 ROUTES REDIRECT
    # ==========================================================================
    @app.route('/')
    def index():
        return redirect(url_for('view.login_page'))
    
    @app.route('/dashboard')
    def dashboard():
        return redirect(url_for('view.dashboard_page'))
    
    @app.route('/incoming_letter')
    def incoming_letter():
        return redirect(url_for('view.incoming_letter_page'))

    @app.route('/diploma')
    def diploma():
        return redirect(url_for('view.diploma_page'))

    @app.route('/user')
    def user():
        return redirect(url_for('view.user_page'))
    
    @app.route('/log')
    def log():
        return redirect(url_for('view.log'))
    
    @app.route('/classification')
    def classification():
        return redirect(url_for('view.classification'))
    
    @app.route('/backup')
    def backup():
        return redirect(url_for('view.backup'))
    
    @app.route('/user_profile')
    def user_profile():
        return redirect(url_for('view.user_profile'))
    
    @app.route('/storage_location')
    def storage_location():
        return redirect(url_for('view.storage_location'))
    
    @app.route('/finance_archive')
    def finance_archive():
        return redirect(url_for('view.finance_archive'))
    
    @app.route('/employee_archive')
    def employee_archive():
        return redirect(url_for('view.employee_archive'))
    
    @app.route('/disposal')
    def disposal():
        return redirect(url_for('view.disposal'))
    
    @app.route('/teacher')
    def teacher():
        return redirect(url_for('view.teacher'))
    
    @app.route('/reference')
    def reference():
        return redirect(url_for('view.reference'))
    
    # 🔥 PENTING: Return app hanya SEKALI di paling bawah
    return app
