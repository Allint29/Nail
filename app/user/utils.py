# -*- coding: utf-8 -*-
from app import db
#from app.main_func.smsc_api import SMSC
from app.user.models import *
from app.my_work.models import *
from datetime import datetime, timedelta
from flask import current_app, flash
from flask_babel import _, get_locale
from flask_login import current_user
from app.main_func import utils as main_utils
from app.user.myemail import send_code_sms
import random

def create_default_user():
    if not User.query.filter(User.username == 'DefaultUser').first():
        user = User(username='DefaultUser', email='example@example.example')
        user.set_password('DefaultUser_')        
        user.set_confirm_email_true()
        user.expire_date_request_confirm_password = main_utils.min_date_for_calculation()
        try:
            db.session.add(user)
            db.session.commit()
        except:
            print(_('Ошибка при создании дефолтного пользователя. Пользователь не создан'))

def set_default_password(user=None, number=None):
    '''
    Метод создает пароль для пользователя пароль по умолчанию
    user - пользователь для которого создается пароль
    number - номер телефона - который используется при регистрации пользователя
    '''
    try:
        if type(user) != str:
            user = user.username
    except:       
        user = None

    try:        
        #если пришла не строка а объект телефона, другое - переводим в ошибку
        if type(number) != str and type(number) != int :
            number = number.number
    except:        
        number = None

    if user and number:
        user = User.query.filter_by(username = user).first()        
        chars_for_pass = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        len_choice = len(chars_for_pass) - 1
        length_pass = 7
        default_password = ""

        if user.trying_to_enter_new_phone < 1:
            return flash(_('Вы исчерпали количество запросов на выдачу паролей по смс. Обратитесь к администрации.'))
        
        for i in range(length_pass):
            num_char = random.randint(0, len_choice)
            default_password = default_password + chars_for_pass[num_char]

        #print(default_password)
        
        if default_password is None or default_password=="":
            return _('Пароль не был назначен. Ошибка в генерации паролей'), False
        try:
            sms = SMSC()  
            sms.send_sms('7'+str(number), f'Логин: {user.username}. Пароль: {default_password}. Используйте для входа на сайт Nail-Master-Krd.')
        except:            
            flash(_('Ошибка при отправке смс с дефолтным паролем. Пароль не отослан'))

        user.set_password(default_password)
        user.trying_to_enter_new_phone =user.trying_to_enter_new_phone - 1

        try:
            db.session.add(user)
            db.session.commit()
        except:
            flash(_('Ошибка при записи в базу пароля по умолчанию. Пароль не сохранен.'))
            

        return _('Вы не создали пароль для входа на сайт. Вам назначен пароль, который выслан Вам в смс сообщении. Используйте его.'), False

    elif not user:
        return _('Отсутствует пользователь для установки пароля по умолчанию.'), False
    elif not number:
        return _('Отсутствует номер телефона для установки пароля по умолчанию.'), False

def save_password_by_phone_registration(user=None, password=None, password2=None):
    '''
    метод создания пароля для учетной записи при регистрации через телефон
    user - string
    password - string
    password2 -string
    '''    
    try:
        if type(user) != str:
            user = user.username
    except:
        user = None

    #для того чтобы обойти свойство required
    if password == "" or not password:
        password = " "

    if user and password:
        if len(str(password)) < 5:
            return _('Пароль должен быть не менее 5 символов.'), False
        if str(password) != str(password2):
            return _('Пароли не совпадают.'), False

        user = User.query.filter_by(username = user).first()
        user.set_password(password)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            return _('Ошибка при записи в базу при создании пароля для пользователя.'), False  

        return _('Поздравляю Вы зарегистрированы!'), True

        pass
    else:
        return _('Ошибка создания пароля для пользователя'), False  
        
def delete_user_phone(current_user_id, number_for_delete, list_phones_user):
    '''
    функция удаляет введенный номер телефона если он есть в БД и если он не последний
    '''
    try:
        number_for_delete = int(number_for_delete)
    except:
        return flash(_(f'Введите номер телефона правильно - только цифры без пробелов.'))
    if UserPhones.query.filter_by(user_id = current_user_id).count() < 2:  
        return flash(_(f'Вы не можете удалить последний зарегистрированный телефон. Сначала зарегистрируйте другой номер.'))  
    elif UserPhones.query.filter_by(user_id = current_user_id).count() < 1:
        return flash(_(f'У Вас нет зарегистрированных телефонов для удаления.'))
    else:
        for num in list_phones_user:             
            if num.number == number_for_delete:     
                try:
                    db.session.delete(num)
                    db.session.commit()
                except:
                    return flash(_(f'Ошибка при внесении изменений базу. Телефон не удален.'))
                return flash(_(f'Вы удалили номер телефона: {number_for_delete}'))          

    return flash(_(f'Такого номера не зарегистрированно.'))
          
def cancel_user_phone(number_for_check, without_delete_user=1, user_str=None):
    '''
    функция предназначена для отмены регистрации нового телефона. 
    Когда выслан код подтверждения на номер абонента и нужно отменить операцию, то эта функция удаляет номер из БД.
    '''
    user = None
    if user_str:
        user = User.query.filter_by(username = user_str).first()

    if number_for_check:
        db.session.delete(number_for_check)
        db.session.commit()
 
    if without_delete_user == 0:
       if user:
            try:
               db.session.delete(user)
               db.session.commit()
            except:
                return flash(_(f'Ошибка при внесении изменений базу. Телефон не удален при отмене регистрации нового телефона.'))

    if without_delete_user == 1:
        return flash(_(f'Вы отменили подтверждение номера телефона.')) 
    else:
        return flash(_(f'Вы отменили регистрацию по номеру телефона.')) 

def step_two_for_enter_phone(number_for_check, code):
    '''
    Функция второго этапа регистрации телефона пользователя.
    Здесь проверяется код с расшифрованным кодом из БД.
    Если коды совпадают, то данный телефон становиться действующим.
    '''
    try:
        int(code)
    except:
        return flash(_(f'Вы не правильно ввели код поддтверждения. Необходимо вводить только цифры.'))
    
    if number_for_check and type(number_for_check) == str:
        number_for_check = UserPhones.query.filter_by(number = number_for_check).first()

    if number_for_check:
        if number_for_check.check_phone_hash_code(code):
            number_for_check.phone_checked = 1
            number_for_check.phone_hash_code = ""
            try:
                db.session.add(number_for_check)
                db.session.commit()
            except:
                return flash(_(f'Ошибка при записи в базу. Номер телефона не внесен в базу')), False
            return flash(_(f'Вы подтвердили номер телефона.')), True
        else:                        
            if number_for_check.trying_to_enter_confirm_code < 1:
                try:
                    db.session.delete(number_for_check)
                    db.session.commit()
                except:
                    print(_(f'Ошибка при записи в базу. Номер телефона не удален при превышении попыток ввода пароля.'))

                return flash(_(f'Вы не правильно ввели код поддтверждения несколько раз. Данный телефон удален из базы. Попробуйте снова зарегистрировать его.')), False
            
            number_for_check.trying_to_enter_confirm_code = number_for_check.trying_to_enter_confirm_code - 1
            try:
                db.session.add(number_for_check)
                db.session.commit()
            except:
                print(_(f'Ошибка при записи в базу. Количество попыток при вводе пароля не уменьшилось.'))
            return flash(_(f'Неверный код подтверждения. Осталось попыток: ') + f'{number_for_check.trying_to_enter_confirm_code}'), False

    return flash(_(f'Нет номера который нужно подтвердить.')), False
    
def step_one_for_enter_phone(number_phone=None, current_user_id=None):
    '''
    Функция регистрации телефона пользователя. 
    На этом шаге телефон вноситься в БД неподтвержденным, 
    а пользователю направляется смс с кодом подтверждения.
    Так же у пользователя отнимается попытка регистрации нового телефона. 
    Если попыток более определенного количества, 
    то ему необходимо связаться с админом для решени данного вопроса
    '''
    try:
        number_phone = int(number_phone)
    except:
        return flash(_(f'Введите номер телефона правильно - только цифры без пробелов.'))

    if not number_phone or not current_user_id:
        return flash(_(f'Отсутствует номер телефона или пользователь для него.'))

    user = User.query.filter_by(id = current_user_id).first()

    if UserPhones.query.filter_by(number = number_phone).count() < 1:
        #если пользватель пытается регистрировать телефон уже 15 раз то отфутболиваем его
        if user.trying_to_enter_new_phone < 1:
            return flash(_('Вы исчерпали количество регистраций новых телефонов. Обратитесь к администрации для возможности новой регистрации.'))
        #если нажали на выслать пароль и телефона нет в базе 
        code = '{:04d}'.format(random.randint(0, 9999))            
        try:
            #sms = SMSC()            
            #sms.send_sms('7'+str(number_phone), f'Код {code} для подтверждения телефона на сайте Nail-Master-Krd.')  

            send_code_sms([{'number': '7'+str(number_phone), 'code': f'{code}'}])

        except:
            flash(_('Ошибка при отправке смс для подтверждения регистрации по телефону'))
        
        new_phone = UserPhones(                   
            number=number_phone,                   
            phone_checked=0,
            phone_hash_code="",
            expire_date_hash=datetime.utcnow() + timedelta(minutes = current_app.config['MINUTES_FOR_CONFIRM_PHONE']),
            black_list = 0,
            user_id=current_user_id,
            )            
        new_phone.set_phone_hash_code(code)      
        
        #уменьшаем количество попыток регистрации нового телефона для пользователя
        user.trying_to_enter_new_phone = user.trying_to_enter_new_phone - 1
        try:
            db.session.add(new_phone)            
            db.session.commit()
        except:
            return flash(_('Ошибка при записи в базу. Попробуйте зарегистрироваться еще раз.'))

        return flash(_('Вам на телефон направлен смс с кодом подтверждения телефона. Введите его в поле подтверждения'))
    else:
        last_time = UserPhones.query.filter_by(number = number_phone).first().expire_date_hash - datetime.utcnow()
        return flash(_(f'Проверьте телефон. Вам был направлен код подтверждения. Повторный запрос можно сделать через | {last_time} | минут '))  
    
def create_new_user_by_phone_registration(number_phone, user_name):
     '''
     Функция создает нового пользователя регистрируемого через телефон, нужны проверки телефона
     '''
     try:
         number_phone = int(number_phone)
     except:
         number_phone = -1
     if len(user_name) == 0:
         return -1     
     if number_phone >= 0:
        type_connection = [t.id for t in ConnectionType.query.all() if str(t.name_of_type).lower() == "телефон"]
        type_connection = 1 if len(type_connection) < 1 else type_connection[0]
        user = User(username=user_name, email=None, email_confirmed=0, role='user', connection_type_id = type_connection, user_from_master = 0)
        #user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            flash(_('Ошибка при записи в базу. При регистрации по телефону пользователь не был внесен в базу.'))
            return -1
        return user.id
     return -1
 
def delete_non_comfirmed_phone():
    '''
    функция проверяет не истек ли срок годности кода подтверждения телефона
    и если истек, то удаляет его из БД
    нужно для работы: db, datetime
    '''
    phones_to_delete = UserPhones.query.filter(UserPhones.phone_checked == 0 and UserPhones.user_from_master == 0).all()
    
    p_to_del = [p.id for p in phones_to_delete \
        if p.expire_date_hash <= datetime.utcnow()]
    
    deleted_objects_phones = UserPhones.__table__.delete().where(UserPhones.id.in_(p_to_del)) 
    try:
        db.session.execute(deleted_objects_phones)
        db.session.commit()
    except:
        print(_('Ошибка при удалении неподтвержденных номеров из базы. Телефоны не удалены'))

def delete_non_comfirmed_email():
    '''
    функция проверяет не истек ли срок годности кода подтверждения телефона
    и если истек, то удаляет его из БД
    нужно для работы: db, datetime
    '''
    for user in User.query.all():
        if user.expire_date_request_confirm_password != main_utils.min_date_for_calculation() \
            and user.expire_date_request_confirm_password <= datetime.utcnow() \
            and user.email_confirmed == 0 \
            and user.user_from_master == 0:
                user.expire_date_request_confirm_password == main_utils.min_date_for_calculation()                
                user.email_confirmed = 0
                user.email = None

        if user.expire_date_request_bufer_mail != main_utils.min_date_for_calculation() \
            and user.expire_date_request_bufer_mail <= datetime.utcnow() \
            and user.email_confirmed == 0:                
                user.bufer_email = None
                user.expire_date_request_bufer_mail = main_utils.min_date_for_calculation()
                
        db.session.add(user)
    try:
        db.session.commit()
    except:
        print(_('Ошибка при сохранении удаления неподтвержденной электронной почты номеров из базы. Почта не удалена'))
    
def delete_user_without_phone_and_confirm_email():
    '''
    функция проверяет есть ли у пользователя подтвержденные телефоны 
    или подтвержденный емайл после истечения некоторого времени с м
    омента внесения его в БД и если нет то удаляетего
    '''
    # Выбираю всех пользователей без подтвержденной почты и если дата подтверждения уже прошла    
    u_out_conf_mail = [u for u in User.query.all() if u.user_from_master == 0 and u.email_confirmed == 0] 
    #во время выборки со сравнением даты и текущего времени нработает неправильно - зеркально
    #здесь вычитаю из юзеров которых нужно удалить тех у кого не истек еще срок подтверждения почты
    u_out_conf_mail = [ user.id for user in u_out_conf_mail if user.registration_date + timedelta(seconds=current_app.config['SECONDS_TO_CONFIRM_EMAIL']) < datetime.utcnow()] #
    #выбрал id user
    print(f'СПИСОК НА УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ: {u_out_conf_mail}')
    #Выбираю все телефоны подтвержденные или с неистекшим сроком годности или подтвержденные
    p_out_conf = [p.user_id for p in UserPhones.query.all() \
        if p.user_id in u_out_conf_mail and p.expire_date_hash != main_utils.min_date_for_calculation() and p.expire_date_hash > datetime.utcnow() \
        or p.user_id in u_out_conf_mail and (p.phone_checked > 0 or p.user_from_master > 0)]
    #выбрал user_id у телефонов
    print(f'СПИСОК ИД ПОЛЬЗОВАТЕЛЕЙ ПОДТВЕРЖДЕННЫХ: {p_out_conf}')
       
    #удаляем юзеров из списка удаления если у него есть действующий телефон
    id_to_del = [user_id for user_id in u_out_conf_mail if not user_id in p_out_conf]
    print(f'СПИСОК ИД ПОЛЬЗОВАТЕЛЕЙ КОТОРЫЕ СЕЙЧАС УДАЛЯЮ: {id_to_del}')
    #удаляю из базы данных юзеров которые остались без подтверждения
    #1)удаляю их телефоны
    #2)удаляю их соцсети
    #3)удаляю самих юзеров
    t_to_del = [p.id for p in UserPhones.query.all() \
        if p.user_id in id_to_del]
    #print(t_to_del)
    s_to_del = [s.id for s in UserInternetAccount.query.all() \
        if s.user_id in id_to_del]
    #print(s_to_del)
    
    post_to_del = [post.id for post in Post.query.all() \
        if post.user_id in id_to_del]

    if len(post_to_del) > 0:
        try:
            deleted_objects_posts = Post.__table__.delete().where(Post.id.in_(post_to_del)) 
            db.session.execute(deleted_objects_posts)
            db.session.commit()
        except:
            print(_('Ошибка при удалении постов из базы при удалении пользователей. Посты не удалены'))
    if len(t_to_del) > 0:
        try:
            deleted_objects_phones = UserPhones.__table__.delete().where(UserPhones.id.in_(t_to_del)) 
            db.session.execute(deleted_objects_phones)
            db.session.commit()
        except:
            print(_('Ошибка при удалении телефонов из базы при удалении пользователей. Телефоны не удалены'))
    if len(s_to_del) > 0:
        try:
            deleted_objects_socials = UserInternetAccount.__table__.delete().where(UserInternetAccount.id.in_(s_to_del))
            db.session.execute(deleted_objects_socials)
            db.session.commit()   
        except:
            print(_('Ошибка при удалении соц.сетей из базы при удалении пользователей. Соц.сети не удалены'))
    if len(id_to_del) > 0:      
        try:
            deleted_objects_user = User.__table__.delete().where(User.id.in_(id_to_del))
            db.session.execute(deleted_objects_user)
            db.session.commit()
        except:
            print(_('Ошибка при удалении пользователя из базы при удалении пользователя. Пользователи не удалены'))
        
def confirm_number(code, phone_number):
        '''
        Функция возвращает правду если хеш сходится
        '''
        phone_to_confirm = UserPhones.query.filter_by(UserPhones.number == phone_number).first()

        return check_password_hash(phone_to_confirm.phone_hash_code, code)


#def add_phone(phone_checked, black_list=0,user_id=2, expire_date_hash = datetime.utcnow(), number=22948567, phone_hash_code=2354):
#    '''
#    функция проверяет не истек ли срок годности кода подтверждения телефона
#    и есл истек, то удаляет его из БД
#    нужно для работы: db, datetime
#    ''' 
#    phone = UserPhones(number=number,
#                       phone_hash_code = phone_hash_code,
#                       phone_checked=phone_checked,
#                       expire_date_hash=expire_date_hash,
#                       black_list = black_list,
#                       user_id=user_id,
#                       )
#
#    db.session.add(phone)
#    db.session.commit()
