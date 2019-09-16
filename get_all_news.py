from app import create_app, db
from app.news.parser.sevendays_news_manikur import get_sevendays_news_manikur

app = create_app()

with app.app_context():
    get_sevendays_news_manikur()