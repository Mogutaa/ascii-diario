from flask import Blueprint, render_template, request, session, redirect, url_for
from functools import wraps
from config import Config
import bcrypt

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password'].encode()
        if bcrypt.checkpw(password, Config.ADMIN_HASH):
            session['admin'] = True
            return redirect(url_for('admin.admin_console'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('terminal'))