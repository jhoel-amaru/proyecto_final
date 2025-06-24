from app import db
from datetime import datetime

class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    loan_type_id = db.Column(db.Integer, db.ForeignKey('loan_type.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    saldo = db.Column(db.Float, nullable=False)
    pagado = db.Column(db.Float, default=0.0)
    fecha = db.Column(db.DateTime, server_default=db.func.now())
    estado = db.Column(db.String(20), default='activo')

    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_fin = db.Column(db.DateTime, nullable=True)
