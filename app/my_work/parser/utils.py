# -*- coding: utf-8 -*-
from datetime import datetime, timedelta;
import requests
from app import db
from app.my_work.models import MyWork, CommentsToMyWorks

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


def is_reklam(text, pattern_list):
    '''
    func check text for substring, substring conteined in pattern_list 
    '''
    try:
        # если тект=ст пустой то возвращаем что рекламы нет
        if text == '' or text == None:
            return False
        
        if text:           
           for pattern in pattern_list:                                  
               f = text.find(f'{pattern}')
               if f > 0:
                   return True                 
           return False
        #если нет текста тотвозвращаем что рекламы нет
        return False

    except:
        print('Ошибка при проверке контента на рекламу')
        return False


                      #photo_date = datetime.fromtimestamp(m.date)                   
                  #photo_date = photo_date.strftime('%Y-%m-%d %H:%M:%S')  


#item = {
#'id' : f'{m.id}', 
#'date' : photo_date, 
#'caption' : f'{m.caption}', 
#'code' : f'{m.code}',
#'url' : f'{m.display_url}', 
#'owner' : f'{m.owner}', 
#'likes' : f'{m.likes_count}', 
#'comments' : comments_for_photo}

#   id = db.Column(db.Integer, primary_key=True)
#   id_site = db.Column(db.String(250), nullable=False)
#   published = db.Column(db.DateTime, nullable=False, default=datetime.now())
#   title = db.Column(db.String, nullable=True)
#   code = db.Column(db.String, nullable=False)
#   url = db.Column(db.String, unique=True, nullable=False)
#   show = db.Column(db.Boolean, unique=False, nullable=False, default=True)
#   owner = db.Column(db.String, nullable=False)
#   likes = db.Column(db.Integer)    
#   source = db.Column(db.String, nullable=False)

def save_my_work(dictionary_of_my_works):
    '''
    func take the dictionary and save it content to bd for other table
    '''
    if type(dictionary_of_my_works) != list:
        print('Вы пытаетесь сохранить не список, а что-то другое')
        return False
    
    for item in dictionary_of_my_works:

       # work_exists1 = MyWork.query.filter(MyWork.url == item['url']).count();
       # work_exists2 = MyWork.query.filter(MyWork.code == item['code']).count();
       # work_exists3 = MyWork.query.filter(MyWork.id_site == item['id']).count();

        work_exists = [w for w in  MyWork.query.all() if w.url == item['url'] or w.code == item['code'] or w.id_site == item['id']]
        
        #print(f"work_exists={work_exists}")
        if len(work_exists) == 0: # and work_exists2 < 1 and work_exists3 < 1:
            #2019-04-27 19:36:33            
            date_p = datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S')
            #date_p == date_p.strftime('%Y-%m-%d %H:%M:%S') 
            #print(item['id'])
            #print(f"lenght_title: {len(item['caption'])}")
            my_work = MyWork(
                id_site=item['id'], 
                published=date_p,
                title=item['caption'],
                code=item['code'],
                url=item['url'],
                owner=item['owner'],
                likes=item['likes'],
                show=True,

                source="instagram"
                )
            try:
                db.session.add(my_work)
                db.session.commit()
            except Exception as e:
                print(f"Ошибка в блоке сохранения работ мастера: {e}________ _________ __________")

        #после проверки БД на новые работы проверяем новые комментарии
        for c in item['comments']:
                #item_comments = c['id']
                #print(item_comments)                
                comment_exists = CommentsToMyWorks.query.filter(CommentsToMyWorks.id_site == c['id']).count(); 
                #comment_exists = [c for c in CommentsToMyWorks.query.all() if c.id_site == c['id']]

                if comment_exists < 1:
                    my_work_id_c = MyWork.query.filter(MyWork.code == c['media']).first().id;
                    
                    date_c = datetime.strptime(c['date'], '%Y-%m-%d %H:%M:%S')
                    comment_to_my_work = CommentsToMyWorks(
                        id_site = c['id'],
                        media = c['media'],
                        owner = c['owner'],
                        published = date_c,
                        text = c['text'],
                        show = True,
                        source = 'instagram',

                        my_work_id = my_work_id_c
                        )       
                    try:
                        db.session.add(comment_to_my_work)
                        db.session.commit()
                    except Exception as e:
                        print(f"Ошибка в блоке сохранения комментариев работ мастера: {e}")

        
    


    
    