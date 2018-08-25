import json
import requests
from flask import g
from flask_babel import _
from app import app
from app.models import Post


def translate(text, post_id):
    locale = g.locale
    # I guess we need to get sourse language from Post table rather then to store it in javascript as MG suggested
    # And language of current user we also can get here I guess
    source_language = Post.query.get(post_id).language
    print('sl', source_language)
    print('locale', locale)
    print('text', text)
    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        _('Sorry, the translation service isnt\'t available now. Try it later.')
    auth = {'Ocp-Apim-Subscription-Key': app.config['MS_TRANSLATOR_KEY']}
    req = f'https://api.microsofttranslator.com/v2/Ajax.svc/Translate?text={text}&from={source_language}&to={locale}'
    r = requests.get(req, headers=auth)
    if r.status_code != 200:
        return _('Sorry, the translation service isnt\'t available now. Try it later.')
    return json.loads(r.content.decode('utf-8-sig'))