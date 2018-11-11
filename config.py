import os

from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
print(basedir)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # for sending stack trace via email if there are any errors
    MAIL_SERVER = os.environ.get('MAIL_SERVER')  # if not given - disable sending errors via email
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # list of emails that will receive error messages
    ADMINS = ['ololo.rodriguez@gmail.com']
    POSTS_PER_PAGE = 5
    LANGUAGES = ['en', 'ru']
    YNDX_TRANSLATE_KEY = os.environ.get('YNDX_TRANSLATE_KEY')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

