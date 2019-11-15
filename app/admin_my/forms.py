from re import *
from datetime import datetime
from flask_wtf import FlaskForm;
from app.user.models import *
from wtforms import Form, HiddenField, StringField, SubmitField, TextAreaField, DateField, SelectField, IntegerField, FormField
from wtforms.validators import UUID, DataRequired, ValidationError, Length, InputRequired, NumberRange, URL, Email, NumberRange
from flask_babel import Babel, _, lazy_gettext as _l
from app.main_func import utils as main_utils

class AdminMenu(FlaskForm):
    '''
    Форма перенаправления из админки: Редактирование Работ, Пользователей, Расписание
    '''    
    to_users = SubmitField(_('Клиенты'), render_kw={"class": "button", "type": "submit"})
    to_works = SubmitField(_('Работы'), render_kw={"class": "button ", "type": "button"})
    to_schedule = SubmitField(_('Расписание'),  render_kw={"class" : "button ", "type": "submit"})


#class EditUsersPhoneForm(FlaskForm):
#    '''
#    Форма телефонов клиента для отображения на станице поиска клиентов
#    '''
#    id_phone = IntegerField(_('ID телефона'),  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
#    number_phone_field = IntegerField(_('Номер'),  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
#    phone_confirmed_field = IntegerField(_('Подтвержден'), validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit", "type": "checkbox"})
#    date_to_expire_field = DateField (_('Дата до удаления'), validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit", "type": "date"})
#    black_list_field = IntegerField(_('Черный список'),  render_kw={"class" : "fl-text-field-user-edit", "type": "checkbox"})
#    to_edit_button = SubmitField(_('Редактор'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})

class EditUsersForm(FlaskForm):
    '''
    Форма обработки Клиентов - удаление, блокировка, создание нового клиента
    '''
    id_user = StringField(_('ID клиента'),  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    username_field= StringField(_('Имя клиента'), validators=[DataRequired()],  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    about_me_field =  StringField(_('О клиенте'), validators=[],  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    email_field = StringField(_('Email'), validators=[],  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    email_confirmed_field = SelectField(_('Почта проверена'), validators=[DataRequired()], choices=[('0', _('Не подтверждена')), ('1', _('Подтверждена'))], render_kw={"class" : "fl-text-field-user-edit"})
    registration_date_field = DateField (_('Дата регистрации'), validators=[], render_kw={"class" : "fl-text-field-user-edit", "type": "date"})
    
    trying_to_enter_new_phone_field = IntegerField(_('Cмен телефона'), validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    role_field = SelectField(_('Права'), validators=[DataRequired()], choices=[('admin', _('Администратор')), ('user', _('Клиент'))],render_kw={"class" : "fl-text-field-user-edit"}) 
    last_seen_field = DateField (_('Последний визит'), validators=[], render_kw={"class" : "fl-text-field-user-edit", "type": "date"})
    type_connection_field=SelectField(_('Связь'), coerce=int, validators=[DataRequired()], render_kw={"class" : "fl-text-field-user-edit"}) #choices=[('whatsapp', _('WhatsApp')), ('vk', _('ВКонтакте')), ('instagram', _('Instagram')), ('_number_phone', _('Телефон'))]
    
    to_save_button = SubmitField(_('Сохранить'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})
    to_edit_phone_button = SubmitField(_('Добавить телефон'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    to_edit_internet_account_button = SubmitField(_('Добавить соц.сеть'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    to_delete_button = SubmitField(_('Удалить'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    to_schedule_button = SubmitField(_('Записать'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})

    to_edit_button = SubmitField(_('Ред. пользователя'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    
    #def __init__(self, edit_users_form=None, phone_forms=None, social_forms=None, dic_val=None, *args, **kwargs):
    #    super(EditUsersForm, self).__init__(*args, **kwargs)
    #    self.original_edit_users_form = edit_users_form
    #    self.original_phone_forms = phone_forms
    #    self.original_social_forms = social_forms
    #    self.original_dic_val = dic_val

    def validate_username_field(self, username_field):
        user = User.query.filter_by(username=str(self.username_field.data)).first()
        if user is not None:
            if str(user.id) != str(self.id_user.data):  
                raise ValidationError(_l('Пожалуйста, используйте другое имя.'))

    def validate_email_field(self, email_field):
        if self.email_field.data != None: 
            if self.email_field.data != "":
                exists_email = [u for u in User.query.all() if str(u.email).lower() == str(self.email_field.data).lower()]
                
                if len(exists_email) > 0:                    
                    if str(exists_email[0].id) != str(self.id_user.data):            
                        raise ValidationError(_l('Эта почта зарегистрирована у другого пользователя.'))
    
                pattern_en = compile('(^|\s)[A-Z-a-z0-9_.]+@([A-Z-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
                pattern_ru = compile('(^|\s)[А-Я-а-я0-9_.]+@([А-Я-а-я0-9]+\.)+[рф]{2}(\s|$)')                
                is_valid = True if pattern_en.match(self.email_field.data) else True if pattern_ru.match(self.email_field.data) else False                
                if is_valid == False:                    
                    raise ValidationError(_l('Введен неправильный адрес электронной почты'))
                

              #  user_email_repit = User.query.filter(str(User.email).lower() == str(self.email_field.data).lower()).first()
              #  
              #  if user_email_repit is not None:
              #      if str(this_user.id) != str(self.id_user.data):
              #          raise ValidationError(_l('Данная почта уже зарегистрирована у другого пользователя.'))

class RouterUserForm(FlaskForm):
    '''
    Форма поиска Клиентов - поиск, удаление, блокировка, создание нового клиента
    '''
    find_field= StringField(_('Имя/телефон/права'), validators=[],  render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    to_find_button = SubmitField(_('Поиск'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})
    to_create_button = SubmitField(_('Новый'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
       

class EditPhoneUserForm(FlaskForm):
    '''
    Форма добавления телефона к пользователю из админки 
    '''
    id_phone_field = StringField(_('Id_телефона'), default=-1, render_kw={"class" : "visually-hidden"})
    user_id_field =  StringField(_('Id_пользователя'), validators=[DataRequired()], default=-1, render_kw={"class" : "visually-hidden"})
    number_phone = StringField(_l('Введите номер телефона'), validators=[], render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    to_black_list = SelectField(_('В черный список'), choices=[('0', _('Отключено')), ('1', _('Включено'))])
    phone_confirmed_field = IntegerField(_('Подтвержден'), validators=[], render_kw={"class" : "fl-text-field-user-edit", "type": "checkbox"})
    to_edit_button = SubmitField(_('Ред. тел.'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})

    to_save_button = SubmitField(_('Изм.'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    to_delete_button = SubmitField(_('Удал.'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    to_cancel_button = SubmitField(_('Отм.'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    
    to_save_submit = SubmitField(_('Сохр.'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})

    def validate_number_phone(self, number_phone):
        exists_phone = UserPhones.query.filter(UserPhones.number == self.number_phone.data).count()
        this_phone = UserPhones.query.filter(UserPhones.number == self.number_phone.data).first()
        #str_number_phone = str(number_phone)
        
        
        if self.number_phone.data is None or self.number_phone.data == "":
            raise ValidationError(_l('Нужно ввести номер телефона.'))

        if exists_phone > 0 and str(this_phone.id) != str(self.id_phone_field.data):            
            raise ValidationError(_l('Этот номер уже зарегистрирован.'))

        if len(self.number_phone.data) < 10:
         #   print('enter min')
            raise ValidationError(_l('Короткий номер! Введите телефон в формате 10 цифр, например 9271102535'))
        
        if len(self.number_phone.data) > 10:
            raise ValidationError(_l('Длинный номер! Введите телефон в формате 10 цифр, например 9271102535'))
        
        #только цифры в номере
        if not self.number_phone.data.isdigit():
            raise ValidationError(_l('Нельзя использовать буквы в номере телефона! Введите телефон в формате 10 цифр, например 9271102535'))
    
        #здесь создаем массив из валидных операторов для отсылки смс
        valide_mobil_code_zone = []
        first_code = 900
    
        while first_code < 1000:
            valide_mobil_code_zone.append(first_code)
            first_code = first_code + 1
    
        if not int((self.number_phone.data)[:3]) in valide_mobil_code_zone:
            raise ValidationError(_l('Данный телефон не принадлежит российским операторам сотовой связи! Введите телефон в формате 10 цифр, например 9271102535'))
        
class EditSocialForm(FlaskForm):
    '''
    Форма форма редактирования соцсети к пользователю из админки
    '''
    id_social_field = StringField(_('Id_соц.записи'),  default=-1, render_kw={"class" : "visually-hidden"})
    user_id_field =  StringField(_('Id_пользователя'), validators=[DataRequired()], default=-1, render_kw={"class" : "visually-hidden"})
    adress_social = StringField(_l('адрес соц. сети'), validators=[DataRequired(), URL(message=_('Неправильно набран адрес'))], render_kw={"class" : "fl-text-field-user-edit", "type": "text"})
    to_black_list = SelectField(_('В черный список'), choices=[('0', _('Отключено')), ('1', _('Включено'))])

    to_edit_button = SubmitField(_('Ред. соц.'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})

    to_save_button = SubmitField(_('Изм.'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    to_delete_button = SubmitField(_('Удал.'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    to_cancel_button = SubmitField(_('Отм.'), render_kw={"class": "button fl-button-field-user-edit", "type": "button"})
    
    to_save_submit = SubmitField(_('Сохр.'), render_kw={"class": "button fl-button-field-user-edit", "type": "submit"})

    def validate_adress_social(self, adress_social):       
        exists_socials =  UserInternetAccount.query.filter(UserInternetAccount.adress_accaunt == self.adress_social.data).count()
        this_social =  UserInternetAccount.query.filter(UserInternetAccount.adress_accaunt == self.adress_social.data).first()
                
        if self.adress_social.data is None or self.adress_social.data == "":
            raise ValidationError(_l('Нужно ввести адрес соцсети.'))

        if exists_socials > 0 and str(this_social.id) != str(self.adress_social.data):
            raise ValidationError(_l('Этот адрес уже зарегистрирован.'))