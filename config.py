import os;
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['Alexeya299@gmail.com']
    MASTER_MAILS = ['Alexeya299@gmail.com', 'frelich25@yandex.ru']
    LANGUAGES = ['en', 'es', 'ru']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    #MY_SMSC_LOGIN = os.environ.get('MY_SMSC_LOGIN') 
    #MY_SMSC_PASSWORD = os.environ.get('My_SMSC_PASSWORD')
    SMSC_HTTPS = os.environ.get('SMSC_HTTPS')
    SMSC_LOGIN = os.environ.get('SMSC_LOGIN')
    SMSC_PASSWORD = os.environ.get('SMSC_PASSWORD')
    SMSC_CHARSET = os.environ.get('SMSC_CHARSET')
    SMSC_POST = os.environ.get('SMSC_POST')
    SMSC_DEBUG = os.environ.get('SMSC_DEBUG')
    SMTP_FROM = os.environ.get('SMTP_FROM')
    SMTP_SERVER = os.environ.get('SMTP_SERVER')

    #погог при котором смс не будут отправляться 
    SMSC_LOW_MONEY_LEVEL = 20.0

    #количество страниц, которое отображается в разделе новостей моды
    POSTS_PER_PAGE = 3

    MINUTES_FOR_CONFIRM_PHONE = 5
    SECONDS_TO_CONFIRM_EMAIL = 600

    #Сдвиг времени региона в часах
    LOCALE_TIME_OFFSET = 3

    #рабочие часы для отправки напоминаний писем и смс часы 0-23
    BEGIN_WORK_TIME = 12
    END_WORK_TIME = 18

    #рабочие часы мастера 0-23
    BEGIN_MASTER_WORK_TIME = 8
    END_MASTER_WORK_TIME = 21

    #время периодичности выполнения разных задачь
    
    PERIOD_CONNECTION_TYPES_LIST = 60    
    PERIOD_MY_WORK_CONTENT = 60 #3600*4    
    PERIOD_SEVENDAYS_NEWS = 60 #3600*5    
    PERIOD_SEVENDAYS_NEWS_CONTENT = 60 #3600*6    
    PERIOD_DELETE_NON_CONFIRM_PHONES = 60    
    PERIOD_DELETE_USER_WHITHOUT_CONTACTS = 120    
    PERIOD_DELETE_EMAIL_IF_NON_CONFIRM = 60    
    PERIOD_CREATE_DAYS_FOR_TWO_MONTH = 60 #3600
    PERIOD_CREATE_GRID_TIME_FOR_ONE_DAY = 60 #1800
