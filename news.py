from faker import Faker
from app.models import Users, Channels, subs, Language, Save, Setting, Message, Comment, \
    Posts, Postarb, Posten, Postfr, Posthau, Postpor, Postsw, Posttype, Rating, Ratingtype
from app import db, createapp
import random
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask_migrate import upgrade
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand, upgrade
import unittest
import os
from app.services.task import app

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
name = '''
                                   (api)
 ███▄    █ ▓█████  █     █░  ██████ 
 ██ ▀█   █ ▓█   ▀ ▓█░ █ ░█░▒██    ▒ 
▓██  ▀█ ██▒▒███   ▒█░ █ ░█ ░ ▓██▄   
▓██▒  ▐▌██▒▒▓█  ▄ ░█░ █ ░█   ▒   ██▒
▒██░   ▓██░░▒████▒░░██▒██▓ ▒██████▒▒
░ ▒░   ▒ ▒ ░░ ▒░ ░░ ▓░▒ ▒  ▒ ▒▓▒ ▒ ░
░ ░░   ░ ▒░ ░ ░  ░  ▒ ░ ░  ░ ░▒  ░ ░
   ░   ░ ░    ░     ░   ░  ░  ░  ░  
         ░    ░  ░    ░          ░  
 ~ By Leslie Etubo T, E. Fabien, Samuel Klein, Marc.

'''

@manager.command
def logo():
    print(name)

def recreate_db():
    with app.app_context():
        #db.drop_all()
        db.create_all()
        db.session.commit()

def seed():
    with app.app_context():
        fake = Faker()
        db.session.add(Users(username='test', number='123456', user_visibility=True))
        db.session.commit()
        for i in range(10):
            passwd = fake.ean8()
            user = fake.user_name()
            db.session.add(Users(username=user, number=fake.zipcode_plus4(), user_visibility=True))
            db.session.commit()
        for v in range(1):
            db.session.add(Posttype(content='text'))
            db.session.commit()
        for j in range(10):
            db.session.add(Channels(name=fake.company(), description=fake.paragraph(),profile_pic=fake.image_url(), background=fake.image_url(), user=random.randint(1,10), css=''))
            db.session.commit()
        for x in range(80):
            db.session.add(Posts(uploader=Users.query.filter_by(id=random.randint(1,10)).first().id, title=fake.sentence(), channel=random.randint(1,10), posttype=1, content=fake.text(), uploader_id=random.randint(1,10), url=fake.domain_word()))
            db.session.commit()
        for y in range(150):
            db.session.add(Comment(language=1, user=random.randint(1,10), post=random.randint(1,80), content=fake.paragraph(), comment_type='text' , public=True))
            db.session.commit()


@manager.command
def run():
    logo()
    recreate_db()
    seed()
    # Error tracking and logging with sentry
    sentry_sdk.init(
        dsn="https://8bac745f37514ce3a64a390156f2a5cc@sentry.io/5188770",
        integrations=[FlaskIntegration()]
    )

    # Initializing log
    # file_handler = RotatingFileHandler('app/logs/'+str(datetime.utcnow())+'-news-app.log', 'a', 1 * 1024 * 1024, 10)
    # file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    # file_handler.setLevel(logging.INFO)
    # app.logger.addHandler(file_handler)
    app.run(
        threaded=True,
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG'),
        # ssl_context='adhoc'
    )


@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/tests', pattern='*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == "__main__":
    manager.run()
