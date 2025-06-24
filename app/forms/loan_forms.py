from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

class LoanRequestForm(FlaskForm):
    monto = FloatField('Monto solicitado', validators=[DataRequired(), NumberRange(min=1)])
    tipo = SelectField('Tipo de préstamo', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Solicitar préstamo')
