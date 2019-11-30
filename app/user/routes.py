# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user
from flask_babel import _, get_locale
from app import db
from app.main_func import utils as main_utils
from app.user import bp
from app.user.forms import LoginForm, RegistrationRequestForm, RegistrationByPhoneForm, RegistrationByPhoneConfirmForm, RegistrationMainForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, RegistrationByPhoneNewPasswordForm, ResetPasswordByPhoneRequestForm, ResetPasswordMainForm
from app.user.models import *
from app.user.myemail import send_password_reset_email, send_new_registration_email
from app.user.utils import delete_non_comfirmed_phone, step_one_for_enter_phone, \
                            step_two_for_enter_phone, cancel_user_phone, create_new_user_by_phone_registration, \
                            save_password_by_phone_registration, set_default_password

#нужен для преобразования строки в словарь и обратно
import json


#################################### Авторизация #######################################


@bp.route('/login', methods=['GET', 'POST'])
def login():
    '''
    func of login user chech authentificated user, pass and empty textbox, and check remember checkbox
    '''
    titleVar=_('Авторизация')
    flash_uncheck=_('Неправильный логин или пароль!')
    flash_check=_('Вы вошли на сайт')
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data) or user.password_hash is None or user.password_hash == "":
            #print("Неправильный логин или пароль")
            flash(flash_uncheck)
            return redirect(url_for('user.login'))
        login_user(user, remember=form.remember_me.data)
        flash(flash_check)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            #print("Нет некста")
            next_page = url_for('main.index')
        return redirect(next_page)
        #print("Загрузил страницу")
    return render_template('user/login.html', title=titleVar, form_login=form)

@bp.route('/logout')
def logout():
    '''
    function of logout of user. Make redirect to main.index page
    '''
    logout_user()
    return redirect(url_for('news.index'))

##########################################################################################################

#################################### Регистрация - главная форма #######################################
@bp.route('/register_main', methods=['GET', 'POST'])
def registration_main():
    form = RegistrationMainForm()
    title = _('Выбор способа регистрации на сайте')
    if form.submit_register_by_email.data:            
        return redirect(url_for('user.register_request'))
    if form.submit_register_by_phone.data:            
        return redirect(url_for('user.registration_by_phone_send'))

    return render_template('user/register_main.html', form=form, title=title)

##########################################################################################################

#################################### Регистрация по телефону #######################################

@bp.route('/register_by_phone_send', methods=['GET', 'POST'])
def registration_by_phone_send():
    '''
    Маршрут отсылает смс с кодом подтвержения на телефон к юзеру и перенаправляет на страницу подтверждения телефона
    '''
    form = RegistrationByPhoneForm()
    title = _('Регистрация по телефонному номеру')
    number = form.number_phone.data
    user = form.username_for_phone.data
    
    if form.validate_on_submit():
        user_id = create_new_user_by_phone_registration(number,user)
        step_one_for_enter_phone(number, user_id)        
        return redirect(url_for('user.registration_by_phone_confirm', data={'number': number, 'user':user}))

    elif request.method == 'GET':
        delete_non_comfirmed_phone()          
        form.username_for_phone.data = user
        form.number_phone.data = number

    return render_template('user/registration_by_phone/register_by_phone.html', form=form, title=title)

@bp.route('/register_by_phone_confirm_<data>', methods=['GET', 'POST'])
def registration_by_phone_confirm(data):
    form = RegistrationByPhoneConfirmForm()
    title = _('Регистрация по телефонному номеру')        
    code = form.code_of_confirm.data
        
    parametri=data.replace("'", '"')
    # dict to str
    #str_json = json.dumps({'my_key': 'my value'})
    # str to dict
    #'{"number": "9271101986", "user": "Allint27"}'
    data = json.loads(parametri)
    user = data['user'] #data[0]['user']    
    number = data['number'] #data[0]['number']

    
    if form.validate_on_submit():
        if form.confirm_registration.data:
            step_two_for_enter_phone(number, code)
            #здесь нужно перенаправление на создание пароля
            return redirect(url_for('user.registration_by_phone_new_password', data={'number': number, 'user':user}))

        if form.phone_button_cancel.data:
            #удаляем номер из БД  
            user_for_del = User.query.filter_by(username = user).first()         
            number_for_check = UserPhones.query.filter_by(user_id = user_for_del.id).first()
            cancel_user_phone(number_for_check, without_delete_user=0, user_str=user) 
            return redirect(url_for('user.login'))


    elif request.method == 'GET':
        delete_non_comfirmed_phone()          
        form.code_of_confirm.data = ""
        #form.number_phone.data = number

    return render_template('user/registration_by_phone/register_by_phone_confirm.html', form=form, title=title, number=number, user=user)

@bp.route('/register_by_phone_new_password_<data>', methods=['GET', 'POST'])
def registration_by_phone_new_password(data):
    form = RegistrationByPhoneNewPasswordForm()
    title = _('Регистрация по телефонному номеру')
    flash_check=_('Поздравляем, Вы зарегистрированы! Теперь Вы можете авторизироваться')
    
    parametri=data.replace("'", '"')
    # dict to str
    #str_json = json.dumps({'my_key': 'my value'})
    # str to dict
    #'{"number": "9271101986", "user": "Allint27"}'
    data = json.loads(parametri)
    user = data['user'] #data[0]['user']    
    number = data['number'] #data[0]['number']
    password = form.password.data
    password2 = form.password2.data
    if form.validate_on_submit():
       if form.confirm_registration.data:           
           msg = save_password_by_phone_registration(user, password, password2)
           flash(msg[0])
           return redirect(url_for('user.login', data={'number': number, 'user':user}))
       else:
           msg = set_default_password(user, number)
           flash(msg[0])
           return redirect(url_for('user.login'))
           

    return render_template('user/registration_by_phone/register_by_phone_new_password.html', form=form, title=title, number=number, user=user)

##########################################################################################################

#################################### Регистрация по электронной почте #######################################


@bp.route('/register_request', methods=['GET', 'POST'])
def register_request():
    '''
    func of register new users in system. Check curent user authentificated, validation of Registered form
    '''
    titleVar = _('Регистрация пользователя. Шаг 1')
    flash_check=_('Поздравляем, Вы зарегистрированы! Чтобы зайти в Ваш профиль пройдите по ссылке в письме, которое было направлено на указанный Вами адрес.')
    flash_uncheck=_('Пользователь с таким логином уже зарегистрирован.')
   
    if current_user.is_authenticated:        
        return redirect(url_for('main.index'))        

    form_mail = RegistrationRequestForm()

    if form_mail.validate_on_submit():      
        type_connection = [t.id for t in ConnectionType.query.all() if str(t.name_of_type).lower() == "почта"]
        type_connection = 1 if len(type_connection) < 1 else type_connection[0]
        user = User(username=form_mail.username.data, email=form_mail.email.data, email_confirmed=0, role='user', connection_type_id = type_connection, user_from_master = 0)
        #user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash(flash_check)
        except:
            flash(_('Ошибка при сохранении в базу при регистрации по электронной почте.'))
        send_new_registration_email(user)
        return redirect(url_for('user.login'))
    return render_template('user/registration_by_email/register_request.html', title=titleVar, form_mail=form_mail)

@bp.route('/register_user_<token>', methods=['GET', 'POST'])
def register_user(token):
    '''
    view of finish of registration new user, create new pass and redirect to login
    '''
    titleVar=_('Регистрация. Шаг 2')
    flash_user_register=_('Поздравляю, Вы зарегистрированы на сайте!')
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_new_registration_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = RegistrationForm()    
    if form.validate_on_submit():        
        user.set_password(form.password.data)        
        user.set_confirm_email_true()
        user.expire_date_request_confirm_password = main_utils.min_date_for_calculation()
        try:
            db.session.add(user)
            db.session.commit()
            flash(flash_user_register)
        except:
            flash(_('Ошибка при записи в базу на этапе окончания регистрации по почте.'))
        return redirect(url_for('user.login'))
    return render_template('user/registration_by_email/register_user.html', title=titleVar, form=form)

##########################################################################################################

##########################################################################################################

######################################  Восстановление пароля главная   ###################################

@bp.route('/reset_password_main', methods=['GET', 'POST'])
def reset_password_main():
    form = ResetPasswordMainForm()
    title = _('Восстановления пароля')
    if form.submit_reset_by_email.data:            
        return redirect(url_for('user.reset_password_request'))
    if form.submit_reset_by_phone.data:            
        return redirect(url_for('user.reset_password_by_phone_request'))

    return render_template('user/reset_password/reset_password_main.html', form=form, title=title)



##########################################################################################################

#################################### Восстановление паролья по телефону #######################################

@bp.route('/reset_password_by_phone_request', methods=['GET', 'POST'])
def reset_password_by_phone_request():
    '''
    Функция высылает на указанный телефон если он есть в БД кастомный пароль
    '''
    titleVar = _('Восстановление пароля')
    flash_check=_('Вам на телефон выслан пароль для входа на сайт.')
    flash_uncheck=_('Ваш телефон не зарегистрирован на сайте. Пройдите регистрацию')
   
    if current_user.is_authenticated:        
        return redirect(url_for('main.index'))        

    form = ResetPasswordByPhoneRequestForm()
    if form.validate_on_submit():
        phone = UserPhones.query.filter_by(number = form.number_phone.data).first()
        user = User.query.filter_by(id=phone.user_id).first()
        set_default_password(user, phone.number)
        flash(flash_check)
        return redirect(url_for('user.login'))
    return render_template('user/reset_password/reset_password_by_phone_request.html', title=titleVar, form=form)

##########################################################################################################


#################################### Восстановление пароля по электронной почте #######################################

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    '''
    view of form to request of link for reset password
    '''
    titleVar=_('Смена пароля')
    flash_to_mail=_('Перейдите по ссылке на почте, для смены пароля.')
    flash_email_not_find=_('Нет пользователей зарегистрированных с данной почтой. Пройдите регистрацию.')
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:            
            send_password_reset_email(user)
            flash(flash_to_mail)
        else:
            flash(flash_email_not_find)
        return redirect(url_for('user.login'))
    return render_template('user/reset_password/reset_password_by_email_request.html',
                           title=titleVar, form=form)

@bp.route('/reset_password_<token>', methods=['GET', 'POST'])
def reset_password(token):
    '''
    view of reset password form after confirm of link from email
    '''
    titleVar=_('Смена пароля')
    flash_change_pass=_('Ваш пароль изменен.')
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        #if email not confirm with first registration it make it confirm
        user.set_confirm_email_true()
        try:
            db.session.add(user)
            db.session.commit()
            flash(flash_change_pass)
        except:
            flash(_('Ошибка при записи в базу на этапе восстановления пароля по почте.'))
        return redirect(url_for('user.login'))
    return render_template('user/reset_password/reset_password_by_email.html', title=titleVar, form=form)

##########################################################################################################
