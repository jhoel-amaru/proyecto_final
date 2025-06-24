from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app import db, login_manager
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
import random

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        ci = request.form.get('ci')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        acepta_terminos = request.form.get('acepta_terminos')

        if not acepta_terminos:
            flash('Debe aceptar los términos y condiciones para registrarse.', 'danger')
            return redirect(url_for('auth.register'))

        if password != password2:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Generar código de verificación aleatorio de 6 dígitos
        codigo_verificacion = str(random.randint(100000, 999999))

        nuevo_usuario = User(
            nombre=nombre,
            apellido=apellido,
            ci=ci,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            username=username,
            password=hashed_password,
            codigo_verificacion=codigo_verificacion
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash(f'Usuario registrado con éxito. Su código de verificación es: {codigo_verificacion}', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'cajero':
                return redirect(url_for('teller.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/terminos')
def terminos():
    return render_template('terminos/terminos.html')
