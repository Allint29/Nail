from datetime import datetime
from flask_wtf import FlaskForm;
from wtforms import Form, HiddenField, StringField, SubmitField, TextAreaField, DateField, SelectField, IntegerField, FormField
from wtforms.validators import DataRequired, ValidationError, Length, InputRequired, NumberRange
from flask_babel import Babel, _, lazy_gettext as _l
from app.main_func import utils as main_utils

class AdminMenu(FlaskForm):
    '''
    Форма перенаправления из админки: Редактирование Работ, Пользователей, Расписание
    '''    
    to_users = SubmitField(_('Клиенты'), render_kw={"class": "button", "type": "submit"})
    to_works = SubmitField(_('Работы'), render_kw={"class": "button ", "type": "button"})
    to_schedule = SubmitField(_('Расписание'),  render_kw={"class" : "button ", "type": "submit"})


class EditUsersPhoneForm(FlaskForm):
    '''
    Форма телефонов клиента
    '''
    id_phone = IntegerField(_('ID телефона'),  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    number_phone_field = IntegerField(_('Номер'),  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    phone_confirmed_field = IntegerField(_('Подтвержден'), validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit", "type": "checkbox"})
    date_to_expire_field = DateField (_('Дата до удаления'), validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit", "type": "date"})
    black_list_field = IntegerField(_('Черный список'),  render_kw={"class" : "fl-text-field-user-edit", "type": "checkbox"})
    to_edit_button = SubmitField(_('Редактор'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})

class EditUsersForm(FlaskForm):
    '''
    Форма обработки Клиентов - удаление, блокировка, создание нового клиента
    '''
    id_user = StringField(_('ID клиента'),  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    username_field= StringField(_('Имя клиента'), validators=[DataRequired],  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    about_me_field =  StringField(_('О клиенте'), validators=[],  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    email_field = StringField(_('Email'), validators=[],  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    email_confirmed_field = SelectField(_('Почта проверена'), validators=[DataRequired()], choices=[('0', _('Не подтверждена')), ('1', _('Подтверждена'))], render_kw={"class" : "fl-text-field-user-edit", "type": "checkbox"})
    registration_date_field = DateField (_('Дата регистрации'), validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit", "type": "date"})
    
    trying_to_enter_new_phone_field = IntegerField(_('Осталось смен телефона'), validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    role_field = SelectField(_('Права'), validators=[DataRequired()], choices=[('admin', _('Администратор')), ('user', _('Клиент'))],render_kw={"class" : "fl-text-field-user-edit"}) 
    last_seen_field = DateField (_('Последний визит'), validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit", "type": "date"})
    type_connection_field=SelectField(_('Связь'), validators=[DataRequired()], choices=[('whatsapp', _('WhatsApp')), ('vk', _('ВКонтакте')), ('instagram', _('Instagram')), ('_number_phone', _('Телефон'))],render_kw={"class" : "fl-text-field-user-edit"}) 
    
    to_edit_button = SubmitField(_('Редактор'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})
    to_delete_button = SubmitField(_('Удалить'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})
    to_schedule_button = SubmitField(_('Записать'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})

class RouterUserForm(FlaskForm):
    '''
    Форма поиска Клиентов - поиск, удаление, блокировка, создание нового клиента
    '''
    find_field= StringField(_('Имя/телефон/права'), validators=[],  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    to_find_button = SubmitField(_('Поиск'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})
    to_create_button = SubmitField(_('Новый'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})
       