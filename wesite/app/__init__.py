import os
from flask import Flask, Response
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_cors import CORS
from flask_caching import Cache
from flask_matomo import *
from flask_msearch import Search
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome


db = SQLAlchemy()
search = Search()
fa = FontAwesome()
basedir= os.path.abspath(os.path.dirname(__file__))
bootstrap = Bootstrap()
cache = Cache(config={'CACHE_TYPE': 'simple'})

SERVER_NAME = 'Lirivi Webserver'

class localFlask(Flask):
    def process_response(self, response):
        #Every response will be processed here first
        response.headers['server'] = SERVER_NAME
        super(localFlask, self).process_response(response)
        return(response)

def create_app(configname):
    app = localFlask(__name__)
    app.config.from_object(config[configname])
    CORS(app)
    db.init_app(app)
    cache.init_app(app)
    search.init_app(app)
    bootstrap.init_app(app)
    fa.init_app(app)
    #matomo = Matomo(app, matomo_url="http://192.168.43.40/matomo",
    #            id_site=1, token_auth="1c3e081497f195c446f8c430236a507b")
    

    from app.site.routes import site
    from app import models

    app.register_blueprint(site, url_prefix='/')
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/debug-sentry')
    def trigger_error():
        division_by_zero = 1 / 0

    return app