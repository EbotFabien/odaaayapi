import os
from dotenv import load_dotenv
from datetime import timedelta

basedir= os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/news'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    #'mysql://root:''@localhost/news' \
    #    or 'sqlite:///' + os.path.join(basedir, 'news.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['en', 'fr', 'arb', 'por']
    RESTPLUS_VALIDATE = True
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True
    SWAGGER_UI_DOC_EXPANSION = None
    RESTPLUS_MASK_SWAGGER = True
    RESTPLUS_VALIDATE = True
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    # mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    # gmail authentication
    MAIL_USERNAME = 'das.sanctity.ds@gmail.com'
    MAIL_PASSWORD = ''
    # mail accounts
    MAIL_DEFAULT_SENDER = 'das.sanctity.ds@gmail.com'
    UPLOAD_FOLDER = os.getcwd()+'/alluploads'
    UPLOAD_FOLDER_MEDIA = os.getcwd()+'/app/static/files'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    CACHE_TYPE: "simple" # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT: 300
    PAGINATE_PAGE_SIZE = 4
    PAGINATE_PAGE_PARAM = "pagenumber"
    PAGINATE_SIZE_PARAM = "pagesize"
    PAGINATE_RESOURCE_LINKS_ENABLED = True

class Development(Config):
    DEBUG = True
    HOST = '127.0.0.1'
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
