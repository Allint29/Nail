from datetime import datetime
from app import db
from app.user.models import SearchableMixin
from app.main_func.search import add_to_index, remove_from_index, query_index
from sqlalchemy.orm import relationship

class News(SearchableMixin, db.Model):
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, unique=True, nullable=False)
    main_picture_url = db.Column(db.String, nullable=True)
    published = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=True)

    def page_news():
        '''
        func to order post by users 
        '''        
        return News.query.filter(News.text.isnot("")).filter(News.text.isnot(None)).order_by(News.published.desc())

    #R11 для подсчета комминтариев к новости добавим метод подсчета
    #R11 далее в шаблоне news.index укажем эту функцию на отображение
    def comments_count(self):
        '''
        method count comments to news
        '''
        return CommentsToNews.query.filter(CommentsToNews.news_id == self.id).count();
    
    

    def __repr__(self):
        return f'<News {self.title} {self.url}>'

class CommentsToNews(db.Model):
    '''
    Класс коментария к новости
    '''
    id = db.Column(db.Integer, primary_key=True);
    text = db.Column(db.Text, nullable=True);
    created = db.Column(db.DateTime, nullable=False, default=datetime.now());
    news_id = db.Column(
        db.Integer,
        db.ForeignKey('news.id', ondelete='CASCADE'),
        index=True
    );

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        index=True
    );

    #R10следующие поля дают ссылку на связанные таблицы с этой моделью
    #R10 relationship -это вирт поле кот ссылается на указанную модель, 
    #а backref - это то как эта ссылка будет выглядеть со стороны указанной модели(у этой модели появится вирт поле comments)
    news = relationship('News', backref='comments');
    user = relationship('User', backref='comments');

    #R10репорт об объекте в удобном для человека виде
    def __repr__(self): 
        return f"<Comment id_comment={self.id} {self.created} {self.text}>"; 