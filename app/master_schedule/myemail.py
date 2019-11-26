from flask import render_template, current_app, url_for
from flask_babel import _
from app.main_func.myemail import send_email

def send_preliminary_email(preliminary_rec): 
    sender_ = current_app.config['ADMINS'][0]
    recipient_ = current_app.config['MASTER_MAILS'][1]
    link_ = url_for('master_schedule.show_schedule_master', dic_val = {'time_date_id' : -1, 'client_id' : -1})
    send_email(_('[Nail-Master-Krd] Заявка на запись к мастеру.'),
               sender=sender_,
               recipients=[recipient_],
               text_body=render_template('myemails/preliminary_mail.txt',
                                         preliminary_rec=preliminary_rec, link=link_),
               html_body=render_template('myemails/preliminary_mail.html',
                                         preliminary_rec=preliminary_rec, link=link_))

def send_info_email(email, begin_time_of_day): 
    sender_ = current_app.config['ADMINS'][0]
    recipient_ = email    
    send_email(_('[Nail-Master-Krd] Вы записаны на прием к мастеру ногтевого сервиса.'),
               sender=sender_,
               recipients=[recipient_],
               text_body=render_template('myemails/info_message.txt',
                                         begin_time_of_day=begin_time_of_day),
               html_body=render_template('myemails/info_message.html',
                                         begin_time_of_day=begin_time_of_day))