from flask import render_template, request, redirect, url_for
from datetime import datetime, timedelta, time, date
from app.master_schedule import bp
from app.decorators.decorators import admin_required
from flask_babel import Babel, _, lazy_gettext as _l
from app.master_schedule.forms import ScheduleTimeToShow, ScheduleMaster
from app.master_schedule.models import DateTable, ScheduleOfDay
from app.master_schedule.utils import take_empty_time_in_shedule

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

            form.date_field_start.data = d_start                    
            form.date_field_start.render_kw={"class" : "shedule-text-field comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : d_start.strftime("%Y-%m-%d")}
           
            form.date_field_end.data = d_end  
            form.date_field_end.render_kw={"class" : "shedule-text-field comment-field", "type": "date", "placeholder" : _('Выберите дату'), "value" : d_end.strftime("%Y-%m-%d")}

            return render_template('master_schedule/schedule_show.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(d_start, d_end), form=form)

    elif request.method == "GET":

        d_start=date.today()
        d_end=date.today()+timedelta(days=7)
        form.date_field_start.data=d_start
        form.date_field_end.data=d_end

    return render_template('master_schedule/schedule_show.html', title=titleVar, list_time_to_show=take_empty_time_in_shedule(d_start, d_end), form=form)
