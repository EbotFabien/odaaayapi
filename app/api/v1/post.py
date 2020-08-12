from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from flask_restplus import Namespace, Resource, fields, marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps
from flask import abort, request, session,Blueprint
from flask import current_app as app
import numpy as np
from app.models import Users, Channels, subs, Posts, Language, Postarb, Posten, Postes, Postfr, \
    Posthau, Postpor, Postsw
from app import db, cache, logging
import json
from tqdm import tqdm
from werkzeug.datastructures import FileStorage

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'API-KEY'
    }
}

# The token decorator to protect my routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'API-KEY' in request.headers:
            token = request.headers['API-KEY']
            try:
                data = jwt.decode(token, app.config.get('SECRET_KEY'))
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

api = Blueprint('api',__name__, template_folder='../templates')
post1=Api( app=api, doc='/docs',version='1.4',title='News API.',\
description='', authorizations=authorizations)
#from app.api import schema
CORS(api, resources={r"/api/*": {"origins": "*"}})

uploader = post1.parser()
uploader.add_argument('file', location='files', type=FileStorage, required=False, help="You must parse a file")
uploader.add_argument('name', location='form', type=str, required=False, help="Name cannot be blank")

post = post1.namespace('/api/post', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
        To get this authorization, please contact out I.T Team ', \
    path='/v1/')

postcreationdata = post.model('postcreationdata', {
    'title': fields.String(required=True),
    'channel': fields.List(fields.String(required=True)),
    'type': fields.Integer(required=True),
    'post_url': fields.String(required=False, default=None),
    'thumb': fields.String(required=False, default=None),
    'content': fields.String(required=True)
})

Updatedata = post.model('Updatedata',{
    'id':  fields.String(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True)
})

deletedata =post.model('deletedata',{
    'id':fields.String(required=True)
})
    
postdata = post.model('postreturndata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'channel_id': fields.Integer(required=True),
    'post_url': fields.String(required=True),
    'uploader': fields.String(required=True),
    'content': fields.String(required=True),
    'uploader_date': fields.DateTime(required=True)
})

langpostdata = post.model('langpostreturndata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True),
})

multiplepost = post.model('',{
    "start": fields.Integer(required=True),
    "limit": fields.Integer(required=True),
    "count": fields.Integer(required=True),
    "next": fields.String(required=True),
    "previous": fields.String(required=True),
    "results": fields.List(fields.Nested(postdata))
})


postreq = post.model('postreq', {
    'arg': fields.String(required=True),
    'all': fields.Boolean(required=True),
    'channel': fields.Integer(required=True),
    'arg_type': fields.String(required=True),
})
Article_verify = post.model('postreq',{
    "Link":fields.String(required=True)
})


@post.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
            },
    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })
@post.route('/post')

class Post(Resource):
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', '') 
            # Still to fix the next and previous WRT Sqlalchemy
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count+"&lang="+lang
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count+"&lang="+lang
            language_dict = {'en': Posten, 'es': Postes, 'ar': Postarb, 'pt': Postpor, 'sw': Postsw, 'fr': Postfr, 'ha': Posthau}
            if lang:
                for i in tqdm(language_dict):
                    if i == lang:
                        table = language_dict.get(i)
                        results = table.query.paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(results, langpostdata)
                }, 200
            else:
                posts = Posts.query.order_by(Posts.uploader_date.desc()).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(posts, postdata)
                }, 200
        else:
            posts = Posts.query.order_by(Posts.uploader_date.desc()).all()
            return marshal(posts, postdata), 200

    @token_required
    @post.expect(Updatedata)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post_id=Posts.query.get(req_data['id'])
        if req_data['content'] is None:
            return {'res':'fail'}, 404
        elif user and post_id:
            post_id.title= req_data['title']
            post_id.content=req_data['content']
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404
        
    @token_required
    @post.expect(deletedata)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post_id=Posts.query.get(req_data['id'])
        if user and post_id:
            db.session.delete(post_id)
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404
    
    @token_required
    @post.expect(Updatedata)
    def patch(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post_id=Posts.query.get(req_data['id'])
        if user and post_id:
            post_id.title= req_data['title']
            post_id.content=req_data['content']
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404
    
    @post.expect(postcreationdata)
    @token_required
    def post(self):
        req_data = request.get_json()
        args = uploader.parse_args()
        title=req_data['title']
        content=req_data['content']
        channel_names = req_data['channel']
        ptype=1
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        channel_list = []
        for i in channel_names:
            name = Channels.query.filter_by(name=i).first()
            if name in user.get_channels():
                channel_list.append(name)
        if ptype == 1:
            newPost = Posts(user.id, title, ptype, content, '1', user.id)
            db.session.add(newPost)
            db.session.commit()
            newPost.launch_translation_task('translate_posts', user.id, 'Translating  post ...')
            for c in channel_list:
                c.add_post(newPost)
                db.session.commit()
            return {
                'status': 1,
                'res': 'Post was made'
            }, 200
        if ptype == 4:
            thumb_url=req_data['thumb'] or None
            post_url=req_data['post_url'] or None
            newPost = Posts(user.id, title, ptype, content, '1', user.id,)
            db.session.add(newPost)
            db.session.commit()
            newPost.launch_translation_task('translate_posts', user.id, 'Translating  post ...')
            for c in channel_list:
                c.add_post(newPost)
                db.session.commit()
            return {
                'status': 1,
                'res': 'Post was made'
            }, 200
        else:
            return {
                'status': 0,
                'res': i+' does not exist or you are not subscribed to it'
            }, 200


@post.doc(
    security='KEY',
    params={ 
            },
    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })
@post.route('/post/article_check')
class Article_check(Resource):
    @post.expect(Article_verify)
    @token_required
    def post(self):
            req_data = request.get_json()
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            LANGUAGE = "english"
            SENTENCES_COUNT = 10
            url= req_data["Link"]
            sum_content=''
            try:
                parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
                stemmer = Stemmer(LANGUAGE)

                summarizer = Summarizer(stemmer)
                summarizer.stop_words = get_stop_words(LANGUAGE)

                for sentence in summarizer(parser.document, SENTENCES_COUNT):
                    sum_content += '\n'+str(sentence)

                return {
                    'status': 1,
                    'res': url,
                    'content':sum_content
                }, 200
            except:
                return {
                        'status': 0,
                        'res': "This Article does not exist" 
                    }, 404
                

@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            },
    responses={
        200: 'ok',
        201: 'created',
        204: 'No Content',
        301: 'Resource was moved',
        304: 'Resource was not Modified',
        400: 'Bad Request to server',
        401: 'Unauthorized request from client to server',
        403: 'Forbidden request from client to server',
        404: 'Resource Not found',
        500: 'internal server error, please contact admin and report issue'
    })

@post.route('/post/users')
class UsersPost(Resource):
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count+"&lang="+lang
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count+"&lang="+lang
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        posts1 = Posts.query.filter_by(uploader_id=user.id).first()
        if user.id == posts1.uploader_id :
            posts = Posts.query.filter_by(posts1.uploader_id).order_by(posts1.uploader_date.desc()).paginate(int(start), int(count), False).items
            return {
                "start": start,
                "limit": limit,
                "count": count,
                "next": next,
                "previous": previous,
                "results": marshal(posts, postdata)
            }, 200
        else :
            return{
                "status":0,
                "res":"User does not have post"
            }