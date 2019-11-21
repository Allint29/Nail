# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request

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

#нужен для преобразования строки в словарь и обратно
import json


#################################### Авторизация #######################################

@bp.route('/', methods=['GET', 'POST'])
def index():
    form_login = LoginForm()
    list_gallary = MyWork.query.filter_by(show=1).order_by(MyWork.published).all()
    list_with_z_index = []
    z=100;
    display='none'
    for work in list_gallary:
        z=z+1
        if z-100 == len(list_gallary):
            display='block'
        list_with_z_index.append({'work': work, 'z' : z, 'display' : display})

    return render_template("welcome/index.html", form_login=form_login, list_gallary = list_gallary, list_with_z_index = list_with_z_index)

@bp.route('/map')
def welcome_map():
    return render_template("welcome/map.html")