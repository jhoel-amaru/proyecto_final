from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class TransferForm(FlaskForm):
    monto = FloatField('Monto', validators=[DataRequired(), NumberRange(min=1)])
    destino = StringField('Cuenta destino', validators=[DataRequired()])
    submit = SubmitField('Transferir')
