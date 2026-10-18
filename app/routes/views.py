"""Halaman HTML aplikasi; data di halaman diambil front-end lewat API."""

from flask import Blueprint, request, jsonify, render_template
from flask.typing import ResponseReturnValue

view_bp = Blueprint('view', __name__)

@view_bp.route('/login', methods=['GET'])
def login_page() -> ResponseReturnValue:
    """Halaman login."""
    return render_template('login.html')

@view_bp.route('/dashboard', methods=['GET'])
def dashboard_page() -> ResponseReturnValue:
    """Halaman dashboard."""
    return render_template('dashboard.html')

@view_bp.route('/incoming_letter', methods=['GET'])
def incoming_letter_page() -> ResponseReturnValue:
    """Halaman surat masuk."""
    return render_template('incoming_letter.html')

@view_bp.route('/outgoing_letter', methods=['GET'])
def outgoing_letter_page() -> ResponseReturnValue:
    """Halaman surat keluar."""
    return render_template('outgoing_letter.html')

@view_bp.route('/classification', methods=['GET'])
def classification_page() -> ResponseReturnValue:
    """Halaman klasifikasi."""
    return render_template('classification.html')

@view_bp.route('/diploma', methods=['GET'])
def diploma_page() -> ResponseReturnValue:
    """Halaman ijazah."""
    return render_template('diploma.html')

@view_bp.route('/log', methods=['GET'])
def log_page() -> ResponseReturnValue:
    """Halaman log aktivitas."""
    return render_template('log.html')

@view_bp.route('/backup', methods=['GET'])
def backup() -> ResponseReturnValue:
    """Halaman backup database."""
    return render_template('backup.html')

@view_bp.route('/user_profile', methods=['GET'])
def user_profile() -> ResponseReturnValue:
    """Halaman Akun Saya."""
    return render_template('user_profile.html')

@view_bp.route('/storage_location', methods=['GET'])
def storage_location() -> ResponseReturnValue:
    """Halaman lokasi simpan."""
    return render_template('storage_location.html')

@view_bp.route('/finance_archive', methods=['GET'])
def finance_archive() -> ResponseReturnValue:
    """Halaman arsip keuangan."""
    return render_template('finance_archive.html')

@view_bp.route('/employee_archive', methods=['GET'])
def employee_archive() -> ResponseReturnValue:
    """Halaman arsip pegawai."""
    return render_template('employee_archive.html')

@view_bp.route('/disposal', methods=['GET'])
def disposal() -> ResponseReturnValue:
    """Halaman pemusnahan arsip."""
    return render_template('disposal.html')

@view_bp.route('/teacher', methods=['GET'])
def teacher() -> ResponseReturnValue:
    """Halaman data guru."""
    return render_template('teacher.html')

@view_bp.route('/reference', methods=['GET'])
def reference() -> ResponseReturnValue:
    """Halaman referensi."""
    return render_template('master_reference.html')
