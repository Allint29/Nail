from datetime import datetime
from sqlalchemy.orm import relationship
from app import db

#item = {
#'id' : f'{m.id}', 
#'date' : photo_date, 
#'caption' : f'{m.caption}', 
#'code' : f'{m.code}',
#'url' : f'{m.display_url}', 
#'owner' : f'{m.owner}', 
#'likes' : f'{m.likes_count}', 
#'comments' : comments_for_photo}
                  

class MyWork(db.Model):   
    id = db.Column(db.Integer, primary_key=True)
    id_site = db.Column(db.String(255), nullable=True)
    published = db.Column(db.DateTime, nullable=False, default=datetime.now())
    title = db.Column(db.Text, nullable=True)
    code = db.Column(db.String(250), nullable=True)
    url = db.Column(db.String(255), unique=True, nullable=True)
    owner = db.Column(db.String(255), nullable=True)
    likes = db.Column(db.Integer)
    show = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    source = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=True)
    #comments_id = ""

    #R11 далее в шаблоне news.index укажем эту функцию на отображение
    def comments_count(self):
        '''
        method count comments to my works
        '''
        return CommentsToMyWorks.query.filter(CommentsToMyWorks.my_work_id == self.id).filter(CommentsToMyWorks.show == 1).count();

    def __repr__(self):
        return f'<Wy work of nail {self.title} {self.url}>'

#comments = {
#'id' : f'{c.id}', 
#'media': f'{c.media}'
#'owner' : f'{c.owner}', 
#'text' : f'{c.text}', 
#'date' : comment_date}

class CommentsToMyWorks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_site = db.Column(db.String(255), nullable=True)
    #media- шифр контента к которому относится данный коммент в инстаграмме
    media = db.Column(db.String(255), nullable=True)
    #owner - создатель комментария
    owner = db.Column(db.String(255), nullable=True)
    published = db.Column(db.DateTime, nullable=False, default=datetime.now())
    text = db.Column(db.Text, nullable=True)
    #show - инструмент для регулирования комментария к показу
    show = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    source = db.Column(db.String(255), nullable=True)

    my_work_id = db.Column(
        db.Integer,
        db.ForeignKey('my_work.id', ondelete='CASCADE'),
        index=True
   )

    def hide_comment(self):
        '''
        func to hide comment
        '''
        if self.show == 1:
            self.show = 0

    def unhide_comment():
        '''
        func to unhide comment
        '''
        if self.show == 0:
            self.show = 1

    def is_showing(self):
        '''
        func return consist of comment, to show or not to show
        '''
        return self.show == 1

    my_work = relationship('MyWork', backref='comments');
                                  