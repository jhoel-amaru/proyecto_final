from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.transaction import Transaction
from app.utils.decorators import teller_required
from datetime import datetime

teller_bp = Blueprint('teller', __name__, url_prefix='/teller')

@teller_bp.route('/dashboard')
@login_required
@teller_required
def dashboard():
    transacciones = (
        Transaction.query
        .filter_by(user_id=current_user.id)
        .order_by(Transaction.fecha.desc())
        .limit(10)
        .all()
    )
    return render_template(
        'teller/dashboard.html',
        user=current_user,
        transacciones=transacciones
    )

@teller_bp.route('/mi_cuenta')
@login_required
@teller_required
def mi_cuenta():
    return render_template('teller/mi_cuenta.html', user=current_user)

@teller_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
@teller_required
def deposit():
    if request.method == 'POST':
        username_destino = request.form['username_destino'].strip()
        celular_cajero = request.form['celular_cajero'].strip()
        monto = request.form['monto'].strip()
        codigo_verificacion = request.form['codigo_cajero'].strip()

        if not (username_destino and celular_cajero and monto and codigo_verificacion):
            flash("Todos los campos son obligatorios.", 'danger')
            return redirect(url_for('teller.deposit'))
        if codigo_verificacion != current_user.codigo_verificacion:
            flash("Código de verificación incorrecto.", 'danger')
            return redirect(url_for('teller.deposit'))

        try:
            monto_val = float(monto)
            if monto_val <= 0:
                raise ValueError
        except ValueError:
            flash("Monto inválido.", 'danger')
            return redirect(url_for('teller.deposit'))

        user_destino = User.query.filter_by(username=username_destino).first()
        if not user_destino:
            flash("Usuario destino no encontrado.", 'danger')
            return redirect(url_for('teller.deposit'))

        # Realizar depósito
        user_destino.balance += monto_val
        trans = Transaction(
            user_id=user_destino.id,
            tipo=f"Depósito por {current_user.username} (cel: {celular_cajero})",
            monto=monto_val
        )
        db.session.add(trans)
        db.session.commit()

        # Mostrar ticket
        return render_template(
            'teller/ticket.html',
            accion="Depósito",
            cliente=user_destino,
            cajero=current_user,
            monto=monto_val,
            fecha=datetime.now()
        )

    return render_template('teller/deposit.html')

@teller_bp.route('/recibir', methods=['GET', 'POST'])
@login_required
@teller_required
def recibir():
    if request.method == 'POST':
        usuario_id = request.form['usuario'].strip()
        monto = request.form['monto'].strip()
        codigo_verificacion = request.form['codigo_cajero'].strip()

        if not (usuario_id and monto and codigo_verificacion):
            flash("Todos los campos son obligatorios.", 'danger')
            return redirect(url_for('teller.recibir'))
        if codigo_verificacion != current_user.codigo_verificacion:
            flash("Código de verificación incorrecto.", 'danger')
            return redirect(url_for('teller.recibir'))

        try:
            monto_val = float(monto)
            if monto_val <= 0:
                raise ValueError
        except ValueError:
            flash("Monto inválido.", 'danger')
            return redirect(url_for('teller.recibir'))

        cliente = User.query.filter(
            (User.username == usuario_id) | (User.ci == usuario_id)
        ).first()
        if not cliente:
            flash("Cliente no encontrado.", 'danger')
            return redirect(url_for('teller.recibir'))
        if cliente.balance < monto_val:
            flash("Saldo insuficiente del cliente.", 'danger')
            return redirect(url_for('teller.recibir'))

        # Recibir dinero
        cliente.balance -= monto_val
        current_user.balance += monto_val
        trans_cliente = Transaction(
            user_id=cliente.id,
            tipo=f"Retiro en caja por {current_user.username}",
            monto=monto_val
        )
        trans_cajero = Transaction(
            user_id=current_user.id,
            tipo=f"Ingreso de {cliente.username}",
            monto=monto_val
        )
        db.session.add_all([trans_cliente, trans_cajero])
        db.session.commit()

        # Mostrar ticket de recibo
        return render_template(
            'teller/ticket.html',
            accion="Recibo",
            cliente=cliente,
            cajero=current_user,
            monto=monto_val,
            fecha=datetime.now()
        )

    return render_template('teller/recibir_dinero.html')
