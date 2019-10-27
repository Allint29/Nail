from app.user.models import User, UserPhones
from flask_wtf import FlaskForm
from flask_babel import Babel, _, lazy_gettext as _l
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from flask import Flask, render_template_string
from flask_wtf import Form
from wtforms import StringField
from wtforms.widgets import html_params, HTMLString

class ButtonWidget(object):
    """
    Renders a multi-line text area.
    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    input_type = 'submit'

    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        return HTMLString('<button {params}>{label}</button>'.format(
            params=self.html_params(name=field.name, **kwargs),
            label=field.label.text)
        )


class ButtonField(StringField):
    widget = ButtonWidget()

################################################# Вход в личный кабинет ##############################################


class LoginForm(FlaskForm):
    '''
    form for enter to private side of site
    '''
    username = StringField(_l('Пользователь'), validators=[DataRequired()], render_kw={"class" : "form-control comment-field field-user", "placeholder": _l("Логин")})
    password = PasswordField(_l('Пароль'), validators=[DataRequired()], render_kw={"class" : "form-control comment-field field-password", "placeholder": _l("Пароль")})
    remember_me = BooleanField(_l('Запомнить меня'), render_kw={"class" : "from-check-input visually-hidden"})
    
    submit = SubmitField(_l('Войти'), render_kw={"class" : "button"})


#########################################################################################################################
               
################################################# Регистрация - общая форма ##############################################

class RegistrationMainForm(FlaskForm):
    '''
    Form to shoose method of registration. It redirect to form for different kind of registration
    '''    
    submit_register_by_email = SubmitField (_('Регистрация по электронной почте'), render_kw={"class" : "btn btn-primary"} )
    submit_register_by_phone = SubmitField (_('    Регистрация по телефону     '), render_kw={"class" : "btn btn-primary"})
#########################################################################################################################
 

################################################# Регистрация по телефону ##############################################


class RegistrationByPhoneForm(FlaskForm):
    '''
    Form to enter login and phone to get registration
    '''
    username_for_phone = StringField(_l('Придумайте логин'), validators=[DataRequired()], render_kw={"class" : "form-control"})
    number_phone = StringField(_l('Телефон'), render_kw={"class" : "form-control"})    


    send_code = SubmitField(_l('Выслать смс с кодом подтверждения'), render_kw={"class" : "btn btn-primary"})   
    
    def validate_username_for_phone(self, username_for_phone):
        user = User.query.filter_by(username=username_for_phone.data).first()
        if user is not None:
            raise ValidationError(_l('Пожалуйста, используйте другое имя.'))

    def validate_number_phone(self, number_phone):       
        exists_phone = UserPhones.query.filter(UserPhones.number == number_phone.data).count()
        
        if self.number_phone.data is None or self.number_phone.data == "":
            raise ValidationError(_l('Нужно ввести номер телефона.'))

        if exists_phone > 0:
            raise ValidationError(_l('Этот номер уже зарегистрирован.'))

        if len(number_phone.data) < 10:
            raise ValidationError(_l('Короткий номер! Введите телефон в формате 10 цифр, например 9271102535'))
        
        if len(number_phone.data) > 10:
            raise ValidationError(_l('Длинный номер! Введите телефон в формате 10 цифр, например 9271102535'))
        
        #только цифры в номере
        if not number_phone.data.isdigit():     
            raise ValidationError(_l('Нельзя использовать буквы в номере телефона! Введите телефон в формате 10 цифр, например 9271102535'))
    
        #здесь создаем массив из валидных операторов для отсылки смс
        valide_mobil_code_zone = []
        first_code = 900
    
        while first_code < 1000:
            valide_mobil_code_zone.append(first_code)
            first_code = first_code + 1
    
        if not int(str(number_phone.data)[:3]) in valide_mobil_code_zone:
            raise ValidationError(_l('Данный телефон не принадлежит российским операторам сотовой связи! Введите телефон в формате 10 цифр, например 9271102535'))

class RegistrationByPhoneConfirmForm(FlaskForm):
    '''
    Форма для подтверждения регистрации по телефону - проверяет код подтверждение с хешем в БД
    '''
    code_of_confirm = StringField(_l('Введите код подтверждения из смс'), render_kw={"class": "form-control" })
    
    confirm_registration = SubmitField(_l('Подтвердить номер телефона'), render_kw={"class" : "btn btn-primary"})   
    phone_button_cancel = SubmitField(_('Отмена'), render_kw={"class": "btn btn-default"})    

class RegistrationByPhoneNewPasswordForm(FlaskForm):    
    '''
    Форма для создания нового пароля при регистрации по телефону
    '''
    password = PasswordField(_l('Пароль'), render_kw={"class" : "form-control"})
    password2 = PasswordField(_l('Повторите пароль'),  render_kw={"class" : "form-control"})
    
    confirm_registration = SubmitField(_l('Завершить регистрацию'), render_kw={"class" : "btn btn-primary"})
    phone_button_cancel = SubmitField(_l('Отмена'), render_kw={"class" : "btn btn-primary"}) 


    
#########################################################################################################################
               
################################################# Регистрация по электронной почте ##############################################

class RegistrationRequestForm(FlaskForm):
    '''
    form to enter login and e-mail of user for registration, form check login and e-mail for doublement
    '''
    username = StringField(_l('Имя пользователя'), validators=[DataRequired()], render_kw={"class" : "form-control"})
    email = StringField(_l('Почта'), validators=[DataRequired(), Email()], render_kw={"class" : "form-control"})
    
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

    def validate_password(self, password):
       # print(password.data)
        #print(password.name)
        if len(password.data) < 5:
            raise ValidationError(_l('Пароль длолжен содержать более 4 символов.'))

#########################################################################################################################

################################################# Восстановление пароля - общая форма ##############################################

class ResetPasswordMainForm(FlaskForm):
    '''
    Форма выбора способа восстановления пароля
    '''    
    submit_reset_by_email = SubmitField (_('Восстановление по электронной почте'), render_kw={"class" : "btn btn-primary"} )
    submit_reset_by_phone = SubmitField (_('    Восстановление по телефону     '), render_kw={"class" : "btn btn-primary"})
#########################################################################################################################
 
################################################# Восстановление пароля по электронной почте ##############################################

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
    
    def validate_password(self, password):
        if len(password.data) < 5:
            raise ValidationError(_l('Пароль длолжен содержать более 4 символов.'))

#########################################################################################################################

################################################# Восстановление пароля по телефону ##############################################

class ResetPasswordByPhoneRequestForm(FlaskForm):
    '''
    class form of enter email to reset password
    '''
    number_phone = StringField(_l('Введите зарегистрированный номер телефона'), validators=[DataRequired()], render_kw={"class" : "form-control"})
    submit = SubmitField(_l('Восстановить пароль'), render_kw={"class" : "btn btn-primary"})
    
    def validate_number_phone(self, number_phone):    
        
        exist_phone = UserPhones.query.filter(UserPhones.number == number_phone.data).first()
                
        if self.number_phone.data is None or self.number_phone.data == "":
            raise ValidationError(_l('Нужно ввести номер телефона.'))

        if not exist_phone:
            raise ValidationError(_l('Данный номер не зарегистрирован на сайте. Пройдите регистрацию.'))

        if exist_phone and exist_phone.black_list == 1:
            raise ValidationError(_l('Ваш номер внесен в черный список. Обратитесь к администрации.'))
        
        if len(number_phone.data) < 10:
            raise ValidationError(_l('Короткий номер! Введите телефон в формате 10 цифр, например 9271102535'))
        
        if len(number_phone.data) > 10:
            raise ValidationError(_l('Длинный номер! Введите телефон в формате 10 цифр, например 9271102535'))
        
        #только цифры в номере
        if not number_phone.data.isdigit():     
            raise ValidationError(_l('Нельзя использовать буквы в номере телефона! Введите телефон в формате 10 цифр, например 9271102535'))
    
        #здесь создаем массив из валидных операторов для отсылки смс
        valide_mobil_code_zone = []
        first_code = 900
    
        while first_code < 1000:
            valide_mobil_code_zone.append(first_code)
            first_code = first_code + 1
    
        if not int(str(number_phone.data)[:3]) in valide_mobil_code_zone:
            raise ValidationError(_l('Данный телефон не принадлежит российским операторам сотовой связи! Введите телефон в формате 10 цифр, например 9271102535'))

#########################################################################################################################
