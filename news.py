from faker import Faker
from app.models import Users, Channel, subs, Language, Save, Setting, Message, Comment, \
    Subcomment,  Posts, Postarb, Posten, Postfr, Posthau, Postpor, \
        Postsw, Posttype, Rating, Ratingtype
from app import db, createapp
import random

app = createapp('dev')
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

def recreate_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()

def seed():
    with app.app_context():
        fake = Faker()
        for i in range(100):
            passwd = fake.ean8()
            user = fake.user_name()
            db.session.add(Users(username=user, email=fake.email(), password_hash=passwd, number=fake.zipcode_plus4()))
            db.session.commit()
        for v in range(1):
            db.session.add(Posttype(content='text'))
            db.session.commit()
        for j in range(40):
            db.session.add(Channel(name=fake.company(), description=fake.paragraph(),profile_pic=fake.image_url(), background=fake.image_url(), user=random.randint(1,100), css=''))
            db.session.commit()
        for x in range(100):
            db.session.add(Posts(uploader=Users.query.filter_by(id=random.randint(1,100)).first().id, title=fake.sentence(), channel=random.randint(1,40), posttype=1, content=fake.text(), uploader_id=random.randint(1,100)))
            db.session.commit()
        for y in range(200):
            db.session.add(Comment(language=1, user=random.randint(1,100), post=random.randint(1,100), content=fake.paragraph(), comment_type='text'))
            db.session.commit()


if __name__ == "__main__":
    print(name)
    recreate_db()
    seed()
    app.run(
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG'),
        #ssl_context='adhoc'
    )
