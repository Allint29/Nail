from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
from flask_babel import Babel, _, lazy_gettext as _l

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    password2 = PasswordField(_l(
        'Повторите пароль'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Установить новый пароль'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Почта'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Отправить ссылку на почту'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Cкажите что-нибудь'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Опубликовать'))

class EditProfileForm(FlaskForm):
    '''
    class for visualisation form for insert some changes in profile of user.
    '''
    username = StringField(_l('Имя пользователя'), validators=[DataRequired()])
    about_me = TextAreaField(_l('Обо мне'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Опубликовать'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_l('Пользователь с таким именем уже есть. Измените имя.'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Имя пользователя'), validators=[DataRequired()])
    email = StringField(_l('Почта'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    password2 = PasswordField(_l(
        'Повторите пароль'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Пожалуйста, используйте другое имя.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Пожалуйста, используйте другую почту.'))


class LoginForm(FlaskForm):
    username = StringField(_l('Пользователь'), validators=[DataRequired()])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Запомнить меня'))
    submit = SubmitField(_l('Войти'))

