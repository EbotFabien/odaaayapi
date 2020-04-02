import os
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_cors import CORS
from flask_caching import Cache
import flask_monitoringdashboard as dashboard




db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
basedir= os.path.abspath(os.path.dirname(__file__))
cache = Cache(config={'CACHE_TYPE': 'simple'})
dashboard.config.init_from(file=os.path.join(basedir, '../config.cfg'))


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
    manager.add_command('db', MigrateCommand)
    

    from .api import api as api_blueprint
    from app import models

    app.register_blueprint(api_blueprint, url_prefix='/api')
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    return app
