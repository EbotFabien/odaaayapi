from faker import Faker
from app.models import Users, Language, Save, Setting, \
    Posts, Translated, Posttype, Rating, Ratingtype, Category
from app import db, createapp
import random
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand, upgrade
import unittest
import os
#from app.services import mail
from flask import current_app
#import ssl
import uuid


#context = ssl.SSLContext()
#context.load_cert_chain('odaaay.crt', 'odaaay.key')


app = createapp(os.getenv('FLASK_CONFIG') or 'dev')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
name = '''(API) ~ By Leslie Etubo T, E. Fabien'''



@manager.command
def logo():
    print(name)


@manager.command
def recreate_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
        print('db')


@manager.command
def languages():
    print('lang')
    with app.app_context():
        language_dict = {'en': "english", 'es': "espagnol", 'ar': "arab",
                         'pt': "portugese", 'sw': "swahili", 'fr': "french", 'ha': "hausa"}
        for i in language_dict:
            lan = Language(lang_type="N", code=i, name=language_dict[i])
            db.session.add(lan)
            db.session.commit()
        lan1 = Posttype(content="Text")
        lan2 = Posttype(content="Video")
        db.session.add(lan1)
        db.session.add(lan2)
        db.session.commit()

@manager.command
def users():
    print('users')
    with app.app_context():
        users_dict = {'one@odaaay.co': "The Herald", 'two@odaaay.co': "West African News", 'three@odaaay.co': "Media Online",
                         'four@odaaay.co': "le Momehein", 'five@odaaay.co': "Zoom"}
        for i in users_dict:
            lang = 'en'
            language= Language.query.filter_by(code=lang).first()
            new = Users(users_dict[i], str(uuid.uuid4()), True, i)
            db.session.add(new)
            new.passwordhash('5kM11kk')
            new.language_id=language.id
            new.special=True
            new.verified_email=True
            new.verified_phone=True
            db.session.commit()

@manager.command
def category():
    print("cat")
    with app.app_context():
        language_dict = ['Sport', 'Technology', 'Science', 'Gaming', 'Entertainment',
                         'Politics and News', 'Education', 'Animals & Pets', 'Autos & Vehicules',
                          'Films & Animations','Music','Finance','People','Religion','dating']
        for i in language_dict:
            lan = Category(name=i)
            db.session.add(lan)
            db.session.commit()


@manager.command
def run():
    #logo()
    # Error tracking and logging with sentry
    
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
        # ssl_context=context
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
    recreate_db()
    languages()
    category()
    users()
    manager.run()
    
    

    # run()


loc="/work/www/cmd/Flask_app/project/app/static/appointment_comments.xls"
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)

sheet.cell_value(0,0)
for i in range(0,4805):
    name=sheet.row_values(i+1)
    json={
        'rdv':int(name[1]),
        'comment':name[3],
        'user':int(name[2]),
    }
    user=json['user']
    #check=requests.get("http://195.15.218.172/manager_app/user/"+str(user), headers={"Authorization":request.headers["Authorization"]})
    #if #check.json()['id']:
    rdv=json['rdv']
    comme=json['comment']
    commen=comment(user_id=user,rdv_id=rdv,contenu=comme)
    db.session.add(commen)
    db.session.commit()