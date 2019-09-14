from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import Babel, _, lazy_gettext as _l
from app.user.models import User

class LoginForm(FlaskForm):
    '''
    form for enter to private side of site
    '''
    username = StringField(_l('Пользователь'), validators=[DataRequired()], render_kw={"class" : "form-control"})
    password = PasswordField(_l('Пароль'), validators=[DataRequired()], render_kw={"class" : "form-control"})
    remember_me = BooleanField(_l('Запомнить меня'), render_kw={"class" : "from-check-input"})
    
    submit = SubmitField(_l('Войти'), render_kw={"class" : "btn btn-primary"})

class RegistrationRequestForm(FlaskForm):
    '''
    form to enter login and e-mail of user for registration, form check login and e-mail for doublement
    '''
    username = StringField(_l('Имя пользователя'), validators=[DataRequired()], render_kw={"class" : "form-control"})
    email = StringField(_l('Почта'), validators=[DataRequired(), Email()], render_kw={"class" : "form-control"})
    #password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    #password2 = PasswordField(_l(
    #    'Повторите пароль'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Зарегистрироваться'), render_kw={"class" : "btn btn-primary"})

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Пожалуйста, используйте другое имя.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Пожалуйста, используйте другую почту.'))

class RegistrationForm(FlaskForm):
    '''
    class of form to first password to new user after check email
    '''

    password = PasswordField(_l('Пароль'), validators=[DataRequired()], render_kw={"class" : "form-control"})
    password2 = PasswordField(_l(
        'Повторите пароль'), validators=[DataRequired(), EqualTo('password')], render_kw={"class" : "form-control"})

    submit = SubmitField(_l('Завершить регистрацию'), render_kw={"class" : "btn btn-primary"})

class ResetPasswordRequestForm(FlaskForm):
    '''
    class form of enter email to reset password
    '''
    email = StringField(_l('Почта'), validators=[DataRequired(), Email()], render_kw={"class" : "form-control"})
    submit = SubmitField(_l('Отправить ссылку на почту'), render_kw={"class" : "btn btn-primary"})


class ResetPasswordForm(FlaskForm):
    '''
    form to enter new password after walked to link from email for reset password
    '''
    password = PasswordField(_l('Пароль'), validators=[DataRequired()], render_kw={"class" : "form-control"})
    password2 = PasswordField(_l(
        'Повторите пароль'), validators=[DataRequired(), EqualTo('password')], render_kw={"class" : "form-control"})
    submit = SubmitField(_l('Установить новый пароль'), render_kw={"class" : "btn btn-primary"})

