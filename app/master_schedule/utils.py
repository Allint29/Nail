#R11для проверки подленности ссылки на перенаправления
from urllib.parse import urlparse, urljoin;
from flask import request, url_for, flash, current_app
from datetime import datetime, timedelta, date
from app.master_schedule.models import DateTable, ScheduleOfDay
from app.user.models import User, UserPhones, UserInternetAccount
from app import db
from app.main_func import utils as main_utils
from app.master_schedule.forms import TimeForm
from flask_babel import Babel, _, lazy_gettext as _l
from app.master_schedule.myemail import *
from app.main_func.smsc_api import SMSC


def delete_all_days_in_schedule():
    '''
    Функция быстрого удаления записей в таблице расписания
    '''
    data_to_delete = DateTable.query.all()
    try:
        for data in data_to_delete:
            db.session.delete(data)

        db.session.commit()
    except Exception as e:
        print(f'Ошибка при удалении всех дней. {e}')

def create_calendar_for_two_month():
    '''
    функция проверяет текущую дату и зазор для формирования расписания на 2 месяца вперед.
    Если текущая дата + 60 дней больше чем последняя запись в таблице то создается расписание 
    на недостающие дни от последней даты в расписании или от текущей даты если записи в таблице
    отсутствуют.
    '''    
    it_date_main = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0)
    end_of_bufer_date = it_date_main + timedelta(days=60)

    list_of_date = sorted(DateTable.query.filter(DateTable.day_date >= it_date_main).all(), key=lambda x: getattr(x, 'day_date'), reverse=False)
    #f=DateTable.query.order_by(DateTable.day_date.desc()).all()
    days_to_fill = 60
    it_date=it_date_main
    last_date = None
    date_to_add = []
    try:
        if len(list_of_date) > 0:
            i=0        
            while i < len(list_of_date):
               # print(list_of_date[i].day_date > it_date,' ', list_of_date[i].day_date,' > ', it_date)
                if list_of_date[i].day_date > it_date:
                    #если дата в списке болше текущей - значит отсутствует и ее надо добавить в список на добавление
                    delta = list_of_date[i].day_date - it_date
                    for d in range(delta.days):
                      #  print("Add it_date")
                        date_to_add.append(it_date)
                        it_date=it_date + timedelta(days=1)

                it_date=it_date + timedelta(days=1)

                if i == len(list_of_date)-1:
                   # print("last date!")
                    lastdate=list_of_date[i].day_date
                
                i=i+1

            if lastdate < end_of_bufer_date:
                #если еще остались не заполненные дни по окончанию списка то их тоже нужно занести в список добавляемых
                delta = end_of_bufer_date - lastdate
                for d in range(delta.days):
                    lastdate=lastdate+timedelta(days=1)
                    date_to_add.append(lastdate)

            for d in date_to_add:
                date_of_schedule = DateTable(day_date = d, day_name = main_utils.make_name_of_day_from_date(d, 'ru')['day'])
                db.session.add(date_of_schedule)
  
        else:
            for day in range(days_to_fill):
                date_of_schedule = DateTable(day_date = it_date, day_name = main_utils.make_name_of_day_from_date(it_date, 'ru')['day'])
                it_date = it_date + timedelta(days=1)
                db.session.add(date_of_schedule)

        db.session.commit()
    except Exception as e:
        print('Ошибка в блоке create_calendar_for_two_month при сохранении. {e}')

def delete_all_times_in_schedule():
    '''
    Функция быстрого удаления записей в таблице расписания
    '''
    data_to_delete = ScheduleOfDay.query.all()
    try:
        for data in data_to_delete:
            db.session.delete(data)
        db.session.commit()
    except Exception as e:
        print(f'Ошибка при быстром удалении сеток расписания из базы.{e}')

def create_query_time_one_day():
    '''
    Функция проходит по всем записанным дням 
    и проверяет нет-ли пропущенных временных 
    отрезков и если есть заполняет их
    '''
    #вычисляем текущую дату с 0:00
    it_date_main = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0)
    #создаем список дней для проверки начиная с текущего дня
   
    list_of_date = DateTable.query.filter(DateTable.day_date >= it_date_main).all()
        
    times_to_add = []
    #Начинаем проверять каждый день
    for day in list_of_date:
        #выбираем таблицу данного дня и выбираем все часы работы
        list_of_time = sorted(ScheduleOfDay.query.filter(ScheduleOfDay.date_table_id == day.id).all(), key=lambda x: getattr(x, 'begin_time_of_day'), reverse=False)
        #print(len(list_of_time))
        if len(list_of_time) > 0: 
            if len(list_of_time) < 24:
                #здесь заполняем отсутствующие таймы
                i=0
                time_zero=datetime(day.day_date.year, day.day_date.month, day.day_date.day, 0, 0)                
                it_time = time_zero
                last_time = None
                while i < len(list_of_time):                
                    if list_of_time[i].begin_time_of_day > it_time:
                        #если текущая запись больше чем проверочное время, нудно выяснить сколько пропущено и добавить эти даты
                        delta = int(((list_of_time[i].begin_time_of_day - it_time).seconds)/3600)
                        #print('не хватает всего в сутках часов:', delta)
                        for d in range(delta):
                          #  print("Add it_time")
                            times_to_add.append({'time': it_time, 'date_id' : day.id})
                            it_time=it_time + timedelta(hours=1)                    

                    if i < len(list_of_time)-1:
                        it_time=it_time + timedelta(hours=1)
                    else:
                        last_time = it_time 
                    #    print('Last time is: ', last_time)
                    i=i+1 

                if last_time < time_zero + timedelta(hours=23):
                    #если последняя запись в списке меньше чем 23 часа то добавляем от этой даты до конца суток
                    delta = int(((time_zero + timedelta(hours=23) - last_time).seconds)/3600)
                #    print('до конца дня еще не хватает', delta)
                    for d in range(delta):
                        last_time = last_time + timedelta(hours=1)
                        times_to_add.append({'time': last_time, 'date_id' : day.id})
                        

            elif len(list_of_time) > 24:
                print("My Exeption: В расписании дня больше 24 часов!!!")
            
        else:
            #если на данный день нет сетки времени просто добавляем ее
            i=0
            d=datetime(day.day_date.year, day.day_date.month, day.day_date.day, 0, 0)
            while i < 24:                
                times_to_add.append({'time': d + timedelta(hours=i), 'date_id' : day.id})
                i=i+1


    #добавляемм все таймы в базу
    try:
        for t in times_to_add:
            time_to_add = ScheduleOfDay(
                        begin_time_of_day = t['time'], 
                        end_time_of_day = t['time'] + timedelta(minutes=59),
                        date_table_id = t['date_id']
                        )
            if t['time'].hour < 8 or t['time'].hour > 21:
                time_to_add.is_empty=0
            else:
                time_to_add.is_empty=1

            db.session.add(time_to_add)

        db.session.commit()  
    except Exception as e:
        print(f'Ошибка в блоке создания сетки create_query_time_one_day времени на один день. {e}')

def take_empty_time_in_shedule(begin_date=None, end_date=None, to_back=None, id_client=None):
    '''
    Функция берет список с временем расписания и возвращает словарь с 
    маркировкой времени расписания - занято, свободно, свободно с ограничениями
    '''    
    print('id_client', id_client)
    try:
        id_client=int(id_client)
        id_client = -1 if id_client < 0 else id_client
    except Exception as e:
        print(f'Ошибка преобразования ID клиента: {e}')
        id_client = -1

    if begin_date == None and end_date == None:
        begin_date = datetime.now()
        end_date = datetime.now()
    elif begin_date == None and end_date != None:
        begin_date = end_date
    elif begin_date != None and end_date == None:
        end_date = begin_date

    try:
        if type(begin_date) == date:
            begin_date=datetime(begin_date.year, begin_date.month, begin_date.day)
    except:
        begin_date=datetime.now()

    try:
        if type(end_date) == date:
            end_date=datetime(end_date.year, end_date.month, end_date.day)
    except:
        print('error in end_date')
        end_date = datetime.now()

    begin_date= main_utils.make_date_from_date_time(begin_date)['date']
    end_date=main_utils.make_date_from_date_time(end_date)['date']

    now_date=main_utils.make_date_from_date_time(datetime.now())['date']
    
    if to_back == None:
        if begin_date > end_date:
            begin_date = end_date
        elif begin_date < now_date or end_date < now_date:
            begin_date = now_date
            end_date = now_date + timedelta(days=7)
    

    list_of_date=DateTable.query.filter(DateTable.day_date >= begin_date).filter(DateTable.day_date <= end_date).order_by(DateTable.day_date).all()
    list_date = []
    i=0
    while i < len(list_of_date):
        list_of_time = ScheduleOfDay.query.filter(ScheduleOfDay.date_table_id == list_of_date[i].id).all()
        
        list_of_work_time = []

        for item in list_of_time:
            t=item.begin_time_of_day.hour
            if t >= current_app.config['BEGIN_MASTER_WORK_TIME'] and t <= current_app.config['END_MASTER_WORK_TIME']:
                list_of_work_time.append(item)
        list_to_show =[]
       
        j=0
        while j<len(list_of_work_time):
            t=list_of_work_time[j].begin_time_of_day.hour
            #добавляю форму для отправки запроса на редактирование            
            edit_form = TimeForm()
            edit_form.id_time.data=list_of_work_time[j].id
            edit_form.id_client.data= id_client
            edit_form.id_date.data= list_of_date[i].id
            #достигли последнего элемента и он свободен, то время свободное
            if t==current_app.config['END_MASTER_WORK_TIME']:
                if list_of_work_time[j].is_empty == True:
                    list_to_show.append({'time': list_of_work_time[j], 'empty': 'free', 'form_edit': edit_form})
                else:
                    list_to_show.append({'time': list_of_work_time[j], 'empty': 'non_free', 'form_edit': edit_form})
       
            else:
                if list_of_work_time[j].is_empty == True:
                    if list_of_work_time[j+1].is_empty == False:
                        list_to_show.append({'time': list_of_work_time[j], 'empty': 'some_free', 'form_edit': edit_form})
                    else:
                        list_to_show.append({'time': list_of_work_time[j], 'empty': 'free', 'form_edit': edit_form})
       
                else:
                    list_to_show.append({'time': list_of_work_time[j], 'empty': 'non_free', 'form_edit': edit_form})
            j=j+1

        list_date.append({'date': list_of_date[i], 'list_work_time': list_to_show})        
        i=i+1 

    return list_date

def take_data_of_fate_for_master(begin_date = None ):
    '''
    ищет один день и возвращает расписание на данный день и формы для каждого тайминга для показа мастеру
    '''
    pass

def reserve_time_shedue(id_shedule_time):
    '''
    Функция переводит тригер занятости времени во включенное состояние и сохраняет это в БД
    '''
    #сначала очищаем форму от записи   
    clear_time_shedue(id_shedule_time)
    time_to_reserve = ScheduleOfDay.query.filter(ScheduleOfDay.id == id_shedule_time).first()    
    time_to_reserve.is_empty=0
    db.session.add(time_to_reserve)
    db.session.commit() 

def clear_time_shedue(id_shedule_time):
    '''
    Функция отчищает время дня для и ставит все значения по уолчанию
    '''
    time_to_reserve = ScheduleOfDay.query.filter(ScheduleOfDay.id == id_shedule_time).first()
    time_to_reserve.work_type = "маникюр".lower()
    time_to_reserve.cost = 0    
    time_to_reserve.name_of_client = 'неизвестно'.lower()    
    time_to_reserve.mail_of_client = 'неизвестно'.lower()
    time_to_reserve.phone_of_client = 'неизвестно'.lower()
    time_to_reserve.adress_of_client = 'неизвестно'.lower()
    time_to_reserve.note = 'примечание'.lower()
    time_to_reserve.connection_type = 0
    time_to_reserve.conection_type_str = 'неизвестно'
    time_to_reserve.client_come_in = 0
    time_to_reserve.info_message_for_client = 0
    time_to_reserve.remind_message_for_client = 0
    time_to_reserve.is_empty = 1
    time_to_reserve.user_id = -1        
    try:
        db.session.add(time_to_reserve)
        db.session.commit()  
    except Exception as e:
        print(f'Ошибка при отчистке времени одного дня. {e}')

def complete_info_for_send_to_js(request_idElem):
    '''
    Фунция формирует данные для отправки в js для оформления визуализации
    request_data - данные переданные сос страницы к серверу
    '''
    data_ = request_idElem.split('_')

    try:
        time_date_id = int(data_[2])
    except:
        return jsonify({'text': 'Не удалось получить ид времени', 'result': 'false'})           
    
    time_ = ScheduleOfDay.query.filter(ScheduleOfDay.id == time_date_id).first()

    if time_== None:
        return {'text': 'Не удалось получить время по ид', 'result': 'false'}

    time_next_ = ScheduleOfDay.query.filter(ScheduleOfDay.begin_time_of_day == time_.begin_time_of_day + timedelta(hours = 1)).first()
    #  #####################################Сначала вношу изменения в БД
      
    time_emty = '' #маркер говорит освободил время или занял

    time_this_send = str(time_.id)
    #изменяю элементы текста по умолчанию
    timeThisClass_send = 'schedule-container-days-free'
    timeThisText_send = 'Свободно'
    timeThisClientText_send = 'Клиент: неизвестно'
    timeThisPriceText_send = 'Цена: 0 руб.'
    timeThisTypeWorkText_send = 'Тип: маникюр'
    timeThisMailText_send = 'Почта: неизвестно'
    timeThisPhoneText_send = 'Тел.: неизвестно'
    timeThisContactsText_send = 'Контакты: неизвестно'
    timeThisNoteText_send = 'Примечание: примечание'

    if data_[1] == 'free':
        #если освобождаю время то отчищаю данные из БД
        clear_time_shedue(time_date_id)
        time_emty = 'free'
        timeThisClass_send = 'schedule-container-days-free'
        timeThisText_send = 'Свободно'

        if time_next_:
            #если следующее время занято, то текущее неполное, иначе свободное
            if time_next_.begin_time_of_day.hour <= current_app.config['END_MASTER_WORK_TIME']:
                if time_next_.is_empty == 0:
                    timeThisClass_send = 'schedule-container-days-some-free'
                    timeThisText_send = 'Неполное время' 
    else:        
        reserve_time_shedue(time_date_id)
        time_emty = 'reserved'
        timeThisClass_send = 'schedule-container-days-non-free'
        timeThisText_send = 'Занято'

    ################### Затем по измененным данным в базе редактирую предшествующий элемент

    #для js нужно послать ид для следующих и предыдущих элементов которые будут менять свои свойства
    time_prev_ = ScheduleOfDay.query.filter(ScheduleOfDay.begin_time_of_day == time_.begin_time_of_day - timedelta(hours = 1)).first()
    
    #time_next_next_ = ScheduleOfDay.query.filter(ScheduleOfDay.begin_time_of_day == time_.begin_time_of_day + timedelta(hours = 2)).first()
    
    time_prev_send = 'none'
    timePrevClass_send = 'none'
    timePrevText_send = 'none'
    
    if time_prev_:
        if time_prev_.begin_time_of_day.hour >= current_app.config['BEGIN_MASTER_WORK_TIME']:
            time_prev_send = str(time_prev_.id)
            #если я освобождаю ячейку, то предыдущая либо занята либо неполное время
            if time_prev_.is_empty == 0: # если впредыдущее время занято
                    timePrevClass_send = 'schedule-container-days-non-free'
                    timePrevText_send = 'Занято'
            else:
                if time_.is_empty == 1: #если текущее время свободно после сохранения
                    timePrevClass_send = 'schedule-container-days-free'
                    timePrevText_send = 'Свободно'
                else:
                    timePrevClass_send = 'schedule-container-days-some-free'
                    timePrevText_send = 'Неполное время'

   # print(timePrevClass_send)
   # print(timePrevText_send)

    #далее формирую контент для отправки в js

    return {
        'text': 'Изменения приняты',
        'result': 'true',
        'type_empty' : time_emty,
        'time_id' : time_this_send,
        'time_this_class_text': timeThisClass_send,
        'time_this_kind_text': timeThisText_send,
        'time_this_client_text': timeThisClientText_send,
        'time_this_price_text': timeThisPriceText_send,
        'time_this_typework_text': timeThisTypeWorkText_send,
        'time_this_mail_text': timeThisMailText_send,
        'time_this_phone_text': timeThisPhoneText_send,
        'time_this_contacts_text': timeThisContactsText_send,
        'time_this_note_text': timeThisNoteText_send,
        #'time_next': time_next_send,
        'time_prev': time_prev_send,
        'time_prev_class_text': timePrevClass_send,
        'time_prev_kind_text': timePrevText_send
                    }

def reserve_time_for_client(dict_of_form):
    '''
    Функция записывает в базу данных клиента на определенное время,
    при выборе занять несколько часов - проверяет свободно ли время - 
    и если свободно - то занимает его за этим клиентом,
    иначе выводит сообщение что времени не хватает, при удачной записи в БД возвращает True
    dict_of_form = {
    'user_id': client_id,
    'time_date_id' : time_date_id,
    'work_type' : form_change.work_type_field.data,
    'cost': form_change.price_field.data,
    'name_of_client': form_change.client_field.data,
    'mail_of_client': form_change.email_client_field.data,
    'phone_of_client': form_change.phone_client_field.data,
    'adress_of_client': form_change.adress_client_field.data,
    'note': form_change.node_field.data,
    'connection_type': form_change.type_connection_field.data,
    'client_come_in': form_change.client_come.data,
    'is_empty': form_change.time_empty_field.data,
    'hours_to_reserve': 'one'
                    }
    '''
    try:
        dict_of_form = dict(dict_of_form)
    except:
        dict_of_form = None

    #print('Данные после передачей в блок записи: _____', dict_of_form)
    try:
        user_id = int(dict_of_form['user_id'])
    except:
        user_id = -1
    try:
        time_date_id = int(dict_of_form['time_date_id'])
    except:
        time_date_id = -1
                     
    if user_id < 0:
        flash(_('Ошибка: Не выбран клиент для внесения его в расписание. Ошибка в блоке записи расписания.'))
        return False
  
    if time_date_id < 0:
        flash(_('Ошибка: Не выбрано время для для записи клиента. Ошибка в блоке записи расписания.'))
        return False
  
    s_time = ScheduleOfDay.query.filter_by(id=time_date_id).first()
    if s_time == None:
        flash(_('Ошибка: При определении времени для записи в расписание. Обратитесь в администрацию. Ошибка в блоке записи расписания.'))
        return False
  
    s_user = User.query.filter_by(id=user_id).first()
    if s_user == None:
        flash(_('Ошибка: При определении клиента для записи в расписание. Обратитесь в администрацию. Ошибка в блоке записи расписания.'))
        return False

    #если все данные корректны записываю данные в таблицу расписания s_time
    #print('Данные для записи: _____', s_time, s_user)
    s_time_to_reserve = []    

    if dict_of_form['hours_to_reserve'] == 'two':
        s_time_to_reserve = [t for t in ScheduleOfDay.query.all() \
            if t.begin_time_of_day > s_time.begin_time_of_day \
            and t.begin_time_of_day < s_time.begin_time_of_day + timedelta(seconds=5400)]
    elif dict_of_form['hours_to_reserve'] == 'three':
        #print(f"i am hear {s_time_to_reserve}")
        s_time_to_reserve = [t for t in ScheduleOfDay.query.all() \
            if t.begin_time_of_day > s_time.begin_time_of_day \
            and t.begin_time_of_day < s_time.begin_time_of_day + timedelta(seconds=9000)]
        #print(f"i am hear {s_time_to_reserve}")
    if len(s_time_to_reserve) > 0:
            for t in s_time_to_reserve:
                if t.is_empty == 0:
                    flash(_('Ошибка: Время которое Вы дополнительно резервируете для клиента занято. Уменьшите время для резерва.'))
        
                    return False

    s_time.work_type = \
        'маникюр' if dict_of_form['work_type'] == 'man' else \
        'педикюр' if dict_of_form['work_type'] == 'ped' else \
        'ман+пед' if dict_of_form['work_type'] == 'man_ped' else \
        'другое' if dict_of_form['work_type'] == 'some' else 'другое'
    s_time.cost = dict_of_form['cost']
    s_time.name_of_client = dict_of_form['name_of_client']
    s_time.mail_of_client = dict_of_form['mail_of_client'] if dict_of_form['mail_of_client'] !='' else 'неизвестно'

    s_time.phone_of_client = dict_of_form['phone_of_client']
    s_time.adress_of_client = dict_of_form['adress_of_client']
    s_time.note = dict_of_form['note']

    s_time.connection_type_str = dict_of_form['connection_type']
    
    try:
        s_time.client_come_in = int(dict_of_form['client_come_in'])
    except:
        s_time.client_come_in = 0
    
    s_time.is_empty = 0
    s_time.user_id = s_user.id

    try:
        db.session.add(s_time)
        db.session.commit()
    except:
        flash(_('Ошибка: При записи в базу данных. Обратитесь в администрацию. Ошибка в блоке записи расписания.'))
        return False
    
    try:
        if len(s_time_to_reserve) > 0:
            for t in s_time_to_reserve:
                t.is_empty = 0
                t.info_message_for_client = 1
                t.remind_message_for_client = 1
                db.session.add(t)
            db.session.commit()
    except:
        flash(_('Ошибка: При резервировании дополнительного времени при записи в базу данных. Обратитесь в администрацию. Ошибка в блоке записи расписания.'))
        return True
    flash(_(f'Время для клиента {s_user.username} зарезервировано успешно.'))        
    #здесь отсылаю смс о том что клиент зарегистрирован на определенное время

    return True

def send_info_message(time_date_id):
    '''
    Функция рассылки сообщений клиентам о том что они записаны на прием 
    1)Проверяет есть телефон или почта у клиента и если есть шлет сообщение
    2)Первое сообщение о том что клиент записан, второе сообщение за день до назначенного дня
    3)если встреча отменена то в блоке отмены встречи данные поля помечаются как исполненные    
    '''
    try:
        time_date_id = int(time_date_id)
    except:
        time_date_id = -1

    if time_date_id < 0:
           flash(_('Ошибка определения ид времени расписания в блоке рассылки информационных сообщений. Сообщение не отправлено. Обратитесь к администратору.'))
           return False

    time_date = ScheduleOfDay.query.filter(ScheduleOfDay.id == time_date_id).first()

    if time_date == None:
        flash(_('Ошибка время не найдено в базе данных. Сообщение не отправлено. Обратитесь к администратору.'))
        return False

    try:
        user_id = int(time_date.user_id)
    except:
        user_id = -1

    if user_id < 0:
        flash(_('Ошибка определения ид клиента. Сообщение не отправлено. Обратитесь к администратору.'))
        return False

    client = User.query.filter(User.id == user_id).first()

    if client == None:
           flash(_('Ошибка клиент не найден в базе данных. Сообщение не отправлено. Обратитесь к администратору.'))
           return False
    client_email = client.email
    client_phone = UserPhones.query.filter(UserPhones.user_id == client.id).first()

    try:
        info_message_for_client = int(time_date.info_message_for_client)
    except:
        info_message_for_client = 1

    if info_message_for_client > 0:
        print(_('Информационное письмо было отправлено клиенту ранее.'))
        flash(_('Информационное письмо было отправлено клиенту ранее.'))
        return False
       
    if client_email == None or client_email =='':    
        flash(_('У клиента не установлена электронная почта. Письмо не отправлено.'))
        print(_('У клиента не установлена электронная почта. Письмо не отправлено.'))
    else:
        #отсылаем письмо на почту
        try:
            send_info_email(client_email, time_date.begin_time_of_day)
            flash(_('Информационное письмо отправлено клиенту.'))
            print(_('Информационное письмо отправлено клиенту.'))
        except:
            flash(_('Ошибка при отправке письма в блоке информационной рассылки при первой записи клиента.'))
            print(_('Ошибка при отправке письма в блоке информационной рассылки при первой записи клиента.'))
    if client_phone == None:
        print(_('У клиента нет зарегистрированных телефонов. Смс не отправлено.'))        
    else:
        get_balance_sms=SMSC()
        get_balance_sms=get_balance_sms.get_balance()

        #проверяем баланс если он меньше заданного остатка смс не высылается и регистрация не происходит
        if main_utils.no_money_sms_balance(current_app.config['SMSC_LOW_MONEY_LEVEL'], main_utils.string_to_float(get_balance_sms)) == False:#отсылаем смс на телефон
            try:            
                list_message=[]
                dic_message={'number': '7'+str(client_phone.number), 'date': f'{time_date.begin_time_of_day.strftime("%d-%m-%Y %H:%M")}'}
                list_message.append(dic_message)
                send_info_sms(list_message)
     #           sms = SMSC()            
     #           sms.send_sms('7'+str(client_phone), f'Вы записаны на маникюр на {time_date.begin_time_of_day.strftime("%d-%m-%Y %H:%M")}. С уважением, Анна. www.nail-master-krd.ru') 
            except:
                flash(_('Ошибка при отправке смс в блоке информационной рассылки при первой записи клиента.'))
                print(_('Ошибка при отправке смс в блоке информационной рассылки при первой записи клиента.'))
        else:
            flash(_('Лимит денежных средств на счету смс центра не позволяет отправить информационное сообщение клиенту. Позвоните ему и сообщите,что он записан на прием.'))
        #отмечает в единице даты - времени что первое письмо отправлено
    time_date.info_message_for_client = 1
    try:
        db.session.add(time_date)
        db.session.commit()
    except:
        print(_('Ошибка при записи в базу отметки, что первое письмо уже отсправлено.'))
        flash(_('Ошибка при записи в базу отметки, что первое письмо уже отсправлено.'))
        return False            
    return True

def send_remaind_messages():
    '''
    функция для включение по расписанию
    Функция рассылки напоминаний о назначенной встрече с мастером
    1) Слать смс за один день до назначенной встречи
    2) слать смс один раз - если один пользователь записан несколько раз, то шлем одно смс по первому времени
    3) слать смс в период с 12:00 до 16:00
    4) слать смс асинхронно
    '''
    #дата. когда смс отсылаеся
    offset = timedelta(hours=current_app.config['LOCALE_TIME_OFFSET'])
    next_date_time_now_offset = datetime.utcnow()+timedelta(days=1)+timedelta(hours=3)
    
    date_ = next_date_time_now_offset.date()
    time_ = next_date_time_now_offset.time()

    if time_.hour < current_app.config['BEGIN_WORK_TIME'] and time_.hour > current_app.config['END_WORK_TIME']:
        print(_(f"Нельзя отправлять смс и письма ранее {current_app.config['BEGIN_WORK_TIME']} или позднее {current_app.config['END_WORK_TIME']}."))
        return False

    #выбрал все таймы на следующий день у которых есть ид юзера которые заняты и которым не отсылалис смс
    list_schedule_all = ScheduleOfDay.query.all()
    list_dates_to_send = [d for d in  list_schedule_all\
        if d.begin_time_of_day.date() == date_ \
        and d.user_id >=0 \
        and d.is_empty==0 \
        and d.remind_message_for_client == 0]

    list_id_users = []
    for d in list_dates_to_send:
        if not d.user_id in list_id_users:
            list_id_users.append(d.user_id)

    if len(list_id_users) <=0:
        print(_('Нет пользователей для отправки сообщений.'))        
        return False

    #выбираем пользователей кому отсылать смс - 
    list_users_for_send = [u for u in User.query.all() if u.id in list_id_users]
    
    if len(list_users_for_send) <= 0:
        print(_('Нет пользователей для отправки сообщений_2.'))        
        return False
    list_users_all = UserPhones.query.all()
    list_phones_for_send = [p for p in list_users_all if p.user_id in list_id_users]
    
    #отправляем письма напоминания
    for u in list_users_for_send:
        time_of_day = None
        for d in list_dates_to_send:
            if d.user_id == u.id:
                # передаю строку
                time_of_day = d
                break
        if u.email == None or u.email =='':        
            print(_(f'У {u.username} не установлена электронная почта. Писмо не отправлено.'))
        else:
            #отсылаем письмо на почту: в начале устанавливаем время для данного юзера
                  
            try:
                if time_of_day != None:
                    send_remind_email(u.email, f'{time_of_day.begin_time_of_day.strftime("%d-%m-%Y %H:%M")}')
            except:
                print(_(f'Ошибка при отправке письма пользователю {u.username} в блоке информационной рассылки при первой записи клиента.'))
        
        client_phone=None

        for p in list_phones_for_send:
            if p.user_id == u.id:
                client_phone=p
                break
        
        if client_phone == None:
            print(_(f'У клиента {u.username} нет зарегистрированных телефонов. Смс не отправлено.'))        
        else:
            get_balance_sms=SMSC()
            get_balance_sms=get_balance_sms.get_balance()

            #проверяем баланс если он меньше заданного остатка смс не высылается и регистрация не происходит
            if main_utils.no_money_sms_balance(current_app.config['SMSC_LOW_MONEY_LEVEL'], main_utils.string_to_float(get_balance_sms)) == False:
                #отсылаем смс на телефон
                try:
                    if time_of_day != None:
                        list_message=[]
                        dic_message={'number': '7'+str(client_phone.number), 'date': f'{time_of_day.begin_time_of_day.strftime("%d-%m-%Y %H:%M")}'}
                        list_message.append(dic_message)
                        send_remind_sms(list_message)
         #               sms = SMSC()            
         #               sms.send_sms('7'+str(client_phone), f'Вы записаны на маникюр на {time_date.begin_time_of_day.strftime("%d-%m-%Y %H:%M")}. С уважением, Анна. www.nail-master-krd.ru') 
                except:
                    print(_(f'Ошибка при отправке смс пользователю {u.username} в блоке информационной рассылки при первой записи клиента.'))
            else:
                print(_('Смс с напоминанием клиенту не отослано, так как лимит денежных средств на счету смс центра меньше допустимого. Пополните баланс.'))
        #отмечает в единице даты - времени что первое письмо отправлено
        time_of_day.remind_message_for_client = 1
        try:
            db.session.add(time_of_day)
            db.session.commit()
        except:
            print(_(f'Ошибка при записи в базу отметки у пользователя {u.username}, что первое письмо уже отсправлено.'))
    return True    
