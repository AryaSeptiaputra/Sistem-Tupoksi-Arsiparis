import os
import atexit
from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager
from werkzeug.wrappers import Response
from flask_cors import CORS
from flask_compress import Compress
from apscheduler.schedulers.background import BackgroundScheduler

from .core.config import settings
from .core.database import engine, Base
from .services.retention_scheduler import check_and_deactivate_archives

# Model di-import agar terdaftar di Base.metadata sebelum create_all
from .models import (diploma, user, classification,
                     log, incoming_letter, outgoing_letter,
                     backup, storage_location, finance_archive,
                     employee_archive, teacher, master_reference)

from app.core import database as db
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_app() -> Flask:
    """Membuat aplikasi Flask beserta konfigurasi, scheduler, dan blueprint.

    Returns:
        Aplikasi Flask yang siap dijalankan.
    """
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    template_dir = os.path.join(app_dir, 'app', 'static', 'html')
    static_dir = os.path.join(app_dir, 'app', 'static')

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Kompresi gzip untuk respons di atas 1 KB, level 6 dari 1-9
    Compress(app)
    app.config['COMPRESS_LEVEL'] = 6
    app.config['COMPRESS_MIN_SIZE'] = 1024

    app.secret_key = settings.SECRET_KEY
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Ubah ke True setelah server memakai HTTPS
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # 86400 detik = 24 jam
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400

    CORS(app, supports_credentials=True)

    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    # 43200 detik = 12 jam
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 43200
    JWTManager(app)

    logger.info("Application started")

    @app.errorhandler(500)
    def internal_error(error: Exception) -> tuple[dict[str, str], int]:
        """Mencatat error 500 dan mengembalikan pesan JSON umum."""
        logger.error(f"Internal server error: {error}")
        return {"error": "Internal server error"}, 500

    @app.errorhandler(404)
    def not_found(error: Exception) -> tuple[dict[str, str], int]:
        """Mencatat URL yang tidak ada dan mengembalikan pesan JSON 404."""
        logger.warning(f"Page not found: {error}")
        return {"error": "Not found"}, 404

    Base.metadata.create_all(bind=engine)

    # Mode debug menjalankan reloader dua proses; scheduler hanya dijalankan
    # di proses anak (WERKZEUG_RUN_MAIN) supaya tidak berjalan ganda.
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        # Setiap hari pukul 00:01 waktu server
        scheduler.add_job(func=check_and_deactivate_archives, trigger="cron", hour=0, minute=1)
        scheduler.start()
        logger.info("Scheduler retensi arsip berjalan (harian)")
        atexit.register(lambda: scheduler.shutdown())

    # Import di dalam fungsi karena modul route meng-import `app.db` dari paket ini
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

    # URL pendek tanpa awalan /page diarahkan ke halaman di blueprint view
    @app.route('/')
    def index() -> Response:
        return redirect(url_for('view.login_page'))

    @app.route('/dashboard')
    def dashboard() -> Response:
        return redirect(url_for('view.dashboard_page'))

    @app.route('/incoming_letter')
    def incoming_letter() -> Response:
        return redirect(url_for('view.incoming_letter_page'))

    @app.route('/diploma')
    def diploma() -> Response:
        return redirect(url_for('view.diploma_page'))

    @app.route('/log')
    def log() -> Response:
        return redirect(url_for('view.log'))

    @app.route('/classification')
    def classification() -> Response:
        return redirect(url_for('view.classification'))

    @app.route('/backup')
    def backup() -> Response:
        return redirect(url_for('view.backup'))

    @app.route('/user_profile')
    def user_profile() -> Response:
        return redirect(url_for('view.user_profile'))

    @app.route('/storage_location')
    def storage_location() -> Response:
        return redirect(url_for('view.storage_location'))

    @app.route('/finance_archive')
    def finance_archive() -> Response:
        return redirect(url_for('view.finance_archive'))

    @app.route('/employee_archive')
    def employee_archive() -> Response:
        return redirect(url_for('view.employee_archive'))

    @app.route('/disposal')
    def disposal() -> Response:
        return redirect(url_for('view.disposal'))

    @app.route('/teacher')
    def teacher() -> Response:
        return redirect(url_for('view.teacher'))

    @app.route('/reference')
    def reference() -> Response:
        return redirect(url_for('view.reference'))

    return app
