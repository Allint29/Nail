from datetime import datetime
from flask_wtf import FlaskForm;
from wtforms import Form, HiddenField, StringField, SubmitField, TextAreaField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Length, InputRequired, NumberRange
from flask_babel import Babel, _, lazy_gettext as _l
from app.master_schedule.models import DateTable, ScheduleOfDay
from app.main_func import utils as main_utils


class CountInt(object):
    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if not message:
            message = u'Field must be between %i and %i characters long.' % (min, max)
        self.message = message

    def __call__(self, form, field):
        l = field.data and len(field.data) or 0
        if l < self.min or self.max != -1 and l > self.max:
            raise ValidationError(self.message)

class ScheduleTimeToShow(FlaskForm):
    '''
    Форма которая показывает время дня и его статус: занято или свободно
    '''    
    date_field_start = DateField (_('с'), validators=[DataRequired()], render_kw={"class" : "shedule-text-field comment-field", "type": "date", "placeholder" : _('Выберите дату')})
    date_field_end = DateField (_('по'), validators=[DataRequired()], render_kw={"class" : "shedule-text-field comment-field", "type": "date", "placeholder" : _('Выберите дату')})
    
    submit = SubmitField(_('Выбрать'), render_kw={"class": "button"});


class ScheduleTimeToShowMaster(FlaskForm):
    '''
    Форма которая показывает время дня и его статус: занято или свободно
    '''    
    date_field = DateField (_('дата'), validators=[DataRequired()], render_kw={"class" : "shedule-text-field-master comment-field", "type": "date", "placeholder" : _('Выберите дату')})
    submit = SubmitField(_('Выбрать'), render_kw={"class": "button"});

class TimeForm(FlaskForm):
    '''
    Форма для выбора времени для редактирования
    '''

    id_time = StringField(_('ID тайминга'),  render_kw={"class" : "", "type": "text"})   
    change_button = SubmitField(_('Изменить'), render_kw={"class": "button", "type": "submit"})
    reserve_button = SubmitField(_('Занять'), render_kw={"class": "button", "type": "submit"})
    delete_button = SubmitField(_('Освободить'), render_kw={"class": "button", "type": "submit"})
    

class ScheduleMaster(FlaskForm):
    '''
    Форма расписание которое видит мастер
    '''
    id_time = StringField(_('ID тайминга'),  render_kw={"class" : "comment-field", "type": "text"})   
    name_time = StringField(_('Время'),  render_kw={"class" : "comment-field", "type": "text"})
    
    client_id_field=StringField(_('Клиент_Id'), validators=[DataRequired()], render_kw={"class" : "comment-field"}, default="")
    client_field=StringField(_('Клиент'), validators=[DataRequired()], render_kw={"class" : "comment-field"}, default="")
    take_client_button = SubmitField(_('Выбрать'), render_kw={"class": "button fl-cancel-field", "type": "button"})
    
    adress_client_field=StringField(_('Соцсети'), render_kw={"class" : "comment-field"}, default="")
    phone_client_field = StringField(_('Телефон'), render_kw={"class" : "comment-field"}, default="")
    email_client_field = StringField(_('Почта'), render_kw={"class" : "comment-field"}, default="")
    type_connection_field=StringField(_('Тип связи'), render_kw={"class" : "comment-field"}, default="")#SelectField(_('Связь'), validators=[DataRequired()], choices=[('whatsapp', _('WhatsApp')), ('vk', _('ВКонтакте')), ('instagram', _('Instagram')), ('_number_phone', _('Телефон'))],render_kw={"class" : "comment-field"}) 

    work_type_field=SelectField(_('Тип работы'), validators=[DataRequired()], choices=[('man', _('Маникюр')), ('ped', _('Педикюр')), ('man_ped', _('Ман+Пед')),('some', _('Другое'))], render_kw={"class" : "comment-field"}) 
    price_field=StringField(_('Цена'), validators=[DataRequired()], render_kw={"class" : "comment-field"}, default="0")
    

    node_field=TextAreaField(_('Примечание'), validators=[DataRequired()], render_kw={"class" : "comment-field"}, default="")
    time_empty_field=SelectField(_('Занять'), validators=[DataRequired()], choices=[(1, _('Свободно')), (0, _('Занято'))],render_kw={"class" : "comment-field"}) 
    reserve_time_for_client_field = SelectField(_('Резерв времени'), validators=[DataRequired()], choices=[('one', _('Один час')), ('two', _('Два часа')), ('three', _('Три часа'))],render_kw={"class" : "comment-field"})
    client_come = SelectField(_('Пришел ли клиент'), validators=[DataRequired()], choices=[(0, _('Нет')), (1, _('Да')),  (2, _('Опоздал'))], render_kw={"class" : "comment-field"}, default=0)

    submit = SubmitField(_('Записать'), render_kw={"class": "button"})
    cancel_field = SubmitField(_('Отменить'), render_kw={"class": "button fl-cancel-field"})
    clear_field = SubmitField(_('Освободить'),  render_kw={"class" : "button clear-field", "type": "submit"})

    def validate_price_field(self, price_field):
        
        if main_utils.is_digit(price_field.data) == False:
            raise ValidationError(_l('Можно вводить только числа'))

        price = float(price_field.data)
        
        if price< 0 or price > 10000:            
            raise ValidationError(_l('Цена не может быть отрицательной или больше 10000'))