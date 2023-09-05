from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from operator import pos

from flask_restplus import Namespace, Resource, fields, marshal, Api
import jwt
import uuid
import os
import pusher
from flask_cors import CORS
from functools import wraps

from sqlalchemy.sql.base import NO_ARG
from app.services import mail
from flask import abort, request, session, Blueprint
from flask import current_app as app
import numpy as np
from app.models import Save, Users, Posts, Language, Translated, Report, Notification, Posttype, Account, Category, Tags
from app import db, cache, logging,sio


#from flask_socketio import SocketIO, emit
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
from sqlalchemy import or_, and_, func, desc, asc

from googletrans import Translator
import stripe
from flask import current_app as app
from config import Config
from datetime import timedelta, datetime, timezone
import cloudinary
import cloudinary.uploader
import numpy as np
import ssl



cloudinary.config(
    cloud_name="odaaay",
    api_key="893419336671437",
    api_secret="lIGoIkb5l7vZGpcD-k18Py49nGQ"
)


# with app.app_context().push():
stripe.api_key = Config.stripe_secret_key


translator = Translator()

pusher_client = pusher.Pusher(
    app_id="1221871",
    key="4cc3ddc1b022abe535ce",
    secret="2d22aad22ff2ebfa6b3e",
    cluster="eu",
    ssl=True
)


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
                data = jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated


api = Blueprint('api', __name__, template_folder='../templates')
post1 = Api(app=api, doc='/docs', version='1.4', title='News API.',
            description='', authorizations=authorizations)
# from app.api import schema  'channel': fields.List(fields.String(required=True)),
CORS(api, resources={r"/api/*": {"origins": "*"}})

uploader = post1.parser()
uploader.add_argument('file', location='files', type=FileStorage,
                      required=False, help="You must parse a file")
uploader.add_argument('name', location='form', type=str,
                      required=False, help="Name cannot be blank")

post = post1.namespace('/api/post',
                       description='This contains routes for core app data access. Authorization is required for each of the calls. \
        To get this authorization, please contact out I.T Team ',
                       path='/v1/')

postcreationdata = post.model('postcreationdata', {
    'title': fields.String(required=True),
    'type': fields.Integer(required=True),
    'post_url': fields.String(required=False, default=None),
    'thumb': fields.String(required=False, default=None),
    'content': fields.String(required=True),
    'lang': fields.String(required=True),
    'translate': fields.Boolean(required=False, default=False),
    'donation': fields.Boolean(required=False, default=False),
    'min': fields.Integer(required=False),
    'category': fields.Integer(required=True),
    'max': fields.Integer(required=False),
    'payment': fields.Boolean(required=False, default=False),
    'price': fields.Integer(required=False),
    'Tags': fields.List(fields.String(required=True)),
    'subscribers': fields.Boolean(required=False, default=False),
    'nsfw': fields.Boolean(required=False, default=False),
    'summarize': fields.Boolean(required=False, default=False),
})

users_dat = post.model('users_dat', {
    'id': fields.Integer(required=True),
    'username': fields.String(required=True),
    'uuid': fields.String(required=True),
    'bio': fields.String(required=True),
    'picture': fields.String(required=True),
})

postdata1 = post.model('postdata1', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'uuid': fields.String(required=True),
    'author': fields.Integer(required=True),
    'user_name': fields.String(required=True),
    'post_type': fields.Integer(required=True),
    'text_content': fields.String(required=True),
    'post_url': fields.String(required=True),
    'audio_url': fields.String(required=True),
    'video_url': fields.String(required=True),
    'created_on': fields.DateTime(required=True),
    'thumb_url': fields.String(required=False),
    'category_id': fields.Integer(required=True),
    'tags': fields.String(required=True),
    'price': fields.Float(required=True),
    'summarize':fields.Boolean(required=False),
    'translate':fields.Boolean(required=False),
    'subs_only':fields.Boolean(required=False),
    'nsfw':fields.Boolean(required=False),
    'uploader_data': fields.List(fields.Nested(users_dat))
})
lang_post = post.model('lang_post', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True),
    'fullcontent': fields.String(required=True),
    'language_id': fields.Integer(required=True),
    'tags': fields.String(required=True),
    'posts': fields.List(fields.Nested(postdata1)),
})

postcreationdata2 = post.model('postcreationdata2', {
    'uuid':fields.String(required=True),
    'title': fields.String(required=True),
    'type': fields.Integer(required=True),
    'post_url': fields.String(required=False, default=None),
    'thumb': fields.String(required=False, default=None),
    'content': fields.String(required=True),
    'lang': fields.String(required=True),
    'translate': fields.Boolean(required=False, default=False),
    'donation': fields.Boolean(required=False, default=False),
    'min': fields.Integer(required=False),
    'category': fields.Integer(required=True),
    'max': fields.Integer(required=False),
    'payment': fields.Boolean(required=False, default=False),
    'price': fields.Integer(required=False),
    'Tags': fields.List(fields.String(required=True)),
    'subscribers': fields.Boolean(required=False, default=False),
    'nsfw': fields.Boolean(required=False, default=False),
    'summarize': fields.Boolean(required=False, default=False),
})

Updatedata = post.model('Updatedata', {
    'id':  fields.String(required=True),
    'title': fields.String(required=True),
    'text_content': fields.String(required=True)
})

deletedata = post.model('deletedata', {
    'id': fields.String(required=True)
})

userdata = post.model('userdata', {
    'id': fields.String(required=True),
    'username': fields.String(required=True),
    'picture': fields.String(required=True),
})

element = post.model('element', {
    'clap_id': fields.Integer(required=True),
    'user_id': fields.Integer(required=True),
    'post_id': fields.Integer(required=True),

})

postdata = post.model('postreturndata', {
    'id': fields.Integer(required=True),
    'uuid': fields.String(required=True),
    'title': fields.String(required=True),
    'post_url': fields.String(required=True),
    'uploader_data': fields.List(fields.Nested(userdata)),
    'text_content': fields.String(required=True),
    'thumb_url': fields.String(required=False),
    'clap': fields.List(fields.Nested(element)),
    'created_on': fields.DateTime(required=True),
})


user_post_sav = post.model('postreturnuserdata', {
    'id': fields.Integer(required=True),
    'uuid': fields.String(required=True),
    'title': fields.String(required=True),
    'post_url': fields.String(required=True),
    'thumb_url': fields.String(required=True),
    'author': fields.String(required=True),
    'text_content': fields.String(required=True),
    'created_on': fields.DateTime(required=True),
})
usernotif = post.model('usernotif', {
    'id': fields.Integer(required=True),
    'post_data': fields.List(fields.Nested(postdata)),
    'created_on': fields.String(required=True),
    'seen': fields.Boolean(required=True),
})

langpostdata = post.model('langpostreturndata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'text_content': fields.String(required=True),
})

multiplepost = post.model('multiple', {  # check this
    "start": fields.Integer(required=True),
    "limit": fields.Integer(required=True),
    "count": fields.Integer(required=True),
    "next": fields.String(required=True),
    "previous": fields.String(required=True),
    "results": fields.List(fields.Nested(postdata))
})
Clap_post = post.model('clap1', {
    'Post_id': fields.String(required=True)
})
saves_post = post.model('saves_post', {
    'Post_id': fields.Integer(required=True)
})
user_clap = post.model('user_clap', {
    'id': fields.Integer(required=True),
    'uuid': fields.String(required=True),
})
post_clap = post.model('clap', {
    'id': fields.Integer(required=True),
    'clap': fields.List(fields.Nested(user_clap))
})

postreq = post.model('postreq', {
    'arg': fields.String(required=True),
    'all': fields.Boolean(required=True),
    'arg_type': fields.String(required=True),
})
Article_verify = post.model('postreq', {
    "Link": fields.String(required=True)
})
verify_notification = post.model('verify_notification', {
    "id": fields.Integer(required=True),
    "user": fields.String(required=True),
})
cato = post.model('cato', {
    "id": fields.Integer(required=True),
    "name": fields.String(required=True),
})
tegs = post.model('tegs', {
    "id": fields.Integer(required=True),
    "tags": fields.String(required=True),
})

saved = post.model('saved', {
    "content": fields.String(required=True),
    "user_id": fields.String(required=True),
    "post___data": fields.List(fields.Nested(user_post_sav)),
})
users_post = post.model('users_post', {
    'User_name': fields.String(required=True),
})


Report_post = post.model('Report_post', {
    'post_id': fields.String(required=True),
    'reason': fields.String(required=True),
    'Type': fields.String(required=True),
})


@post.doc(
    security='KEY',
    params={
            'category': 'category'
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
@post.route('/post/tags')
class ptag(Resource):
    def get(self):
        if request.args:
            category = request.args.get('category', None)
            # Still to fix the next and previous WRT Sqlalchemy
           
            
            if category == None:
                results = Tags.query.distinct(Tags.tags).all()#paginate(    #order_by(func.random())
                    #int(start), int(count), False).items
                
                results1=[]
                for tag in results:
                    total=Tags.query.filter_by(tags=tag.tags).count()
                    if total > 4:
                        results1.append(tag)
            else:  
                results = Tags.query.distinct(Tags.tags).join(Posts, (Posts.id == Tags.post)).filter(   #order_by(func.random())
                    Posts.category_id == category).all()#.paginate(int(start), int(count), False).items
                
                results1=[]
                for tag in results:
                    total=Tags.query.filter_by(tags=tag.tags).count()
                    if total > 4:
                        results1.append(tag)
            return {
                
                "results": marshal(results1, tegs)
            }, 200


@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
             'lang': 'Language'
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
@post.route('/upload')
class Upl(Resource):
    @token_required
    @post.expect(uploader)
    def post(self):
        args = uploader.parse_args()
        destination = Config.UPLOAD_FOLDER_MEDIA
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        File = args['file']
        Name = args['name']
        if File.mimetype == "image/jpeg":
            fila = os.path.join(destination, str(
                data['uuid']), 'post')  # ,Name)
            if os.path.isdir(fila) == False:
                os.makedirs(fila)
            fil = os.path.join(fila, Name)  # ,Name)
            File.save(fil)
            upload_result = cloudinary.uploader.upload('https://odaaay.com/api/static/files/'+str(data['uuid'])+"/post/"+Name)
            return {
                "status": 1,
                "thumb_url":upload_result["secure_url"], #str(data['uuid'])+"/post/"+Name,
            }, 200

        if File.mimetype == "image/jpg":
            fila = os.path.join(destination, str(
                data['uuid']), 'post')  # ,Name)
            if os.path.isdir(fila) == False:
                os.makedirs(fila)
            fil = os.path.join(fila, Name)  # ,Name)
            File.save(fil)
            upload_result = cloudinary.uploader.upload('https://odaaay.com/api/static/files/'+str(data['uuid'])+"/post/"+Name)
            return {
                "status": 1,
                "thumb_url":upload_result["secure_url"], #str(data['uuid'])+"/post/"+Name,
            }, 200
        else:
            return {
                "status": 0,
                "res": "Put a Jpeg file",
            }, 200


@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
             'lang': 'Language'
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
@post.route('/bot/post')
class botPost(Resource):
    def post(self):
        
        if request.method == 'POST':
            user = Users.query.filter_by(id=1).first()
            user.launch_bot_task('bot_post','Creating  post ...',request.data)
            return {
                        'status': 1,
                        'res': 'Post were made',
                    }, 200
            
    
@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
             'lang': 'Language'
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
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', '')
            # Still to fix the next and previous WRT Sqlalchemy
            next = "/api/v1/post?start=" + \
                str(int(start)+1)+"&limit="+limit+"&count="+count+"&lang="+lang
            previous = "/api/v1/post?start=" + \
                str(int(start)-1)+"&limit="+limit+"&count="+count+"&lang="+lang
            language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
            if lang:
                for i in tqdm(language_dict):
                    if i == lang:
                        current_lang = Language.query.filter_by(code=i).first()
                        results = Translated.query.filter_by(language_id=current_lang.id).paginate(
                            int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(results, langpostdata)
                }, 200
            else:
                posts = Posts.query.order_by(Posts.created_on.desc()).paginate(
                    int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(posts, postdata)
                }, 200
        else:
            posts = Posts.query.order_by(Posts.created_on.desc()).all()
            return marshal(posts, postdata), 200

    @token_required
    @post.expect(Updatedata)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post_id = Posts.query.get(req_data['id'])
        if req_data['content'] is None:
            return {'res': 'fail'}, 404
        elif user and post_id:
            post_id.title = req_data['title']
            post_id.content = req_data['content']
            db.session.commit()
            return {'res': 'success'}, 200
        else:
            return {'res': 'fail'}, 404

    @token_required
    @post.expect(deletedata)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post_id = Posts.query.get(req_data['id'])
        trans = Translated.query.filter_by(post_id=post_id.id).all()
        if user.id == post_id.uploader_id:
            if post_id.paid == False:
                post_id.visibility = False
                db.session.commit()
                for i in trans:
                    i.visibility = False
                    db.session.commit()
                return {'res': 'success'}, 200
            else:
                return {'res': 'this is a paid post'}, 200
        else:
            return {'res': 'fail'}, 404

    @token_required
    @post.expect(Updatedata)
    def patch(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post_id = Posts.query.get(req_data['id'])
        if user and post_id:
            post_id.title = req_data['title']
            post_id.content = req_data['content']
            db.session.commit()
            return {'res': 'success'}, 200
        else:
            return {'res': 'fail'}, 404
    
    @post.expect(postcreationdata)
    @token_required
    def post(self):
        req_data = request.get_json()
        args = uploader.parse_args()
        title = req_data['title']
        content = req_data['content']
        if content == None :
            return {
                'status': 0,
                'res': 'Please insert content'
            }, 400
        post_auto_lang = translator.detect(content)
        lang = str(post_auto_lang.lang)
        ptype = req_data['type']
        translated = req_data['translate']
        summarized = req_data['summarize']
        category = req_data['category']
        subs = req_data['subscribers']
        donation = req_data['donation']
        payment = req_data['payment']
        thumb_url_ = req_data['thumb'] or None
        nsf = req_data['nsfw']
        tags = req_data['Tags']
        s = str(tags)
        if lang != None: 
            got_language = lang#req_data['lang']
        '''else:
            got_language='o'
        if lang == got_language:
            print('language good')
        else:
            if lang != None:
                got_language=lang'''
        
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        language = Language.query.filter_by(code=got_language).first()
        followers_ = user.is_followers()
        post_done = Posts.query.filter(and_(Posts.title==title,Posts.visibility==True)).first()
        if language != None:
            lang = language.id
        else:
            lang =1
        if payment == True and subs == True:
            return {
                'status': 0,
                'res': 'Subs and payment cant match'
            }, 400
        if payment == True and thumb_url_ == None:
            return {
                'status': 0,
                'res': 'Please pt a thumb'
            }, 400
        if donation == True and req_data['max'] >= 100:
            return {
                'status': 0,
                'res': 'Please fix donaton price'
            }, 400
        if post_done is None:
            if ptype == 1:
                sum_content = ''
                newPost = Posts(user.id, title, ptype, content, lang)
                db.session.add(newPost)
                db.session.commit()
                newPost.summarize = summarized
                newPost.translate = translated
                newPost.subs_only = subs
                newPost.category_id = category
                newPost.thumb_url = thumb_url_
                newPost.nsfw = nsf
                newPost.tags = s[1:-1]
                newPost.user_name = user.username
                db.session.commit()
                steps = np.random.randint(25,550)
                if user.special == True:
                    for i in range(steps):
                        newPost.add_clap(user.id)
                        db.session.commit()
                if payment == True:
                    acc = Account.query.filter_by(user=user.id).first()
                    newPost.thumb_url_ = thumb_url_
                    # db.session.commit()
                    if acc is not None:
                        Price = req_data['price']
                        product = stripe.Product.create(
                            name=newPost.title+' post by '+user.username,
                        )
                        price = stripe.Price.create(
                            product=product['id'],
                            unit_amount=req_data['price']*100,
                            currency='usd',
                        )
                        newPost.product_id = product['id']
                        newPost.price_id = price["id"]
                        newPost.paid = True
                        newPost.price = float(req_data['price'])
                        db.session.commit()

                    else:
                        return {
                            'status': 0,
                            'res': 'Please create a stripe account'
                        }, 200
                if donation == True:
                    acc = Account.query.filter_by(user=user.id).first()
                    if acc is not None:
                        mini = req_data['min']
                        maxi = req_data['max']
                        product = stripe.Product.create(
                            name=newPost.title+' post  donation by '+user.username,
                        )
                        newPost.donation_id = product['id']
                        newPost.mini = float(mini)
                        newPost.maxi = float(maxi)
                        db.session.commit()
                    else:
                        return {
                            'status': 0,
                            'res': 'Please create a stripe account'
                        }, 200
                if tags != []:
                    for tag in tags:
                        new_tag = Tags(post=newPost.id,
                                       tags=tag, category=category)
                        db.session.add(new_tag)
                        db.session.commit()
                
                if summarized == True and translated == True :
                    newPost.launch_translation_task(
                        'translate_posts', user.id, 'Translating  post ...')

                if translated == True and summarized == False :
                    newPost.launch_translation_task(
                        'translate_posts', user.id, 'Translating  post ...')
                if summarized == True and translated == False :
                    newPost.launch_summary_task(
                        'summarize_posts', user.id, 'summarizing  post ...')
                if summarized == False and translated == False :
                    parser = HtmlParser.from_string(
                        newPost.text_content, '', Tokenizer(language.name))
                    stemmer = Stemmer(language.name)
                    summarizer = Summarizer(stemmer)
                    summarizer.stop_words = get_stop_words(language.name)

                    for sentence in summarizer(parser.document, 2):
                        sum_content += '\n'+str(sentence)

                    new_check = Translated.query.filter(
                        and_(Translated.title == newPost.title, Translated.language_id == lang)).first()
                    if new_check is None:
                        new_row = Translated(post_id=newPost.id, title=newPost.title, content=sum_content,
                                             language_id=lang, fullcontent=newPost.text_content, tags=newPost.tags)
                        db.session.add(new_row)
                        db.session.commit()
                
                
                for i in followers_:
                    notif_add = Notification(
                        "user" + user.username + "has made a post Titled"+title, i, newPost.id)
                    db.session.add(notif_add)
                    db.session.commit()
                    newPost.launch_notif_task('post_notify_users',i,notif_add,user,'broadcasting  post ...')
                    
                    
                return {
                    'status': 1,
                    'res': 'Post was made',
                    'post_id': newPost.id,
                    'content':newPost.text_content,
                    'post_uuid': newPost.uuid,
                }, 200
            if ptype == 2:
                thumb_url_ = req_data['thumb'] or None
                post_url_ = req_data['post_url'] or None
                sum_content = ''
                newPost = Posts(user.id, title, ptype, content,
                                lang, thumb_url=thumb_url_, post_url=post_url_)
                db.session.add(newPost)
                db.session.commit()
                newPost.post_url = post_url_
                newPost.user_name = user.username
                newPost.thumb_url = thumb_url_
                newPost.category_id = category
                newPost.summarize = summarized
                newPost.translate = translated
                newPost.tags = s[1:-1]
                newPost.subs_only = subs
                db.session.commit()
                steps = np.random.randint(25,550)
                if user.special == True:
                    for i in range(steps):
                        newPost.add_clap(user.id)
                        db.session.commit()
                if payment == True:
                    acc = Account.query.filter_by(user=user.id).first()
                    if acc:
                        Price = req_data['price']
                        product = stripe.Product.create(
                            name=newPost.title+' post by '+user.username,
                        )
                        price = stripe.Price.create(
                            product=product['id'],
                            unit_amount=req_data['price']*100,
                            currency='usd',
                        )
                        newPost.product_id = product['id']
                        newPost.price_id = price["id"]
                        newPost.paid = True
                        newPost.price = float(req_data['price'])
                        db.session.commit()
                    else:
                        return {
                            'status': 0,
                            'res': 'Please create a stripe account'
                        }, 200
                if donation == True:
                    acc = Account.query.filter_by(user=user.id).first()
                    if acc:
                        mini = req_data['min']
                        maxi = req_data['max']
                        product = stripe.Product.create(
                            name=newPost.title+' post  donation by '+user.username,
                        )
                        newPost.donation_id = product['id']
                        newPost.mini = float(mini)
                        newPost.maxi = float(maxi)
                        db.session.commit()
                    else:
                        return {
                            'status': 0,
                            'res': 'Please create a stripe account'
                        }, 200
                if tags != []:
                    for tag in tags:
                        new_tag = Tags(post=newPost.id,
                                       tags=tag, category=category)
                        db.session.add(new_tag)
                        db.session.commit()
                
                if summarized and translated == True:
                    newPost.launch_translation_task(
                        'translate_posts', user.id, 'Translating  post ...')

                if translated == True and summarized == False :
                    newPost.launch_translation_task(
                        'translate_posts', user.id, 'Translating  post ...')
                if summarized == True and translated == False and got_language != 'o':
                    newPost.launch_summary_task(
                        'summarize_posts', user.id, 'summarizing  post ...')
                if summarized == False and translated == False :
                    parser = HtmlParser.from_string(
                        newPost.text_content, '', Tokenizer(language.name))
                    stemmer = Stemmer(language.name)
                    summarizer = Summarizer(stemmer)
                    summarizer.stop_words = get_stop_words(language.name)

                    for sentence in summarizer(parser.document, 2):
                        sum_content += '\n'+str(sentence)

                    new_check = Translated.query.filter(
                        and_(Translated.title == newPost.title, Translated.language_id == lang)).first()
                    if new_check is None:
                        new_row = Translated(post_id=newPost.id, title=newPost.title, content=sum_content,
                                             language_id=lang, fullcontent=newPost.text_content, tags=newPost.tags)
                        db.session.add(new_row)
                        db.session.commit()

                
                
                for i in followers_:
                    notif_add = Notification(
                        "user" + user.username + "has made a post Titled"+title, i, newPost.id)
                    db.session.add(notif_add)
                    db.session.commit()
                    newPost.launch_notif_task('post_notify_users',i,notif_add,user,'broadcasting  post ...')

                db.session.commit()
                return {
                    'status': 1,
                    'res': 'Post was made',
                    'post_id': newPost.id,
                    'content': newPost.text_content,
                    'post_uuid': newPost.uuid,
                }, 200
            else:
                return {
                    'status': 0,
                    'res': i+' does not exist or you are not subscribed to it'
                }, 200
        else:
            return {
                'status': 0,
                'res': 'Post exists already'
            }, 200


@post.doc(
    security='KEY',
    params={
        'start': 'Value to start from',
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
@post.route('/post/receive/notification')
class receive_check(Resource):
    @token_required
    # @user.marshal_with(userinfo)
    def get(self):
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            user_id = request.args.get('user_id', None)
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
            now_utc = datetime.now(timezone.utc)
            start_ = datetime.combine(now_utc, datetime.min.time())
            if user:
                notif = Notification.query.filter(and_(Notification.user_id == user.id, Notification.created_on >= start_ - timedelta(
                    days=7))).order_by(desc(Notification.created_on)).paginate(int(start), int(count), False).items
                next = "/api/v1/post/receive/notification?start=" + \
                    str(int(start)+1)+"&limit="+limit+"&count="+count
                previous = "/api/v1/post/receive/notification?start=" + \
                    str(int(start)-1)+"&limit="+limit+"&count="+count

                if user.id:
                    return{
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next,
                        "previous": previous,
                        "results": marshal(notif, usernotif)
                    }, 200
            else:
                return{
                "status": 0
                }, 200

    @post.expect(verify_notification)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        ID = req_data["id"]
        user = req_data["user"]
        notif = Notification.query.filter_by(id=ID).first()
        if notif:
            notif.seen = True
            db.session.commit()
            # pusher_client.trigger(user, 'usernotification', {
            # 'message':{
            #    'id':notif.id,
            #    'user':user,
            #    'time':str(notif.created_on),
            #    'seen':notif.seen,
            # }
            # })
            return{
                "status": 1
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
@post.route('/post/articlecheck')
class Article_check(Resource):
    @post.expect(Article_verify)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        LANGUAGE = "english"
        SENTENCES_COUNT = 10
        url = req_data["Link"]
        if url == '' or url == "" :
            return {
                'status': 2,
                'res': "Please input a link"
            }, 200
        sum_content = ''
        x = requests.get(url)
        if x is not None:

            soup = BeautifulSoup(x.content, 'html.parser')
            document = Article(x.content, url)

            metas = soup.findAll('meta')

            thumbnail=''
            for i in metas:
                if i.get('property') == "og:image":
                    thumbnail = i.get('content')
            parser = HtmlParser.from_string(
                document.readable, '', Tokenizer(LANGUAGE))
            stemmer = Stemmer(LANGUAGE)
            summarizer = Summarizer(stemmer)
            summarizer.stop_words = get_stop_words(LANGUAGE)

            for sentence in summarizer(parser.document, 20):
                sum_content += '\n'+str(sentence)

            title = soup.find('title').get_text()

            if sum_content == '':
                sum_content = document.readable

            return {
                'status': 1,
                'res': url,
                'title': title,
                'thumb': thumbnail,
                'content': sum_content,

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
    # @cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            next = "/api/v1/post/users?start=" + \
                str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post/users?start=" + \
                str(int(start)-1)+"&limit="+limit+"&count="+count
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
            posts1 = Posts.query.filter_by(uploader_id=user.id).first()
            if posts1 is not None:
                if user.id == posts1.uploader_id:
                    pgPosts = Posts.query.filter_by(uploader_id=posts1.uploader_id).order_by(
                        Posts.uploader_date.desc()).paginate(int(start), int(count), False)
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
                else:
                    return{
                        "status": 0,
                        "res": "User does not have post"
                    }
        else:
            return{
                "status": 0,
                "res": "No request found"
            }


@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'post_id': 'Post UUID of post'
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
    # @cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            next = "/api/v1/post?start=" + \
                str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start=" + \
                str(int(start)-1)+"&limit="+limit+"&count="+count
            post_id = request.args.get('post_id', None)
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
            posts = Posts.query.filter_by(uuid=post_id).first()
            if user:
                if posts:
                    count_claps = posts.No__claps()
                    clappedpost = Posts.query.filter_by(uuid=post_id).order_by(
                        Posts.id.desc()).paginate(int(start), int(count), False).items
                    return {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next,
                        "previous": previous,
                        "amt_shouts": count_claps,
                        "results": marshal(clappedpost, post_clap)
                    }, 200
                else:
                    return{
                        "status": 0,
                        "res": "This post does not have any clap"
                    }, 200

            else:
                return{
                    "status": 0,
                    "res": "Token not found"
                }, 200
        else:
            return{
                "status": 0,
                "res": "No request found"
            }, 200

    @post.expect(Clap_post)
    @token_required
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post = Posts.query.filter_by(uuid=req_data['Post_id']).first()

        if user:
            if post.has_clapped(user):
                post.remove_clap(user)
                db.session.commit()
                return{
                    "status": 1,
                    "res": "You have deleted the clap"
                }, 200
        else:
            return{
                "status": 0,
                "res": "Insert token"
            }, 200
    # delete route to be done

    @post.expect(Clap_post)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post = Posts.query.filter_by(uuid=req_data['Post_id']).first()
        author = Users.query.filter_by(id=post.author).first()

        if user:
            #if post.has_clapped(user):
            #    return{
            #        "status": 0,
            #        "res": "You have already clapped on this post"
            #    }, 200
            if user:
                if post.has_clapped(user):
                    post.remove_clap(user)
                    db.session.commit()
                    return{
                        "status": 1,
                        "res": "You have deleted the clap"
                    }, 200
                else:
                    post.add_clap(user.id)
                    db.session.commit()
                    sio.emit('clap', {
                            'user':author.uuid,
                            'follower_name':user.username,
                            'follower_uuid':user.uuid,
                            'key':'post',
                            'message': user.username+' has just liked your post',
                            'post_uuid':req_data['Post_id'],
                            })
                    return{
                        "status": 1,
                        "res": "You have clapped on this post"
                    }, 200
            else:
                return{
                    "status": 0,
                    "res": "Insert token"
                }, 200
        else:
            return{
                "status": 0,
                "res": "Insert token"
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
@post.route('/post/Save')
class save_post(Resource):
    @token_required
    # @cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            next = "/api/v1/post?start=" + \
                str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start=" + \
                str(int(start)-1)+"&limit="+limit+"&count="+count
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
            if user:
                user_saves = Save.query.filter_by(user_id=user.id).order_by(
                    Save.id.desc()).paginate(int(start), int(count), False).items
                if user_saves:
                    return {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next,
                        "previous": previous,
                        "results": marshal(user_saves, saved)
                    }, 200
                else:
                    return{
                        "status": 0,
                        "res": "User does not have saved posts"
                    }
            else:
                return{
                    "status": 0,
                    "res": "User does not exist"
                }
        else:
            return{
                "status": 0,
                "res": "Request failed"
            }

    @post.expect(saves_post)
    @token_required
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post = Posts.query.filter_by(id=req_data['Post_id']).first()
        Saves = Save.query.filter(
            and_(Save.user_id == user.id, Save.post_id == post.id)).first()

        if Saves:
            db.session.delete(Saves)
            db.session.commit()
        else:
            return{
                "status": 0,
                "res": "Fail"
            }

    @post.expect(saves_post)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post = Posts.query.filter_by(id=req_data['Post_id']).first()
        Saves = Save.query.filter(
            and_(Save.user_id == user.id, Save.post_id == post.id)).first()
        if Saves:
            return{
                "status": 0,
                "res": "Post has already been saved"
            }
        if post:
            save = Save(user.id, post.content, post.id)
            db.session.add(save)
            db.session.commit()
            return{
                "status": 1,
                "res": "Post has been saved"
            }

        else:
            return{
                "status": 0,
                "res": "Fail"
            }


@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'posts_id': 'The post id'

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
@post.route('/post/usersaves')  # User_Saves
class user_save_post(Resource):
    @token_required
    # @cache.cached(300, key_prefix='all_posts')
    @post.marshal_with(user_post_sav)
    def get(self):
        if request.args:
            posts_id = request.args.get('posts_id')
            req_data = request.get_json()
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
            posts_saved = Posts.query.filter_by(id=posts_id).first()
            user_post_saved = Posts.query.join(
                Save, (Save.user_id == user.id)).filter(
                    Save.post_id == posts_saved.id).first()
            if user_post_saved:
                return {user_post_saved}, 200
            else:
                return{
                    "status": 0,
                    "res": "Fail"
                }, 400
        else:
            return{
                "status": 0,
                "res": "Bad request"
            }, 400
# Not tested


@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'posts_id': 'The post id'

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
@post.route('/post/userposts')  # user_post
class views_post(Resource):
    @post.expect(users_post)
    @token_required
    def post(self):
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            # Still to fix the next and previous WRT Sqlalchemy
            next = "/api/v1/post?start=" + \
                str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start=" + \
                str(int(start)-1)+"&limit="+limit+"&count="+count
            req_data = request.get_json()
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
            user_actual = Users.query.filter_by(
                username=req_data['User_name']).first()
            post = Posts.query.filter_by(id=req_data['Post_id']).first()

            if user_actual.is_blocking(user):
                return{
                    "status": 1,
                    "res": "user is not found"
                }
            if user_actual:
                _user_post = Posts.query.filter_by(uploader_id=user_actual.id).order_by(
                    Posts.uploader_date.desc()).paginate(int(start), int(count), False).items
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
                    "status": 0,
                    "res": "Fail"
                }
        else:
            return{
                "status": 0,
                "res": "Fail"
            }


@post.doc(
    security='KEY',
    params={
        'posts_id': 'The post id'

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
@post.route('/post/Reportpost')
class Report_post_(Resource):
    @post.expect(Report_post)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post = Posts.query.filter_by(id=req_data['post_id']).first()

        if user is None:
            return{
                "status": 0,
                "res": "Fail"
            }
        if post:
            Report_sent = Report(
                req_data['reason'], user.email, user.id, post.id, post.uploader_id, req_data['Type'])
            db.session.add(Report_sent)
            db.session.commit()
            return{
                "status": 1,
                "res": "Post has been reported"
            }

        else:
            return{
                "status": 0,
                "res": "Fail"
            }
            # fff


@post.doc(
    security='KEY',
    params={
        'address': 'ip_address'
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
    # @token_required
    # @cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start = 1
            count = 5
            ip_address = request.args.get('address')

            if country is None:
                return{
                    'status': 0,
                    'res': 'Please input country'
                }
            else:
                New = Posts.query.order_by(Posts.uploader_date.desc()).filter_by(
                    country=country).paginate(int(start), int(count), False).items
                Trending = Posts.query.order_by(func.random()).filter_by(
                    country=country).paginate(int(start), int(count), False).items
                Best = Posts.query.order_by(func.random()).filter_by(
                    country=country).paginate(int(start), int(count), False).items

                return {
                    "New": marshal(New, postdata),
                    "Trending": marshal(Trending, postdata),
                    "Best": marshal(Best, postdata)
                }, 200

        else:
            return{
                'status': 0,
                'res': 'request failed'
            }, 400
            # fff


@post.doc(
    security='KEY',
    params={'post_id': 'Value of post ID '
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
@post.route('/specific/post')
class Post(Resource):
    @token_required
    # @cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            post_id = request.args.get('post_id')
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()

            if post_id and user:
                posts = Posts.query.filter_by(id=post_id).first()
                return {

                    "results": marshal(posts, postdata)
                }, 200
            else:
                return{
                    'status': 0,
                    'res': 'request failed'
                }, 400

        else:
            return{
                'status': 0,
                'res': 'request failed'
            }, 400


@post.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
             'lang': 'Language'
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
@post.route('/modify/post')
class ModifyPost(Resource):
    @post.expect(postcreationdata2)
    @token_required
    def post(self):
        req_data = request.get_json()
        title = req_data['title']
        post = req_data['uuid']
        content = req_data['content']
        if content == None :
            return {
                'status': 0,
                'res': 'Please insert content'
            }, 400
        post_auto_lang = translator.detect(title)
        lang = str(post_auto_lang.lang)
        translated = req_data['translate']
        summarized = req_data['summarize']
        category = req_data['category']
        subs = req_data['subscribers']
        donation = req_data['donation']
        payment = req_data['payment']
        thumb_url_ = req_data['thumb'] or None
        nsf = req_data['nsfw']
        tags = req_data['Tags']
        s = str(tags)
        got_language = req_data['lang']
        if lang == got_language:
            pass
        else:
            if lang != None:
                got_language=lang
        
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        language = Language.query.filter_by(code=got_language).first()
        if language != None:
            lang = language.id
        else:
            lang =1
        followers_ = user.is_followers()
        newPost=Posts.query.filter_by(uuid=post).first()

        if post:
            sum_content=''
            newPost.title = title
            newPost.text_content = content
            newPost.orig_lang = lang
            newPost.summarize = summarized
            newPost.translate = translated
            newPost.subs_only = subs
            newPost.category_id = category
            newPost.thumb_url = thumb_url_
            newPost.nsfw = nsf
            newPost.tags = s[1:-1]
            db.session.commit()

            dele=Translated.__table__.delete().where(Translated.post_id == newPost.id)
            db.session.execute(dele)
            db.session.commit()
            dele=Tags.__table__.delete().where(Tags.post == newPost.id)
            db.session.execute(dele)
            db.session.commit()

            if tags != []:
                    for tag in tags:
                        new_tag = Tags(post=newPost.id,
                                       tags=tag, category=category)
                        db.session.add(new_tag)
                        db.session.commit()

            if summarized == True and translated == True:
                    newPost.launch_translation_task(
                        'translate_posts', user.id, 'Translating  post ...')

            if translated == True and summarized == False:
                newPost.launch_translation_task(
                    'translate_posts', user.id, 'Translating  post ...')
            if summarized == True and translated == False:
                newPost.launch_summary_task(
                    'summarize_posts', user.id, 'summarizing  post ...')
            if summarized == False and translated == False:
                parser = HtmlParser.from_string(
                    newPost.text_content, '', Tokenizer(language.name))
                stemmer = Stemmer(language.name)
                summarizer = Summarizer(stemmer)
                summarizer.stop_words = get_stop_words(language.name)

                for sentence in summarizer(parser.document, 2):
                    sum_content += '\n'+str(sentence)

                new_check = Translated.query.filter(
                    and_(Translated.title == newPost.title, Translated.language_id == lang)).first()
                if new_check is None:
                    new_row = Translated(post_id=newPost.id, title=newPost.title, content=sum_content,
                                            language_id=lang, fullcontent=newPost.text_content, tags=newPost.tags)
                    db.session.add(new_row)
                    db.session.commit()
            db.session.commit()
            return {
                'status': 1,
                'res': 'Post was modified',
                'post_id': newPost.id,
                'post_uuid': newPost.uuid,
            }, 200

        else:
            return {
                'status': 0,
                'res': 'Post does not exist'
            }, 400



@post.doc(
    security='KEY',
    params={'lang': 'Language'},
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
        500: 'internal server error, please contact admin and report '
    })
@post.route('/modifyarticle/<id>')
class homeArticle(Resource):
    def get(self, id):
        language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
       
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()

        
        
        if id:
            lang = request.args.get('lang', None)
            current_lang = Language.query.filter_by(code=lang).first()
            posts_feed = Posts.query.filter_by(uuid=id).first()
            user1 = Users.query.filter_by(id=posts_feed.author).first()
            translation=Translated.query.filter(and_(
                    Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
            
            if user1 == user:
                return {
                    "results": {
                        "lang": lang,
                        'translated_feed': marshal(translation,lang_post)
                    }
                }, 200
            else:
                return {
                    'status':0,
                    'res':"you are not the author"
                    }, 200

                

@post.doc(
    security='KEY',
    params={'lang': 'Language'},
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
        500: 'internal server error, please contact admin and report '
    })
@post.route('/langarticle/<id>')
class homeArticle(Resource):
    def get(self, id):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if id:
            posts_feed = Posts.query.filter_by(uuid=id).first()
            user1 = Users.query.filter_by(id=posts_feed.author).first()
            translation=Translated.query.filter(and_(
                    Translated.post_id == posts_feed.id))
            
            if user1 == user:
                if translation.count() > 1:
                    return {
                        'status':1,
                        'res':"All translations available"
                    }, 200
                else:
                    trans=translation.first()
                    current_lang = Language.query.filter_by(id=trans.language_id).first()
                    return {
                        'status':0,
                        'res':current_lang.code
                    }, 200