from email.mime import image
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, FileField, PasswordField, BooleanField, MultipleFileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp



class AddItemForm(FlaskForm):
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	price = FloatField("Preço:", validators=[DataRequired()])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()])
	details = StringField("Detalhes:", validators=[DataRequired()])
	price_id = StringField("Stripe id:", validators=[DataRequired()])
	submit = SubmitField("Adicionar")

class AddBannerForm(FlaskForm):
	image = FileField("Imagem:", validators=[DataRequired()])
	submit = SubmitField("Salvar")

class OrderEditForm(FlaskForm):
	status = StringField("Status:", validators=[DataRequired()])
	submit = SubmitField("Update")

class AdminRegisterForm(FlaskForm):
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	phone = StringField("Telefone:", validators=[DataRequired(), Length(max=30)])
	email = StringField("Email:", validators=[DataRequired(), Email()])
	password = PasswordField("Senha:", validators=[DataRequired(), Regexp("^[a-zA-Z0-9_\-&$@#!%^*+.]{8,30}$", message='Password must be 8 characters long and should contain letters, numbers and symbols.')])
	confirm = PasswordField("Confirmar Senha:",validators=[EqualTo('password', message='Passwords must match')])
	admin = BooleanField("Admin")
	submit = SubmitField("Cadastrar")