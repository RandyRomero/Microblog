import json
import requests
from flask import g
from flask_babel import _
from app import app
from app.models import Post


def translate(text, post_id):

    # I guess we need to get sourse language from Post table rather then to store it in javascript as MG suggested
    source_language = Post.query.get(post_id).language
    curr_user_lang = g.locale

    # Prepare languages string for a request as Yandex Translator API says it should look.
    # It can detect source language if it is not denoted.
    lang_request = f'{source_language}-{curr_user_lang}' if source_language else curr_user_lang

    not_available_msg = _('Sorry, the translation service isnt\'t available now. Try it later.')

    if 'YNDX_TRANSLATOR_KEY' not in app.config or not app.config['YNDX_TRANSLATOR_KEY']:
        return not_available_msg
    api_key = app.config['YNDX_TRANSLATOR_KEY']
    req = f'https://translate.yandex.net/api/v1.5/tr.json/translate?key={api_key}&text={text}&lang={lang_request}'
    r = requests.get(req)
    response = r.json()

    # Errors by yandex translator api
    if r.status_code != 200:
        error_code = response['code']
        print('Error code:', error_code)
        if error_code == 401:
            print('Error 401, invalid Yandex Translator API key')
        elif error_code == 402:
            print('Error 402, blocked Yandex Translator API key')
        elif error_code == 403:
            print('Error 403, exceeded the daily limit on the amount of translated text')
            return _('Service is unavailable today. Please, try it tomorrow.')
        elif error_code == 413:
            print('Error 413, exceeded the maximum text size')
            return _('Text is too long to be translated, sorry.')
        elif error_code == 422:
            print('Error 422, the text cannot be translated')
            return _('Sorry, the text cannot be translated.')
        elif error_code == 501:
            print('Error 501, the specified translation direction is not supported.')
            return _('Sorry, service doesn\'t support translation between these two languages.')
        else:
            print('Unknown error by Yandex Translator API.')
        return not_available_msg

    #TODO add other error messages

    return response['text'][0]