import json
import sys
import time
from flask import render_template
from rq import get_current_job
from app import createapp, db
from app.models import Users, Posts, Task
from app.services.mail import send_email
import os


app = createapp(os.getenv('FLASK_CONFIG') or 'dev')
app.app_context().push()

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        user = Users.query.get(task.user_id)
        user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()


def export_posts(user_id):
    try:
        user = Users.query.get(user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = user.posts.count()
        for post in user.posts.order_by(Posts.timestamp.asc()):
            data.append({'body': post.body,
                         'timestamp': post.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i )

        send_email('News app your posts',
                sender=app.config['ADMINS'][0], recipients=[user.email],
                text_body=render_template('mail/export_posts.txt', user=user),
                html_body=render_template('mail/export_posts.html',
                                          user=user),
                attachments=[('posts.json', 'application/json',
                              json.dumps({'posts': data}, indent=4))],
                sync=True)
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())

def translate_posts(post_id, user_id):
    languages = ['es']
    post = Posts.query.get(post_id)
    user = Users.query.get(user_id)
    try:
        translation = app.ts.translate(text=post.content, src='en', dest=languages)
        for i in range(10):
            time.sleep(1)
            _set_task_progress(100 * i)
        print(translation)
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())