# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user
from flask_babel import _, get_locale
from app import db
from app.user import bp
from app.user.forms import LoginForm, RegistrationRequestForm, RegistrationForm, \
     ResetPasswordRequestForm, ResetPasswordForm
from app.user.models import User
from app.user.myemail import send_password_reset_email, send_new_registration_email


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
        if user is None or not user.check_password(form.password.data):
            flash(flash_uncheck)
            return redirect(url_for('user.login'))
        login_user(user, remember=form.remember_me.data)
        flash(flash_check)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('user/login.html', title=titleVar, form=form)


@bp.route('/logout')
def logout():
    '''
    function of logout of user. Make redirect to main.index page
    '''
    logout_user()
    return redirect(url_for('news.index'))


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

    form = RegistrationRequestForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, email_confirmed=0, role='user')
        #user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(flash_check)
        send_new_registration_email(user)
        return redirect(url_for('user.login'))
    return render_template('user/register_request.html', title=titleVar, form=form)


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
    return render_template('user/reset_password_request.html',
                           title=titleVar, form=form)

@bp.route('/register_user/<token>', methods=['GET', 'POST'])
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
        db.session.commit()
        flash(flash_user_register)
        return redirect(url_for('user.login'))
    return render_template('user/register_user.html', title=titleVar, form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
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
        db.session.commit()
        flash(flash_change_pass)
        return redirect(url_for('user.login'))
    return render_template('user/reset_password.html', title=titleVar, form=form)

