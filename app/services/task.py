from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import json
import sys
import time
from flask import render_template
from rq import get_current_job
from app.models import Users, Posts, Task,Translated, Language,Postsummary
from app.services.mail import send_email
import os
from tqdm import tqdm
from googletrans import Translator
from flask import current_app as app
from app import db, cache, logging ,createapp
from sqlalchemy import or_, and_, distinct, func
#from rake_nltk import Rake
#from multi_rake import Rake


app = createapp(os.getenv('FLASK_CONFIG') or 'dev')
app.app_context().push()


translator = Translator()

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        user = Users.query.get(task.user_id)
        #user.add_prog_notification('task_progress', {'task_id': job.get_id(), 'progress': progress})
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
            data.append({'body': post.content,'timestamp': post.uploader_date.isoformat() + 'Z'})
            i += 1
            _set_task_progress(100 * i )

        send_email('News app your posts',
                sender=app.config['ADMINS'][0], recipients=[user.email],
                text_body=render_template('mail/export_posts.txt', user=user),
                html_body=render_template('mail/export_posts.html', user=user),
                attachments=[('posts.json', 'application/json', json.dumps({'posts': data}, indent=4))],
                sync=True)
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())

def translate_posts(post_id, user_id):
    languages = ['en', 'es', 'pt', 'sw', 'ha', 'ar', 'fr']
    post = Posts.query.get(post_id)
    if post:
        user = Users.query.get(user_id)
        post_auto_lang = translator.detect(post.title)
    user_default_lang = str(post_auto_lang.lang)
    post_language = Language.query.filter_by(code=user_default_lang).first()
    sum_content = ''
    # tag collector
   # rake = Rake()

    if post.post_url is None:
        parser = HtmlParser.from_string(post.text_content, '', Tokenizer(post_language.name))
        stemmer = Stemmer(post_language.name)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(post_language.name)

        for sentence in summarizer(parser.document, 4):
            sum_content += '\n'+str(sentence)
        if sum_content == '':
            sum_content = post.text_content
    try:
        for j in languages:
            if j == user_default_lang:
                current_lang = Language.query.filter_by(code=user_default_lang).first()
                #table = language_dict.get(user_default_lang)
                #keywords = rake.apply(sum_content)
                if post is not None:
                    new_row = Translated(post_id=post_id,title=post.title,content=sum_content,language_id=current_lang.id, tags=str('dddd'))#[x[0] for x in keywords[:5]]))
                    db.session.add(new_row)
                    db.session.commit()
        title_translation = app.ts.translate(text=post.title, src=user_default_lang, dest=languages)
        content_translation = app.ts.translate(text=sum_content, src=user_default_lang, dest=languages)
        p = 1
        for i in tqdm(languages):
            # _set_task_progress(p/len(languages) * 100)
            for j in languages:
                if i == j and i != user_default_lang:
                   current_lang = Language.query.filter_by(code=i).first()
                   # table = language_dict.get(i)
                   #keywords = rake.apply(content_translation[i])
                   new_check =Translated.query.filter(and_(Translated.title==title_translation[i],Translated.language_id==current_lang.id)).first()
                   if new_check is None:
                        new_row = Translated(post_id=post_id,title=title_translation[i],content=content_translation[i],language_id=current_lang.id, tags=str('ddddddd'))#[x[0] for x in keywords[:5]]))
                        db.session.add(new_row)
                        db.session.commit()
                        p += 1         
    except:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())


def summarize_posts(post_id, user_id):
    #languages = ['en', 'es', 'pt', 'sw', 'ha', 'ar', 'fr']
    post = Posts.query.get(post_id)
    user = Users.query.get(user_id)
    post_auto_lang = translator.detect(post.title)
    user_default_lang = str(post_auto_lang.lang)
    post_language = Language.query.filter_by(code=user_default_lang).first()
    sum_content = ''

    if post.post_url is None:
        try:
            parser = HtmlParser.from_string(post.text_content, '', Tokenizer(post_language.name))
            stemmer = Stemmer(post_language.name)
            summarizer = Summarizer(stemmer)
            summarizer.stop_words = get_stop_words(post_language.name)

            for sentence in summarizer(parser.document, 4):
                sum_content += '\n'+str(sentence)
            if sum_content == '':
                sum_content = post.text_content
            new_check =Translated.query.filter(and_(Translated.title==post.title,Translated.language_id==post_language.id)).first()
            if new_check is None:
                new_row = Translated(post_id=post_id,title=post.title,content=sum_content,language_id=post_language.id, tags=str('dddd'))
                db.session.add(new_row)
                db.session.commit()
        except:
            _set_task_progress(100)
            app.logger.error('Unhandled exception', exc_info=sys.exc_info())

    