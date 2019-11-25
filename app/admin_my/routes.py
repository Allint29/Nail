import re
from flask import render_template, url_for, redirect, request, flash
from datetime import datetime, timedelta, date
from app.admin_my import bp
from app import db
from app.decorators.decorators import admin_required
from flask_babel import _
from app.admin_my.forms import *
from app.user.models import User, UserPhones, ConnectionType, UserInternetAccount
from app.my_work.models import *
from app.news.models import *

from app.main_func.utils import parser_time_client_from_str, parser_start_end_date_from_str
from app.main_func import utils as main_utils

from app.admin_my.utils import set_default_password_admin, user_delete_admin, show_preliminary_desk

from app.master_schedule.models import *


@bp.route('/', methods=['GET', 'POST'])
@admin_required
def admin_index():
    '''
    Страница распределения маршрутов админки
    '''
    titleVar='Панель админа'
    form_admin_menu = AdminMenu()

    if form_admin_menu.to_schedule.data:
        #при вызове расписания из пункта меню пользователя передаем никакого клиента в форму
        return redirect(url_for('master_schedule.show_schedule_master', dic_val ={'time_date_id' : -1 , 'client_id' : -1}))

    if form_admin_menu.to_works.data:             
        return redirect(url_for('admin_my.list_my_work'))

    if form_admin_menu.to_news.data:
        return redirect(url_for('admin_my.list_news'))

    if form_admin_menu.to_users.data:        
        return redirect(url_for('admin_my.find_users', dic_val ={'time_date_id' : -1 , 'client_id' : -1}))

    if form_admin_menu.to_desk_preliminary_rec.data:
        return redirect(url_for('admin_my.preliminary_desk'))

    return render_template('admin_my/index.html', title=titleVar, form_admin_menu=form_admin_menu)

@bp.route('/find_users_form_<dic_val>', methods=['GET', 'POST'])
@admin_required
def find_users(dic_val):
    '''
    Вывод страницы редактирования клиентов
    '''
    titleVar='Редактирование клиентов'
    list_edit_users_form = []
    find_form = RouterUserForm()
    users = []
    
    try:
        dic_val = parser_time_client_from_str(dic_val)
    except:
        dic_val = {'time_date_id' : -1, 'client_id' : -1}

    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']    

    if request.method == "POST":
        if find_form.validate_on_submit():
            if find_form.to_find_button.data:
                result = find_form.find_field.data
                users = list(set(User.query.filter(UserPhones.user_id == User.id).filter(UserPhones.number.like(f'%{str(result)}%')).all() + \
                User.query.filter(User.username.like(f'%{result}%')).all() + \
                User.query.filter(User.role.like(f'%{result}%')).all()))
                if find_form.find_field.data == "" or None:
                    users =  User.query.all()
      
    elif request.method == "GET":        
            #отображать всех клиентов
            users =  User.query.all()
            find_form.find_field.data = ""

    for u in users:
        conection_type = ConnectionType.query.filter(ConnectionType.id == u.connection_type_id).first()

        edit_users_form = EditUsersForm()
        list_phones = []
      #  edit_users_form = EditUsersForm(request.POST, obj=u)
        edit_users_form.id_user.data = u.id
        edit_users_form.username_field.data=u.username
        edit_users_form.about_me_field.data =  u.about_me
        edit_users_form.email_field.data = u.email
        edit_users_form.email_confirmed_field.data = "0" if u.email_confirmed == 0 else "1"           
        edit_users_form.registration_date_field.data = u.registration_date if u.registration_date else datetime.utcnow()
        edit_users_form.trying_to_enter_new_phone_field.data = u.trying_to_enter_new_phone
        
        edit_users_form.role_field.data = 'admin' if u.role == 'admin' else 'user'    

        edit_users_form.last_seen_field.data = u.last_seen if u.last_seen else datetime.utcnow()
        edit_users_form.type_connection_field.data = conection_type.name_of_type  if conection_type else None
        
        for p in u.phones:
            
            form_phone = EditPhoneUserForm()
            form_phone.id_phone_field.data = p.id
            form_phone.number_phone.data = p.number
            form_phone.to_black_list.data = p.black_list
            form_phone.phone_confirmed_field.data = p.phone_checked
           # form_phone.date_to_expire_field.data = p.expire_date_hash if p.expire_date_hash else datetime.utcnow()

            list_phones.append(form_phone)

        
        list_edit_users_form.append((edit_users_form, list_phones))           


    return render_template('admin_my/find_users.html', title=titleVar, find_form=find_form, list_edit_users_form=list_edit_users_form, time_date_id=time_date_id, client_id=client_id)

@bp.route('/edit_users_form_<dic_val>', methods=['GET', 'POST'])
@admin_required
def edit_user_form(dic_val):
    '''
    Маршрут создания или редактирования пользователя    
    '''   
    try:
        dic_val = parser_time_client_from_str(dic_val)
    except:
        dic_val = {'time_date_id' : -1, 'client_id' : -1, 'number_phone' : ''}

    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']
    number_ = dic_val['number_phone']

    edit_users_form = EditUsersForm()

    u = User.query.filter_by(id = client_id).first()
    conection_type = ConnectionType.query.filter(ConnectionType.id == u.connection_type_id).first() if u else None
    con_types = ConnectionType.query.all()
    groups_list=[(i.id, i.name_of_type) for i in con_types]

    #данные для вывода которые не завиясят от клиента и должны быть в форме
    edit_users_form.id_user.data = u.id if u else None     
    edit_users_form.type_connection_field.choices  = groups_list #[0,1,4,5]#conection_type.name_of_type if conection_type else 0
    if not u:
        edit_users_form.trying_to_enter_new_phone_field.data = 15
       
    phones = UserPhones.query.filter(UserPhones.user_id==u.id).all() if u else []
    phone_forms = []
    for p in phones:
        phone_form = EditPhoneUserForm()
        phone_form.id_phone_field.data = p.id
        phone_form.number_phone.data = p.number
        phone_form.to_black_list.data = p.black_list
        phone_forms.append(phone_form)
   
    socials = UserInternetAccount.query.filter(UserInternetAccount.user_id == u.id).all() if u else []
    social_forms =[]
    for s in socials:
        soc_form = EditSocialForm()
        soc_form.id_social_field.data = s.id
        soc_form.adress_social.data = s.adress_accaunt
        soc_form.to_black_list.data = s.black_list
        social_forms.append(soc_form) 

    if request.method == "POST":
        if edit_users_form.validate_on_submit():
            user_to_save = u if u else User()
            user_to_save.username = edit_users_form.username_field.data
            user_to_save.about_me = edit_users_form.about_me_field.data            
            user_to_save.email = edit_users_form.email_field.data
            user_to_save.email_confirmed = edit_users_form.email_confirmed_field.data
            print(edit_users_form.registration_date_field.data)
            if edit_users_form.id_user.data == None or edit_users_form.id_user.data =="":
                user_to_save.registration_date =  datetime.utcnow()#edit_users_form.registration_date_field.data
            user_to_save.user_from_master = 1
            user_to_save.trying_to_enter_new_phone = edit_users_form.trying_to_enter_new_phone_field.data
            
            if not user_to_save.password_hash or user_to_save.password_hash == "":
                user_to_save.set_password(set_default_password_admin()[0])

            user_to_save.role = 'admin' if edit_users_form.role_field.data == 'admin' else 'user'
            user_to_save.connection_type_id = edit_users_form.type_connection_field.data
            user_to_save.last_seen = edit_users_form.last_seen_field.data
            try:
                db.session.add(user_to_save)
                db.session.commit()         
                #перенаправляю на форму с созданным клиентом
                flash(_('Изменения в профиле пользователя успешно сохранены.'))
            except:
                flash(_('Ошибка при записи в базу: Изменения в профиле пользователя НЕ сохранены.'))
            return redirect(url_for('admin_my.edit_user_form', dic_val= {'time_date_id' : dic_val['time_date_id'], 'client_id' : user_to_save.id, 'number_phone' : dic_val['number_phone']}))

    elif request.method == "GET":        
        if u:
            edit_users_form.role_field.data = 'admin' if u.role == 'admin' else 'user'
            edit_users_form.email_field.data = u.email   
            edit_users_form.email_confirmed_field.data = '0' if u.email_confirmed == 0 else '1'
            edit_users_form.username_field.data = u.username
            edit_users_form.about_me_field.data =  u.about_me        
            edit_users_form.type_connection_field.data = u.connection_type_id
            edit_users_form.registration_date_field.data = u.registration_date if u.registration_date != None else datetime.utcnow()
            edit_users_form.last_seen_field.data = u.last_seen if u.last_seen !=None else datetime.utcnow()#.strftime('%d/%m/%Y %H:%M')
            edit_users_form.trying_to_enter_new_phone_field.data = u.trying_to_enter_new_phone
        else:
            edit_users_form.role_field.data = 'user'
        
    return render_template('admin_my/edit_user.html', edit_users_form = edit_users_form, phone_forms=phone_forms, social_forms=social_forms, dic_val = dic_val)

@bp.route('/delete_users_form_<dic_val>', methods=['GET', 'POST'])
@admin_required
def delete_user_form(dic_val):
    try:
        dic_val = parser_time_client_from_str(dic_val)
    except:
        dic_val = {'time_date_id' : -1, 'client_id' : -1}
    
    client_id = int(dic_val['client_id'])
    
    u = User.query.filter_by(id = client_id).first()

    if u == None:
        flash=_('Ошибка: Пользователь для удаления отсутствует.')
        return redirect(url_for('admin_my.find_users', dic_val={'time_date_id' : -1, 'client_id' : -1}))

    edit_users_form = EditUsersForm()
    conection_type = ConnectionType.query.filter(ConnectionType.id == u.connection_type_id).first() if u else None
    con_types = ConnectionType.query.all()
    groups_list=[(i.id, i.name_of_type) for i in con_types]

    if request.method == "POST":
        #Для удаления пользователя нужно удалить телефоны, соцсети, индексы юзера в расписании переделать на -1
        user_delete_admin(u.id)
        return redirect(url_for('admin_my.find_users', dic_val ={'time_date_id' : -1 , 'client_id' : -1}))
        
    elif request.method == "GET":
        edit_users_form.id_user.data = u.id
        edit_users_form.type_connection_field.choices = groups_list

        phones = UserPhones.query.filter(UserPhones.user_id==u.id).all() if u else []
        phone_forms = []
        for p in phones:
            phone_form = EditPhoneUserForm()
            phone_form.id_phone_field.data = p.id
            phone_form.number_phone.data = p.number
            phone_form.to_black_list.data = p.black_list
            phone_forms.append(phone_form)
   
        socials = UserInternetAccount.query.filter(UserInternetAccount.user_id == u.id).all() if u else []
        social_forms =[]
        for s in socials:
            soc_form = EditSocialForm()
            soc_form.id_social_field.data = s.id
            soc_form.adress_social.data = s.adress_accaunt
            soc_form.to_black_list.data = s.black_list
            social_forms.append(soc_form) 

        edit_users_form.role_field.data = 'admin' if u.role == 'admin' else 'user'
        edit_users_form.email_field.data = u.email   
        edit_users_form.email_confirmed_field.data = '0' if u.email_confirmed == 0 else '1'
        edit_users_form.username_field.data = u.username
        edit_users_form.about_me_field.data =  u.about_me        
        edit_users_form.type_connection_field.data = u.connection_type_id
        edit_users_form.registration_date_field.data = u.registration_date if u.registration_date != None else datetime.utcnow()
        edit_users_form.last_seen_field.data = u.last_seen if u.last_seen !=None else datetime.utcnow()#.strftime('%d/%m/%Y %H:%M')
        edit_users_form.trying_to_enter_new_phone_field.data = u.trying_to_enter_new_phone
                             
    return render_template('admin_my/delete_user.html', edit_users_form = edit_users_form, phone_forms=phone_forms, social_forms=social_forms, dic_val = dic_val)

#Дейтсвия с телефоном пользователя

@bp.route('/change_phone_<dic_val>_<id_phone>', methods=['GET', 'POST'])
@admin_required
def edit_phone(dic_val, id_phone=-1):
    '''
    Действие сохраняет изменения в телефоне пользователя
    '''    
    try:
        id_phone = int(id_phone)
    except:
        id_phone = -1

    try:
        dic_val = parser_time_client_from_str(dic_val)
    except:
        dic_val = {'time_date_id' : -1, 'client_id' : -1,  'number_phone' : ''}


    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']
    number_ = dic_val['number_phone']

    form = EditPhoneUserForm()
    number_for_edit = UserPhones.query.filter_by(id = id_phone).first()
    user = User.query.filter_by(id=client_id).first()
    
    if form.validate_on_submit():
        if number_for_edit:
            #если номер существует
            number_for_edit.number = form.number_phone.data
            number_for_edit.black_list = 0 if form.to_black_list.data == '0' else 1   
            try:
                db.session.add(number_for_edit)
                db.session.commit();
                flash(_('Номер изменен успешно.'))
            except:
                flash(_('Ошибка при записи в базу: Изменения в телефоне пользователя не сохранены.'))
            return redirect(url_for('admin_my.edit_user_form', dic_val = dic_val))
        else:
            #если не существует            
            if user:                
                #клиент есть - создаем для него новый телефон
                number_for_edit = UserPhones()
                number_for_edit.user_id = user.id
                number_for_edit.number = form.number_phone.data
                number_for_edit.black_list = 0              
                number_for_edit.phone_checked = 1      
                try:
                    db.session.add(number_for_edit)
                    db.session.commit();  
                    flash(_(f'Для пользователя {user.username} добавлен новый номер телефона: {form.number_phone.data}.'))
                except:
                    flash (_('Ошибка при записи в базу: Для пользователя {user.username} не удалось сохранить изменения в телефоне.'))
                return redirect(url_for('admin_my.edit_user_form', dic_val = dic_val))
            else:                
                #нет клиента и нет номера - ошибка
                flash(_('Ошибка: Отсутствует клиент для которого добавляется новый телефон. Вернитесь и вберите клиента.'))
                return redirect(url_for('admin_my.edit_user_form', dic_val = dic_val))

    elif request.method == 'GET':
        #возвращаю данные по телефону
        if number_for_edit:
            #редактирование имеющегося телефона - здесь не нужно знать ид пользователя     
            form.id_phone_field.data=number_for_edit.id
            form.user_id_field.data = number_for_edit.user_id
            form.to_black_list.data = '0' if number_for_edit.black_list == 0 else '1'
            form.number_phone.data = number_for_edit.number 
        else:
            form.id_phone_field.data='-1'
            form.user_id_field.data = client_id if client_id>=0 else '-1'
            form.to_black_list.data = 0
            form.number_phone.data = number_
    return render_template('admin_my/edit_phone.html', form=form, dic_val=dic_val)  

@bp.route('/delete_phone_<dic_val>_<id_phone>', methods=['GET', 'POST'])
@admin_required
def delete_phone(dic_val, id_phone=-1):
    '''
    Действие удаляет телефон перенаправляе на страницу поиска клиента 
    '''    
    try:
        id_phone = int(id_phone)
    except:
        id_phone = -1

    phone_to_del = UserPhones.query.filter_by(id = id_phone).first()
    
    if phone_to_del:
        try:
            db.session.delete(phone_to_del)
            db.session.commit()
            flash(_(f'Телефон {phone_to_del.number} удален успешно'))
        except:
            flash(_('Ошибка при записи в базу: Телефон пользователя удалить не удалось.'))
        return redirect(url_for('admin_my.find_users', dic_val = dic_val))
    else:
        return redirect(url_for('admin_my.edit_phone', dic_val = dic_val, id_phone=id_phone))
    
#Дейтсвия с соцсетью пользователя

@bp.route('/change_socials_<dic_val>_<id_socials>', methods=['GET', 'POST'])
@admin_required
def edit_socials(dic_val, id_socials=-1):
    '''
    Действие сохраняет изменения в соц сети пользователя
    '''    
    try:
        id_socials = int(id_socials)
    except:
        id_socials = -1

    try:
        dic_val = parser_time_client_from_str(dic_val)
    except:
        dic_val = {'time_date_id' : -1, 'client_id' : -1}

    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']

    form = EditSocialForm()
    adress_for_edit = UserInternetAccount.query.filter_by(id = id_socials).first()
    user = User.query.filter_by(id=client_id).first()

    if form.validate_on_submit():
        if adress_for_edit:
            #если аккаунт существует
            adress_for_edit.adress_accaunt = form.adress_social.data
            adress_for_edit.black_list = 0 if form.to_black_list.data == '0' else 1
            try:
                db.session.add(adress_for_edit)
                db.session.commit();
                flash(_('Адрес соц. сети изменен успешно.'))
            except:
                flash(_('Ошибка при записи в базу: Адрес соц. сети НЕ изменен.'))
            return redirect(url_for('admin_my.edit_user_form', dic_val = dic_val))
        else:
            #если не существует            
            if user:                
                #клиент есть - создаем для него новый телефон
                adress_for_edit = UserInternetAccount()
                
                adress_for_edit.user_id = user.id
                adress_for_edit.adress_accaunt = form.adress_social.data
                adress_for_edit.black_list = 0
                try:
                    db.session.add(adress_for_edit)
                    db.session.commit();  
                    flash(_(f'Для пользователя {user.username} внесены изменения в адрес соц.сети: {form.adress_social.data}.'))
                except:
                    flash(_('Ошибка при записи в базу: Адрес соц. сети НЕ изменен.'))                
                return redirect(url_for('admin_my.edit_user_form', dic_val = dic_val))
            else:                
                #нет клиента и нет номера - ошибка
                flash(_('Ошибка: Отсутствует клиент для которого изменяются дпнные соцсети. Вернитесь и вберите клиента.'))
                return redirect(url_for('admin_my.edit_user_form', dic_val = dic_val))

    elif request.method =="GET":
        #возвращаю данные по соц. сети
        if adress_for_edit:
            #редактирование имеющегося телефона - здесь не нужно знать ид пользователя     
            form.id_social_field.data=adress_for_edit.id
            form.user_id_field.data = adress_for_edit.user_id
            form.to_black_list.data = '0' if adress_for_edit.black_list == 0 else '1'
            form.adress_social.data = adress_for_edit.adress_accaunt 
        else:
            form.id_social_field.data='-1'
            form.user_id_field.data = client_id if client_id>=0 else '-1'
            form.to_black_list.data = 0
            form.adress_social.data = ''

    return render_template('admin_my/edit_socials.html', form=form, dic_val=dic_val)

@bp.route('/delete_socials_<dic_val>_<id_socials>', methods=['GET', 'POST'])
@admin_required
def delete_socials(dic_val, id_socials=-1):
    '''
    Действие удаляет телефон перенаправляе на страницу поиска клиента 
    '''    
    try:
        id_socials = int(id_socials)
    except:
        id_socials = -1
            
    socials_to_del = UserInternetAccount.query.filter_by(id = id_socials).first()
    
    if socials_to_del:
        try:
            db.session.delete(socials_to_del)
            db.session.commit()
            flash(_('Профиль социальной сети клиента удален успешно.'))
        except:
            flash(_(f'Ошибка: Удалить соц.сеть {socials_to_del.adress_accaunt} не удалось.'))
            return redirect(url_for('admin_my.edit_socials', dic_val = dic_val, id_socials=id_socials))
        flash(_(f'Удалена соц.сеть {socials_to_del.adress_accaunt}.'))
        return redirect(url_for('admin_my.find_users', dic_val = dic_val))
    else:
        flash(_(f'Ошибка: Не выбрана соц. сеть для удаления.'))
        return redirect(url_for('admin_my.edit_socials', dic_val = dic_val, id_socials=id_socials))


@bp.route('/list_my_work_form', methods=['GET', 'POST'])
@admin_required
def list_my_work():
    '''
    Вывод страницы c работами мастера
    '''
    #dic_date = parser_start_end_date_from_str(dic_date)    
    titleVar='Редактирование отображения работ'
    list_edit_users_form = []
    time_form = MyWorkTimeToShowForm()    
    list_my_works=[]
    list_my_works_and_comments_forms=[]
    list_comment=[]
    users = []
    #start_date = #dic_date['start_date'].date()
    #end_date = #dic_date['end_date'].date()
    start_date =(datetime.utcnow() -timedelta(days=30)).date()
    end_date = datetime.utcnow().date()
                
    if request.method == "POST":         
        if time_form.validate_on_submit():
            
            #print('Проверку прошли')
            start_date = time_form.date_field_start.data
            end_date =time_form.date_field_end.data
            list_my_works = [w for w in MyWork.query.all() if w.published.date() >= start_date and w.published.date() <= end_date]
            for w in list_my_works:
                my_work_form = EditMyWorksForm(id_my_work_field = w.id,
                                               id_site_field = w.id_site,
                                               published_field = w.published.strftime('%d/%m/%Y %H:%M'),
                                               title_field = w.title,
                                               code_field = w.code,
                                               url_field = w.url,
                                               owner_field = w.owner,
                                               likes_field = w.likes,
                                               show_list_field = '0' if w.show == 0 else '1',
                                               source_field = w.source,
                                               content_field = w.content
                                               )
                list_comment = [c for c in CommentsToMyWorks.query.all() if c.media == w.code or c.my_work_id == w.id]
                list_comment_forms = []
                for c in list_comment:
                    coment_form = EditMyWorksCommentsForm(
                        id_my_work_field =c.id,
                        id_site_field = c.id_site,
                        media_field = c.media,
                        owner_field = c.owner,
                        published_field = c.published.strftime('%d/%m/%Y %H:%M'),
                        text_field = c.text,
                        show_list_field = '0' if c.show == 0 else '1',
                        source_field = c.source)
                    list_comment_forms.append(coment_form)
        
                list_my_works_and_comments_forms.append({'my_work_form': my_work_form, 'list_comment_form': list_comment_forms})

    elif request.method == "GET":
        time_form.date_field_start.data=start_date
        time_form.date_field_end.data=end_date
        list_my_works = [w for w in MyWork.query.all() if w.published.date() >= start_date and w.published.date() <= end_date]        
        for w in list_my_works:
            my_work_form = EditMyWorksForm(id_my_work_field = w.id,
                                           id_site_field = w.id_site,
                                           published_field = w.published.strftime('%d/%m/%Y %H:%M'),
                                           title_field = w.title,
                                           code_field = w.code,
                                           url_field = w.url,
                                           owner_field = w.owner,
                                           likes_field = w.likes,
                                           show_list_field = '0' if w.show == 0 else '1',
                                           source_field = w.source,
                                           content_field = w.content
                                           )
            list_comment = [c for c in CommentsToMyWorks.query.all() if c.media == w.code or c.my_work_id == w.id]
            list_comment_forms = []
            for c in list_comment:
                coment_form = EditMyWorksCommentsForm(
                    id_my_work_field =c.id,
                    id_site_field = c.id_site,
                    media_field = c.media,
                    owner_field = c.owner,
                    published_field = c.published.strftime('%d/%m/%Y %H:%M'),
                    text_field = c.text,
                    show_list_field = '0' if c.show == 0 else '1',
                    source_field = c.source)
                list_comment_forms.append(coment_form)

            list_my_works_and_comments_forms.append({'my_work_form': my_work_form, 'list_comment_form': list_comment_forms})
                       
   # dic_date={'start_date': start_date.strftime('%Y-%m-%d_%H-%M'),'end_date': end_date.strftime('%Y-%m-%d_%H-%M')} 
    
    return render_template('admin_my/list_my_work.html', time_form = time_form, list_my_works_and_comments_forms = list_my_works_and_comments_forms) #,  list_my_works=list_my_works, list_comment=list_comment, dic_date=dic_date


@bp.route('/save_my_work', methods=['POST'])
@admin_required
def save_my_work():
    '''
    Действие сохранения изменений в форме работы
    '''
    form = EditMyWorksForm()
    try:
        id = int(form.id_my_work_field.data)        
    except:        
        id = -1

    if form.validate_on_submit():
        if id >=0:        
            work = MyWork.query.filter(MyWork.id == id).first()
            work.title = form.title_field.data
            work.show = 0 if form.show_list_field.data=='0' else 1
            work.content = form.content_field.data
            try:
                db.session.add(work)
                db.session.commit()
                flash(_('Изменения в контенте работы мастера сохранены.'))
            except:
                flash(_('Ошибка при записи в базу: Изменения в контенте работы мастера НЕ сохранены.'))
    else:
        flash(_('Ошибка: Изменения в контенте работы мастера НЕ сохранены.'))

    return redirect(main_utils.get_redirect_target())
    
@bp.route('/edit_comment_to_my_work', methods=['GET', 'POST'])
@admin_required
def edit_comment_to_my_work():
    '''
    Вывод страницы редактирования работы
    '''
    form = EditMyWorksCommentsForm()
    try:
        id = int(form.id_my_work_field.data)        
    except:        
        id = -1

    if form.validate_on_submit():
        if id >=0:        
            comment = CommentsToMyWorks.query.filter(CommentsToMyWorks.id == id).first()
            comment.text = form.text_field.data
            comment.show = 0 if form.show_list_field.data=='0' else 1
            try:
                db.session.add(comment)
                db.session.commit()     
                flash(_('Изменения в контенте комментария к работе мастера сохранены успешно.'))
            except:
                flash(_('Ошибка при записи в базу: Изменения в контенте комментария к работе мастера НЕ сохранены.'))


    return redirect(main_utils.get_redirect_target())

@bp.route('/list_news', methods=['GET', 'POST'])
@admin_required
def list_news():
    '''
    Вывод страницы c новостными лентами с других сайтов
    '''
    titleVar='Редактирование отображения новостей'
    
    time_form = MyWorkTimeToShowForm()    
    start_date =(datetime.utcnow() -timedelta(days=60)).date()
    end_date = datetime.utcnow().date()
    list_news_and_comments_forms = []

    if request.method == "POST":         
        if time_form.validate_on_submit():            
            #print('Проверку прошли')
            start_date = time_form.date_field_start.data
            end_date =time_form.date_field_end.data

            list_news = [n for n in News.query.order_by(News.published.desc()) if n.published.date() >= start_date and n.published.date() <= end_date]        
            for n in list_news:
                news_form = EditNewsForm(id_news_field = n.id,
                                               title_field = n.title,
                                               url_field = n.url,
                                               main_picture_url = n.main_picture_url,
                                               published_field = n.published.strftime('%d/%m/%Y %H:%M'),                                           
                                               source_field = n.source,
                                               show_list_field = '0' if n.show == 0 else '1'
                                               )
                list_comment = [c for c in CommentsToNews.query.order_by(CommentsToNews.created.desc()) if c.news_id == n.id]
                list_comment_forms = []
                for c in list_comment:
                    coment_form = EditNewsCommentsForm(
                        id_my_work_field =c.id,
                        text_field = c.text,
                        published_field = c.created.strftime('%d/%m/%Y %H:%M'),
                        show_list_field = '0' if c.show == 0 else '1'
                        )
                    list_comment_forms.append(coment_form)

                list_news_and_comments_forms.append({'news_form': news_form, 'list_comment_form': list_comment_forms})
                    
           
    elif request.method == "GET":
        time_form.date_field_start.data=start_date
        time_form.date_field_end.data=end_date
        list_news = [n for n in News.query.order_by(News.published.desc()) if n.published.date() >= start_date and n.published.date() <= end_date]        
        for n in list_news:
            news_form = EditNewsForm(id_news_field = n.id,
                                           title_field = n.title,
                                           url_field = n.url,
                                           main_picture_url = n.main_picture_url,
                                           published_field = n.published.strftime('%d/%m/%Y %H:%M'),                                           
                                           source_field = n.source,
                                           show_list_field = '0' if n.show == 0 else '1'
                                           )
            list_comment = [c for c in CommentsToNews.query.order_by(CommentsToNews.created.desc()) if c.news_id == n.id]
            list_comment_forms = []
            for c in list_comment:
                coment_form = EditNewsCommentsForm(
                    id_my_work_field =c.id,
                    text_field = c.text,
                    published_field = c.created.strftime('%d/%m/%Y %H:%M'),
                    show_list_field = '0' if c.show == 0 else '1'
                    )
                list_comment_forms.append(coment_form)

            list_news_and_comments_forms.append({'news_form': news_form, 'list_comment_form': list_comment_forms})
                       
   # dic_date={'start_date': start_date.strftime('%Y-%m-%d_%H-%M'),'end_date': end_date.strftime('%Y-%m-%d_%H-%M')} 
    #print(list_news_and_comments_forms)
    return render_template('admin_my/list_news.html', time_form = time_form, list_news_and_comments_forms = list_news_and_comments_forms) #,  list_my_works=list_my_works, list_comment=list_comment, dic_date=dic_date

@bp.route('/save_news', methods=['POST'])
@admin_required
def save_news():
    '''
    Действие сохранения изменений в форме работы
    '''
    form = EditNewsForm()
    try:
        id = int(form.id_news_field.data)          
    except:        
        id = -1        

    if form.validate_on_submit():        
        if id >=0:        
            news = News.query.filter(News.id == id).first()
            #news.title = form.title_field.data
            news.show = 0 if form.show_list_field.data=='0' else 1
            #news.content = form.content_field.data
            try:
                db.session.add(news)
                db.session.commit()
                flash(_('Изменения в контенте новости сохранены успешно.'))
            except:
                flash(_('Ошибка при записи в базу: Изменения в контенте новости НЕ сохранены.'))
    else:
        flash(_('Ошибка сохранения изменений в контенте новости.'))

    return redirect(main_utils.get_redirect_target())

@bp.route('/edit_comment_to_news', methods=['POST'])
@admin_required
def edit_comment_to_news():
    '''
    Вывод страницы редактирования комментария к новости
    '''
    form = EditNewsCommentsForm()
    try:
        id = int(form.id_my_work_field.data)        
    except:        
        id = -1

    if form.validate_on_submit():
        comment = CommentsToNews.query.filter(CommentsToNews.id == id).first()
        if form.to_save_submit.data:
            if id >=0: 
                comment.text = form.text_field.data
                comment.show = 0 if form.show_list_field.data=='0' else 1
                try:
                    db.session.add(comment)
                    db.session.commit()         
                    flash(_('Изменения к комментарию новости сохранены успешно.'))
                except:
                    flash(_('Ошибка при записи в базу: Изменения к комментарию новости НЕ сохранены.'))
        elif form.to_delete_submit.data:
                try:
                    db.session.delete(comment)
                    db.session.commit()
                    flash(_('Комментарий к новости удален успешно.'))
                except:
                    flash(_('Ошибка при записи в базу: Комментарий к новости НЕ удален.'))
    else:
        flash(_('Ошибка редактирования комментария.'))

    return redirect(main_utils.get_redirect_target())

@bp.route('/preliminary_desk', methods=['GET', 'POST'])
@admin_required
def preliminary_desk():
    '''
    Вывод страницы c заявками на запись к мастеру
    '''
      
    start_date =(datetime.utcnow() - timedelta(days=30))
    end_date = datetime.utcnow() + timedelta(days=60)
    filter_form = FilterForm()
    list_pre_rec =[]
    dic_pre_rec = []

    if request.method == 'POST':
        if filter_form.validate_on_submit():
            start_date = filter_form.date_field_start.data
            end_date = filter_form.date_field_end.data

            list_pre_rec=show_preliminary_desk(start_date, start_date, \
                filter_form.filter_include_date_field.data, \
                filter_form.filter_worked_field.data)
          
    elif request.method == 'GET':
        filter_form.date_field_start.data = start_date.date()
        filter_form.date_field_end.data  = end_date.date()
        filter_form.filter_worked_field.data = 'non_worked'
        filter_form.filter_include_date_field.data = 'non_include'       
    
        list_pre_rec=show_preliminary_desk(start_date.date(), start_date.date(), \
            filter_form.filter_include_date_field.data, \
            filter_form.filter_worked_field.data)

    return render_template('admin_my/preliminary_desk.html', \
        filter_form=filter_form, list_pre_rec=list_pre_rec)

@bp.route('/preliminary_router_<pre_id>', methods=['GET', 'POST'])
@admin_required
def preliminary_router(pre_id):
    '''
    Вывод страницы c заявками на запись к мастеру
    '''
    try:
        pre_id = int(pre_id)
    except:
        flash(_('Ошибка при определении ид предзаписи: Возврат обратно.'))
        return redirect(main_utils.get_redirect_target())

    #определиз запись для обработки
    pre = PreliminaryRecord.query.filter(PreliminaryRecord.id == pre_id).first()

    if pre == None:
        flash(_('Ошибка данной предзаписи нет в базе: Возврат обратно.'))
        return redirect(main_utils.get_redirect_target())

    #определяю нужное время - на всякий случай принудительно привожу данный параметр округляя до часов
    pre_time = datetime(pre.time_to_record.year, pre.time_to_record.month, pre.time_to_record.day, pre.time_to_record.hour, 0)
    date_time = ScheduleOfDay.query.filter(ScheduleOfDay.begin_time_of_day == pre_time).first()
    #ищу зарегистрирован ли телефон и определяю к нему клиента    
    phone = UserPhones.query.filter(UserPhones.number == pre.phone_of_client).first()
    user=None
    if phone:
        user = User.query.filter(User.id == phone.user_id).first()

    if user:
        #если клиент найден, то перенаправляю на время для резервации с ид временем и ид юзера
        flash(_('Вы направлены на страницу расписания - выберите время для записи клиента.'))
        return redirect(url_for('master_schedule.show_schedule_master', dic_val = {'time_date_id' : date_time.id, 'client_id' : user.id}))
        
    else:
        #иначе перенаправляю на создание нового пользователя с ид времени.
        flash(_('Вы направлены на страницу создания нового пользователя - создайте клиента и нажмите "Записать" для записи на это время.'))
        return redirect(url_for('admin_my.edit_user_form', dic_val = {'time_date_id' : date_time.id, 'client_id' : -1, 'number_phone' : pre.phone_of_client}))
        
@bp.route('/preliminary_message_worked_<pre_id>', methods=['GET', 'POST'])
@admin_required
def preliminary_message_worked(pre_id):
    '''
    Вывод страницы c заявками на запись к мастеру
    '''
    try:
        pre_id = int(pre_id)
    except:
        flash(_('Ошибка при определении ид предзаписи в блоке сохранения отработанной заявки на прием: Возврат обратно.'))
        return redirect(main_utils.get_redirect_target())

    #определиз запись для обработки
    pre = PreliminaryRecord.query.filter(PreliminaryRecord.id == pre_id).first()

    if pre == None:
        flash(_('Ошибка данной предзаписи нет в базе: Возврат обратно.'))
        return redirect(main_utils.get_redirect_target())

    pre.message_worked = 1

    try:
        db.session.add(pre)
        db.session.commit()
        flash(_('Предзапись успешно помечена как обработанная.'))
    except:
        flash(_('Ошибка при записи в базу в блоке сохранения предзаписи как обработанной. Возврат обратно.'))

    return redirect(main_utils.get_redirect_target())