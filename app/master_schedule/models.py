# -*- coding: utf-8 -*-
from datetime import datetime
from time import time
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, loginF
from app.main_func import utils as main_utils
from wtforms.validators import DataRequired, Length

class DateTable(db.Model):
    '''
    Модель даты к которой будет привязана временная сетка
    '''
    id = db.Column(db.Integer, primary_key=True)
    day_date = db.Column(db.DateTime, default=main_utils.min_date_for_calculation())
