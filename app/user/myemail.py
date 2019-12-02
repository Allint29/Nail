from flask import render_template, current_app
from flask_babel import _
from app.main_func.myemail import send_email, send_sms


def send_password_reset_email(user):
    token = user.get_reset_password_token(expires_in=current_app.config['SECONDS_TO_CONFIRM_EMAIL'])    
    send_email(_('[Nail] Ссылка на восстановление пароля'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('myemails/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('myemails/reset_password.html',
                                         user=user, token=token))

def send_mail_reset_email(user, mail):
    token = user.get_new_registration_token(expires_in=current_app.config['SECONDS_TO_CONFIRM_EMAIL'])    
    send_email(_('[Nail] Ссылка на подтверждение Вашей почты'),
               sender=current_app.config['ADMINS'][0],
               recipients=[mail],
               text_body=render_template('myemails/reset_email.txt',
                                         user=user, token=token),
               html_body=render_template('myemails/reset_email.html',
                                         user=user, token=token))

def send_new_registration_email(user):
    token = user.get_new_registration_token(expires_in=current_app.config['SECONDS_TO_CONFIRM_EMAIL'])    
    send_email(_('[Nail] Ссылка на подтверждение регистрации на сайте NailMasterKrd'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('myemails/registration_info.txt',
                                         user=user, token=token),
               html_body=render_template('myemails/registration_info.html',
                                         user=user, token=token))


def send_code_sms(list_message=[]):
    '''
    отправить сообщение смс клиенту, принимает dic_message={'number': '79271101986', 'msg': 'text message for client'}
    '''    
    #f'Код {code} для подтверждения телефона на сайте Nail-Master-Krd.'
    # list_message=[{'number': '7'+str(client_phone.number), 'code': 'code'}]
    if len(list_message) <= 0:
        return
    list_to_send=[]
    for m in list_message:
        number_=m['number']
        msg = f'{m["code"]} - код подтвержд. тел. на сайте nail-master-krd.ru'
        list_to_send.append({'number': str(number_), 'msg': msg})
    #отсылаю список получателей и самих смс в модуль отправки
    send_sms(list_to_send)

def send_default_password_sms(list_message=[], user = ''):
    '''
    отправить сообщение смс клиенту, принимает dic_message={'number': '79271101986', 'msg': 'text message for client'}
    '''    
    #f'Код {code} для подтверждения телефона на сайте Nail-Master-Krd.'
    # list_message=[{'number': '7'+str(client_phone.number), 'code': 'code'}]
    if len(list_message) <= 0:
        return
    list_to_send=[]
    for m in list_message:
        number_=m['number']
        msg = f'Ваш логин: {user}, ваш пароль: {m["code"]}.'
        list_to_send.append({'number': str(number_), 'msg': msg})
    #отсылаю список получателей и самих смс в модуль отправки
    send_sms(list_to_send)


#from flask_mail import Message
#from app import mail
#
#def send_email(subject, sender, recipients, text_body, html_body):
#    msg = Message(subject, sender=sender, recipients=recipients)
#    msg.body = text_body
#    msg.html = html_body
#
#    def send_async_email(msg):
#        with app.app_context():
#            mail.send(msg)
#    
#    send_async_email(msg)
#
#
   # mail.send(msg)
#
#    #tvnhrzmktgdgseac
#    #gzrlmfrgchddrgsr
#from app import app_web
#from config import Config
#import smtplib
#
#gmail_user = current_app.config['MAIL_USERNAME']#"alexeya299@gmail.com"
#print(gmail_user)
#gmail_pwd = "gzrlmfrgchddrgsr"
#TO = current_app.config['ADMINS']#'alexeya29@yandex.ru'
#SUBJECT = "Testing sending using gmail2"
#TEXT = "Testing sending mail using gmail servers"
#server = smtplib.SMTP('smtp.gmail.com', 587)
#server.ehlo()
#server.starttls()
#server.login(gmail_user, gmail_pwd)
#BODY = '\r\n'.join(['To: %s' % TO,
#        'From: %s' % gmail_user,
#        'Subject: %s' % SUBJECT,
#        '', TEXT])
#
#server.sendmail(gmail_user, [TO], BODY)
#print ('email sent')
	

#gmail_user = current_app.config['MAIL_USERNAME'] #"alexeya299@gmail.com"
#gmail_pwd =  "gzrlmfrgchddrgsr"  #"gzrlmfrgchddrgsr"
#TO = current_app.config['ADMINS']#'alexeya29@yandex.ru'
#SUBJECT = "Testing sending using gmail2"
#TEXT = "Testing sending mail using gmail servers"
#server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])#('smtp.gmail.com', 587)
#server.ehlo()
#server.starttls()
#
#server.login(gmail_user, gmail_pwd)
#
#BODY = '\r\n'.join(['To: %s' % TO,
#        'From: %s' % gmail_user,
#        'Subject: %s' % SUBJECT,
#        '', TEXT])
#
#server.sendmail(gmail_user, [TO], BODY)
#print ('email sent')