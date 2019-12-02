from flask import request, render_template_string
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Length, EqualTo, Email
from flask_babel import Babel, _, lazy_gettext as _l
from app.user.models import User, UserPhones
from app.main_func import utils as main_utils
from wtforms.widgets import html_params, HTMLString
from flask_wtf import Form


################################################ Формы для редактирования данных профиля ###########################################

class CreateNewEmail(FlaskForm):
    '''
    Форма для создания нового пароля
    '''
    username = HiddenField(_l('Логин'), validators=[DataRequired()], render_kw={"class" : "form-control my-input-field"})
    email = StringField(_l('Введите электронную почту'), validators=[DataRequired(), Email()], render_kw={"class" : "form-control my-input-field"})
    
    confirm_registration = SubmitField(_l('Выслать ссылку'), render_kw={"class" : "button"})
    cancel_registration = SubmitField(_l('Отменить'), render_kw={"class" : "button"})


    def validate_email(self, email):
        user = User.query.filter_by(email=self.email.data).first()
        if user is not None: 
            if user.username != self.username.data:                
                raise ValidationError(_l('Пожалуйста, используйте другую почту.'))            

class CreateNewEmailCongratulation(FlaskForm):
    '''
    Форма поздравления пользователя с подтверждением адреса электронной почты
    '''
    submit = SubmitField(_l('Сохранить новый email'), render_kw={"class" : "button"})
    
class CreateNewPassword(FlaskForm):
    '''
    Форма для создания нового пароля
    '''
    old_password = PasswordField(_l('Старый пароль'), validators=[DataRequired()], render_kw={"class" : "form-control my-input-field"})

    password = PasswordField(_l('Пароль'), validators=[DataRequired()], render_kw={"class" : "form-control my-input-field"})
    password2 = PasswordField(_l(
        'Повторите пароль'), validators=[DataRequired(), EqualTo('password')], render_kw={"class" : "form-control my-input-field"})
    
    confirm_registration = SubmitField(_l('Сохранить'), render_kw={"class" : "button"})

    def validate_password(self, password):
        if len(password.data) < 5:
            raise ValidationError(_l('Пароль длолжен содержать более 4 символов.'))

class EditProfileForm(FlaskForm):
    '''
    class for visualisation form for insert some changes in profile of user.
    '''
    username = StringField(_l('Логин'), validators=[DataRequired()], render_kw={"class": "form-control my-input-field"})
    about_me = TextAreaField(_l('Обо мне'), validators=[Length(min=0, max=140)], render_kw={"class": "form-control my-input-field"})    

    submit = SubmitField(_l('Сохранить'), render_kw={"class": "button"})
    phone_button = SubmitField(_('Ред. телефон'), render_kw={"class": "button"})
    email_button = SubmitField(_('Добавить почту'), render_kw={"class": "button"})
    email_change_button = SubmitField(_('Изменить почту'), render_kw={"class": "button"})
    change_password_button = SubmitField(_('Изменить пароль'), render_kw={"class": "button"})


    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                name = username.data
                username.data = self.original_username
                raise ValidationError(_l(f'Пользователь с именем {name} уже есть. Измените имя.'))
    
class EditProfilAddPhoneForm(FlaskForm):
    '''
    class for visualisation form to add phone of user.
    '''
    number_phone = StringField(_l('Введите номер телефона'), render_kw={"class": "form-control my-input-field"})
    code_of_confirm = StringField(_l('Введите код подтверждения из смс'), render_kw={"class": "form-control my-input-field" })

    submit = SubmitField(_l('Выслать код'), render_kw={"class": "button"}) #сохраняем номер и хэш в бд
    commit_confirm = SubmitField(_l('Подтвердить номер'), render_kw={"class": "button"}) #сверяем с хешем 
    phone_button_delete = SubmitField(_('Удалить'), render_kw={"class": "button"})
    phone_button_cancel = SubmitField(_('Отмена'), render_kw={"class": "button"})


    def __init__(self, original_number_phone, *args, **kwargs):
        super(EditProfilAddPhoneForm, self).__init__(*args, **kwargs)
        self.original_number_phone = original_number_phone

    def validate_number_phone(self, number_phone):       
        exists_phone = UserPhones.query.filter(UserPhones.number == number_phone.data).count()

        
        if self.number_phone.data is None or self.number_phone.data == "":
            raise ValidationError(_l('Нужно ввести номер телефона.'))

      #  if exists_phone > 0:
      #      raise ValidationError(_l('Этот номер уже зарегистрирован.'))

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

################################################################################################################################

################################################ Формы для функционала страницы ###########################################

               
class PostForm(FlaskForm):
    post = TextAreaField(_l('Cкажите что-нибудь'), validators=[
        DataRequired(), Length(min=1, max=140)], render_kw={"class": "form-control my-input-field"})
    submit = SubmitField(_l('Опубликовать'), render_kw={"class": "button"})
    
#здесь вставить коментарий к коментарию

class SearchForm(FlaskForm):
    '''       
          Поле q не требует никаких объяснений, поскольку оно аналогично другим текстовым 
          полям, которые я использовал в прошлом. Для этой формы я решил не использовать кнопку отправки. 
          Для формы, которая имеет текстовое поле, браузер отправит форму, когда вы нажмете Enter 
          с фокусом на поле, поэтому кнопка не нужна. Я также добавил
          функцию конструктора __init__, которая предоставляет значения для аргументов formdata и csrf_enabled, 
          если они не предоставляются вызывающим. Аргумент formdata определяет, откуда Flask-WTF получает формы. 
          По умолчанию используется request.form, где Flask помещает значения форм, которые 
          передаются через запрос POST. Формы, представленные через запрос GET, получают значения
          полей в строке запроса, поэтому мне нужно указать Flask-WTF на request.args, где Flask 
          записывает аргументы строки запроса. И, как вы помните, формы добавили CSRF-защиту по 
          умолчанию, с добавлением токена CSRF, который добавляется в форму через конструкцию form.hidden_tag() в шаблонах. Д
          ля работы с интерактивными поисковыми ссылками CSRF-защиту необходимо отключить, поэтому я устанавливаю csrf_enabled в False, 
          так что Flask-WTF знает, что ему необходимо обходить проверку CSRF для этой формы.
    '''
    q = StringField(_l('Поиск'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):

        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

################################################################################################################################
