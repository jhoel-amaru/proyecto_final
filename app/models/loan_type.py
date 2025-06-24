from app import db

class LoanType(db.Model):
    __tablename__ = 'loan_type'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    monto_maximo = db.Column(db.Float, nullable=False)
    plazo_dias = db.Column(db.Integer, nullable=False)
    interes = db.Column(db.Float, nullable=False)
    duracion_dias = db.Column(db.Integer, nullable=False)  # <- aquí debe estar

    loans = db.relationship('Loan', backref='loan_type', lazy=True)
