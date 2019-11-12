#R11для проверки подленности ссылки на перенаправления
from urllib.parse import urlparse, urljoin;
from flask import request, url_for;
from datetime import datetime, timedelta, date
from app.master_schedule.models import DateTable, ScheduleOfDay
from app import db
from app.main_func import utils as main_utils
from app.master_schedule.forms import TimeForm

def delete_all_days_in_schedule():
    '''
    Функция быстрого удаления записей в таблице расписания
    '''
    data_to_delete = DateTable.query.all()
    for data in data_to_delete:
        db.session.delete(data)

    db.session.commit()

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


def delete_all_times_in_schedule():
    '''
    Функция быстрого удаления записей в таблице расписания
    '''
    data_to_delete = ScheduleOfDay.query.all()
    for data in data_to_delete:
        db.session.delete(data)

    db.session.commit()

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

   # print(len(times_to_add))
        #добавляемм все таймы в базу
    for t in times_to_add:
        time_to_add = ScheduleOfDay(
                    begin_time_of_day = t['time'], 
                    end_time_of_day = t['time'] + timedelta(minutes=59),
                    date_table_id = t['date_id']
                    )
        if t['time'].hour < 8 or t['time'].hour > 21:
            time_to_add.is_empty=0

        db.session.add(time_to_add)
    db.session.commit()
        


def take_empty_time_in_shedule(begin_date=None, end_date=None, to_back=None):
    '''
    Функция берет список с временем расписания и возвращает словарь с маркировкой времени расписания - занято, свободно, свободно с ограничениями
    '''    

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
            if t >= 8 and t <= 21:
                list_of_work_time.append(item)
        list_to_show =[]
       
        j=0
        while j<len(list_of_work_time):
            t=list_of_work_time[j].begin_time_of_day.hour
            #добавляю форму для отправки запроса на редактирование
            
            edit_form = TimeForm()
            edit_form.id_time.data=list_of_work_time[j].id
            
            #достигли последнего элемента и он свободен, то время свободное
            if t==21:
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

def reserve_time_shedue(id_shedule_time):
    '''
    Функция переводит тригер занятости времени во включенное состояние и сохраняет это в БД
    '''
    #сначала очищаем форму от записи
    clear_time_shedue(id_shedule_time)
    time_to_reserve = ScheduleOfDay.query.filter(ScheduleOfDay.id == id_shedule_time).first()    
    time_to_reserve.is_empty=0
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
    time_to_reserve.client_come_in = 0
    time_to_reserve.is_empty=1
    time_to_reserve.user_id = None          
    db.session.commit()  

