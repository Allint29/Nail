# -*- coding: utf-8 -*-
from datetime import datetime
from time import time
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, loginF
from app.main_func import utils as main_utils
from wtforms.validators import DataRequired, Length, Email
from sqlalchemy.orm import relationship
#from app.user.models import User

class DateTable(db.Model):
    '''
    Модель даты к которой будет привязана временная сетка
    '''
    id = db.Column(db.Integer, primary_key=True)
    day_date = db.Column(db.DateTime, default=main_utils.make_date_from_date_time(main_utils.min_date_for_calculation()))
    day_name = db.Column(db.String(15), default=main_utils.make_name_of_day_from_date(main_utils.min_date_for_calculation()))
    
    time = db.relationship('ScheduleOfDay', backref='date_table', lazy='dynamic')

    def __repr__(self):
        return f'<Date_of_schedule {self.day_date} {self.day_name}>'

    def __init__(self, *args, **kwargs):
        super(DateTable, self).__init__(*args, **kwargs)

class ScheduleOfDay(db.Model):
    '''
    Модель куска времени, которое может быть занято для работы, связано с датами связью много к одному
    begin_time_of_day = 
    end_time_of_day =
    work_type =
    cost =
    name_of_client =
    adress_of_client =
    note =
    client_come_in =
    is_empty =
    user_id =
    date_table_id =
    '''
    id = db.Column(db.Integer, primary_key=True)
    #начало работы
    begin_time_of_day = db.Column(db.DateTime, default=main_utils.make_date_from_date_time(main_utils.min_date_for_calculation()))
    end_time_of_day = db.Column(db.DateTime, default=main_utils.make_date_from_date_time(main_utils.min_date_for_calculation()))
    #тип работы
    work_type = db.Column(db.String, default='маникюр')
    #цена работы
    cost = db.Column(db.Integer, default=0)

    #информация о клиенте
    #имя клиента не связано с таблицей клиента
    name_of_client = db.Column(db.String, default='неизвестно')
    #почта не связана с таблицей клиента, может быть пустым, вставляется из данных клиента если есть
    mail_of_client = db.Column(db.String, default='неизвестно')
    #телефон не связан с таблицей клиента, вставляется значение из телефонов клиента если есть
    phone_of_client = db.Column(db.String, default='неизвестно')
    #адрес не связан с таблицей клиента - в соцсети
    adress_of_client = db.Column(db.String, default='неизвестно')
    # описание не связано с таблицей клиента
    note = db.Column(db.String, default='примечание')

    #тип связи
    connection_type=db.Column(db.Integer, default=0)
    #тип связи строка
    connection_type_str=db.Column(db.String, default='телефон')


    #поле говорит о том пришел ли клиент
    client_come_in = db.Column(db.Integer, default=0)

    #свойство  указывающе занято ли время    
    is_empty = db.Column(db.Integer, default=0)
    
    #связь с таблицей зарегистрированных пользователей (жестко не привязана)
    user_id = db.Column(db.Integer, default=-1)

    #поле которое говорит системе отослано ли сообщение клиенту, что он записан - 
    #должно меняться при записи клиента на определенное время. 0 - не отослано 1 - отослано
    info_message_for_client = db.Column(db.Integer, default=0)

    #поле которое говорит системе отослано ли сообщение клиенту, которое напоминает клиенту, что он записан.
    # 0 - не отослано 1 - отослано
    remind_message_for_client = db.Column(db.Integer, default=0)
    
    #связь с таблицей даты
    date_table_id = db.Column(db.Integer, db.ForeignKey('date_table.id'))

    def __init__(self, *args, **kwargs):
        super(ScheduleOfDay, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Time_of_schedule {self.begin_time_of_day} {self.end_time_of_day}>'


class PreliminaryRecord(db.Model):
    '''
    Таблица предзаписи клиента. Клиент оставляет заявку на запись через главную страницу сайта.    
    '''
    id = db.Column(db.Integer, primary_key=True)
    #имя клиента не связано с таблицей клиента
    name_of_client = db.Column(db.String, default='')
    phone_of_client = db.Column(db.Integer, default = -1)
    message_of_client = db.Column(db.String, default='')
    #метка говорит о том что сообщение обработано
    message_worked = db.Column(db.Integer, default = 0)
    time_to_record = db.Column(db.DateTime, default=main_utils.min_date_for_calculation())

    def __repr__(self):
        return f'<PreliminaryRecord phone={self.phone_of_client}, name={self.name_of_client}, message={self.message_of_client}, time={self.time_to_record}>'