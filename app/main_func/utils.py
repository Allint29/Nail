#R11для проверки подленности ссылки на перенаправления
from urllib.parse import urlparse, urljoin;
from flask import request, url_for;
from datetime import datetime, timedelta, date
import math

def is_safe_url(target):
    '''
    func take link from request(our web site - ref_url - http://127.0.0.1:5000) and check reference is our
    '''
    ref_url = urlparse(request.host_url);
    test_url = urlparse(urljoin(request.host_url, target));
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc;

def get_redirect_target():
   '''
   func check if in adress line is param NEXT or contain request.referrer
   it return first from its two link
   '''
   for target in request.values.get('next'), request.referrer:
       if not target:
           continue;

       if is_safe_url(target):
           return target;

   return url_for("news.index")


def min_date_for_calculation():
    '''
    функция возвращает минимальное значение для данной модели
    '''
    return datetime.strptime('1/1/2000 0:00', '%d/%m/%Y %H:%M')

def default_email():
    '''
    функция возвращает минимальное значение для данной модели
    '''
    return str("example@mail.com")

def make_date_from_date_time(date_my):
    '''
    Функция делает дату формата День/Месяц/Год 0:00
    форматы парсинга: datetime, date
    string: '%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M'
    default: if None return 2000/1/1 0:00
             if exeption return 2000/1/1 0:00
    '''
    default_date = datetime(2000, 1, 1, 0, 0)

    if not date_my:        
        return {'date' : default_date, 'parsed' : False }

    if type(date_my) == datetime or type(date_my) == date:           
        return {'date' : datetime(date_my.year, date_my.month, date_my.day, 0, 0), 'parsed' : True }

    if type(date_my) == str:
        try:                    
            date_my = datetime.strptime(date_my,'%Y/%m/%d %H:%M:%S')
            return {'date' : datetime(date_my.year, date_my.month, date_my.day, 0, 0), 'parsed' : True }
        except:        
            pass

        try:           
            date_my = datetime.strptime(date_my,'%Y/%m/%d %H:%M')
            return {'date' : datetime(date_my.year, date_my.month, date_my.day, 0, 0), 'parsed' : True }
        except:
            pass

    return {'date' : default_date, 'parsed' : False }


def make_name_of_day_from_date(date_my=None, lang='en'):
    '''
    Функция делает из даты название дня недели
    на вход принимаает date или datetime
    date_my - datetime, date, str('%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M')
    '''
    lang=lang.lower()
    
    if lang != 'en' and lang != 'ru':
        lang = 'en'

    days={'ru': ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье'],'en' : ['Monday','Tuesday','Wensday','Thursday','Friday','Saturday','Sunday']}
    default_day = datetime(2000, 1, 1, 0, 0).weekday()

    if not date_my:
        {'day' : days[f'{lang}'][default_day.weekday()], 'parsed': False}

    try:
        if type(date_my) == datetime or type(date_my) == date:           
            return {'day' : days[f'{lang}'][date_my.weekday()], 'parsed': True}
    except:
        pass

    if type(date_my) == str:
        try:
            date_my = datetime.strptime(date_my,'%Y/%m/%d %H:%M:%S').weekday()
            return {'day' : days[f'{lang}'][date_my], 'parsed': True}
        except:
            pass

        try:
            date_my = datetime.strptime(date_my,'%Y/%m/%d %H:%M').weekday()
            return {'day' : days[f'{lang}'][date_my], 'parsed': True}
        except:
            pass

    return {'day' : days[f'{lang}'][default_day.weekday()], 'parsed': False}

def take_hours_from_datetime(date_for_parse=None):
    '''
    функция возвращает часы даты у которой нужно узнать время 
    '''
    if not date_for_parse:
        return {'time' : None, 'parsed': False}    
    try:
        if type(date_for_parse) == datetime or type(date_for_parse) == date:             
            zero_time= make_date_from_date_time(date_for_parse)            
            if zero_time['parsed'] == True:
                time_of_day = (date_for_parse - zero_time['date']).seconds/3600                
                return {'time' : int(math.floor(time_of_day)), 'parsed' : True }
            return {'time' : None, 'parsed': False}
    except:
        return {'time' : None, 'parsed': False}

def is_digit(string):
    '''
    функция проверяет является ли строка числом(int double float) 
    '''
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False