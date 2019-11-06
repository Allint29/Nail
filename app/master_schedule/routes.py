from flask import render_template, request, redirect, url_for
from datetime import datetime, timedelta, time, date
from app.master_schedule import bp
from app.decorators.decorators import admin_required
from flask_babel import Babel, _, lazy_gettext as _l
from app.master_schedule.forms import ScheduleTimeToShow, ScheduleMaster, TimeForm,ScheduleTimeToShowMaster
from app.master_schedule.models import DateTable, ScheduleOfDay
from app.master_schedule.utils import take_empty_time_in_shedule, clear_time_shedue, reserve_time_shedue
from app import db


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
        return render_template('master_schedule/index.html', title=titleVar, form=form)

    return render_template('master_schedule/index.html', title=titleVar, form=form)




@bp.route('/show_schedule', methods=['GET', 'POST'])
def show_schedule():
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
                    d_end=d_start
              
            form.date_field_start.render_kw={"class" : "shedule-text-field comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : d_start.strftime("%Y-%m-%d")}
            form.date_field_end.render_kw={"class" : "shedule-text-field comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : d_end.strftime("%Y-%m-%d")}

            return render_template('master_schedule/schedule_show.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(d_start, d_end), form=form)

    elif request.method == "GET":
        d_start=date.today()
        d_end=date.today()+timedelta(days=7)
        form.date_field_start.data=d_start
        form.date_field_end.data=d_end

    return render_template('master_schedule/schedule_show.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(d_start, d_end), form=form)


date_to_show = None
@bp.route('/show_schedule_master', methods=['GET', 'POST'])
def show_schedule_master():
    titleVar = _('Расписание')    
    form=ScheduleTimeToShowMaster()   
    form_time=TimeForm()    
    global date_to_show
    if request.method == 'POST':   
        if form.validate_on_submit():
            if form.submit.data:                
                date_to_show = form.date_field.data      
                print("2 ", date_to_show)
            if not date_to_show:
                date_to_show=datetime.now()
            form.date_field.render_kw={"class" : "shedule-text-field-master comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : date_to_show.strftime("%Y-%m-%d")}          
            
            return render_template('master_schedule/schedule_show_master.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(date_to_show, date_to_show, to_back=1), form=form)
        
        if form_time.validate_on_submit():
            if form_time.reserve_button.data:      
                reserve_time_shedue(form_time.id_time.data)           
            if form_time.delete_button.data: 
                clear_time_shedue(form_time.id_time.data)
            if form_time.change_button.data:                
                return redirect(url_for('master_schedule.show_schedule_master_details', time_to_details_id=form_time.id_time.data))

            if not date_to_show:
                date_to_show=datetime.now()
            form.date_field.data = date_to_show
            form.date_field.render_kw={"class" : "shedule-text-field-master comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : date_to_show.strftime("%Y-%m-%d")}
            return render_template('master_schedule/schedule_show_master.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(date_to_show, date_to_show, to_back=1), form=form)
                
    elif request.method == "GET":    
        if date_to_show == None: 
            date_to_show=date.today()        
        form.date_field.data=date_to_show       

    return render_template('master_schedule/schedule_show_master.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(date_to_show, date_to_show, to_back=1), form=form)


@bp.route('/show_schedule_master_details_<time_to_details_id>', methods=['GET', 'POST'])
def show_schedule_master_details(time_to_details_id):
    '''
    Маршрут к странице детализации расписания мастера на день
    '''
    time_to_details=ScheduleOfDay.query.filter_by(id=time_to_details_id).first()
    form_change=ScheduleMaster()
    form_change.id_time.data=time_to_details.id

    if form_change.cancel_field.data:
        return redirect(url_for('master_schedule.show_schedule_master'))

    if request.method == "POST":
        if form_change.submit.data:
            pass
        if form_change.clear_field:
            #здесь очищаю форму
            clear_time_shedue(time_to_details.id)
            return redirect(url_for('master_schedule.show_schedule_master'))

    if request.method == "GET":
        #TODO сделать поле связанное с типом связи с клиентом
        if time_to_details.work_type.lower() == "маникюр".lower():     
            form_change.work_type_field.data = "man"
        elif time_to_details.work_type.lower() == "педикюр".lower():
            form_change.work_type_field.data = "ped"
        elif time_to_details.work_type.lower() == "ман_пед".lower():
            form_change.work_type_field.data = "man_ped"
        else:
            form_change.work_type_field.data = "some"
            
        if time_to_details.is_empty == 0:
            form_change.time_empty_field.data = "0"
        else:
            form_change.time_empty_field.data = "1"

        if time_to_details.cost <= 0:
            form_change.price_field.data = 0
        elif time_to_details.cost > 0:
            form_change.price_field.data = time_to_details.cost
        else:
            form_change.price_field.data = 0
      
        form_change.client_field.data = time_to_details.name_of_client
        form_change.adress_client_field.data = time_to_details.adress_of_client
        form_change.node_field.data = time_to_details.note
        form_change.client_come.data = time_to_details.client_come_in

    return render_template('master_schedule/index.html', form=form_change)

