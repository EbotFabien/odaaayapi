import os
from flask import Flask, Response
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_script import Manager
from flask_cors import CORS
from flask_caching import Cache
import flask_monitoringdashboard as dashboard
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_matomo import *
from werkzeug.http import HTTP_STATUS_CODES
import werkzeug
#from redis import Redis
import rq
import rq_dashboard
from flask_googletrans import translator
from flask_msearch import Search


db = SQLAlchemy()
search = Search()
mail = Mail()
basedir= os.path.abspath(os.path.dirname(__file__))
cache = Cache(config={'CACHE_TYPE': 'simple'})
dashboard.config.init_from(file=os.path.join(basedir, '../config.cfg'))
limiter = Limiter(key_func=get_remote_address)

SERVER_NAME = 'Google Web Server v0.1.0'

class localFlask(Flask):
    def process_response(self, response):
        #Every response will be processed here first
        response.headers['server'] = SERVER_NAME
        super(localFlask, self).process_response(response)
        return(response)

def createapp(configname):
    app = localFlask(__name__)
    app.config.from_object(config[configname])
    CORS(app)
    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    dashboard.bind(app)
    limiter.init_app(app)
    app.ts = translator(app)
    search.init_app(app)
    #matomo = Matomo(app, matomo_url="http://192.168.43.40/matomo",
    #            id_site=1, token_auth="1c3e081497f195c446f8c430236a507b")
    #app.redis = Redis.from_url(app.config['REDIS_URL'])
    #app.task_queue = rq.Queue('newsapp-tasks', connection=app.redis)
    

    from .api import api as api_blueprint
    from app import models
    #from app.errors.handlers import errors

    
    app.register_blueprint(api_blueprint, url_prefix='/api')
    #app.register_blueprint(rq_dashboard.blueprint, url_prefix='/rq')
    #app.register_blueprint(errors)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/')
    def index():
        return "Hello from News-app"

    @app.route('/debug-sentry')
    def trigger_error():
        division_by_zero = 1 / 0

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return 'bad request!', 400

    @app.errorhandler(werkzeug.exceptions.NotFound)
    def handle_bad_request(e):
        return 'bad request!', 404
        
    @app.errorhandler(werkzeug.exceptions.InternalServerError)
    def handle_bad_request(e):
        return 'Internal server error', 500

    return app


