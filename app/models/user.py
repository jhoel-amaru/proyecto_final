from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(20), unique=True, nullable=False)
    direccion = db.Column(db.String(200))
    saldo = db.Column(db.Float, default=0.0)
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='cliente')
    balance = db.Column(db.Float, default=0.0)
    codigo_verificacion = db.Column(db.String(10))  # Código permanente del cajero

    transacciones = db.relationship('Transaction', backref='usuario', lazy=True)
    loans = db.relationship('Loan', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
