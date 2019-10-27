# -*- coding: utf-8 -*-
from datetime import datetime
from time import time
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, loginF
from app.main_func import utils as main_utils
from wtforms.validators import DataRequired, Length
from sqlalchemy.orm import relationship
#from app.user.models import User

class DateTable(db.Model):
    '''
    Модель даты к которой будет привязана временная сетка
    '''
    id = db.Column(db.Integer, primary_key=True)
    day_date = db.Column(db.DateTime, default=main_utils.make_date_from_date_time(main_utils.min_date_for_calculation()))
    day_name = db.Column(db.String, default=main_utils.make_name_of_day_from_date(main_utils.min_date_for_calculation()))
    
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
    name_of_client = db.Column(db.String, default='неизвестно')
    adress_of_client = db.Column(db.String, default='неизвестно')
    note = db.Column(db.String, default='примечание')
    
    #поле говорит о том пришел ли клиент
    client_come_in = db.Column(db.Integer, default=0)

    #свойство  указывающе занято ли время
    is_empty = db.Column(db.Integer, default=1)
    #связь с таблицей зарегистрированных пользователей
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #связь с таблицей даты
    date_table_id = db.Column(db.Integer, db.ForeignKey('date_table.id'))

    def __init__(self, *args, **kwargs):
        super(ScheduleOfDay, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f'<Time_of_schedule {self.begin_time_of_day} {self.end_time_of_day}>'