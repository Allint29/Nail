from app import create_app, db
from app.news.parser import sevendays_news_manikur
from app.my_work.parser import anna_nails_ani
app = create_app()

with app.app_context():
    #sevendays_news_manikur.get_sevendays_news_manikur()
    sevendays_news_manikur.get_news_content()
    #anna_nails_ani.get_anna_nails_ani_snippets()
    #anna_nails_ani.get_anna_nails_content()