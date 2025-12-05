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

@view_bp.route('/form_incoming_letter', methods=['GET'])
def form_incoming_letter():
    return render_template('form_incoming_letter.html')

@view_bp.route('/form_outgoing_letter', methods=['GET'])
def form_outgoing_letter():
    return render_template('form_outgoing_letter.html')

@view_bp.route('/user_profile', methods=['GET'])
def user_profile():
    return render_template('user_profile.html')

@view_bp.route('/form_diploma', methods=['GET'])
def form_diploma():
    return render_template('form_diploma.html')

@view_bp.route('/classification_add', methods=['GET'])
def classification_add():
    return render_template('classification_add.html')

@view_bp.route('/classification/edit', methods=['GET'])
def classification_edit_page():
    cls_id = request.args.get('id')
    return render_template('classification_edit.html')

@view_bp.route('/form_incoming_letter/edit', methods=['GET'])
def form_incoming_letter_edit_page():
    cls_id = request.args.get('id')
    return render_template('form_incoming_letter.html')

@view_bp.route('/form_outgoing_letter/edit', methods=['GET'])
def form_outgoing_letter_edit_page():
    cls_id = request.args.get('id')
    return render_template('form_outgoing_letter.html')

@view_bp.route('/form_diploma/edit', methods=['GET'])
def form_diploma_edit_page():
    cls_id = request.args.get('id')
    return render_template('form_diploma.html')