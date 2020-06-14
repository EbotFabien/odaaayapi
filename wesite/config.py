import os
from dotenv import load_dotenv
from datetime import timedelta

basedir= os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-site'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'website.sqlite')
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True 
    LANGUAGES = ['en', 'fr', 'arb', 'por']
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    CACHE_TYPE: "simple" # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT: 300
    MSEARCH_INDEX_NAME = 'msearch'
    MSEARCH_BACKEND = 'elasticsearch'
    MSEARCH_PRIMARY_KEY = 'id'
    MSEARCH_ENABLE = False
    ELASTICSEARCH = {"hosts": ["127.0.0.1:9200"]}

class Development(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000

class Production(Config):
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 80


config = {
    'dev': Development,
    'prod': Production,
    'default': Development
}
