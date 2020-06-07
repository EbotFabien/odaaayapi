import os
from app import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand, upgrade
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from app.models import Posts, Summary
from apscheduler.schedulers.background import BackgroundScheduler
import atoma, requests, urllib


app = create_app(os.getenv('FLASK_CONFIG') or 'dev')

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
scheduler = BackgroundScheduler()

def cnn_job():
    response = requests.get('https://rss.app/feeds/wBmyARKrtXxgDwXO.xml')
    feed = atoma.parse_rss_bytes(response.content)
    source = 'cnn'
    source_desc = feed.description
    for items in feed.items:
        title = items.title
        pubdate = items.pub_date
        description = items.description
        link = resolve(items.link)
        params = { 
            'title':title, 
            'description':description, 
            'link':link, 
            'pubdate':pubdate, 
            'source':source, 
            'source_desc':source_desc 
        }
        r = requests.post(url="http://localhost:5000/post?", params=params)

def nytimes_job():
    response = requests.get('https://rss.app/feeds/xjzF20dcef1KMUnw.xml')
    feed = atoma.parse_rss_bytes(response.content)
    source = 'ny_times'
    source_desc = feed.description
    for items in feed.items:
        title = items.title
        pubdate = items.pub_date
        description = items.description
        link = resolve(items.link)
        params = { 
            'title':title, 
            'description':description, 
            'link':link, 
            'pubdate':pubdate, 
            'source':source, 
            'source_desc':source_desc 
        }
        r = requests.post(url="http://localhost:5000/post?", params=params)


def resolve(url):
    return urllib.request.urlopen(url).geturl()

def create_db():
    with app.app_context():
        db.create_all()
        db.session.commit()

job = scheduler.add_job(cnn_job, 'interval', minutes=10)
#job1 = scheduler.add_job(nytimes_job, 'interval', minutes=1)

@manager.command
def run():
    create_db()
    scheduler.start()
    sentry_sdk.init(
        dsn="https://8bac745f37514ce3a64a390156f2a5cc@sentry.io/5188770",
        integrations=[FlaskIntegration()]
    )
    app.run(
        threaded=True,
        host=app.config.get('HOST'),
        port=app.config.get('PORT'),
        debug=app.config.get('DEBUG'),
        #ssl_context='adhoc'
    )

if __name__ == "__main__":
    manager.run()
    