from datetime import datetime
from app import db
from app.user.models import SearchableMixin
from app.main_func.search import add_to_index, remove_from_index, query_index

class News(SearchableMixin, db.Model):
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    url = db.Column(db.String, unique=True, nullable=False)
    published = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<News {self.title} {self.url}>'