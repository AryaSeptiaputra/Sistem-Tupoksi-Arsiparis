from flask import Blueprint, request, jsonify, render_template

view_bp = Blueprint('view', __name__)

@view_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@view_bp.route('/dashboard', methods=['GET'])
def dashboard_page():
    return render_template('dashboard.html')

@view_bp.route('/incoming_letter', methods=['GET'])
def incoming_letter_page():
    return render_template('incoming_letter.html')

@view_bp.route('/outgoing_letter', methods=['GET'])
def outgoing_letter_page():
    return render_template('outgoing_letter.html')

@view_bp.route('/classification', methods=['GET'])
def classification_page():
    return render_template('classification.html')

@view_bp.route('/diploma', methods=['GET'])
def diploma_page():
    return render_template('diploma.html')

@view_bp.route('/user', methods=['GET'])
def user_page():
    return render_template('user.html')

@view_bp.route('/log', methods=['GET'])
def log_page():
    return render_template('log.html')

@view_bp.route('/backup', methods=['GET'])
def backup():
    return render_template('backup.html')