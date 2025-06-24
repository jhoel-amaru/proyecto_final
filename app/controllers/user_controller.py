from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.loan import Loan
from app.models.loan_type import LoanType
from app.models.transaction import Transaction
from app.models.user import User
from datetime import datetime, timedelta
import random
from app.models.capital_general import CapitalGeneral

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    transacciones = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.fecha.desc()).limit(20).all()
    return render_template('user/dashboard.html', user=current_user, transacciones=transacciones)

@user_bp.route('/mi_cuenta')
@login_required
def mi_cuenta():
    return render_template('user/mi_cuenta.html', user=current_user)

@user_bp.route('/borrar_cuenta')
@login_required
def borrar_cuenta():
    deuda = Loan.query.filter_by(user_id=current_user.id, estado='activo').first()
    if deuda:
        flash('No puedes borrar la cuenta mientras tengas deudas activas.', 'danger')
        return redirect(url_for('user.mi_cuenta'))
    
    Transaction.query.filter_by(user_id=current_user.id).delete()
    Loan.query.filter_by(user_id=current_user.id).delete()
    user = User.query.get(current_user.id)
    db.session.delete(user)
    db.session.commit()
    flash('Cuenta eliminada exitosamente.', 'success')
    return redirect(url_for('auth.logout'))


@user_bp.route('/mis_prestamos', methods=['GET', 'POST'])
@login_required
def mis_prestamos():
    tipos = LoanType.query.all()
    prestamos = Loan.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        tipo_id = request.form.get('loan_type_id')
        monto = float(request.form.get('monto'))

        tipo = LoanType.query.get(tipo_id)
        if not tipo:
            flash('Tipo de préstamo inválido.', 'danger')
            return redirect(url_for('user.mis_prestamos'))

        if monto > tipo.monto_maximo:
            flash(f'El monto excede el máximo permitido: Bs. {tipo.monto_maximo}', 'danger')
            return redirect(url_for('user.mis_prestamos'))

        capital = CapitalGeneral.query.first()
        if capital.monto < monto:
            flash('El banco no tiene suficiente capital.', 'danger')
            return redirect(url_for('user.mis_prestamos'))

        capital.monto -= monto

        fecha_inicio = datetime.now()
        fecha_fin = fecha_inicio + timedelta(days=tipo.duracion_dias)
        saldo_final = monto * (1 + tipo.interes / 100)

        prestamo = Loan(
            user_id=current_user.id,
            loan_type_id=tipo.id,
            monto=monto,
            saldo=saldo_final,
            pagado=0.0,
            estado='activo',
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        current_user.balance += monto
        db.session.add(prestamo)
        db.session.commit()
        flash('Préstamo otorgado y capital actualizado.', 'success')
        return redirect(url_for('user.mis_prestamos'))

    prestamos_info = [{
        'id': p.id,
        'nombre': p.loan_type.nombre,
        'tiempo_restante': max((p.fecha_fin - datetime.now()).days, 0),
        'total_a_pagar': p.saldo,
        'estado': p.estado,
        'saldo': p.saldo,
        'pagado': p.pagado
    } for p in prestamos]

    return render_template('user/mis_prestamos.html', tipos=tipos, prestamos=prestamos_info)

@user_bp.route('/pagar_prestamo/<int:loan_id>', methods=['POST'])
@login_required
def pagar_prestamo(loan_id):
    prestamo = Loan.query.get_or_404(loan_id)
    monto_pago = float(request.form.get('monto'))

    if current_user.balance < monto_pago:
        flash('Saldo insuficiente.', 'danger')
        return redirect(url_for('user.mis_prestamos'))

    capital = CapitalGeneral.query.first()

    prestamo.pagado += monto_pago
    prestamo.saldo -= monto_pago
    current_user.balance -= monto_pago
    capital.monto += monto_pago

    if prestamo.saldo <= 0:
        prestamo.estado = 'cerrado'

    db.session.commit()
    flash('Pago exitoso y capital actualizado.', 'success')
    return redirect(url_for('user.mis_prestamos'))

@user_bp.route('/transferencia', methods=['GET', 'POST'])
@login_required
def transferencia():
    if request.method == 'POST':
        username_destino = request.form.get('username')
        monto_str = request.form.get('monto')

        # Validar monto
        try:
            monto = float(monto_str)
            if monto <= 0:
                flash('El monto debe ser mayor a cero.', 'danger')
                return redirect(url_for('user.transferencia'))
        except (ValueError, TypeError):
            flash('Monto inválido.', 'danger')
            return redirect(url_for('user.transferencia'))

        destino = User.query.filter_by(username=username_destino).first()

        if not destino:
            flash('Usuario destino no existe.', 'danger')
            return redirect(url_for('user.transferencia'))

        if destino.id == current_user.id:
            flash('No puedes transferirte a ti mismo.', 'danger')
            return redirect(url_for('user.transferencia'))

        if current_user.balance < monto:
            flash('Saldo insuficiente.', 'danger')
            return redirect(url_for('user.transferencia'))

        try:
            # Actualizar balances
            current_user.balance -= monto
            destino.balance += monto

            # Crear transacciones con monto negativo para emisor y positivo para receptor
            trans_emisor = Transaction(
                user_id=current_user.id,
                tipo='transferencia enviada',
                monto=-monto
            )
            trans_receptor = Transaction(
                user_id=destino.id,
                tipo='transferencia recibida',
                monto=monto
            )

            db.session.add(trans_emisor)
            db.session.add(trans_receptor)
            db.session.commit()
            flash(f'Transferencia de Bs. {monto} a {destino.username} realizada con éxito.', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al realizar la transferencia: {str(e)}', 'danger')

        return redirect(url_for('user.transferencia'))

    transacciones = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.fecha.desc()).all()
    return render_template('user/transferencia.html', transacciones=transacciones)


@user_bp.route('/depositar', methods=['GET', 'POST'])
@login_required
def depositar():
    if request.method == 'POST':
        cajero_username = request.form.get('cajero_username')
        celular_cajero = request.form.get('celular_cajero')
        codigo_cajero = request.form.get('codigo_cajero')
        monto = float(request.form.get('monto'))

        if not cajero_username or not celular_cajero or not codigo_cajero:
            flash('Debe completar todos los datos del cajero', 'danger')
            return redirect(url_for('user.depositar'))

        current_user.balance += monto
        db.session.add(Transaction(user_id=current_user.id, tipo=f'Depósito por cajero {cajero_username}', monto=monto, fecha=datetime.now()))
        db.session.commit()
        flash('Depósito realizado', 'success')
    return render_template('user/depositar.html')

@user_bp.route('/retirar')
@login_required
def retirar():
    codigo = random.randint(100000, 999999)
    return render_template('user/retirar.html', user=current_user, codigo=codigo)
