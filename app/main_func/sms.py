#!/usr/bin/env python
# -*- coding: utf8 -*-
 
""" Автор Титов А.В. t_aleksandr_v@inbox.ru 17.02.2015 """
 
""" Скрипт предназначен для отправки СМС через сайт sms.ru """
#""" Принимает следующие аргументы:"""
# 
#""" -i или --idsender - id пользователя на sms.ru"""
#""" -t или --to - номер телефона получателя в формате 79219996660"""
#""" -s или --subject - текст сообщения на латинице"""
# 
# 
#from urllib2 import urlopen
#from optparse import OptionParser
# 
# 
#def sendsms(idsender,subject,to):
# 
#    subject = subject.replace(" ","+")
#    url="http://sms.ru/sms/send?api_id=%s&text=%s&to=%s" %(idsender,subject,to)
#    res=urlopen(url)
# 
#if __name__ == '__main__':
# 
#    parser = OptionParser()
# 
#    parser.add_option("-i", "--ваш ключ", dest="idsender", default="ваш ключ", help="ID user on sms.ru", metavar="IDSENDER")
#    parser.add_option("-t", "--ваш телефон", dest="to", default="ваш телефон", help="to telephone number", metavar="TO")
#    parser.add_option("-s", "--temperatyra 32", dest="subject", default="Jara tut, otkroy okno", help="Name of subject", metavar="SUBJECT")
# 
#    (options, args) = parser.parse_args()
# 
#    sendsms(options.idsender,options.subject,options.to)