# -*- coding: utf-8 -*-
import urllib
import urllib.request
import json
import time
from flask import current_app
from config import Config
 
def send_sms(phones, text, total_price=1):
    login = current_app.config['SMSC_LOGIN']      # Логин в smsc
    password = current_app.config['SMSC_PASSWORD']     # Пароль в smsc
    sender = 'Anna'    # Имя отправителя
    # Возможные ошибки
    errors = {
        1: 'Ошибка в параметрах.',
        2: 'Неверный логин или пароль.',
        3: 'Недостаточно средств на счете Клиента.',
        4: 'IP-адрес временно заблокирован из-за частых ошибок в запросах. Подробнее',
        5: 'Неверный формат даты.',
        6: 'Сообщение запрещено (по тексту или по имени отправителя).',
        7: 'Неверный формат номера телефона.',
        8: 'Сообщение на указанный номер не может быть доставлено.',
        9: 'Отправка более одного одинакового запроса на передачу SMS-сообщения либо более пяти одинаковых запросов на получение стоимости сообщения в течение минуты. '
    }
    # Отправка запроса
    url = "http://smsc.ru/sys/send.php?login=%s&psw=%s&phones=%s&mes=%s&cost=%d&sender=%s&fmt=3" % (login, password, phones, text, total_price, sender)
    print(url)
    answer = json.loads(urllib.request.urlopen(url).read())
    if 'error_code' in answer:
        # Возникла ошибка
        return errors[answer['error_code']]
    else:
        if total_price == 1:
            # Не отправлять, узнать только цену
            print ('Будут отправлены: %d SMS, цена рассылки: %s' % (answer['cnt'], answer['cost'].encode('utf-8')))
        else:
            # СМС отправлен, ответ сервера
            return answer
 
#print send_sms("7111111111111", 'Текст сообщения')


## ... допустим, что функция выше уже имеется в нашем скрипте
# 
## Отправляем на 3 номера телефона один и тот же текст. Разделяем номера телефона через ;
#send_sms("7111111111111;722222222222;7333333333333", 'Текст сообщения')
#  
## Рассылка на несколько номеров
#phones = ('711111111', '722222222', '7333333333333')
#text = 'текст для письма!'
#for number in phones:
#    send = send_sms(number, text)
#    if 'cnt' in send:
#        print 'На номер %s, сообщение отправлено успешно!' % number
#        time.sleep(30) # Засыпаем передачу на 30 сек - ограничение...
#    else:
#        print send
#        print 'Ошибка...'