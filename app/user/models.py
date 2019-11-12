# -*- coding: utf-8 -*-
from datetime import datetime
from hashlib import md5 #гравотар
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, loginF
from app.main_func import utils as main_utils
from wtforms import validators #validators import DataRequired, Length
from app.master_schedule.models import ScheduleOfDay
#from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from sqlalchemy.orm import relationship

from app.main_func.search import add_to_index, remove_from_index, query_index

import random



#создаю таблицу связей многие ко многим, которая фактически не является самостоятельной таблицей
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class ConnectionType(db.Model):
    '''
    Таблица хранит данные о возможных типах связи с пользователем
    '''
    id = db.Column(db.Integer, primary_key=True)
    name_of_type = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref='connection_type', lazy='dynamic')

    def __repr__(self):
        return '<Connection_type={}, id ={}, checked={}>'.format(self.id, self.name_of_type)



class UserPhones(db.Model):
    '''
    Класс телефонов пользователя - 
    1) связывается с пользователем отношением много к одному, 
    2) номера не могут повторяться, 
    4) номер подтверждается по смс в которое отсылаем смс с номером, хеш этого кода записывается в БД на определенное время если не подтверждается номер то удаляем его из БД
    3) если номер подтвержден, то в момент подтверждения телефон становиться подтвержденным
    '''

    id = db.Column(db.Integer, primary_key=True)

    #номер телефона пользователя
    number = db.Column(db.Integer, nullable=False)
    #хеш для подтверждения телефона пользователя удаляется при новом подтверждении телефона
    #логика - создается код из цифр и отсылается пользователю и записывается хеш этих цифр в БД, после проверяетя как пароль
    phone_hash_code = db.Column(db.String(128))  
    #телефон подтвержден
    phone_checked = db.Column(db.Integer, nullable=False, default=0)
    expire_date_hash = db.Column(db.DateTime, default=main_utils.min_date_for_calculation())
    black_list = db.Column(db.Integer, nullable=False, default=0)
    #максимальное количество попыток подтверждения номера телефона
    trying_to_enter_confirm_code = db.Column(db.Integer, default=3)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  #  date_time_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def set_phone_hash_code(self, code):
        self.phone_hash_code = generate_password_hash(code)
       
    def check_phone_hash_code(self, code):
        '''
        Функция возвращает правду если хеш сходится
        '''
        return check_password_hash(self.phone_hash_code, code)
 

    def __repr__(self):
        return '<Phone={}, id ={}, checked={}>'.format(self.number, self.id, self.phone_checked)


class UserInternetAccount(db.Model):
    '''
    Класс описывает электронный аккаунт и связь с пользователем
    '''
    id = db.Column(db.Integer, primary_key=True)
    adress_accaunt = db.Column(db.Integer, primary_key=True, index=True, unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<UserInternetAccount={}>'.format(self.adress_accaunt)


class User(UserMixin, db.Model):
    '''
    user class is a table for attribute of users info
    id -
    username -
    email - 
    password_hash - 
    posts - 
    about_me - 
    last_seen - 
    get_reset_password_token - method
    verify_reset_password_token - method
    followed_posts - method
    follow
    unfollow
    is_following
    avatar - method
    check_password - method
    '''
    id = db.Column(db.Integer, primary_key=True)
    
    username = db.Column(db.String(64), index=True, unique=True)
    about_me = db.Column(db.String(140))

    email = db.Column(db.String(120))
    email_confirmed = db.Column(db.Integer)
    expire_date_request_confirm_password = db.Column(db.DateTime, default=main_utils.min_date_for_calculation())

    
    expire_date_request_bufer_mail = db.Column(db.DateTime, default=main_utils.min_date_for_calculation())
    bufer_email = db.Column(db.String(120))

    
    #дата регистрации пользователя
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    #максимальное количество попыток зарегистрировать новый телефоны
    trying_to_enter_new_phone = db.Column(db.Integer, default=15)
    password_hash = db.Column(db.String(128))
    
    #юзеры и админы
    role = db.Column(db.String(10), index=True);
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    #типы связи с клиентом
    connection_type_id = db.Column(db.Integer, db.ForeignKey('connection_type.id'))
    #телефоны клиента
    phones = db.relationship('UserPhones', backref='user', lazy='dynamic')
    #электронные аккаунты клиента
    internet_accaunts = db.relationship('UserInternetAccount', backref='user', lazy='dynamic')

    #обратная ссылка из таблицы расписания для связи зарегистрированного пользователя и времени записи на прием
    date_of_schedules = db.relationship('ScheduleOfDay', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def has_phone(self):
        '''
        функция возвращает правду если  у пользователя есть хотябы один подтвержденный телефон
        '''
        return UserPhones.query.filter(UserPhones.user_id == self.id).filter(UserPhones.phone_checked == 1).all().count() > 0

    def set_confirm_email_true(self):
        '''
        func change in db status email from not confirm to confirm by create new pass
        '''
        if self.email_confirmed != 1:
            self.email_confirmed = 1

    def set_password(self, password):
        '''
        func to generate hash pass for save in db
        '''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''
        func chech hash pass from bd with secret key and resume tru or false
        '''
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        '''
        func return aatar from srvice Gravatar
        '''
        digest = None
        if not self.email or self.email == "":
            digest = "example@mail.com"
        else:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        '''
        func for subscribe to see oa activety user
        '''
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        '''
        func for unsubscribe to see oa activety user
        '''
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        '''
        func for check that user not folowed twice on one user
        '''
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    def followed_posts(self):
        '''
        func to order post by users 
        '''
        followed = Post.query.join(
        followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)

        own = Post.query.filter_by(user_id=self.id)
     
        return followed.union(own).order_by(Post.timestamp.desc())

    
    def get_new_registration_token(self, expires_in=600):
        '''
        func to create token link for request registration new user. time of life 10min for default
        '''
        return jwt.encode(
            {'register_user': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


    @staticmethod
    def verify_new_registration_token(token):
        '''
        func to decode token from link to registartion new user
        '''
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['register_user']
        except:
            return
        return User.query.get(id)

    def get_reset_password_token(self, expires_in=600):
        '''
        func to create token link for request reset password. time of life 10min for default
        '''
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @property
    def is_admin(self):
        '''
        property of user - return true ifuser is Administrator group
        '''
        return self.role == 'admin'


    @staticmethod
    def verify_reset_password_token(token):
        '''
        func to decode token from link to reset pass
        '''
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
          

@loginF.user_loader
def load_user(id):
    return User.query.get(int(id))


class SearchableMixin(object):
    '''
    Для поддержки поиска - класс SearchableMixin, который при подключении к модели 
    даст ему возможность автоматически управлять полнотекстовым индексом, связанным 
    с моделью SQLAlchemy. Класс mixin будет выступать в качестве "связующего" слоя 
    между мирами SQLAlchemy и Elasticsearch 
    '''
    @classmethod
    #classmethod- это тоже самое что static в c#
    def search(cls, expression, page, per_page):
        '''
        Функция search() возвращает запрос, 
        который заменяет список идентификаторов, 
        а также передает общее количество результатов 
        поиска в качестве второго возвращаемого значения.
        '''
        #здесь cls - тоже что и self чтобы было ясно, что этот метод получает в
        # качестве первого аргумента класс, а не экземпляр.
        #Метод класса search() обертывает функцию query_index() из app/search.py 
        #заменяя список идентификаторов объектов на фактические объекты.
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        #переопределяю переменную на определение нашедшихся данных ксли возвращается словарь
        # то беру поле словаря, если число само число
        #почему-то в разных вариантах ведет себя по разному
        totalVal = 50
      
        if type(total) is not int:
            totalVal = total['value']
        elif type(total) is int:
            totalVal = total
        
        if totalVal == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), totalVal

    @classmethod
    def before_commit(cls, session):
        '''
        Обработчик before полезен, потому что сеанс еще не был зафиксирован, 
        поэтому я могу глянув на него выяснить, какие объекты будут добавлены, 
        изменены и удалены, доступны как session.new session.dirty 
        и session.deleted соответственно.
        Я использую session._changes словарь для записи этих объектов в месте,
        которое переживет все фиксации сеанса, потому что, как только сеанс пофиксится 
        я буду использовать их для обновления индекса Elasticsearch.
        '''
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        '''
        Вызов обработчика after_commit() означает, что сеанс успешно завершен, 
        поэтому сейчас самое время внести изменения на стороне Elasticsearch.
        Объект сеанса имеет переменную _changes, которую я добавил в before_commit(), 
        поэтому теперь я могу перебирать добавленные, измененные и удаленные объекты и 
        выполнять соответствующие вызовы для функций индексирования в app/search.py.
        '''
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        '''
        Метод класса reindex() — это простой вспомогательный метод, 
        который можно использовать для обновления индекса со всеми 
        данными из реляционной стороны. Вы видели, как я делал что-то 
        подобное из сеанса оболочки Python выше, чтобы выполнить начальную 
        загрузку всех сообщений в тестовый индекс. Используя этот метод, 
        я могу опубликовать Post.reindex(), чтобы добавить все записи в базу 
        данных в индекс поиска (search index).        '''

        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

#Обратите внимание, что вызовы db.event.listen() не входят в класс, а следуют после него. 
#Они устанавливают обработчики событий, которые вызывают before и after для каждой фиксации. 
#Теперь модель Post автоматически поддерживает индекс полнотекстового поиска для сообщений.
#
#Чтобы включить класс SearchableMixin в модель Post, я должен добавить его в качестве подкласса, 
#и мне также необходимо подключить befor и after события фиксации:

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

class Post(SearchableMixin, db.Model):
    '''
    class of users posts
    id - 
    body - 
    timestamp -
    user_id - 
    '''
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)