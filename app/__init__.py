import os
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand, upgrade
from flask_script import Manager
from flask_cors import CORS
from flask_caching import Cache
import flask_monitoringdashboard as dashboard
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_matomo import *


db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
basedir= os.path.abspath(os.path.dirname(__file__))
cache = Cache(config={'CACHE_TYPE': 'simple'})
dashboard.config.init_from(file=os.path.join(basedir, '../config.cfg'))
limiter = Limiter(key_func=get_remote_address)




def createapp(configname):
    app = Flask(__name__)
    app.config.from_object(config[configname])
    CORS(app)
    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    manager = Manager(app)
    dashboard.bind(app)
    limiter.init_app(app)
  #  matomo = Matomo(app, matomo_url="http://192.168.43.40/matomo",
   #             id_site=1, token_auth="1c3e081497f195c446f8c430236a507b")
    manager.add_command('db', MigrateCommand)
    
    # Cron job for changing log files daily and backing up db

    from .api import api as api_blueprint
    from app import models

    app.register_blueprint(api_blueprint, url_prefix='/api')
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/debug-sentry')
    def trigger_error():
        division_by_zero = 1 / 0

    return app

