from datetime import datetime
from hashlib import md5 #гравотар
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, loginF

from wtforms.validators import DataRequired, Length
from wtforms import StringField, TextAreaField, SubmitField

from app.search import add_to_index, remove_from_index, query_index


#создаю таблицу связей многие ко многим, которая фактически не является самостоятельной таблицей
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


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
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

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



    def get_reset_password_token(self, expires_in=600):
        '''
        func to create token link for request reset password. time of life 10min for default
        '''
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

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
        данных в индекс поиска (search index).
        '''

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