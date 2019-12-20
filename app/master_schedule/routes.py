from app import db
from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta, time, date
from app.master_schedule import bp
from app.decorators.decorators import admin_required
from flask_babel import Babel, _, lazy_gettext as _l
from app.master_schedule.forms import ScheduleTimeToShow, ScheduleMaster, TimeForm, ScheduleTimeToShowMaster, PreliminaryForm
from app.user import models as user_models #User, UserPhones, ConnectionType
from app.master_schedule.models import DateTable, ScheduleOfDay, PreliminaryRecord
from app.master_schedule.utils import take_empty_time_in_shedule, clear_time_shedue, reserve_time_shedue, reserve_time_for_client, send_info_message
from app.main_func import utils  as main_utils
from app.master_schedule.myemail import send_preliminary_email


@bp.route("/show_schedule_reserve", methods=['POST'])
@admin_required
def show_schedule_reserve():
    '''
    маршрут сохранения изменений в расписании в части резервирования времени
    '''
    form_time=TimeForm()  
    time_date_id = str(request.form.get('id_time'))
    client_id = str(request.form.get('id_client'))          
    begin_date_id = str(request.form.get('id_date'))
    if form_time.validate_on_submit():
        if form_time.reserve_button.data:
            reserve_time_shedue(request.form.get('id_time'))
        if form_time.delete_button.data:
            clear_time_shedue(request.form.get('id_time'))
        if form_time.change_button.data:
            #здесь изменяем данные времени записи
            return redirect(url_for('master_schedule.show_schedule_master_details', dic_val = {'time_date_id' : time_date_id, 'client_id' : client_id}))
    return redirect(url_for("master_schedule.show_schedule_master", dic_val = {'time_date_id' : time_date_id, 'client_id' : client_id, 'begin_date_id' : begin_date_id}))

@bp.route("/js_show_schedule_reserve", methods=['POST'])
#@admin_required
def js_show_schedule_reserve():
    '''
    маршрут сохранения изменений в расписании в части резервирования времени для js
    '''
    data_ = request.form.get('idElem').split('_')

    try:
        time_date_id = int(data_[2])
    except:
        return jsonify({'text': 'Не удалось получить ид времени', 'result': 'false'})           
    
    time_ = ScheduleOfDay.query.filter(ScheduleOfDay.id == time_date_id).first()
   
    if time_== None:
        return jsonify({'text': 'Не удалось получить время по ид', 'result': 'false'})

    time_emty = ''
    if data_[1] == 'free':
        time_.is_empty = 1
        time_emty = 'free'

    else:
        time_.is_empty = 0
        time_emty = 'reserved'
    try:
        db.session.add(time_)
        db.session.commit()
    except:
        return jsonify({'text': 'Не удалось сохранить изменения в базе данных', 'result': 'false'})

    return jsonify({'text': 'Изменения приняты', 'result': 'true', 'time_id' : str(time_date_id), 'type_empty' : time_emty})


@bp.route('/show_schedule_master_<dic_val>', methods=['GET', 'POST'])
@admin_required
def show_schedule_master(dic_val):
    '''
    Действие представление общего расписания для мастера, где есть элементы управления со временем - детали, освободить, занять 
    dic_val = {'time_date_id': string number, 'client_id': string number, 'number_phone' : string number, 'begin_date_id' : string number, 'end_date_id' : string number}
    
    '''
    try:
        dic_val = main_utils.parser_time_client_from_str(dic_val)
    except:
        dic_val = {'time_date_id' : -1, 'client_id' : -1, 'begin_date_id' : -1}
 
    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']
    begin_date_id = dic_val['begin_date_id']

    date_to_show = DateTable.query.filter(DateTable.id == begin_date_id).first()    
    date_to_show = date.today() if date_to_show == None else date_to_show.day_date.date()
    titleVar = _('Расписание')    
    form=ScheduleTimeToShowMaster()   
    form_time=TimeForm()
   
    if request.method == 'POST':   
        if form.validate_on_submit():
            if form.submit.data:
                date_to_show = form.date_field.data
            if not date_to_show:
                date_to_show=datetime.now()

            list_time_to_show=take_empty_time_in_shedule(date_to_show, date_to_show, to_back=1, id_client = client_id)

            form.date_field.render_kw={"class" : "shedule-text-field-master comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : date_to_show.strftime("%Y-%m-%d")}          
            
            return render_template('master_schedule/schedule_show_master.html', title=titleVar, list_time_to_show=list_time_to_show, form=form)
        
        #if form_time.validate_on_submit():
        #   # if form_time.reserve_button.data:
        #   #     return redirect(url_for('master_schedule.show_schedule_reserve', dic_val = dic_val))
        #        #reserve_time_shedue(form_time.id_time.data)
        #    if form_time.delete_button.data:
        #        clear_time_shedue(form_time.id_time.data)
        #    if form_time.change_button.data:
        #        #здесь изменяем данные времени записи
        #        return redirect(url_for('master_schedule.show_schedule_master_details', dic_val = {'time_date_id' : form_time.id_time.data, 'client_id' : client_id}))
        #
        #    if not date_to_show:
        #        date_to_show=datetime.now()
        #    form.date_field.data = date_to_show
        #    form.date_field.render_kw={"class" : "shedule-text-field-master comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : date_to_show.strftime("%Y-%m-%d")}
        #    return render_template('master_schedule/schedule_show_master.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(date_to_show, date_to_show, to_back=1), form=form)
                
    elif request.method == "GET":
        if date_to_show == None:
            date_to_show=date.today()
        form.date_field.data=date_to_show
        list_time_to_show=take_empty_time_in_shedule(date_to_show, date_to_show, to_back=1, id_client = client_id)

    return render_template('master_schedule/schedule_show_master.html', title=titleVar, list_time_to_show=list_time_to_show, form=form)



@bp.route('/show_schedule_master_details_<dic_val>', methods=['GET', 'POST'])
@admin_required
def show_schedule_master_details(dic_val):
    '''
    Маршрут к странице детализации расписания мастера на день. 
    Здесь вводим информацию о клиенте и работе
    '''
    try:
        dic_val = main_utils.parser_time_client_from_str(dic_val)
    except:
        dic_val = {'time_date_id' : -1, 'client_id' : -1}

    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']
        
    form_change=ScheduleMaster()    

    if form_change.cancel_field.data:
        #раз отменяю выбор времени обнуляю его счетчик, но клиента оставляю
        return redirect(url_for('master_schedule.show_schedule_master', dic_val = {'time_date_id' : -1 , 'client_id' : client_id}))
       
    if request.method == "POST":
        if form_change.validate_on_submit():
            if form_change.submit.data:
                #блок сохранения в расписании,  так же нужно обнулить индексы клиента и расписания
                time_date_id = form_change.id_time.data
                client_id = form_change.client_id_field.data
                print('time_date_id:', time_date_id)
                print('client_id:', client_id)
                #connection_type = ConnectionType.query.filter(ConnectionType.id == u.connection_type_id).first() if u else None
                #connection_type=
                dict_of_form = {
                    'user_id': client_id,
                    'time_date_id' : time_date_id,
                    'work_type' : form_change.work_type_field.data,
                    'cost': form_change.price_field.data,
                    'name_of_client': form_change.client_field.data,
                    'mail_of_client': form_change.email_client_field.data,
                    'phone_of_client': form_change.phone_client_field.data,
                    'adress_of_client': form_change.adress_client_field.data,
                    'note': form_change.node_field.data,
                    'connection_type': form_change.type_connection_field.data,
                    'client_come_in': form_change.client_come.data,
                    'is_empty': form_change.time_empty_field.data,
                    'hours_to_reserve': form_change.reserve_time_for_client_field.data
                    }
                #print('Данные перед передачей в блок записи: _____', dict_of_form)
                if reserve_time_for_client(dict_of_form) == True:
                    #print('отослали сообщение')
                    send_info_message(dict_of_form['time_date_id'])
                return redirect(url_for('master_schedule.show_schedule_master', dic_val=dic_val))
           
            if form_change.clear_field:
                #здесь очищаю форму, ,  так же нужно обнулить индексы клиента и расписания
                clear_time_shedue(time_date_id)
                return redirect(url_for('master_schedule.show_schedule_master', dic_val = {'time_date_id' : -1 , 'client_id' : -1}))

    elif request.method == "GET":
        #TODO сделать поле связанное с типом связи с клиентом\
        time_to_details=ScheduleOfDay.query.filter_by(id=time_date_id).first()
        if time_to_details == None:
            flash(_('Ошибка: Время для записи клиента в расписание не выбрано.'))
            return redirect(url_for('master_schedule.show_schedule_master', dic_val = {'time_date_id' : -1 , 'client_id' : client_id}))
        
        form_change.id_time.data= time_to_details.id #if time_to_details == None else time_to_details.id
        form_change.name_time.data = time_to_details.begin_time_of_day.strftime('%d/%m/%Y %H:%M')
        
        account_user=None
        phone_user=None
        connect_type=None

        user = user_models.User.query.filter_by(id = client_id).first()
        if user:
            account_user = user_models.UserInternetAccount.query.filter(user_models.UserInternetAccount.user_id == client_id).first()
            phone_user = user_models.UserPhones.query.filter(user_models.UserPhones.user_id == client_id).first()
            connect_type = user_models.ConnectionType.query.filter_by(id = user.connection_type_id).first()
                                   
        form_change.client_id_field.data = time_to_details.user_id if user == None else user.id
        form_change.client_field.data = time_to_details.name_of_client if user == None else user.username
        form_change.adress_client_field.data = time_to_details.adress_of_client if account_user == None else account_user.adress_accaunt
        form_change.phone_client_field.data = time_to_details.phone_of_client if phone_user == None else phone_user.number
        form_change.email_client_field.data = time_to_details.mail_of_client if user == None else user.email
        form_change.type_connection_field.data = time_to_details.connection_type if connect_type == None else connect_type.name_of_type

        form_change.work_type_field.data = "man" if time_to_details.work_type.lower() == "маникюр".lower() else \
            "ped" if time_to_details.work_type.lower() == "педикюр".lower() else \
            "man_ped" if time_to_details.work_type.lower() == "ман_пед".lower() else "some"

        form_change.time_empty_field.data = "0" if time_to_details.is_empty == 0 else "1"        
        form_change.price_field.data = 0 if time_to_details.cost <= 0 else time_to_details.cost if time_to_details.cost > 0 else 0       
        form_change.node_field.data = time_to_details.note
        form_change.client_come.data = \
            "0" if time_to_details.client_come_in == 0 else \
            "1" if time_to_details.client_come_in == 1 else \
            "2" if time_to_details.client_come_in == 2 else "0"

    return render_template('master_schedule/shedule_details.html', form=form_change, dic_val ={'time_date_id': time_date_id, 'client_id':client_id} )


@bp.route('/show_schedule', methods=['GET', 'POST'])
def show_schedule():
    '''
    Действие показа страницы расписания для клиента
    '''
    titleVar = _('Расписание')    
    form=ScheduleTimeToShow()

    if request.method == 'POST':
        if form.validate_on_submit():
            d_start=form.date_field_start.data
            d_end=form.date_field_end.data

            if d_start < date.today():
                d_start = date.today()
            else:
                if d_start > d_end:
                    d_end = d_start
              
            form.date_field_start.render_kw={"class" : "shedule-text-field comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : d_start.strftime("%Y-%m-%d")}
            form.date_field_end.render_kw={"class" : "shedule-text-field comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : d_end.strftime("%Y-%m-%d")}

            return render_template('master_schedule/schedule_show.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(d_start, d_end), form=form)

    elif request.method == "GET":
        d_start=date.today()
        d_end=date.today()+timedelta(days=7)
        form.date_field_start.data=d_start
        form.date_field_end.data=d_end

    
    return render_template('master_schedule/schedule_show.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(d_start, d_end), form=form)


@bp.route('/preliminary_record_<dic_val>', methods=['GET', 'POST'])
def preliminary_record(dic_val):
    '''
    Маршрут к странице завок на запись
    '''
    try:
        dic_val = main_utils.parser_time_client_from_str(dic_val)
    except:
        dic_val = {'time_date_id' : -1, 'client_id' : -1}
 
    time_date_id = dic_val['time_date_id']
    client_id = dic_val['client_id']

    if time_date_id < 0:
        flash(_('Ошибка: Не выбрано время для записи.'))
        return redirect(main_utils.get_redirect_target())
    
    client = user_models.User.query.filter(user_models.User.id == client_id).first()    
    date_time = ScheduleOfDay.query.filter(ScheduleOfDay.id == time_date_id).first()

    if date_time == None:
        flash(_('Ошибка: Не выбрано время для записи.'))
        return redirect(main_utils.get_redirect_target())
    form = PreliminaryForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            #запись на доску запросов на запись отсылка письма мастеру
            try:
                date_time = datetime.strptime(form.time_to_record_field.data, '%d-%m-%Y %H:%M')
            except:
                flash(_('Ошибка: Невозможно определить дату.'))
                return redirect(main_utils.get_redirect_target())

            #print(type(date_time))
            pre_record = PreliminaryRecord(name_of_client = form.name_of_client_field.data, 
                                           phone_of_client = form.number_phone.data,
                                           message_of_client = form.message_of_client_field.data,
                                           message_worked = 0,
                                           time_to_record = date_time
                                           )
            to_send = 0
            try:
                db.session.add(pre_record)
                db.session.commit()            
                to_send = 1
                flash(_(f'Заявка на прием к мастеру на время {pre_record.time_to_record} отправлена успешно.'))
            except:
                flash(_('Ошибка записи в базу: Не удалось произвести запись. Повторите попытку позже.'))
            #отсылаем письмо мастеру
            if to_send == 1:
                try:
                    send_preliminary_email(pre_record)
                except:
                    flash(_('Ошибка отправки письма: Не удалось отправить сообщение мастеру. Повторите попытку позже.'))
            return redirect(url_for('welcome.index'))

    elif request.method == 'GET':
        #если ищет время авторизированный пользователь
        if client:
            client_phone = user_models.UserPhones.query.filter(user_models.UserPhones.user_id == client.id).first()
            form = PreliminaryForm(name_of_client_field = client.username, \
                number_phone = client_phone.number if client_phone else '', \
                message_of_client_field='', \
                message_worked_field=0, \
                time_to_record_field = date_time.begin_time_of_day.strftime('%d-%m-%Y %H:%M'))        
        else:
            form = PreliminaryForm(name_of_client_field = '', \
                number_phone = '', \
                message_of_client_field='', \
                message_worked_field=0, \
                time_to_record_field = date_time.begin_time_of_day.strftime('%d-%m-%Y %H:%M')) 


        #print('time_date_id____',time_date_id,'client_id____',client_id)

    return render_template('master_schedule/shedule_preliminary_record.html', form=form, dic_val = dic_val)

@bp.route('/', methods=['GET', 'POST'])
@admin_required
def index():
    titleVar=_('Расписание')
    form=ScheduleMaster()

    if request.method=="POST":
        if form.validate_on_submit():
            pass
        else:
            pass         
    elif request.method=="GET":
        pass
        #return render_template('master_schedule/index.html', title=titleVar, form=form)

    return render_template('master_schedule/index.html', title=titleVar, form=form)
