from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class DepositForm(FlaskForm):
    ci = StringField('CI del cliente', validators=[DataRequired()])
    monto = FloatField('Monto', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Depositar')

class WithdrawForm(FlaskForm):
    ci = StringField('CI del cliente', validators=[DataRequired()])
    monto = FloatField('Monto', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Retirar')
