from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_debugtoolbar import DebugToolbarExtension
from flask_script import Manager
from flask_cors import CORS
from flask_caching import Cache
from flask_marshmallow import Marshmallow



db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
cache = Cache(config={'CACHE_TYPE': 'simple'})
ma = Marshmallow()


def createapp(configname):
    app = Flask(__name__)
    app.config.from_object(config[configname])
    CORS(app)
    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    manager = Manager(app)
    #toolbar = DebugToolbarExtension(app)
    manager.add_command('db', MigrateCommand)

    from .api import api as api_blueprint
    from app import models

    app.register_blueprint(api_blueprint, url_prefix='/api')
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    return app
