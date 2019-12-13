# -*- coding: utf-8 -*-
from datetime import datetime, timedelta;
#R9 который в зависимости от ОС можно выставить в программе - это модуль locale и инфо о ситеме - модуль platform
from bs4 import BeautifulSoup
from app.my_work.models import MyWork, CommentsToMyWorks
from app.my_work.parser.utils import is_reklam, save_my_work, get_html
import json
from app import db
from instagram import Account, Media, WebAgent, WebAgentAccount, Story, Location, Tag, Comment
#import threads
#locker=0

def get_anna_nails_content():
    '''
    func come in instagramm of human and take from it photos and comments to them
    '''
    #global locker
#   #
    #if locker == 1:
    #     return False   
   
    #locker = BoundedSemaphore(value=1) 
    #with locker:
    photos = []
    try:


        #locker = 1
        agent = WebAgent()
        account = Account("anna_nails_ani")

        agent.update(account)

        count_download_photos = 1000    
        #если в БД меньше 50 записей то считываем максимальное коичество записей иначе 10
        #if MyWork.query.count() < 50:
        #    count_download_photos = 300        
        
        #вычисляем дату на которой нужно остановится и не рассматривать дальше контент если это не первая загрузка
          
        date_to_stop_search = MyWork.query.order_by(MyWork.published.desc()).first()
        if date_to_stop_search:
             date_to_stop_search = date_to_stop_search.published - timedelta(days=14) 

        #создаем агента на считывание с аккаунта данных по контенту
        media=agent.get_media(account, count=count_download_photos)

        # список работ для добавления в БД
        photos = []
        #список комментариев которые не нужно сохранять в БД
        reklama_pattern_list = {'реклам', 'клам', 'услуг', 'предлагаю', 'пиар'}
        reclama_owner_list = {'master_and_model123'}
              
        count_photo = 0
        for med in media:            
              for m in med:                                                     
                  if  m != None and not m.is_video:        
                     # print('Код медиа:' f'{m.code}')
                      photo_date = datetime.fromtimestamp(m.date)                 
                         
                      count_photo = count_photo + 1
                      #если достигли определенной даты после которй не нужно загружать больше не ищем                      
                      if date_to_stop_search and photo_date <= date_to_stop_search:
                         # print('Достигли максимальной даты поиска')
                          break
                      photo_date = photo_date.strftime('%Y-%m-%d %H:%M:%S') 
                     # print(f'{type(date_to_stop_search)}' + '!!!!!!!' + f'{type(photo_date)}')
                      #print(f'Считано фоток: {count_photo}, id_site: {m.id}')

                      comment=agent.get_comments(media=m, count=30)
                      comments_for_photo = []                  
                      if comment[0]:
                          for c in comment[0]:
                              if is_reklam(f'{c.owner}', reclama_owner_list) == False:   
                                  if is_reklam(c.text, reklama_pattern_list) == False:
                                      #print(f'{c.media}')
                                      comment_date = datetime.fromtimestamp(c.created_at)
                                      comment_date = comment_date.strftime('%Y-%m-%d %H:%M:%S')   
                                      comments = {'id' : f'{c.id}', 'media': f'{c.media}', 'owner' : f'{c.owner}', 'text' : f'{c.text}', 'date' : comment_date}
                                      comments_for_photo.append(comments)
                      
                      item = {'id' : f'{m.id}', 'caption' : f'{m.caption}', 'code' : f'{m.code}', 'date' : photo_date, 'url' : f'{m.display_url}', 'owner' : f'{m.owner}', 'likes' : f'{m.likes_count}', 'comments' : comments_for_photo}
                      photos.append(item)
        
    except Exception as e:
        pass
        print(f"Error: Type None! {e}")
    except(AttributeError):
        print("Atribute Error!")

    #locker=0

    #try:
    save_my_work(photos)
   # except Exception as e:
   #     print(f"Ошибка!!!!!!!: {e}")
    
#    print(f"Цикл закончен locker = {locker}")

    #print(type(photos) == list)    

    #agent = WebAgent()
    #account = Account("anna_nails_ani")
    #
    #agent.update(account)
    #
    #media=agent.get_media(account, count=20)
    #
    #for med in media:
    #    try:
    #      for m in med:
    #                                                 
    #          if  m != None and not m.is_video:
    #
    #              print(m.id)
    #              print(m.display_url)
    #              comment=agent.get_comments(media=m, count=35)
    #              if comment:
    #                  for c in comment[0]:
    #                    print(c.text)
    #              print(m.owner)
    #    except(TypeError):
    #            print("Type None!")
    #    except(AttributeError):
    #        print("Atribute Error!")
       # print(m)
   # media = Media("Bk09NSFn3IX")
   # media1, pointer = agent.get_media(account)
   # media2, pointer = agent.get_media(account, pointer=pointer, count=50, delay=1)

   # photos = []
   # agent = WebAgentAccount("alexeya29")
   # agent.auth("Allint25_29")
   # 
   # medias, pointer = agent.feed()
   # for media in medias:
   #     if not media.is_video:
   #         print(media.display_url)
   #         photos.append(media.display_url)
   # 
   # 
   # while not pointer is None:
   #     medias, pointer = agent.feed(pointer=pointer)
   #     for media in medias:
   #         if not media.is_video:
   #             print(media.display_url)
   #             photos.append(media.display_url)
   #


#    r = requests.get('https://www.instagram.com/anna_nails_ani/')
#    soup = BeautifulSoup(r.text, 'lxml')
#    
#    script = soup.find('script', text=lambda t: t.startswith('window._sharedData'))
#    page_json = script.text.split(' = ', 1)[1].rstrip(';')    
#    data = json.loads(page_json)
#   # print(data)
#    f=data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
#   # print(f)
#    i=0
#    for post in f:
#        i=i+1
#        
#    #    #image_src = post['node']['thumbnail_resources'][1]['src']
#    #    #print(image_src)
#        print(i)
#        print(post['node']['id'])
#        print(post['node']['id'])

#   # html = get_html('https://www.instagram.com/anna_nails_ani/')
   # 
   # #print(html)
   # if html:
   #     soup = BeautifulSoup(html, 'lxml')
   #     print(soup)
   #     all_news = soup.find('div')#, class_='_2z6nI')
   #     print (all_news)
   #     all_news = all_news.findAll('div', class_='b-story__content')
   #     #result_news = []


