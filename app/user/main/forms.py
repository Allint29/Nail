from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import Babel, _, lazy_gettext as _l
from app.user.models import User


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

class PostForm(FlaskForm):
    post = TextAreaField(_l('Cкажите что-нибудь'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Опубликовать'))

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

