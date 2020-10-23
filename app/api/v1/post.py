from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from flask_restplus import Namespace, Resource, fields, marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps
from app.services import mail
from flask import abort, request, session,Blueprint
from flask import current_app as app
import numpy as np
from app.models import Save , Users, Channels, subs, Posts, Language, Postarb, Posten, Postes, Postfr, \
    Posthau, Postpor, Postsw,Report,Notification
from app import db, cache, logging
import json
from tqdm import tqdm
from werkzeug.datastructures import FileStorage
from breadability.readable import Article

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import requests
from bs4 import BeautifulSoup
import bleach
from sqlalchemy import or_,and_,func


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
    'content': fields.String(required=True),
    'lang':fields.String(required=True),
})

Updatedata = post.model('Updatedata',{
    'id':  fields.String(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True)
})

deletedata =post.model('deletedata',{
    'id':fields.String(required=True)
})

channelfinal = post.model('channelreturndata',{
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'description': fields.String(required=True)
})
channeldata=post.model('channelreturndata',{
    'channel_id': fields.Integer(required=True),
})
postdata = post.model('postreturndata', {
    'id': fields.Integer(required=True),
    'uuid':fields.String(required=True),
    'title': fields.String(required=True),
    'post_url': fields.String(required=True),
    'uploader': fields.String(required=True),
    'content': fields.String(required=True),
    'thumb_url': fields.String(required=False),
    'uploader_date': fields.DateTime(required=True),
    'postchannel': fields.List(fields.Nested(channelfinal))
})
user_post_sav = post.model('postreturnuserdata', {
    'id': fields.Integer(required=True),
    'uuid':fields.String(required=True),
    'title': fields.String(required=True),
    'postchannel': fields.List(fields.Nested(channelfinal)),
    'post_url': fields.String(required=True),
    'thumb_url': fields.String(required=True),
    'uploader': fields.String(required=True),
    'content': fields.String(required=True),
    'uploader_date': fields.DateTime(required=True)
})

langpostdata = post.model('langpostreturndata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True),
})

multiplepost = post.model('multiple',{  #check this
    "start": fields.Integer(required=True),
    "limit": fields.Integer(required=True),
    "count": fields.Integer(required=True),
    "next": fields.String(required=True),
    "previous": fields.String(required=True),
    "results": fields.List(fields.Nested(postdata))
})
Clap_post = post.model('clap1',{
    'Post_id':fields.String(required=True)
})
saves_post = post.model('saves_post',{
    'Post_id':fields.Integer(required=True)
})
user_clap = post.model('user_clap',{
    'id':fields.Integer(required=True),
    'uuid':fields.String(required=True),
})
post_clap = post.model('clap',{
    'id':fields.Integer(required=True),
    'clap': fields.List(fields.Nested(user_clap))
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
saved = post.model('saved',{
    "content":fields.String(required=True),
    "user_id":fields.String(required=True),
    "post___data":fields.List(fields.Nested(user_post_sav)),
})
users_post =  post.model('users_post',{
    'User_name':fields.String(required=True),
})
Report_post = post.model('Report_post',{
    'post_id':fields.String(required=True),
    'reason':fields.String(required=True),
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
        ptype= req_data['type']
        got_language = req_data['lang']
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        language=Language.query.filter_by(code=got_language).first()
        channel_list = []
        followers_=user.is_followers()
        for i in channel_names:
            name = Channels.query.filter_by(name=i).first()
            if name in user.get_channels():
                channel_list.append(name)
        if len(channel_list) != 0:
            if ptype == 1:
                newPost = Posts(user.id, title, ptype, content, language.id, user.id)
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
                thumb_url_=req_data['thumb'] or None
                post_url_=req_data['post_url'] or None
                newPost = Posts(user.id, title, ptype, content, language.id, user.id, thumb_url=thumb_url_, post_url=post_url_)
                db.session.add(newPost)
                db.session.commit()
                newPost.post_url=post_url_
                newPost.thumb_url=thumb_url_
                db.session.commit()
                newPost.launch_translation_task('translate_posts', user.id, 'Translating  post ...')
                for c in channel_list:
                    c.add_post(newPost)
                    db.session.commit()
                for i in followers_:
                    notif_add = Notification("user" + user.username + "has made a post Titled"+title,i.id)
                    db.session.add(notif_add)
                    db.session.commit()
                for i in channel_names:
                    names = Channels.query.filter_by(name=i).first()
                    Mod =names.moderator
                    notif_add1 = Notification("user" + user.username + "has uploaded a post to "+names.name,Mod)
                    db.session.add(notif_add1)
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
        else:
           return {
                'status': 0,
                'res': 'No channel found'
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
            x = requests.get(url)
            if x is not None:
                
                soup = BeautifulSoup(x.content, 'html.parser')   
                document= Article(x.content, url)

                metas=soup.findAll('meta')

                for i in metas:
                    if i.get('property') == "og:image":
                        thumbnail=i.get('content')

                title=soup.find('title').get_text()

               

                return {
                    'status': 1,
                    'res': url,
                    'title':title,
                    'thumbnail':thumbnail,
                    'content':str(document.readable)

                }, 200
            else:
                return {
                        'status': 0,
                        'res': "This Article does not exist" 
                    }, 200
                

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
            next = "/api/v1/post/users?start="+str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post/users?start="+str(int(start)-1)+"&limit="+limit+"&count="+count
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            posts1 = Posts.query.filter_by(uploader_id=user.id).first()
            if user.id == posts1.uploader_id :
                pgPosts = Posts.query.filter_by(uploader_id=posts1.uploader_id).order_by(Posts.uploader_date.desc()).paginate(int(start), int(count), False)
                posts = pgPosts.items
                total = pgPosts.total
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "totalPages": total,
                    "results": marshal(posts, postdata)
                }, 200
            else :
                return{
                    "status":0,
                    "res":"User does not have post"
                }
        else:
            return{
                    "status":0,
                    "res":"No request found"
                }       
        
@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'post_id':'Post ID of post'
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

@post.route('/post/Shout')
class ShoutPost(Resource):  
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count
            post_id  = request.args.get('post_id', None)
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            posts = Posts.query.filter_by(id=post_id).first()
            if user:
                if posts:
                    clappedpost=Posts.query.filter_by(id=post_id).order_by(Posts.id.desc()).paginate(int(start), int(count), False).items
                    return  {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(clappedpost, post_clap)
                }, 200
                else:
                    return{
                        "status":0,
                        "res":"This post does not have any clap"
                    }, 200

            else :
                return{
                    "status":0,
                    "res":"Token not found"
                }, 200
        else:
            return{
                    "status":0,
                    "res":"No request found"
                }, 200    
       
    @post.expect(Clap_post)   
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post= Posts.query.filter_by(id=req_data['Post_id']).first()
        
        if post.has_clapped(user):
            return{
                "status":0,
                "res":"You have already clapped on this post"
            }, 200
        if user:
            post.add_clap(user)
            db.session.commit()
            return{
                "status":1,
                "res":"You have clapped on this post"
            }, 200
        else:
            return{
                "status":0,
                "res":"Insert token"
            }, 200 
    #delete route to be done


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

@post.route('/post/Save')
class save_post(Resource): 
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            channel=request.args.get('channel_id')
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            if user:
                user_saves=Save.query.filter_by(user_id=user.id).order_by(Save.id.desc()).paginate(int(start), int(count), False).items
                if user_saves:
                    return  {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next,
                        "previous": previous,
                        "results": marshal(user_saves, saved)
                    }, 200
                else:
                    return{
                        "status":0,
                        "res":"User does not have saved posts"
                    }
            else:
                 return{
                        "status":0,
                        "res":"User does not exist"
                    }
        else:
            return{
                        "status":0,
                        "res":"Request failed"
                    }

    @post.expect(saves_post) 
    @token_required
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post= Posts.query.filter_by(id=req_data['Post_id']).first()
        Saves= Save.query.filter(and_(Save.user_id == user.id , Save.post_id == post.id)).first()

        if Saves:
            db.session.delete(Saves)
            db.session.commit()
        else:
           return{
                    "status":0,
                    "res":"Fail"
                }      

    @post.expect(saves_post)   
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post= Posts.query.filter_by(id=req_data['Post_id']).first()
        Saves= Save.query.filter(and_(Save.user_id == user.id , Save.post_id == post.id)).first()
        if Saves:
            return{
                "status":0,
                "res":"Post has already been saved"
            } 
        if post:
            save= Save(user.id,post.content,post.id)
            db.session.add(save)
            db.session.commit()
            return{
                "status":1,
                "res":"Post has been saved"
            }  
                
        else:
            return{
                    "status":0,
                    "res":"Fail"
                }

                
       

@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'posts_id':'The post id'
    
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
 
@post.route('/post/user_Save')
class user_save_post(Resource): 
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    @post.marshal_with(user_post_sav)
    def get(self):
        if request.args:
            posts_id=request.args.get('posts_id')
            req_data = request.get_json()
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            posts_saved = Posts.query.filter_by(id=posts_id).first()
            user_post_saved = Posts.query.join(
                Save,(Save.user_id == user.id)).filter(
                    Save.post_id == posts_saved.id).first()
            if user_post_saved:
                return {user_post_saved},200
            else:
                return{
                    "status":0,
                    "res":"Fail"
                },400
        else:
            return{
                    "status":0,
                    "res":"Bad request"
                },400
#Not tested

@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'posts_id':'The post id'
    
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
 
@post.route('/post/user_post')
class views_post(Resource):
    @post.expect(users_post)   
    @token_required
    def post(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            # Still to fix the next and previous WRT Sqlalchemy
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count
            req_data = request.get_json()
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            user_actual= Users.query.filter_by(username=req_data['User_name']).first()
            post= Posts.query.filter_by(id=req_data['Post_id']).first()

            if user_actual.is_blocking(user) :
                return{
                    "status":1,
                    "res":"user is not found"
                }  
            if user_actual:
                _user_post=Posts.query.filter_by(uploader_id=user_actual.id).order_by(Posts.uploader_date.desc()).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(_user_post, postdata)
                }, 200
            
                    
            else:
                return{
                        "status":0,
                        "res":"Fail"
                    }
        else:
            return{
                    "status":0,
                    "res":"Fail"
                }


@post.doc(
    security='KEY',
    params={
            'posts_id':'The post id'
    
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
 
@post.route('/post/Report_post')
class Report_post(Resource):
    @post.expect(Report_post)   
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post= Posts.query.filter_by(id=req_data['post_id']).first()

        if user is None:
            return{
                    "status":0,
                    "res":"Fail"
                }
        if post:
            Report_sent=Report(req_data['reason'],user.email,user.id,post.id,post.uploader_id)
            mail.Report(user.email,req_data['reason'])
            return{
                "status":1,
                "res":"Post has been reported"
            } 

                
        else:
            return{
                "status":0,
                "res":"Fail"
            }
            #fff

@post.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'Discovery_Type' : 'state the type of discovery',
            'country':'State the country'
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
@post.route('/post/Discovery')

class Discovery(Resource):
    #@token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            Discovery_Type = request.args.get('Discovery_Type') 
            country = request.args.get('country')
            # Still to fix the next and previous WRT Sqlalchemy
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count

            if country is None:
                return{
                    'status':0,
                    'res': 'Please input country'
                }
            if Discovery_Type == 'New':
                posts = Posts.query.order_by(Posts.uploader_date.desc()).filter_by(country=country).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(posts, postdata)
                }, 200
            if Discovery_Type == 'Trending':
                posts = Posts.query.order_by(func.random()).filter_by(country=country).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(posts, postdata)
                }, 200
            if Discovery_Type == 'Best':
                posts = Posts.query.order_by(func.random()).filter_by(country=country).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(posts, postdata)
                }, 200     

            #fff