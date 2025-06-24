from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo

class CreateTellerForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    sucursal = StringField('Sucursal', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    correo = StringField('Correo', validators=[DataRequired()])
    ci = StringField('CI', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Guardar')

class LoanTypeForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    monto_maximo = FloatField('Monto máximo', validators=[DataRequired()])
    plazo_dias = IntegerField('Plazo (días)', validators=[DataRequired()])
    interes = FloatField('Interés (%)', validators=[DataRequired()])
    submit = SubmitField('Guardar')
