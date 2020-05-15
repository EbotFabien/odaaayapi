import json
import sys
import time
from flask import render_template
from rq import get_current_job
from app import createapp, db
from app.models import Users, Posts, Task, Postarb, Posten, Postfr, Posthau, Postpor, Postsw, Postes, Language
from app.services.mail import send_email
import os
from tqdm import tqdm


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
        for post in user.posts.order_by(Posts.uploader_date.asc()):
            data.append({'body': post.content,
                         'timestamp': post.uploader_date.isoformat() + 'Z'})
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
    languages = ['en', 'es', 'pt', 'sw', 'ha', 'ar', 'fr']
    language_dict = {'en': Posten, 'es': Postes, 'ar': Postarb, 'pt': Postpor, 'sw': Postsw, 'fr': Postfr, 'ha': Posthau}
    post = Posts.query.get(post_id)
    user = Users.query.get(user_id)
    user_default_lang = 'en'
    try:
        title_translation = app.ts.translate(text=post.title, src=user_default_lang, dest=languages)
        content_translation = app.ts.translate(text=post.content, src=user_default_lang, dest=languages)
        p = 1
        for i in tqdm(languages):
            _set_task_progress(p/len(languages) * 100)
            for j in language_dict:
                if i == j:
                   current_lang = Language.query.filter_by(code=i).first()
                   table = language_dict.get(i)
                   new_row = table(post_id, title_translation[i], content_translation[i], current_lang.id)
                   db.session.add(new_row)
                   db.session.commit()
                   p += 1         
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())

