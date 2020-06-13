from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from flask import Blueprint, render_template, abort, request, url_for
from jinja2 import TemplateNotFound
from app.models import Posts, Summary
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from tqdm import tqdm
from app import db
import json, bs4
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import gettz
from marshmallow import Schema, fields

site = Blueprint('site', __name__, template_folder = 'templates')

LANGUAGE = "english"
SENTENCES_COUNT = 10

class PostSchema(Schema):
    id = fields.Str()
    uuid = fields.Str()
    title = fields.Str()
    description = fields.Str()
    link = fields.Str()
    pubdate = fields.Str()
    source = fields.Str()
    source_desc = fields.Str()
    thumb= fields.Str()
    timestamp = fields.Str()

schema = PostSchema()

@site.route('/', methods=['GET'])
def index():
    if request.args:
        start  = request.args.get('page', None)
        count = request.args.get('count', None)
        posts = Posts.query.order_by(Posts.timestamp.desc()).paginate(int(start), int(count), False)
        next_url = url_for('site.index', start=posts.next_num,  count=int(count)) if posts.has_next else None 
        previous = url_for('site.index', start=posts.prev_num,  count=int(count)) if posts.has_prev else None 
    else:
        posts = Posts.query.order_by(Posts.timestamp.desc()).paginate(1, 10, False)
        next_url = url_for('site.index', start=2,  count=10) if posts.has_next else None
        previous = None  
    return render_template('index.html', posts=posts.items, next_url=next_url, previous_url=previous)

@site.route('/summary/<int:id>', methods=['GET'])
def post_summary(id):
    post_id = id
    arguments = request.args.get('json', None)
    summary = Summary.query.filter_by(post_id=id).first_or_404()
    if arguments:
        return json.dumps({
            'content':summary.content,
            'source':summary.posts.source,
            'data':summary.posts.description,
            'date':str(summary.posts.pubdate),
            'title':summary.posts.title,
            'link':summary.posts.link,
            'description':summary.posts.source_desc
        })
    else:
        posts = Posts.query.order_by(Posts.timestamp.desc()).paginate(1, 10, False)
        next_url = url_for('site.index', start=2,  count=10) if posts.has_next else None
        previous = None  
        return render_template('index.html', posts=posts.items, next_url=next_url, previous_url=previous)


@site.route('/post', methods=['POST'])
def make_post():
    title = request.args.get('title', None)
    description = request.args.get('description', None)
    link = request.args.get('link', None)
    pubdate = parse(request.args.get('pubdate', None))
    source = request.args.get('source', None)
    source_desc = request.args.get('source_desc', None)
    sum_content = ''
    url = link
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        sum_content += '\n'+str(sentence)
    if title is None or description is None or pubdate is None or sum_content is None:
        return {'response': 'error'}, 404
    else:
        ex_post = Posts.query.filter_by(title=title).first()
        if ex_post:
            return {'res':'exist'}, 200
        else:
            soup = bs4.BeautifulSoup(description, "html.parser")
            try:
                thumburl = soup.div.find('img')
            except:
                thumburl=None
                print("No image")
            thumb = soup.div.img['src'] if thumburl else None
            post = Posts(title, description, link, pubdate, source, source_desc, thumb)
            db.session.add(post)
            db.session.commit()
            summary = Summary(sum_content, post.id)
            db.session.add(summary)
            db.session.commit()
    return {'response': 'success'}, 200

@site.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')
    # results = Posts.query.msearch(keyword,fields=['title'],limit=20).filter(...)
    # or
    # results = Posts.query.filter(...).msearch(keyword,fields=['title'],limit=20).filter(...)
    # elasticsearch
    # keyword = "title:book AND content:read"
    # more syntax please visit https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html
    results = Posts.query.msearch(keyword,limit=50).all()
    if results:
        return schema.dumps(results, many=True), 200
    else:
        return {'res':'none'}, 200

@site.route('/notification', methods=['GET'])
def notification():
    results = Posts.query.order_by(Posts.timestamp.desc()).paginate(1, 10, False)
    if results:
        return schema.dumps(results.items, many=True), 200
    else:
        return {'res':'none'}, 200

@site.route('/new', methods=['GET'])
def new():
    if request.args:
        start  = request.args.get('page', None)
        count = request.args.get('count', None)
        posts = Posts.query.order_by(Posts.timestamp.desc()).paginate(int(start), int(count), False)
        next_url = url_for('site.index', start=posts.next_num,  count=int(count)) if posts.has_next else None 
        previous = url_for('site.index', start=posts.prev_num,  count=int(count)) if posts.has_prev else None 
    else:
        posts = Posts.query.order_by(Posts.timestamp.desc()).paginate(1, 10, False)
        next_url = url_for('site.index', start=2,  count=10) if posts.has_next else None
        previous = None  
    return schema.dumps(posts.items, many=True), 200