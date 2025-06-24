# app/controllers/transfer_controller.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.capital_general import CapitalGeneral

transfer_bp = Blueprint('transfer', __name__, url_prefix='/transfer')

def registrar_transaccion(user, tipo, monto):
    t = Transaction(user_id=user.id, tipo=tipo, monto=monto)
    db.session.add(t)

@transfer_bp.route('/cliente_a_cliente', methods=['POST'])
@login_required
def cliente_a_cliente():
    if current_user.role != 'cliente':
        flash('Solo clientes pueden transferir', 'danger')
        return redirect(url_for('user.dashboard'))

    destinatario_username = request.form.get('username')
    monto = float(request.form.get('monto'))

    destinatario = User.query.filter_by(username=destinatario_username, role='cliente').first()
    
    if not destinatario:
        flash('Cliente destino no encontrado', 'danger')
        return redirect(url_for('transfer.cliente_a_cliente'))

    if current_user.saldo < monto:
        flash('Saldo insuficiente', 'danger')
        return redirect(url_for('transfer.cliente_a_cliente'))

    try:
        # Transferencia
        current_user.saldo -= monto
        destinatario.saldo += monto

        # Registrar transacciones
        trans_envio = Transaction(
            user_id=current_user.id,
            tipo=f'Transferencia a {destinatario.username}',
            monto=-monto
        )
        trans_recep = Transaction(
            user_id=destinatario.id,
            tipo=f'Recibo de {current_user.username}',
            monto=monto
        )

        db.session.add_all([trans_envio, trans_recep])
        db.session.commit()

        flash('¡Transferencia exitosa!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('transfer.cliente_a_cliente'))

@transfer_bp.route('/admin_a_cajero', methods=['GET', 'POST'])
@login_required
def admin_a_cajero():
    if current_user.role != 'admin':
        flash('Solo admin puede usar esta función.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        try:
            monto = float(request.form.get('monto'))
        except:
            flash('Monto inválido.', 'danger')
            return redirect(url_for('transfer.admin_a_cajero'))

        if monto <= 0:
            flash('Monto debe ser mayor a 0.', 'danger')
            return redirect(url_for('transfer.admin_a_cajero'))

        cajero = User.query.filter_by(username=username, role='cajero').first()
        if not cajero:
            flash('Cajero no encontrado.', 'danger')
            return redirect(url_for('transfer.admin_a_cajero'))

        # Obtener capital general admin (debes tener un solo registro)
        capital_general = CapitalGeneral.query.first()
        if not capital_general or capital_general.monto < monto:
            flash('Capital general insuficiente.', 'danger')
            return redirect(url_for('transfer.admin_a_cajero'))

        try:
            capital_general.monto -= monto
            cajero.saldo += monto

            registrar_transaccion(current_user, 'admin→cajero', -monto)
            registrar_transaccion(cajero, f'recibo de admin (${monto})', monto)

            db.session.commit()
            flash(f'Transferencia de Bs. {monto} a cajero {cajero.username} realizada con éxito.', 'success')
            return redirect(url_for('transfer.admin_a_cajero'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error en transferencia: {str(e)}', 'danger')
            return redirect(url_for('transfer.admin_a_cajero'))

    return render_template('transfer/admin_a_cajero.html')

@transfer_bp.route('/cliente_a_cajero', methods=['POST'])
@login_required
def cliente_a_cajero():
    if current_user.role != 'cliente':
        flash('Solo clientes pueden usar esta función', 'danger')
        return redirect(url_for('user.dashboard'))

    cajero_username = request.form.get('username')
    monto = float(request.form.get('monto'))

    cajero = User.query.filter_by(username=cajero_username, role='cajero').first()

    if not cajero:
        flash('Cajero no encontrado', 'danger')
        return redirect(url_for('transfer.cliente_a_cajero'))

    if current_user.saldo < monto:
        flash('Saldo insuficiente', 'danger')
        return redirect(url_for('transfer.cliente_a_cajero'))

    try:
        # Transferencia
        current_user.saldo -= monto
        cajero.saldo += monto

        # Registrar transacciones
        trans_cliente = Transaction(
            user_id=current_user.id,
            tipo=f'Transferencia a cajero {cajero.username}',
            monto=-monto
        )
        trans_cajero = Transaction(
            user_id=cajero.id,
            tipo=f'Recibo de cliente {current_user.username}',
            monto=monto
        )

        db.session.add_all([trans_cliente, trans_cajero])
        db.session.commit()

        flash('¡Dinero enviado al cajero!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('transfer.cliente_a_cajero'))



@transfer_bp.route('/cajero_a_cliente', methods=['POST'])
@login_required
def cajero_a_cliente():
    if current_user.role != 'cajero':
        flash('Solo cajeros pueden transferir', 'danger')
        return redirect(url_for('teller.dashboard'))

    cliente_username = request.form.get('username')
    monto = float(request.form.get('monto'))

    cliente = User.query.filter_by(username=cliente_username, role='cliente').first()

    if not cliente:
        flash('Cliente no encontrado', 'danger')
        return redirect(url_for('transfer.cajero_a_cliente'))

    if current_user.saldo < monto:
        flash('Saldo insuficiente', 'danger')
        return redirect(url_for('transfer.cajero_a_cliente'))

    try:
        # Transferencia
        current_user.saldo -= monto
        cliente.saldo += monto

        # Registrar transacciones
        trans_cajero = Transaction(
            user_id=current_user.id,
            tipo=f'Transferencia a cliente {cliente.username}',
            monto=-monto
        )
        trans_cliente = Transaction(
            user_id=cliente.id,
            tipo=f'Recibo de cajero {current_user.username}',
            monto=monto
        )

        db.session.add_all([trans_cajero, trans_cliente])
        db.session.commit()

        flash('¡Dinero enviado al cliente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('transfer.cajero_a_cliente'))