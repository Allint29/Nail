# -*- coding: utf-8 -*-
#импортируем модуль celery для создания очередей задач и передачи егьо в хранилище задач redis
from celery import Celery
from datetime import datetime, timedelta
import random
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
#функции которые должны периодически генерировать дни года и отрезки расписания у этих дней
from app.master_schedule.utils import create_calendar_for_two_month, create_query_time_one_day
from app.admin_my.utils import set_first_line_number, fill_select_connection_type

#важно не называть просто app чтобы исключить конфликт с app от celery
flask_app = create_app();
celery_app = Celery('tasks', broker="redis://localhost:6379/0");
dict_of_line = {}

def check_time_for_do(dict_of_line_key, time_lag = 60, random_ = True):
    '''
    функция проверяет входящий пункт словаря и выдает разрешение на произвлодство дальнейших действий
    '''
     #{'create_connection_types_list' : {'datetime_' :datetime.utcnow(), 'do_many_times' : True}}
    dict_of_line_key = str(dict_of_line_key)


    if not dict_of_line_key in dict_of_line:
        print(f'Ошибка в блоке распределения задач. Отсутствует ключ {dict_of_line_key} в словаре {dict_of_line}')
        return False

    if not 'datetime_' in dict_of_line[f'{dict_of_line_key}']:
        print(f'Ошибка в блоке распределения задач. Отсутствует ключ "datetime_" в словаре {dict_of_line}')
        return False

    if not 'do_many_times' in dict_of_line[f'{dict_of_line_key}']:
        print(f'Ошибка в блоке распределения задач. Отсутствует ключ "do_many_times" в словаре {dict_of_line}')
        return False

    time_value = None
    do_many_times = None

    if type(dict_of_line[f'{dict_of_line_key}']['datetime_']) != datetime:
        print(f'Ошибка в блоке распределения задач. Переданное значение не является типом datetime')
        return False

    time_value = dict_of_line[f'{dict_of_line_key}']['datetime_']

    try:        
        do_many_times = bool(dict_of_line[f'{dict_of_line_key}']['do_many_times'])
    except:
        do_many_times = True
        print(f'Ошибка в блоке распределения задач. Не удалось преобразовать булево значение')      

    #print(f'Для {dict_of_line_key} -- {do_many_times}')
    
    if time_value > datetime.utcnow():
        return False
       
    random_lag = 0
    if random_:
        random_lag = random.randint(0,30)

    dict_of_line[f'{dict_of_line_key}']['datetime_'] = datetime.utcnow() + timedelta(seconds = time_lag + random_lag)

    return True


@celery_app.task
def create_connection_types_list():
    '''
    Задача создания списка типов связ с пользователем 
    '''
    #проверка на очередь - если не моя очередь то пропускаю действие

    with flask_app.app_context():

        if check_time_for_do('create_connection_types_list', random_= False) == True:    
            #print(f'From create_connection_types_list next: _____{dict_of_line["create_connection_types_list"]}')
            fill_select_connection_type()

@celery_app.task
def my_work_content():
    '''
    func take content of news from site habr
    '''
    #проверка на очередь - если не моя очередь то пропускаю действие

    with flask_app.app_context():        
        if check_time_for_do('my_work_content') == True:    
            #print(f'From my_work_content next: ____ {dict_of_line["my_work_content"]}')
            anna_nails_ani.get_anna_nails_content()

@celery_app.task
def sevendays_news():
    '''
    func take title of news from site habr
    '''
    #проверка на очередь - если не моя очередь то пропускаю действие

    with flask_app.app_context():
        if check_time_for_do('sevendays_news') == True:    
            #print(f'From sevendays_news next: _____{dict_of_line["sevendays_news"]}')
            sevendays_news_manikur.get_sevendays_news_manikur()
        
@celery_app.task
def sevendays_news_content():
    '''
    func take content of news from site habr
    '''
    #проверка на очередь - если не моя очередь то пропускаю действие

    with flask_app.app_context():
        if check_time_for_do('sevendays_news_content') == True:    
            #print(f'From sevendays_news_content next: _____{dict_of_line["sevendays_news_content"]}')
            sevendays_news_manikur.get_news_content()

@celery_app.task
def delete_non_confirm_phones():
    '''
    Задача на удаление не подтвержденных номеров по истесении их времени жизни
    '''
    #проверка на очередь - если не моя очередь то пропускаю действие

    with flask_app.app_context():
        if check_time_for_do('delete_non_confirm_phones') == True:    
            #print(f'From delete_non_confirm_phones next: _____{dict_of_line["delete_non_confirm_phones"]}')
            delete_non_comfirmed_phone()

@celery_app.task
def delete_user_without_contacts():
    '''
    Задача на удаление не подтвержденных номеров по истесении их времени жизни
    '''
    with flask_app.app_context():
          #проверка на очередь - если не моя очередь то пропускаю действие
        if check_time_for_do('delete_user_without_contacts') == True:    
            #print(f'From delete_user_without_contacts next: _____{dict_of_line["delete_user_without_contacts"]}')
            delete_user_without_phone_and_confirm_email()

@celery_app.task
def delete_email_if_non_confirm():
    '''
    Задача на удаление не подтвержденных номеров по истесении их времени жизни
    '''
    with flask_app.app_context():
        if check_time_for_do('delete_email_if_non_confirm') == True:    
            #print(f'From delete_email_if_non_confirm next: _____{dict_of_line["delete_email_if_non_confirm"]}')
           
            delete_non_comfirmed_email()

@celery_app.task
def create_days_for_two_month():
    '''
    Задача проверки наличия дня в расписании и если его нет в ближайшие месяцы, то создает этот день
    '''
    #проверка на очередь - если не моя очередь то пропускаю действие

    with flask_app.app_context():
        if check_time_for_do('create_days_for_two_month') == True:    
            #print(f'From create_days_for_two_month next: _____{dict_of_line["create_days_for_two_month"]}')           
            create_calendar_for_two_month()

@celery_app.task
def create_grid_time_for_one_day():
    '''
    Задача создания сетки расписания дня для ранее созданных дней 
    '''
    #проверка на очередь - если не моя очередь то пропускаю действие
    with flask_app.app_context():
        if check_time_for_do('create_grid_time_for_one_day') == True:    
            #print(f'From create_grid_time_for_one_day next: _____{dict_of_line["create_grid_time_for_one_day"]}')             
            create_query_time_one_day()


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
    
    #словарь хранит время запуска задач если приложение запускается первый раз или после перезагрузки
    global dict_of_line
    step = 60
    dict_of_line = {
         'create_connection_types_list' : {'datetime_' :datetime.utcnow(), 'do_many_times' : False},#datetime.utcnow(),
         'my_work_content' :  {'datetime_' :datetime.utcnow() + timedelta(seconds = (step + random.randint(2,4))), 'do_many_times' : True},#datetime.utcnow() + timedelta(seconds = (step + random.randint(2,4))),
         'sevendays_news' : {'datetime_' :datetime.utcnow() + timedelta(seconds = (2 * step + random.randint(5,7))), 'do_many_times' : True},# datetime.utcnow() + timedelta(seconds = (2 * step + random.randint(5,7))),
         'sevendays_news_content' :  {'datetime_' :datetime.utcnow() + timedelta(seconds = (3 * step + random.randint(8,10))), 'do_many_times' : True},#datetime.utcnow() + timedelta(seconds = (3 * step + random.randint(8,10))),
         'delete_non_confirm_phones' :  {'datetime_' :datetime.utcnow() + timedelta(seconds = (4 * step + random.randint(11,13))), 'do_many_times' : True},#datetime.utcnow() + timedelta(seconds = (4 * step + random.randint(11,13))),
         'delete_user_without_contacts' :  {'datetime_' :datetime.utcnow() + timedelta(seconds = (5 * step + random.randint(14,16))), 'do_many_times' : True},#datetime.utcnow() + timedelta(seconds = (5 * step + random.randint(14,16))),
         'delete_email_if_non_confirm' :  {'datetime_' :datetime.utcnow() + timedelta(seconds = (6 * step + random.randint(17,19))), 'do_many_times' : True},#datetime.utcnow() + timedelta(seconds = (5 * step + random.randint(17,19))),
         'create_days_for_two_month' :  {'datetime_' :datetime.utcnow() + timedelta(seconds = (7 * step + random.randint(20,21))), 'do_many_times' : True},#datetime.utcnow() + timedelta(seconds = (5 * step + random.randint(20,21))), 
         'create_grid_time_for_one_day' :  {'datetime_' :datetime.utcnow() + timedelta(seconds = (8 * step + random.randint(22,23))), 'do_many_times' : True},#datetime.utcnow() + timedelta(seconds = (5 * step + random.randint(22,23))), 
         }
    #{'datetime' :datetime.utcnow(), 'do_many_times' : True}

    print('First emnter ________________', dict_of_line)

    #задачи инициализации списка типа связи: Порядок в очереди 0
    sender.add_periodic_task(crontab(minute='*/1'), create_connection_types_list.s())

    #задачи генерации контрента работ мастера: Порядок в очереди 1
    sender.add_periodic_task(crontab(minute='*/1'), my_work_content.s())

    #задачи генерации конента новостей с сайта 7days Порядок в очереди 2
    sender.add_periodic_task(crontab(minute='*/1'), sevendays_news.s())
    #Порядок в очереди 3
    sender.add_periodic_task(crontab(minute='*/1'), sevendays_news_content.s())    

    #задачи на чистку базы данных от лишних, неподтвержденных данных #Порядок в очереди 4
    sender.add_periodic_task(crontab(minute='*/1'), delete_non_confirm_phones.s())
    #Порядок в очереди 5
    sender.add_periodic_task(crontab(minute='*/1'), delete_user_without_contacts.s())
    #Порядок в очереди 6
    sender.add_periodic_task(crontab(minute='*/1'), delete_email_if_non_confirm.s())

    #задачи на генерацию расписания #Порядок в очереди 7
    sender.add_periodic_task(crontab(minute='*/1'), create_days_for_two_month.s())

    #задачи на генерацию расписания #Порядок в очереди 8 - замыкаю очередь
    sender.add_periodic_task(crontab(minute='*/1'), create_grid_time_for_one_day.s())


        