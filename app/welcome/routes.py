# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request, jsonify

from flask_login import current_user, login_user, logout_user
from flask_babel import _, get_locale
from app import db
from app.main_func import utils as main_utils
from app.welcome import bp
from app.user.forms import LoginForm, RegistrationRequestForm, RegistrationByPhoneForm, RegistrationByPhoneConfirmForm, RegistrationMainForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, RegistrationByPhoneNewPasswordForm, ResetPasswordByPhoneRequestForm, ResetPasswordMainForm
from app.user.models import User, UserPhones
from app.user.myemail import send_password_reset_email, send_new_registration_email
from app.user.utils import delete_non_comfirmed_phone, step_one_for_enter_phone, \
                            step_two_for_enter_phone, cancel_user_phone, create_new_user_by_phone_registration, \
                            save_password_by_phone_registration, set_default_password
from app.my_work.models import MyWork
from app.news.models import MasterNews

#нужен для преобразования строки в словарь и обратно
import json

@bp.route('/show_alert', methods=['GET', 'POST'])
def show_alert():
    print('111')
    return "4454"

@bp.route('/load_image', methods=['POST'])
def load_image():
    '''
    Маршрут принимает пост запрос от ajax, сравнивает 
    поступившие данные на предмет возможности загрузки 
    нового фото и если фото нужно загружать, то возвращает 
    данные для генерации нового элемента html - это id, url,
    '''
    try:
        toForvard = int(request.form['toForvard'])
    except:
        print('не удалось преобразовать направление движения. Возвращаю вперед')
        toForvard = 1
    try:
        idImage = int(request.form['idImage'])
    except:
        print('не удалось преобразовать idImage. Возвращаю -1')
        idImage = -1

    if idImage > 0:        
        #если удалось спарсить id последней картинки
        #лист полученный из post запроса
        listImages = request.form['listAllImages'].split(',')       
        listFactImages = request.form['listFactIdImages'].split(',')
        listImages = [i for i in listImages if i not in listFactImages]
        list_int_Images=[]

        for id in listImages:
            try:
                id = int(id)
            except:
                id = -1
            if id >= 0:            
                list_int_Images.append(id)

    list_all_works = MyWork.query.all()
    if len(list_int_Images) > 5:
        if (toForvard == 1):
            list_works_to_show = [{'id': w.id, 'url': w.url} for w in list_all_works if w.id in list_int_Images[-5:]]
        elif (toForvard == 0):
            list_works_to_show = [{'id': w.id, 'url': w.url} for w in list_all_works if w.id in list_int_Images[0:5]]
    else:
         list_works_to_show = [{'id': w.id, 'url': w.url} for w in list_all_works if w.id in list_int_Images]
           
    return jsonify({'listImages': list_works_to_show, 'idImage': request.form['idImage']})


@bp.route('/map')
def welcome_map():
    return render_template("welcome/map.html")

#################################### Авторизация #######################################

@bp.route('/', methods=['GET', 'POST'])
def index():
    form_login = LoginForm()
    #блок добавления фотографий галереи сначала подгружаю только 10 картинок и осылаю ориентиры начала списка и конец
    list_gallary = MyWork.query.filter_by(show=1).order_by(MyWork.published).all()
    list_id_gallary = ','
    list_id_gallary = list_id_gallary.join([str(w.id) for w in list_gallary])
    list_with_z_index = []
    z=100;
    display='none'
    for work in list_gallary[-5:]:
        z=z+1
        if z-100 == len(list_gallary[-5:]):
            display='block'
        list_with_z_index.append({'work': work, 'z' : z, 'display' : display})
    ################################################################################
    
    #блок добавления новостей сайта
    list_news = MasterNews.query.order_by(MasterNews.published.desc())[0:3]
    count_list_news = len(list_news)
    #################################################################################



    return render_template("welcome/index.html", form_login=form_login, \
        list_gallary = list_gallary, list_with_z_index = list_with_z_index, \
        list_news=list_news, count_list_news=count_list_news, \
        list_id_gallary=list_id_gallary)

