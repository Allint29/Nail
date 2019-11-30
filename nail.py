from app import create_app, db #, cli
from app.main_func import cli
from app.user.models import User, Post, UserPhones, UserInternetAccount
from app.news.models import News, CommentsToNews, MasterNews
from app.my_work.models import CommentsToMyWorks, MyWork
from app.master_schedule.models import DateTable, ScheduleOfDay, PreliminaryRecord
from app.admin_my.models import ActionLine, PriceList, WorkType

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = create_app()
cli.register(app)
 
@app.shell_context_processor
def make_shell_context():
    return {'db': db, \
        'User': User, 'Post': Post, \
        'News' : News, 'CommentsToNews': CommentsToNews, 'MasterNews': MasterNews, \
        'UserPhones' : UserPhones, 'UserInternetAccount': UserInternetAccount, \
        'MyWork' : MyWork, 'CommentsToMyWorks' : CommentsToMyWorks, \
        'DateTable' : DateTable, 'ScheduleOfDay': ScheduleOfDay, 'PreliminaryRecord' : PreliminaryRecord, \
        'ActionLine': ActionLine, 'PriceList': PriceList, 'WorkType': WorkType
      }