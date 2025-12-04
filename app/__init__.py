import os
from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager

from .core.config import settings
from .core.database import engine, Base
from .models import diploma, user, classification, log, incoming_letter, outgoing_letter, backup

from app.core import database as db

def create_app():
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    template_dir = os.path.join(app_dir, 'assets', 'html')
    print(template_dir)

    static_dir = os.path.join(app_dir, 'assets')

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
    from .routes.views import view_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(classification_bp, url_prefix="/classification")
    app.register_blueprint(incoming_letter_bp, url_prefix="/incoming_letter")
    app.register_blueprint(outgoing_letter_bp, url_prefix="/outgoing_letter")
    app.register_blueprint(diploma_bp, url_prefix="/diploma")
    app.register_blueprint(log_bp, url_prefix="/log")   
    app.register_blueprint(backup_bp, url_prefix="/backup")
    app.register_blueprint(view_bp, url_prefix="/page")

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
    
    @app.route('/backup')
    def backup():
        return redirect(url_for('view.backup'))
    
    @app.route('/form_incoming_letter')
    def form_incoming_letter():
        return redirect(url_for('view.form_incoming_letter'))
    
    @app.route('/form_outgoing_letter')
    def form_outgoing_letter():
        return redirect(url_for('view.form_outgoing_letter'))
    
    @app.route('/user_profile')
    def user_profile():
        return redirect(url_for('view.user_profile'))

    return app