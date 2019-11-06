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
    id_phone = IntegerField(_('ID телефона'),  render_kw={"class" : "fl-text-field", "type": "text"})
    number_phone_field = IntegerField(_('Номер'),  render_kw={"class" : "fl-text-field", "type": "text"})
    phone_confirmed_field = IntegerField(_('Подтвержден'), validators=[DataRequired()], render_kw={"class" : "fl-text-field", "type": "checkbox"})
    date_to_expire_field = DateField (_('Дата до удаления'), validators=[DataRequired()], render_kw={"class" : "fl-text-field", "type": "date"})
    black_list_field = IntegerField(_('Черный список'),  render_kw={"class" : "fl-text-field", "type": "checkbox"})


class EditUsersForm(FlaskForm):
    '''
    Форма обработки Клиентов - поиск, удаление, блокировка, создание нового клиента
    '''
    id_user = IntegerField(_('ID клиента'),  render_kw={"class" : "fl-text-field", "type": "text"})
    username_field= StringField(_('Имя клиента'), validators=[DataRequired],  render_kw={"class" : "fl-text-field", "type": "text"})
    about_me_field =  StringField(_('О клиенте'), validators=[],  render_kw={"class" : "fl-text-field", "type": "text"})
    email_field = StringField(_('Email'), validators=[],  render_kw={"class" : "fl-text-field", "type": "text"})
    email_confirmed_field = SelectField(_('Почта проверена'), validators=[DataRequired()], choices=[('0', _('Не подтверждена')), ('1', _('Подтверждена'))], render_kw={"class" : "fl-text-field", "type": "checkbox"})
    registration_date_field = DateField (_('Дата регистрации'), validators=[DataRequired()], render_kw={"class" : "fl-text-field", "type": "date"})
   
    trying_to_enter_new_phone_field = IntegerField(_('Осталось смен телефона'), validators=[DataRequired()], render_kw={"class" : "fl-text-field", "type": "text"})
    role_field = SelectField(_('Права'), validators=[DataRequired()], choices=[('admin', _('Администратор')), ('user', _('Клиент'))],render_kw={"class" : "fl-text-field"}) 
    last_seen_field = DateField (_('Последний визит'), validators=[DataRequired()], render_kw={"class" : "fl-text-field", "type": "date"})
    type_connection_field=SelectField(_('Связь'), validators=[DataRequired()], choices=[('whatsapp', _('WhatsApp')), ('vk', _('ВКонтакте')), ('instagram', _('Instagram')), ('_number_phone', _('Телефон'))],render_kw={"class" : "fl-text-field"}) 
    #phones  = SelectField(coerce=int)
    #phone_form_field = FormField(EditUsersPhoneForm)

#class ScheduleMaster(FlaskForm):
#    '''
#    Форма расписание которое видит мастер
#    '''
#    id_time = StringField(_('ID тайминга'),  render_kw={"class" : "comment-field", "type": "text"})   
#            
#    work_type_field=SelectField(_('Тип работы'), validators=[DataRequired()], choices=[('man', _('Маникюр')), ('ped', _('Педикюр')), ('man_ped', _('Ман+Пед')),('some', _('Другое'))], render_kw={"class" : "comment-field"}) 
#    price_field=StringField(_('Цена'), validators=[DataRequired()], render_kw={"class" : "comment-field"}, default="0")
#    
#    type_connection_field=SelectField(_('Связь'), validators=[DataRequired()], choices=[('whatsapp', _('WhatsApp')), ('vk', _('ВКонтакте')), ('instagram', _('Instagram')), ('_number_phone', _('Телефон'))],render_kw={"class" : "comment-field"}) 
#
#    client_field=StringField(_('Клиент'), validators=[DataRequired()], render_kw={"class" : "comment-field"}, default="")
#    adress_client_field=StringField(_('Адрес'), validators=[DataRequired()], render_kw={"class" : "comment-field"}, default="")
#    node_field=TextAreaField(_('Примечание'), validators=[DataRequired()], render_kw={"class" : "comment-field"}, default="")
#    time_empty_field=SelectField(_('Занять'), validators=[DataRequired()], choices=[(1, _('Свободно')), (0, _('Занято'))],render_kw={"class" : "comment-field"}) 
#    reserve_time_for_client_field = SelectField(_('Резерв времени'), validators=[DataRequired()], choices=[('one', _('Один час')), ('two', _('Два часа')), ('three', _('Три часа'))],render_kw={"class" : "comment-field"})
#    client_come = SelectField(_('Пришел ли клиент'), validators=[DataRequired()], choices=[(0, _('Нет')), (1, _('Да')),  (2, _('Опоздал'))], render_kw={"class" : "comment-field"}, default=0)
#
#    submit = SubmitField(_('Записать'), render_kw={"class": "button"})
#    cancel_field = SubmitField(_('Отменить'), render_kw={"class": "button fl-cancel-field"})
#    clear_field = SubmitField(_('Освободить'),  render_kw={"class" : "button clear-field", "type": "submit"})
#
#    def validate_price_field(self, price_field):
#        
#        if main_utils.is_digit(price_field.data) == False:
#            raise ValidationError(_l('Можно вводить только числа'))
#
#        price = float(price_field.data)
#        
#        if price< 0 or price > 10000:            
#            raise ValidationError(_l('Цена не может быть отрицательной или больше 10000'))