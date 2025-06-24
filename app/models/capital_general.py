from app import db

class CapitalGeneral(db.Model):
    __tablename__ = 'capital_general'

    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<CapitalGeneral Bs. {self.monto}>'
