import os
from dotenv import load_dotenv
from datetime import timedelta

basedir= os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:odaaayAdmin@localhost/news"
    SQLALCHEMY_DATABASE_URI =  "postgresql+psycopg2://postgres:1234@localhost/news" # 'sqlite:///' + os.path.join(basedir, 'news.sqlite')
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    # 'mysql://root:''@localhost/news' \
    # "postgresql+psycopg2://postgres:odaaayAdmin@localhost/news"
    #  postgresql+psycopg2://postgres:1234@localhost/news
    #    or 'sqlite:///' + os.path.join(basedir, 'news.sqlite')
    # 'postgresql://localhost/news'
    # 'postgresql+psycopg2://test:test@db/test'
    SQLALCHEMY_TRACK_MODIFICATIONS = True 
    LANGUAGES = ['en', 'fr', 'arb', 'por']
    RESTPLUS_VALIDATE = True
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True
    SWAGGER_UI_DOC_EXPANSION = None
    RESTPLUS_MASK_SWAGGER = True
    RESTPLUS_VALIDATE = True
    STRIPE_KEY_PUB = 'pk_test_NFegWC0KCmYbYcdODYzmf7pJ00TGEsHHbh'
    STRIPE_KEY_SEC = 'sk_test_IRUKv5saDJtl2B605DVTYm6I00Si1ogtf5'
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    # mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    # gmail authentication
    MAIL_USERNAME = 'touchone0001@gmail.com'
    MAIL_PASSWORD = 'onetouch000100'
    # mail accounts
    MAIL_DEFAULT_SENDER = 'touchone0001@gmail.com'
    UPLOAD_FOLDER = os.getcwd()+'/static'
    UPLOAD_FOLDER_MEDIA = os.getcwd()+'/app/static/files'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    CACHE_TYPE= "simple" # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT= 300
    PAGINATE_PAGE_SIZE = 4
    PAGINATE_PAGE_PARAM = "pagenumber"
    PAGINATE_SIZE_PARAM = "pagesize"
    PAGINATE_RESOURCE_LINKS_ENABLED = True
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    RQ_DASHBOARD_USERNAME='rqadmin'
    RQ_DASHBOARD_PASSWORD='adminnews'
    QUEUES = ['default']
    ADMINS = ['touchone0001@gmail.com']
    TWILIO_ACCOUNT_SID = 'ACfa2f374c7f24b74c6849fe081fdd9e26'
    TWILIO_AUTH_TOKEN = 'c7fbb80be7f81d96e0b6882e2614a9be'
    TWILIO_NUMBER = '+19798032477'#'MG6cc4fd3b321ad1b75c7f66f39e4cea06'
    RQ_DASHBOARD_USERNAME = 'rq'
    RQ_DASHBOARD_PASSWORD =  'password'
    RQ_DASHBOARD_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    MSEARCH_INDEX_NAME = 'msearch'
    MSEARCH_BACKEND = 'elasticsearch'
    MSEARCH_PRIMARY_KEY = 'id'
    MSEARCH_ENABLE = False
    ELASTICSEARCH = {"hosts": ["127.0.0.1:9200"]}

class Development(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 8000

class Production(Config):
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 80


config = {
    'dev': Development,
    'prod': Production,
    'default': Development
}
