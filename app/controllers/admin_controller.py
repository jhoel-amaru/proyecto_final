from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.loan import Loan
from app.models.loan_type import LoanType
from werkzeug.security import generate_password_hash
import random

from app.models.capital_general import CapitalGeneral

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash("Acceso denegado: solo administradores.", 'danger')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    capital = CapitalGeneral.query.first()
    capital_monto = capital.monto if capital else 10000000.0
    num_cajeros = User.query.filter_by(role='cajero').count()
    num_clientes = User.query.filter_by(role='cliente').count()
    return render_template('admin/dashboard.html', capital_general=capital_monto,
                           num_cajeros=num_cajeros, num_clientes=num_clientes)

@admin_bp.route('/send_money', methods=['GET', 'POST'])
@login_required
@admin_required
def send_money():
    if request.method == 'POST':
        username = request.form.get('username')
        telefono = request.form.get('telefono')
        codigo = request.form.get('codigo')
        monto = float(request.form.get('monto'))

        user = User.query.filter_by(username=username, telefono=telefono, codigo_verificacion=codigo).first()

        if not user:
            flash("Usuario no encontrado o datos incorrectos.", 'danger')
            return redirect(url_for('admin.send_money'))

        user.saldo += monto
        db.session.commit()
        flash(f"Se enviaron Bs. {monto} a {user.username}.", 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/send_money.html')

@admin_bp.route('/loans')
@login_required
@admin_required
def loan_list():
    prestamos = LoanType.query.all()
    return render_template('admin/loan_list.html', loans=prestamos)

@admin_bp.route('/loan/create', methods=['GET', 'POST'])
@login_required
@admin_required
def loan_create():
    if request.method == 'POST':
        nombre = request.form['nombre']
        monto = float(request.form['monto'])
        plazo_meses = int(request.form['plazo_meses'])
        interes = float(request.form['interes'])

        nuevo_tipo = LoanType(
            nombre=nombre,
            monto_maximo=monto,
            plazo_dias=plazo_meses * 30,
            interes=interes,
            duracion_dias=plazo_meses * 30  # <-- Aquí asignamos duracion_dias
        )
        db.session.add(nuevo_tipo)
        db.session.commit()

        flash('Tipo de préstamo creado exitosamente', 'success')
        return redirect(url_for('admin.loan_create'))

    tipos = LoanType.query.all()
    return render_template('admin/loan_create.html', prestamos=tipos)

@admin_bp.route('/loan/edit/<int:loan_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def loan_edit(loan_id):
    tipo = LoanType.query.get_or_404(loan_id)
    if request.method == 'POST':
        tipo.nombre = request.form['nombre']
        tipo.monto_maximo = float(request.form['monto'])
        tipo.plazo_dias = int(request.form['plazo_meses']) * 30
        tipo.interes = float(request.form['interes'])
        tipo.duracion_dias = int(request.form['plazo_meses']) * 30  # <-- Aquí también asignamos duracion_dias
        db.session.commit()
        flash('Tipo de préstamo actualizado', 'success')
        return redirect(url_for('admin.loan_create'))
    return render_template('admin/loan_edit.html', tipo=tipo)

@admin_bp.route('/loan/delete/<int:loan_id>', methods=['POST'])
@login_required
@admin_required
def loan_delete(loan_id):
    tipo = LoanType.query.get_or_404(loan_id)
    db.session.delete(tipo)
    db.session.commit()
    flash('Tipo de préstamo eliminado', 'success')
    return redirect(url_for('admin.loan_create'))

@admin_bp.route('/tellers')
@login_required
@admin_required
def teller_list():
    cajeros = User.query.filter_by(role='cajero').all()
    return render_template('admin/teller_list.html', cajeros=cajeros)

@admin_bp.route('/teller/create', methods=['GET', 'POST'])
@login_required
@admin_required
def teller_create():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        ci = request.form.get('ci')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(ci=ci).first() or \
           User.query.filter_by(correo=correo).first() or \
           User.query.filter_by(username=username).first():
            flash("Datos duplicados detectados. Verifique CI, correo o usuario.", 'danger')
            return redirect(url_for('admin.teller_create'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        codigo_verificacion = str(random.randint(100000, 999999))

        nuevo_cajero = User(
            nombre=nombre,
            apellido=apellido,
            ci=ci,
            direccion=direccion,
            telefono=telefono,
            correo=correo,
            username=username,
            password=hashed_password,
            role='cajero',
            codigo_verificacion=codigo_verificacion
        )

        db.session.add(nuevo_cajero)
        db.session.commit()

        flash(f"Cajero creado con código de verificación: {codigo_verificacion}", 'success')
        return redirect(url_for('admin.teller_list'))

    return render_template('admin/teller_form.html')
