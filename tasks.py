# -*- coding: utf-8 -*-
#импортируем модуль celery для создания очередей задач и передачи егьо в хранилище задач redis
from celery import Celery

#импортируем модуль который отвечает за расписание - это очень гибкий модуль позволяет настроить 
#расписание по любым параметрам
from celery.schedules import crontab

#в  данном случае у нас Alchemy завязан с flask поэтому обращаться нужно через flask
#иначе если используется другой модуль есть автономный модуль sqlAlchemy
#импортируем из папки программы главную функ запуска из файла  __init__
from app import create_app
#импортируем функцию чтения новостей с сайта и создания БД из модуля поиска новости с сайта питон
from app.news.parser import sevendays_news_manikur
from app.my_work.parser import anna_nails_ani
from app.user.utils import delete_non_comfirmed_phone, delete_user_without_phone_and_confirm_email, \
    delete_non_comfirmed_email

#важно не называть просто app чтобы исключить конфликт с app от celery
flask_app = create_app();
celery_app = Celery('tasks', broker="redis://localhost:6379/0");

@celery_app.task
def sevendays_news():
    '''
    func take title of news from site habr
    '''
    with flask_app.app_context():
        sevendays_news_manikur.get_sevendays_news_manikur()
        
@celery_app.task
def sevendays_news_content():
    '''
    func take content of news from site habr
    '''
    with flask_app.app_context():
        sevendays_news_manikur.get_news_content()

@celery_app.task
def my_work_content():
    '''
    func take content of news from site habr
    '''
    with flask_app.app_context():
        anna_nails_ani.get_anna_nails_content()

@celery_app.task
def delete_non_confirm_phones():
    '''
    Задача на удаление не подтвержденных номеров по истесении их времени жизни
    '''
    with flask_app.app_context():
        delete_non_comfirmed_phone()

@celery_app.task
def delete_user_without_contacts():
    '''
    Задача на удаление не подтвержденных номеров по истесении их времени жизни
    '''
    with flask_app.app_context():
        delete_user_without_phone_and_confirm_email()

@celery_app.task
def delete_email_if_non_confirm():
    '''
    Задача на удаление не подтвержденных номеров по истесении их времени жизни
    '''
    with flask_app.app_context():
        delete_non_comfirmed_email()

#функция запускает что либо, что идет за ним после того как запуститься сам celery и сделает коннект
#к очереди и будет готова к решению задач
#sender - это объект который позволяет управлять celery изнутри нашей функции
#**kwargs - будут передаваться другие аргументы в данноом случае это не так важно
#если запустить эту функцию из celery то ничего не произойдет для того чтобы она работала нужно 
#подписаться на событие при помощи celery-beat:
#1) напрямую из терминала linux запустить сначала celery а после бит: $ celery -A tasks beat
#2)либо запустить бит и воркер параллельно, но на серьезном продакшене так делать не нужно: celery -A tasks worker -B --loglevel=info 
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    '''
    func set start to needed time to load title of news and content of news to DB
    '''
    #запускаем проверку на появление новых новостей с периодом 1 минута
    #здесь habr_snippets.s() s() - это сделать сигнатуру функции (мы вызываем не саму функциюб а си) , говорим функции что ее нужно запустить изнутри
    
    sender.add_periodic_task(crontab(minute='*/1'), sevendays_news.s())
    sender.add_periodic_task(crontab(minute='*/1'), sevendays_news_content.s())    
    sender.add_periodic_task(crontab(minute='*/1'), my_work_content.s())
    sender.add_periodic_task(crontab(minute='*/1'), delete_non_confirm_phones.s())
    sender.add_periodic_task(crontab(minute='*/1'), delete_user_without_contacts.s())
    sender.add_periodic_task(crontab(minute='*/1'), delete_email_if_non_confirm.s())


        