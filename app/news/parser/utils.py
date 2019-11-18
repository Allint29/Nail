# -*- coding: utf-8 -*-
from app import db
import requests
from app.news.models import News

def get_html(url): 
    '''
    func get web site by link or print error
    '''
    #Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36
    #headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    try: 
        result = requests.get(url, headers=headers)
        result.raise_for_status()
        return result.text
    except(requests.exceptions.RequestExeption, ValueError):
        print('Сетевая ошибка')
        return False


def save_news(title, image_source, url, published, source, text):
    '''
    func create object News chack that no double in bd and save it in bd if none
    '''    
    # print('text = empty')
    

    news_exists = News.query.filter(News.url == url).count();
    #print(news_exists)
    if news_exists < 1:
        news_news=News(
            title=title, 
            main_picture_url=image_source, 
            url=url, 
            published=published, 
            source=source, 
            text=text)
        db.session.add(news_news)
        db.session.commit()

