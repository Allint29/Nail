# -*- coding: utf-8 -*-
from app import db
from sqlalchemy.orm import relationship

class ActionLine(db.Model):
    '''
    Сущность хранит одно единственное значение - число, по которому запускаются 
    действия по расписанию. В действиях по расписанию перед выполнением проверяется число хранящиеся в таблице и если
    данное число меньше, чем нужно то процесс не запускается
    '''
    id = db.Column(db.Integer, primary_key=True)
    #поле которое используется для маркера задачи, которая сейчас должна выполняться
    line_number = db.Column(db.Integer)
    #поле отвесает за время когда задача должна выполняться
    time_for_start = db.Column(db.DateTime)
    time_lag = db.Column(db.Integer)


class WorkType(db.Model):
    '''
    Тип работы мастера: Маникюр, Педикюр, Ремонт, Другое.
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    # приоритет вывода в прайс листе
    priority_to_show = db.Column(db.Integer, default = 100)

    price_lists = db.relationship('PriceList', backref = 'work_type', cascade="all, delete-orphan",  lazy='dynamic')

    def __repr__(self):
        return f'<WorkType {self.name}>'


class PriceList(db.Model):
    '''
    Сущность хранит информацию о ценах и скидках на работы мастера
    '''
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.Text)
    price = db.Column(db.Integer, default=0)
    discount = db.Column(db.Integer, default=0)

    work_type_id = db.Column(db.Integer, db.ForeignKey('work_type.id'))

    def __repr__(self):
        return f'<PriceListItem {self.title} {self.text} {self.price}>'


