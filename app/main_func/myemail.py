from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail
from app.main_func.smsc_api import SMSC

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_async_sms(app, phone, msg):       
    with app.app_context():
        sms = SMSC()
        #sms.send_sms("79271101986,79200217222", 'Test message')
        sms.send_sms(str(phone), str(msg))

def send_sms(list_message=[]):
    '''
    Функция отправляет очередь смс по пользователям , словарь пользователя и сообщение для него 
    dic_message={'number': '79271101986', 'msg': 'text message for client'}    
    '''
    print('send_sms:', list_message)
    for m in list_message:
        Thread(target=send_async_sms, args=(current_app._get_current_object(), m['number'], m['msg'])).start()

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