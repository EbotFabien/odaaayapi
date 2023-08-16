import os
from dotenv import load_dotenv
from datetime import timedelta

basedir= os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:odaaayAdmin@localhost/news"
    #SQLALCHEMY_DATABASE_URI =  "postgresql+psycopg2://postgres:1234@localhost/news" # 'sqlite:///' + os.path.join(basedir, 'news.sqlite')
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    # 'mysql://root:''@localhost/news' \
    # "postgresql+psycopg2://postgres:odaaayAdmin@localhost/news"
    #  postgresql+psycopg2://postgres:1234@localhost/news
    #    or 'sqlite:///' + os.path.join(basedir, 'news.sqlite')
    # 'postgresql://localhost/news'
    # 'postgresql+psycopg2://test:test@db/test'
    COMPRESS_REGISTER= True
    COMPRESS_MIMETYPES = ['application/json']
    CACHE_TYPE = 'simple'
    SQLALCHEMY_TRACK_MODIFICATIONS = True 
    LANGUAGES = ['en', 'fr', 'arb', 'por']
    GOOGLE_ID = "945224984879-lpaj6i3p37432uavn683bbf4m9i0kj0j.apps.googleusercontent.com"
    GOOGLE_SECRET= "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"
    RESTPLUS_VALIDATE = True
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True
    SWAGGER_UI_DOC_EXPANSION = None
    RESTPLUS_MASK_SWAGGER = True
    RESTPLUS_VALIDATE = True
    STRIPE_KEY_PUB = 'pk_test_NFegWC0KCmYbYcdODYzmf7pJ00TGEsHHbh'
    STRIPE_KEY_SEC = 'sk_test_IRUKv5saDJtl2B605DVTYm6I00Si1ogtf5'
    stripe_secret_key= 'sk_test_IRUKv5saDJtl2B605DVTYm6I00Si1ogtf5'
    stripe_publishable_key= 'pk_test_NFegWC0KCmYbYcdODYzmf7pJ00TGEsHHbh'
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    # mail settings 'smtp.googlemail.com' 'smtp.gmail.com'#
    MAIL_SERVER = 'live.smtp.mailtrap.io'
    MAIL_PORT = 587#465
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    # gmail authentication
    MAIL_USERNAME ='admin'#'touchone0001@gmail.com' #'admin@odaaay.com'
    MAIL_PASSWORD ='135e0572f1c4c4c5fcd55e0585731efd'#'jdzgojermumwzmyd'#'onetouch000100''Tas76-fdt88M'
    # mail accounts
    #MAIL_DEFAULT_SENDER ='info@resilion.eu'#'touchone0001@gmail.com' 'admin@odaaay.com'
    UPLOAD_FOLDER = os.getcwd()+'/static'
    UPLOAD_TEMP = os.getcwd()+'/app/app/services/templates'
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
    ADMINS = ['info@resilion.eu']
    TWILIO_ACCOUNT_SID = 'AC34d11121e84d9beaf449f2d85e0aa9e0'
    TWILIO_SERVICE = 'VA9feeac8c10bfb8462fdb156da6b51e76'
    TWILIO_AUTH_TOKEN = 'dc514fbcff751ce60f83237bd902e352'
    #TWILIO_NUMBER = '+19798032477'#'MG6cc4fd3b321ad1b75c7f66f39e4cea06'
    RQ_DASHBOARD_USERNAME = 'rq'
    RQ_DASHBOARD_PASSWORD =  'password'
    RQ_DASHBOARD_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    MSEARCH_INDEX_NAME = 'msearch'
    MSEARCH_BACKEND = 'elasticsearch'
    MSEARCH_PRIMARY_KEY = 'id'
    MSEARCH_ENABLE = True
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
