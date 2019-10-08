import json
import requests
#from app import app_web
from flask import current_app
from flask_babel import _

def translate(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
            not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Ошибка: сервис перевода неправильно сконфигурирован.')
    token = current_app.config['MS_TRANSLATOR_KEY']
    print('!!!!!!!!!!!!!!!!453463!!!!!!!!!')
    url_trans = 'https://translate.yandex.net/api/v1.5/tr.json/translate'

    trans_option = {'key':token, 'lang': f'{source_language}-{dest_language}', 'text': text}
    
    webRequest = requests.get(url_trans, params = trans_option)
    print(webRequest.text)
    if webRequest.status_code != 200:
        return _('Ошибка: сервис перевода неисправен')
    t = json.loads(webRequest.content.decode('utf-8-sig'))
    #t = t[36:(len(t)-3)]
    return t['text']
    