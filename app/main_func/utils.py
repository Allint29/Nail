#R11для проверки подленности ссылки на перенаправления
from urllib.parse import urlparse, urljoin;
from flask import request, url_for;
from datetime import datetime, timedelta

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

#def make_date_from_date_time(date):
#    '''
#    Функция делает дату формата День/Месяц/Год 0:00
#    '''
#    try:
#        time_with_zero=datetime.strptime(day_2.strftime('%Y/%m/%d'), '%Y/%m/%d')
#        return date