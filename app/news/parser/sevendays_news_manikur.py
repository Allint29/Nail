﻿# -*- coding: utf-8 -*-
from datetime import datetime, timedelta;
from bs4 import BeautifulSoup
#R9 который в зависимости от ОС можно выставить в программе - это модуль locale и инфо о ситеме - модуль platform
import locale;
import platform;
from app.news.parser.utils import get_html, save_news
from app import db
from app.news.models import News


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

def get_sevendays_news_manikur():
    '''
    func come in web of 7days in box of mail news and parse it to format db and save it
    '''
    html = get_html('https://7days.ru/search/?search_all=1&q=%EC%E0%ED%E8%EA%FE%F0')
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        all_news = soup.find('li', class_='j-slide b-slider__item b-slider__item_state_selected')
        all_news = all_news.findAll('div', class_='b-story_content-type_horizontal')
        
        image_source = None
        for news in all_news:
            image_source = news.find('img', class_='b-story__image')['src']
            source = 'https://7days.ru'
            title = news.find('a', class_='b-story__text').text
            url = source + news.find('a', class_='b-story__text')['href']
            published = news.find('div', class_='b-story__meta').find('span', class_='b-story__date').text.replace(' ', '').replace('в', ' ').replace('|', '').replace('.', '/')
            #print(image_source, title)
            #print(url)
            #print(f'Дата публикации: {published}')
            text = ''

            try:
                published = parse_sevendays_news_date(published)
                #published = datetime.strptime(published, '%Y-%m-%d')
                #print(published)
            except ValueError:
                published = datetime.now()
                #print('WRONG')

            try:
                save_news(title, image_source, url, published, source, text)
            except:
                print("Ошибка связи Elasticsearch нет подключения. Порт: 9200")
            #  all_news = all_news.findAll('div', class_='b-story__content')
      #  #result_news = []
      #
      #  for news in all_news:                    
      #      title = news.find('a').text
      #      source = 'https://7days.ru'
      #      url = source + news.find('a')['href']
      #      published = news.find('div', class_='b-story__meta').find('span', class_='b-story__date').text.replace(' ', '').replace('в', ' ').replace('|', '').replace('.', '/')
      #      text = ''
      #
      #      try:
      #          published = parse_sevendays_news_date(published)
      #          #published = datetime.strptime(published, '%Y-%m-%d')
      #          #print(published)
      #      except ValueError:
      #          published = datetime.now()
      #          #print('WRONG')
      #      save_news(title, url, published, source, text)
      #      #result_news.append({'title' : title, 'source' : source, 'paublished' : published, 'url' : url, 'text' : text})
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

def get_news_content():
    '''
    function take posts without text-content
    '''
    #R9 is_ позволяет сделать сравнение на идентичность с жэталонным параметром
    news_without_text = News.query.filter(News.text.is_(None));
    news_with_space_text = News.query.filter(News.text == "")

    #R9 после запроса заголовков по новостям мы в цикле перебираем все и не делаем сто запросов на один сайт
    for news in news_without_text:        
        html = get_html(news.url);
        #если html не пустая то иниц beautifulsoup - для расвознования текста на страничке
        if html:
   #         #укажем парсер
            soup = BeautifulSoup(html, "html.parser");
   #         #берем текст новости далее- но текст - это не красиво поэтому нужно взять формат html
            news_text = soup.find('div', class_="b-pure-content b-pure-content_type_detail  b-story__section j-story-content js-mediator-article").decode_contents();
            
   #         #если текст получен, то мы берем его и сохраняем
            if news_text:
                news.text = news_text;
                db.session.add(news);                
                db.session.commit();

       #R9 Если поля текста без текста но строковый класс
    for news in news_with_space_text:        
        html = get_html(news.url);
        #если html не пустая то иниц beautifulsoup - для расвознования текста на страничке
        if html:
   #         #укажем парсер
            soup = BeautifulSoup(html, "html.parser");
   #         #берем текст новости далее- но текст - это не красиво поэтому нужно взять формат html
            news_text = soup.find('div', class_='b-pure-content').decode_contents();
            #print(news_text)
   #        # #если текст получен, то мы берем его и сохраняем
            if news_text:
                news.text = news_text;
                db.session.add(news);                
                db.session.commit();

