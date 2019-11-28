import re
import json
import random
from datetime import datetime, timedelta, date
from app import db
from app.user.models import User, UserPhones, UserInternetAccount, ConnectionType

from app.master_schedule.models import *
from app.admin_my.models import ActionLine

from flask import flash
from flask_babel import _

def set_first_line_number(number_now, period_sec=60):
    '''
    Функция проверяет есть ли данные в таблице очереди расписания заданий и если нет то создает его.    
    int number_last - задача которая выполнятеся перед текущей
    int number_now - задача, которая должна выполниться сейчас
    int number_next - задача которая должна выполниться за ней
    Первая задача имеет индекс 0, 

    При первой инициализации проверяем есть ли записи с задачами ниже данной записи
    если нет то возвращаем Фалсе, если есть предыдущая задача, то создаем новую запись с 
    текущей задачей возвращаем тру и устанавливаем новое время для пропуска действия на запуск
    
    '''
    
    try:        
        number_now = int(number_now)  
        
    except:
        print(f"Ошибка при введении очереди исполнения задачь. Данные введены не в формате Int и задачи {number_last} {number_now} {number_next} исполняться не будут.")
        return False

    try:
        period_sec = int(period_sec)
    except:
        period_sec = 60
    
    line_numbers = ActionLine.query.order_by(ActionLine.line_number).all()
    line_numbers = line_numbers if line_numbers is not None else []    
    
    if number_now == len(line_numbers):
        #если номер задачи равен длинне массива задач значит этой задачи еще не внесено и ее нужно внести 
        l_number = ActionLine()
        #устанавливаю первую задачу на выполнение
        l_number.line_number = number_now
        l_number.time_for_start = datetime.utcnow()+timedelta(seconds=period_sec)
        l_number.time_lag = period_sec
        db.session.add(l_number)
        db.session.commit()
           
    line_numbers_for_change = ActionLine.query.order_by(ActionLine.line_number).all()
    line_numbers_for_change = line_numbers_for_change if line_numbers_for_change is not None else []
    
    if number_now < len(line_numbers_for_change):
        #если номер действия уже в таблице - так как номер 
        if line_numbers_for_change[number_now].time_for_start < datetime.utcnow():
            #если текущее время превышает временной лаг в БД то пропускаем действие на выполнение
            #при этом устанавливаю новое время исполнения для данного действия
            if number_now == 0:
                #если эта первое действие - то просто прибавляем лаг времени до следующего исполнения
                line_numbers_for_change[number_now].time_for_start = datetime.utcnow()+timedelta(seconds=period_sec)
                line_numbers_for_change[number_now].time_lag = period_sec
            elif number_now > 0:
                #если вторая запись то проверяем чтобы лаг между событиями был не менее минуты,
                #если меньше то прибавляем временной лаг ко времени предыдущего события
                next_time_this = line_numbers_for_change[number_now].time_for_start = datetime.utcnow()+timedelta(seconds=period_sec)
                next_time_prev = line_numbers_for_change[number_now -1].time_for_start
                add_seconds = 0
                for item in range(0, number_now-1):
                    delta_time =(next_time_this - line_numbers_for_change[number_now - item].time_for_start).seconds 
                    
                    if  abs(delta_time) < period_sec and delta_time >= 0:
                        add_seconds = add_seconds + random.randint(60,90)
                    elif  abs(delta_time) < period_sec and delta_time < 0:
                        add_seconds = add_seconds + random.randint(60,90)


               # delta_time =(next_time_this - next_time_prev).seconds                
                #if  abs(delta_time) < period_sec and delta_time >= 0:
                #    #если получается временной лаг меньше лага необходимого для прошлой задачи, но число положительное, то
                #    #то следующий старт данной задачи 
                #    line_numbers_for_change[number_now].time_for_start = next_time_prev + timedelta(seconds = (period_sec + random.randint(2,10)))
                #    line_numbers_for_change[number_now].time_lag = period_sec
                #elif  abs(delta_time) < period_sec and delta_time < 0:
                #    line_numbers_for_change[number_now].time_for_start = next_time_this + + timedelta(seconds = (period_sec - random.randint(2,10)))
                #    line_numbers_for_change[number_now].time_lag = period_sec
                #else:
                line_numbers_for_change[number_now].time_for_start = next_time_this + timedelta(seconds = add_seconds)
                line_numbers_for_change[number_now].time_lag = period_sec

            db.session.add(line_numbers[number_now])
            db.session.commit()
            return True

    return False

def fill_select_connection_type(mass_type = ['WhatsApp', 'Instagram', 'Телефон', 'ВКонтакте', 'Почта']):
    '''
    Функция заполняет таблицу типов связи спользователем
    Очередь: 0
    '''
    #основная функция 
    types = [t.name_of_type for t in ConnectionType.query.all()]
    types = [] if types == None else types

    types_to_put = [t for t in mass_type if t not in types]

    for t in types_to_put:
        type = ConnectionType()
        type.name_of_type = t
        db.session.add(type)
    db.session.commit()
    
def set_default_password_admin():
    '''
    Метод создает пароль для пользователя по умолчанию
    user - может быть передан объект или имя
    ''' 
    chars_for_pass = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    len_choice = len(chars_for_pass) - 1
    length_pass = 7
    default_password = ""

    for i in range(length_pass):
        num_char = random.randint(0, len_choice)
        default_password = default_password + chars_for_pass[num_char]

    #print(default_password)
    
    if default_password is None or default_password=="":
        print('user_password')
        return 'user_password', False

    print(default_password)
    return str(default_password), True

def user_delete_admin(user_id):
    '''
    Функция удаляет телефоны, соц.сети, пользователя, устанавливает все индексы в расписании от этого пользователя -1
    Возвращает результат удачно ли удален юзер
    '''
    try:
        user_id = int(user_id)
    except:
        user_id = -1

    user = User.query.filter_by(id = user_id).first()

    if user == None:   
        flash(_('Ошибка: Пользователь для удаления не найден.'))
        return False  
    
    p_to_del = [p.id for p in UserPhones.query.all() if p.user_id == user.id]
    try:
        deleted_objects_phones = UserPhones.__table__.delete().where(UserPhones.id.in_(p_to_del))
        db.session.execute(deleted_objects_phones)
        db.session.commit()
        flash(_('Телефон удаляемого пользователя удален.'))
    except:
        flash(_('Ошибка: При удалении телефона пользователя в блоке удаления пользователя.'))
        return False

    s_to_del = [s.id for s in UserInternetAccount.query.all() if s.user_id == user.id]
    try:
        deleted_objects_socials = UserInternetAccount.__table__.delete().where(UserInternetAccount.id.in_(s_to_del))
        db.session.execute(deleted_objects_socials)
        db.session.commit()
        flash(_('Соц. сеть удаляемого пользователя удалена.'))
    except:
        flash(_('Ошибка: При удалении соц.сети пользователя в блоке удаления пользователя.'))
        return False

    try:
        shedules_user_to_del = ScheduleOfDay.query.filter(ScheduleOfDay.user_id == user.id).all()
        shedules_user_to_del = shedules_user_to_del if shedules_user_to_del else []
        for s in shedules_user_to_del:
            s.user_id = -1
            db.session.add(s)        
        db.session.commit()
        flash(_('Ссылки в расписании на удаляемого пользователя удалены из листа распиания.'))
    except:
        flash(_('Ошибка: При внесении изменений в расписание об удаляемом пользователе в блоке удаления пользователя.'))
        return False

    try:
        db.session.delete(user)
        db.session.commit()        
        flash(_(f'Пользователь {user.username} успешно удален'))
    except:
        flash(_('Ошибка: При удалении пользователя в блоке удаления пользователя.'))
        return False

    return True

def show_preliminary_desk(start_date=date.today(), end_date=(date.today() + timedelta(days=30)), filter_include_date_field_data='include', filter_worked_field_data='non_worked'):
    '''
    Функция возвращает список данных для показа на странице предзаписи
    start_date-datetime
    end_date-datetime
    filter_include_date_field_data-string
    filter_worked_field_data-string
    '''   
    
    if type(start_date) != date and type(end_date) != date:
        start_date=date.today()
        end_date=start_date + timedelta(days=30)
        print('обе не даты')
    elif type(start_date) == date and type(end_date) != date:
        start_date = start_date
        end_date=start_date + timedelta(days=30)
        print('первая дата вторая не дата')
    elif type(start_date) != date and type(end_date) == date:
        if end_date < date.today():
            start_date = end_date - timedelta(days=30)
            end_date = end_date
            print('первая не дата вторая дата вторая дата меньше текущего времени')
        else:
            start_date = date.today()
            end_date = end_date
            print('первая не дата вторая дата вторая дата больше или равна текущего времени')
    elif type(start_date) == date and type(end_date) == date:
        start_date=start_date
        end_date=end_date
        print('обе даты')
    else:
        print('ушел в блок дейттайм')
        if type(start_date) != datetime and type(end_date) != datetime:
            start_date=datetime.utcnow().date()
            end_date=(datetime.utcnow() + timedelta(days=30)).date()
            
        elif type(start_date) == datetime and type(end_date) != datetime:
            start_date = start_date.date()
            end_date=(start_date.date() + timedelta(days=30)).date()
        elif type(start_date) != datetime and type(end_date) == datetime:
            if end_date.date() < datetime.utcnow().date():
                start_date = (end_date.date() - timedelta(days=30)).date()
                end_date = end_date.date()
            else:
                start_date = datetime.utcnow().date()
                end_date = end_date.date()
        else:
            start_date=start_date.date()
            end_date=end_date.date()

    #print(f'{filter_include_date_field_data}-----------------{len(filter_worked_field_data)}-----------{len("non_include")}')

    incl=filter_include_date_field_data
    #print(incl)
    #print(incl == str('non_include'))

    if filter_include_date_field_data != 'include' and filter_include_date_field_data != 'non_include':
        #print("Ошибка")
        filter_include_date_field_data = 'include'

    if filter_worked_field_data != 'non_worked' and filter_worked_field_data != 'worked' and filter_worked_field_data != 'all':
        filter_worked_field_data = 'non_worked'

    print('filter_include_date_field_data: ',filter_include_date_field_data)
    print('filter_worked_field_data: ',filter_worked_field_data)
    print('start_date: ',start_date, type(start_date))
    print('end_date: ',end_date, type(end_date))

    #здесь при выборе даты учитываем и фильтр формы
    if filter_include_date_field_data == 'include':
          #если учитываю даты
          print('учитываю даты')
          if filter_worked_field_data == 'worked':
              #учитываю только отработанные заявки
              list_pre_rec = [r for r in PreliminaryRecord.query.order_by(PreliminaryRecord.time_to_record.desc()) \
                  if r.time_to_record.date() >= start_date and r.time_to_record.date() <= end_date and r.message_worked > 0]
          elif filter_worked_field_data == 'non_worked':
              list_pre_rec = [r for r in PreliminaryRecord.query.order_by(PreliminaryRecord.time_to_record.desc()) \
                  if r.time_to_record.date() >= start_date and r.time_to_record.date() <= end_date and r.message_worked == 0]
          else:
              list_pre_rec = [r for r in PreliminaryRecord.query.order_by(PreliminaryRecord.time_to_record.desc()) \
                  if r.time_to_record.date() >= start_date and r.time_to_record.date() <= end_date]

    else:
        print('НЕ учитываю даты')
        #если не учитываю даты
        if filter_worked_field_data == 'worked':
            #учитываю только отработанные заявки
            list_pre_rec = [r for r in PreliminaryRecord.query.order_by(PreliminaryRecord.time_to_record.desc()) \
                if r.message_worked > 0]
        elif filter_worked_field_data == 'non_worked':
            list_pre_rec = [r for r in PreliminaryRecord.query.order_by(PreliminaryRecord.time_to_record.desc()) \
                if r.message_worked == 0]
        else:
            list_pre_rec = [r for r in PreliminaryRecord.query.order_by(PreliminaryRecord.time_to_record.desc())]
         


    return list_pre_rec

def parser_dic_master_news(dic_master_news):
    '''
    Функция парсит словарь со строки запроса в питоновский словарь 
    dic_master_news = {'news_id' : '-1'}
    '''
    print('dictionary: ',dic_master_news)
    try:
        dic_master_news = json.loads(dic_master_news.replace("'", '"').replace("Undefined".lower(), '-1'))   
    except:
        print('Ошибка: при парсинге словаря dic_master_news из строки запроса методом json.loads в блоке parser_dic_master_news ')
        return {'news_id' : -1}
    pass
    print('dictionary_id: ',dic_master_news['news_id'])
    try:
        news_id = int(dic_master_news['news_id'])
    except:
        news_id = -1
    print('news_id: ',news_id)

    return {'news_id' : news_id}