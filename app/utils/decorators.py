from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Acceso solo para administradores.')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def teller_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'cajero':
            flash('Acceso solo para cajeros.')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
