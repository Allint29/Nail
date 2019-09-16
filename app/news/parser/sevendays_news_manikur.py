# -*- coding: utf-8 -*-
from datetime import datetime, timedelta;
import requests
#R9 который в зависимости от ОС можно выставить в программе - это модуль locale и инфо о ситеме - модуль platform
import locale;
import platform;
from app import db
from app.news.models import News
from bs4 import BeautifulSoup

#R9 выставляем русскую локализацию - это позволит распозновать месяцы и дни в русскоязычном написании
if platform.system() == "Windows":
    locale.setlocale(locale.LC_ALL, "russian");
else:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

def parse_sevendays_news_date(date_str):
    '''
    function parse date from format "сегодня в 20:30" to utc format
    '''
    try:
        return datetime.strptime(date_str, '%d/%m/%Y %H:%M' )
    except ValueError:
        print("WRONG")
        return datetime.now()

def get_html(url): 
    try:
        result = requests.get(url)
        result.raise_for_status()
        return result.text
    except(requests.RequestExeption, ValueError):
        print('Сетевая ошибка')
        return False


def get_sevendays_news_manikur():
    '''
    func come in web of 7days in box of mail news and parse it to format db and save it
    '''
    html = get_html('https://7days.ru/search/?search_all=1&q=%EC%E0%ED%E8%EA%FE%F0')
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        all_news = soup.find('li', class_='j-slide b-slider__item b-slider__item_state_selected')
        all_news = all_news.findAll('div', class_='b-story__content')
        #result_news = []

        for news in all_news:                    
            title = news.find('a').text
            source = 'https://7days.ru'
            url = source + news.find('a')['href']
            published = news.find('div', class_='b-story__meta').find('span', class_='b-story__date').text.replace(' ', '').replace('в', ' ').replace('|', '').replace('.', '/')
            text = ''

            try:
                published = parse_sevendays_news_date(published)
                #published = datetime.strptime(published, '%Y-%m-%d')
                #print(published)
            except ValueError:
                published = datetime.now()
                #print('WRONG')
            save_news(title, url, published, source, text)
            #result_news.append({'title' : title, 'source' : source, 'paublished' : published, 'url' : url, 'text' : text})
        #    print({'title' : title, 'source' : source, 'paublished' : published, 'url' : url, 'text' : text})
        #return result_news
        #
        #    print(title)
        #    print(source)
        #    print(url)
        #    print(published)
        #    print(text)
            #
    #return False
        #print (result_news)

def save_news(title, url, published, source, text):
    '''
    func create object News chack that no double in bd and save it in bd if none
    '''
    
    news_exists = News.query.filter(News.url == url).count();
    if news_exists < 1:
        news_news=News(title=title, url=url, published=published, source=source, text=text)
        db.session.add(news_news)
        db.session.commit()

if __name__ == '__main__':
    get_sevendays_news_manikur()


