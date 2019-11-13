import re
from flask import render_template, url_for, redirect, request, flash
from datetime import datetime
from app.admin_my import bp
from app import db
from app.decorators.decorators import admin_required
from flask_babel import _
from app.admin_my.forms import AdminMenu, EditUsersForm,  RouterUserForm, EditPhoneUserForm, EditSocialForm
from app.user.models import User, UserPhones, ConnectionType, UserInternetAccount

from app.main_func.utils import parser_time_client_from_str
from app.main_func import utils as main_utils

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

    if form_admin_menu.to_users.data:        
        return redirect(url_for('admin_my.find_users', dic_val ={'time_date_id' : -1 , 'client_id' : -1}))

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

    dic_val = parser_time_client_from_str(dic_val)    
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
    dic_val = parser_time_client_from_str(dic_val)
    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']

    edit_users_form = EditUsersForm()

    u = User.query.filter_by(id = client_id).first()
    conection_type = ConnectionType.query.filter(ConnectionType.id == u.connection_type_id).first() if u else None
    con_types = ConnectionType.query.all()
    groups_list=[(i.id, i.name_of_type) for i in con_types]

    edit_users_form.id_user.data = u.id if u else None
    edit_users_form.username_field.data = u.username if u else None
    edit_users_form.about_me_field.data =  u.about_me if u else None
    edit_users_form.email_field.data = u.email if u else None
    edit_users_form.email_confirmed_field.data = '0' if u and u.email_confirmed == 0 else '1' if u and u.email_confirmed == 1 else '0'         
    edit_users_form.registration_date_field.data = u.registration_date if u and u.registration_date else datetime.utcnow()
    edit_users_form.trying_to_enter_new_phone_field.data = u.trying_to_enter_new_phone if u else '15'
    
    edit_users_form.role_field.data = 'admin' if u and u.role == 'admin' else 'user' if u and u.role == 'user' else 'user'     
    
    edit_users_form.last_seen_field.data = u.last_seen if u and u.last_seen else datetime.utcnow()

    edit_users_form.type_connection_field.choices  = groups_list #[0,1,4,5]#conection_type.name_of_type if conection_type else 0
    edit_users_form.type_connection_field.data = u.connection_type_id if u else 0

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
       # if edit_users_form.validate_on_submit():
       #     pass

        return render_template('admin_my/edit_user.html', edit_users_form = edit_users_form, phone_forms=None, social_forms=None, dic_val = dic_val)

    elif request.method == "GET":
        pass 

    return render_template('admin_my/edit_user.html', edit_users_form = edit_users_form, phone_forms=phone_forms, social_forms=social_forms, dic_val = dic_val)

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

    dic_val = parser_time_client_from_str(dic_val)
    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']

    form = EditPhoneUserForm()
    number_for_edit = UserPhones.query.filter_by(id = id_phone).first()
    user = User.query.filter_by(id=client_id).first()
    
    if form.validate_on_submit():
        if number_for_edit:
            #если номер существует
            number_for_edit.number = form.number_phone.data
            number_for_edit.black_list = 0 if form.to_black_list.data == '0' else 1            
            db.session.add(number_for_edit)
            db.session.commit();
            flash(_('Номер изменен.'))
        else:
            #если не существует            
            if user:                
                #клиент есть - создаем для него новый телефон
                number_for_edit = UserPhones()
                number_for_edit.user_id = user.id
                number_for_edit.number = form.number_phone.data
                number_for_edit.black_list = 0              
                number_for_edit.phone_checked = 1                
                db.session.add(number_for_edit)
                db.session.commit();  
                flash(_(f'Для пользователя {user.username} добавлен новый номер телефона: {form.number_phone.data}.'))
            else:                
                #нет клиента и нет номера - ошибка
                flash(_('Ошибка: Отсутствует клиент для которого добавляется новый телефон. Вернитесь и вберите клиента.'))

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
            form.number_phone.data = ''


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
        db.session.delete(phone_to_del)
        db.session.commit()
        return redirect(url_for('admin_my.find_users', dic_val = dic_val))
    else:
        return redirect(url_for('admin_my.edit_phone', dic_val = dic_val, id_phone=id_phone))
    
#Дейтсвия с соцсетью пользователя

@bp.route('/change_socials_<dic_val>_<id_socials>', methods=['GET', 'POST'])
@admin_required
def edit_socials(dic_val, id_socials=-1):
    '''
    Действие сохраняет изменения в телефоне пользователя
    '''    
    try:
        id_socials = int(id_socials)
    except:
        id_socials = -1

    dic_val = parser_time_client_from_str(dic_val)
    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']

    form = EditSocialForm()
    adress_for_edit = UserInternetAccount.query.filter_by(id = id_socials).first()
    user = User.query.filter_by(id=client_id).first()

    if form.validate_on_submit():
        if adress_for_edit:
            #если номер существует
            adress_for_edit.adress_accaunt = form.adress_social.data
            adress_for_edit.black_list = 0 if form.to_black_list.data == '0' else 1            
            db.session.add(adress_for_edit)
            db.session.commit();
            flash(_('Адрес соцю сети изменен.'))
        else:
            #если не существует            
            if user:                
                #клиент есть - создаем для него новый телефон
                adress_for_edit = UserInternetAccount()
                
                adress_for_edit.user_id = user.id
                adress_for_edit.adress_accaunt = form.adress_social.data
                adress_for_edit.black_list = 0

                print('adress_for_edit.user_id:' , adress_for_edit.user_id, \
                    'adress_for_edit.adress_accaunt: ' , adress_for_edit.adress_accaunt, \
                    'adress_for_edit.black_list: ', adress_for_edit.black_list)
                db.session.add(adress_for_edit)
                db.session.commit();  
                flash(_(f'Для пользователя {user.username} внесены изменения в адрес соц.сети: {form.adress_social.data}.'))
            else:                
                #нет клиента и нет номера - ошибка
                flash(_('Ошибка: Отсутствует клиент для которого изменяются дпнные соцсети. Вернитесь и вберите клиента.'))

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
        except:
            flash(_(f'Ошибка: Удалить соц.сеть {socials_to_del.adress_accaunt} не удалось.'))
            return redirect(url_for('admin_my.edit_socials', dic_val = dic_val, id_socials=id_socials))
        flash(_(f'Удалена соц.сеть {socials_to_del.adress_accaunt}.'))
        return redirect(url_for('admin_my.find_users', dic_val = dic_val))
    else:
        flash(_(f'Ошибка: Не выбрана соц. сеть для удаления.'))
        return redirect(url_for('admin_my.edit_socials', dic_val = dic_val, id_socials=id_socials))