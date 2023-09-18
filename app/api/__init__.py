from flask import Blueprint, url_for
api = Blueprint('api', __name__, template_folder='../templates')
from flask_restplus import Api, Resource, fields, reqparse, marshal
from flask import Blueprint, render_template, abort, request, session
from flask_cors import CORS
from functools import wraps
from tqdm import tqdm
from flask import current_app as app
from datetime import datetime, timedelta
from app import db, limiter, cache, bycrypt, createapp  
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from werkzeug.utils import redirect
import werkzeug
import json
import shortuuid
import jwt
import uuid
import os
from flask import current_app as app
from sqlalchemy import func, or_, and_
import re
import random

import stripe
from .v1 import user, info, token, search, post, payment
from app.models import Report, Users, Language, Save, Setting, \
    Posttype, Rating, Ratingtype, Translated, Posts, Reporttype, Post_Access, Tags
from sqlalchemy import or_, and_, desc, asc
from flask import current_app as app


from config import Config
from datetime import datetime

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration





# with app.app_context().push():
stripe.api_key = Config.stripe_secret_key
# API security eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiZmFiaWVuIiwidXVpZCI6ImJlNTM1NDBlLWExMzItNDJiNy1iNzlkLTI4MWFhZGM1MWZjMyIsImV4cCI6MTYzMDg2ODQ1OCwiaWF0IjoxNjI4Mjc2NDU4fQ.u4KyP0J3qzV0coE3-kozIKI0sc8ZrEUYMWvUbQbSHQM
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
                data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated


v = 0
if v == 1:
    @property
    def specs_url(self):
        return url_for(self.endpoint('specs'), _external=True, _scheme='https')
    Api.specs_url = specs_url

# class MyApi(Api):
    # @property
    # def specs_url(self):
    #"""Monkey patch for HTTPS"""
    #scheme = 'http' if '8000' in self.base_url else 'https'
    # return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


apisec = Api(app=api, doc='/docs', version='1.9.0', title='Odaaay API.',
             description='This documentation contains all routes to access the Odaaay API. \npip install googletransSome routes require authorization and can only be gotten \
    from the odaaay company', license='../LICENSE', license_url='www.odaaay.com', contact='leslie.etubo@gmail.com', authorizations=authorizations)
CORS(api, resources={r"/api/*": {"origins": "*"}})

from . import schema
from app.services import mail, phone
uploader = apisec.parser()
uploader.add_argument('file', location='files', type=FileStorage,
                      required=True, help="You must parse a file")
uploader.add_argument('name', location='form', type=str,
                      required=True, help="Name cannot be blank")

apisec.add_namespace(info)
apisec.add_namespace(user)
apisec.add_namespace(token)
apisec.add_namespace(post)
apisec.add_namespace(search)
apisec.add_namespace(payment)




login = apisec.namespace('/api/auth',
                         description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ',
                         path='/v1/')

signup = apisec.namespace('/api/auth',
                          description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ',
                          path='/v1/')

home = apisec.namespace('/api/home',
                        description="All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.",
                        path='/v1/')

message = apisec.namespace('/api/mesage/user*',
                           description="All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.",
                           path='/v1/')


@login.doc(
    params={},

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
@login.route('/auth/login')
class Login_email(Resource):
    # @limiter.limit("1/hour")
    # Limiting the user request to localy prevent DDoSing
    @login.expect(schema.full_login)
    def post(self):
        app.logger.info('User login with user_name')
        count = 5
        req_data = request.get_json()
        email = req_data['email']
        password = req_data['password']
        user1 = Users.query.filter_by(email=email).first()
        if user1:
            if user1.verified_email == True:
                if user1.verify_password(password) != False:
                    user1.tries = 0
                    if user1.customer_id == None:
                        customer = stripe.Customer.create(
                            email=email,  # see if phone number can be used
                            payment_method='pm_card_visa',
                            invoice_settings={
                                'default_payment_method': 'pm_card_visa',
                            },
                        )
                        user1.customer_id = customer['id']
                    db.session.commit()
                    token = jwt.encode({
                        'user': user1.username,
                        'uuid': user1.uuid,
                        'exp': datetime.utcnow() + timedelta(days=30),
                        'iat': datetime.utcnow()
                    },
                        app.config.get('SECRET_KEY'),
                        algorithm='HS256')
                    data={
                        'uuid':user1.uuid,
                        'id':user1.id,
                        'name':user1.username,
                        'profile_picture':user1.picture ,
                        'email':user1.email,
                        'background':user1.background,
                        'handle':user1.handle,
                    }
                    return {
                        'status': 1,
                        'res': 'success',
                        'uuid': user1.uuid,
                        'token': str(token),
                        'data':data
                    }, 200

                else:
                    if user1.tries < count:
                        user1.tries += 1
                        db.session.commit()
                        return {'status': 0,'res': 'Wrong password'}, 401

                    if user1.tries >= count:
                        user1.user_visibility = False
                        db.session.commit()
                        return {'res': 'Your account is blocked,contact service'}, 401
            else:
                user1.code=int(random.randrange(100000, 999999))
                db.session.commit()
                mail.verify_email(email,user1.code)
                return {
                    'status': 6,
                    'res': 'User account deactivated,a mail has been sent to verify your account'
                }, 200
        else:
            return {
                'status': 7,
                'res': 'User does not exist'
            }, 200


@signup.doc(
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
@signup.route('/auth/signup')
class Signup_email(Resource):
    # Limiting the user request to localy prevent DDoSing
    #@limiter.limit("10/hour")
    @signup.expect(schema.signupdataemail)
    def post(self):
        signup_data = request.get_json()
        if signup_data:
            # lang
            username = signup_data['user_name'] or None
            email1 = signup_data['email']
            password = signup_data['password'] or None
            code = signup_data['code'] or None
            email = Users.query.filter_by(email=email1).first()
            user = Users.query.filter_by(username=username).first()
            if code is not None:
                if user.verified_email == False:
                    if user.code == code : #and user.code_expires_in < datetime.now() :
                        link ='https://odaaay.com/'+'en/login'
                        user.verified_email = True
                        user.user_visibility = True
                        db.session.commit()
                        mail.welcome_email(user.email,user.username)
                        token = jwt.encode({
                            'user': user.username,
                            'uuid': user.uuid,
                            'exp': datetime.utcnow() + timedelta(days=30),
                            'iat': datetime.utcnow()
                        },
                            app.config.get('SECRET_KEY'),
                            algorithm='HS256')
                        data={
                            'uuid':user.uuid,
                            'id':user.id,
                            'name':user.username,
                            'profile_picture':user.picture ,
                            'email':user.email,
                            'background':user.background,
                            'handle':user.handle,
                        }
                        return {'status': 1,
                                    'res': 'success',
                                    'uuid': user.uuid,
                                    'token': str(token),
                                    'data':data
                                },200
                    else:
                        return {
                        'status': 0,
                        'res': 'Code has been taken'
                    }, 200
                else:
                    return {
                        'status': 0,
                        'res': 'Code has been sent'
                    }, 200
            if email is not None:
                return {
                    'status': 1,
                    'res': 'email is taken'
                }, 200
            if user is not None:
                return {
                    'status': 2,
                    'res': 'user_name is taken'
                }, 200
            lang = signup_data['lang'] or None
            language= Language.query.filter_by(code=lang).first()
            new = Users(username, str(uuid.uuid4()), False, email1)
            db.session.add(new)
            new.passwordhash(password)
            new.language_id=language.id
            new.code=int(random.randrange(100000, 999999))
            new.rescue=uuid.uuid4()
            new.code_expires_in=datetime.utcnow() + timedelta(days=1)
            db.session.commit()
            link = 'https://odaaay.co/api/v1/auth/email_verification/' + \
                str(new.uuid)
            mail.verify_email(email1,new.code)
            return {
                'status': 3,
                'res': 'please verify your account'
            }, 200

        else:
            return {
                'status': 0,
                'res': 'No data'
            }, 201


@signup.doc(
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
@signup.route('/auth/resetpassword')
class Reset(Resource):
    # Limiting the user request to localy prevent DDoSing
    #@limiter.limit("10/hour")
    @signup.expect(schema.resetpassword)
    def post(self):
        signup_data = request.get_json()
        if signup_data:
            email = signup_data['email']
            lang = signup_data['lang']
            check = Users.query.filter_by(email=email).first()
            if check:
                verification_code = phone.generate_code()
                token = check.get_reset_token()
                if lang=='en':
                    link='https://odaaay.com/app/resetpassword'
                else:
                    link='https://odaaay.com/'+lang+'/app/resetpassword'
                
                mail.reset_password(email, link)
                return {
                    'status': 1,
                    'res': 'email has been sent'
                }, 200
            else:
                return {
                    'status': 0,
                    'res': 'user not found'
                }, 201


@signup.doc(
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
@signup.route('/auth/confirmpassword')
class Confirmp(Resource):
    # Limiting the user request to localy prevent DDoSing
    #@limiter.limit("10/hour")
    @signup.expect(schema.confirmpassword)
    def post(self):
        signup_data = request.get_json()
        if signup_data:
            token = signup_data['token']
            check = Users.verify_reset_token(token)
            if check is not None:
                check.passwordhash(signup_data['password'])
                check.verified_email = True
                check.user_visibility = True
                db.session.commit()
                return {
                    'status': 1,
                    'res': 'user password has been reset'
                }, 200
            else:
                return {
                    'status': 0,
                    'res': 'token has expired,please get a new token'
                }, 201


@signup.route('/auth/email_verification/<uuid>')
class email_verification(Resource):
    # Limiting the user request to localy prevent DDoSing
    # @limiter.limit("10/hour")
    # @signup.expect(schema.verifyemail)
    def get(self, uuid):
        if uuid:
            exuser = Users.query.filter_by(uuid=uuid).first()
            if exuser:
                link = 'https://odaaay.com/en/login'
                exuser.verified_email = True
                exuser.user_visibility = True
                db.session.commit()
                mail.welcome_email(exuser.email)
                return redirect(link)

            else:
                return {
                    'res': 'User doesnt exist',
                    'status': 1
                }, 200
# Home still requires paginated queries for user's phone not to load forever


@cache.cached(300, key_prefix='all_home_posts')
@home.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'lang': 'i18n',
            'paid': 'if is for paid posts or not',
            'category': 'category of posts',
            'tag': 'tag of posts',
             'count': 'Number results per page',
            'recent': 'recent posts',
             'id': 'Article id'},
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
@home.route('/home')
class Home(Resource):
    def get(self):
        # user getting data for their home screen
        try:
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
        except:
            user = None
        saved = []
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', None)
            pay = request.args.get('paid', None)
            cat = request.args.get('category', None)
            tag = request.args.get('tag', None)
            post_type = request.args.get('ptype', '1')
            recent = request.args.get('recent', None)
            # Still to fix the next and previous WRT Sqlalchemy
            language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}

            for i in language_dict:
                if i == lang: 
                    current_lang = Language.query.filter_by(code=i).first()
                    if pay == None:
                        if recent == 'recent':
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(desc(Posts.created_on)).filter(and_(Posts.paid == False,Posts.thumb_url != None,Posts.nsfw == False))

                        if recent == 'thumb':
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False,Posts.thumb_url == None,Posts.nsfw == False))

                        if cat == None and tag == None and recent == None:
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False,Posts.thumb_url != None,Posts.nsfw == False))#.order_by(func.random())
                        
                        if cat == None and tag == None and recent == 'thumb':
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False,Posts.thumb_url == None,Posts.nsfw == False))

                        if cat != None and tag == None:
                            posts_feeds = Translated.query.filter(and_(Translated.language_id == current_lang.id, Translated.category_id == cat)).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False,Posts.thumb_url != None,Posts.nsfw == False))
                        
                        if cat != None and tag == None and recent == 'thumb':
                            posts_feeds = Translated.query.filter(and_(Translated.language_id == current_lang.id, Translated.category_id == cat)).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False,Posts.thumb_url == None,Posts.nsfw == False))

                        if tag != None and cat == None:
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(Posts).join(
                                Tags, (Tags.post == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False, Tags.tags == tag,Posts.thumb_url != None))
                        
                        if tag != None and cat == None and recent == 'thumb':
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(Posts).join(
                                Tags, (Tags.post == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False, Tags.tags == tag,Posts.thumb_url == None,Posts.nsfw == False))

                        if tag != None and cat != None:
                            posts_feeds = Translated.query.filter(and_(Translated.language_id == current_lang.id, Translated.category_id == cat)).join(
                                Posts).join(Tags, (Tags.post == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False, Tags.tags == tag ,Posts.thumb_url != None,Posts.nsfw == False))
                        
                        if tag != None and cat != None and recent == 'thumb':
                            posts_feeds = Translated.query.filter(and_(Translated.language_id == current_lang.id, Translated.category_id == cat)).join(
                                Posts).join(Tags, (Tags.post == Translated.post_id)).order_by(asc(Posts.created_on)).filter(and_(Posts.paid == False, Tags.tags == tag ,Posts.thumb_url == None,Posts.nsfw == False))
                                
                        posts_feed = posts_feeds.paginate(    
                            int(start), int(count), False)
                        total = (posts_feed.total/int(count))
                        next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(
                            limit), count=int(count)) if posts_feed.has_next else None
                        previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(
                            limit), count=int(count)) if posts_feed.has_prev else None
                        feed=posts_feed.items
                        all=[]
                        
                        #for i in feed:
                           # all.append(i.post_id)

                        if user is not None:
                            user_saves = Save.query.filter_by(
                                user_id=user.id).order_by(Save.id.desc()).all()
                            user_posts = posts_feeds.all()
                            for i in user_posts:
                                for j in user_saves:
                                    if i.post_id == j.post_id:
                                        saved.append(j.post_id)
                            feed = posts_feed.items
                            if cat == None and tag == None and recent == None:
                                random.shuffle(feed)
                            inte=[]
                            for i in feed:
                                post = Posts.query.filter_by(
                                    id=i.post_id).first()
                                if post.not_interested(user):
                                    feed.remove(i)
                                    inte.append(i.post_id)
                            return {
                                "start": start,
                                "limit": limit,
                                "count": count,
                                "next": next_url,
                                "lang": lang,
                                "previous": previous,
                                "totalPages": total,
                                "results": {
                                    'post_saved': saved,
                                    "not_interest":inte,
                                    "feed": marshal(feed, schema.lang_post)
                                }
                            }, 200
                        else:
                            return {
                                "start": start,
                                "limit": limit,
                                "count": count,
                                "next": next_url,
                                "lang": lang,
                                "previous": previous,
                                "totalPages": total,
                                "results": {
                                    'feed': marshal(posts_feed.items, schema.lang_post)
                                    #'all':all,
                                }
                            }, 200
                    if pay == 'paid':#Posts.paid == True
                        if recent == 'recent':
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(asc(Posts.created_on)).filter(Posts.thumb_url != None)
                        if cat == None and tag == None:
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(desc(Posts.created_on)).filter(Posts.thumb_url != None)
                        if cat != None and tag == None:
                            posts_feeds = Translated.query.filter(and_(Translated.language_id == current_lang.id, Translated.category_id == cat)).join(
                                Posts,(Posts.id == Translated.post_id)).order_by(desc(Posts.created_on)).filter(Posts.thumb_url != None)
                        if tag != None and cat == None:
                            posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(Posts).join(
                                Tags, (Tags.post == Translated.post_id)).order_by(desc(Posts.created_on)).filter(and_(Posts.thumb_url != None, Tags.tags == tag))
                        if tag != None and cat != None:
                            posts_feeds = Translated.query.filter(and_(Translated.language_id == current_lang.id, Translated.category_id == cat)).join(
                                Posts).join(Tags, (Tags.post == Translated.post_id)).order_by(desc(Posts.created_on)).filter(and_(Posts.thumb_url != None, Tags.tags == tag))
                        posts_feed = posts_feeds.paginate(
                            int(start), int(count), False)
                        total = (posts_feed.total/int(count))
                        next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(
                            limit), count=int(count)) if posts_feed.has_next else None
                        previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(
                            limit), count=int(count)) if posts_feed.has_prev else None

                        if user is not None:
                            user_saves = Save.query.filter_by(
                                user_id=user.id).order_by(Save.id.desc()).all()
                            user_posts = posts_feeds.all()
                            for i in user_posts:
                                for j in user_saves:
                                    if i.post_id == j.post_id:
                                        saved.append(j.post_id)
                            feed = posts_feed.items
                            for i in feed:
                                post = Posts.query.filter_by(
                                    id=i.post_id).first()
                                if post.not_interested(user):
                                    feed.remove(i)
                            return {
                                "start": start,
                                "limit": limit,
                                "count": count,
                                "next": next_url,
                                "lang": lang,
                                "previous": previous,
                                "totalPages": total,
                                "results": {
                                    'post_saved': saved,
                                    "feed": marshal(feed, schema.lang_post)
                                }
                            }, 200
                        else:
                            return {
                                "start": start,
                                "limit": limit,
                                "count": count,
                                "next": next_url,
                                "lang": lang,
                                "previous": previous,
                                "totalPages": total,
                                "results": {
                                    'feed': marshal(posts_feed.items, schema.lang_post)
                                }
                            }, 200
        '''else:
            posts_trending = Posts.query.limit(10).all()
            posts_feed = Posts.query.limit(10).all()
            posts_discover = Posts.query.limit(10).all()
            if user is not None:
                user_saves=Save.query.filter_by(user_id=user.id).order_by(Save.id.desc()).all()
                for i,j in zip(posts_feed,user_saves):
                    if i.id == j.post_id :
                        saved.append(j.post_id)
                return {
                    'post_saved':saved,
                    'feed': marshal(posts_feed, schema.postdata)
                }, 200       
            else:
                return {
                    'feed': marshal(posts_feed, schema.postdata)
                }, 200 '''


@cache.cached(300, key_prefix='all_video_posts')
@home.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
             'id': 'Article id',
            'lang': 'Language'},
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
@home.route('/video')
class Videos(Resource):
    def get(self):
        # user getting data for their home screen
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', None)
            post_type = request.args.get('ptype', '1')
            # Still to fix the next and previous WRT Sqlalchemy
            language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
            for i in language_dict:
                if i == lang:
                    current_lang = Language.query.filter_by(code=i).first()
                    posts_feed = Translated.query.filter_by(language_id=current_lang.id).join(Posts).order_by(
                        func.random()).filter(Posts.post_type == 2).paginate(int(start), int(count), False)
                    total = (posts_feed.total/int(count))
                    next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(
                        limit), count=int(count)) if posts_feed.has_next else None
                    previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(
                        limit), count=int(count)) if posts_feed.has_prev else None
                    return {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next_url,
                        "lang": lang,
                        "previous": previous,
                        "totalPages": total,
                        "results": {
                            'feed': marshal(posts_feed.items, schema.lang_post)
                        }
                    }, 200
        else:
            posts_trending = Posts.query.limit(10).all()
            posts_feed = Posts.query.limit(10).all()
            posts_discover = Posts.query.limit(10).all()
            return {
                'feed': marshal(posts_feed, schema.postdata)
            }, 200


@home.route('/discover')
class Discover(Resource):
    def get(self):
        # user getting data for their home screen
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', None)
            post_type = request.args.get('ptype', '1')
            # Still to fix the next and previous WRT Sqlalchemy
            language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
            for i in language_dict:
                if i == lang:
                    current_lang = Language.query.filter_by(code=i).first()
                    posts_feed = Translated.query.filter_by(language_id=current_lang.id).join(Posts).order_by(desc(Posts.id)).filter(
                        and_(Posts.thumb_url != None, Posts.paid == False)).paginate(int(start), int(count), False)
                    total = (posts_feed.total/int(count))
                    next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(
                        limit), count=int(count)) if posts_feed.has_next else None
                    previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(
                        limit), count=int(count)) if posts_feed.has_prev else None
                    return {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next_url,
                        "lang": lang,
                        "previous": previous,
                        "totalPages": total,
                        "results": {
                            'feed': marshal(posts_feed.items, schema.lang_post)
                        }
                    }, 200
        else:
            posts_trending = Posts.query.limit(10).all()
            posts_feed = Posts.query.limit(10).order_by(desc(Posts.id)).all()
            posts_discover = Posts.query.limit(10).all()
            return {
                'feed': marshal(posts_feed, schema.postdata)
            }, 200


@home.route('/related')
class Related(Resource):
    def get(self):
        # user getting data for their home screen
        if request.args:
            start = request.args.get('start', None)
            limit = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', None)
            post_type = request.args.get('ptype', '1')
            # Still to fix the next and previous WRT Sqlalchemy
            language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
            for i in language_dict:
                if i == lang:
                    current_lang = Language.query.filter_by(code=i).first()
                    posts_feed = Translated.query.filter_by(language_id=current_lang.id).join(Posts).filter(
                        Posts.post_type == 2).order_by(func.random()).paginate(int(start), int(count), False)
                    total = (posts_feed.total/int(count))
                    next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(
                        limit), count=int(count)) if posts_feed.has_next else None
                    previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(
                        limit), count=int(count)) if posts_feed.has_prev else None
                    return {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next_url,
                        "lang": lang,
                        "previous": previous,
                        "totalPages": total,
                        "results": {
                            'feed': marshal(posts_feed.items, schema.lang_post)
                        }
                    }, 200
        else:
            posts_trending = Posts.query.limit(10).all()
            posts_feed = Posts.query.limit(10).order_by(desc(Posts.id)).all()
            posts_discover = Posts.query.limit(10).all()
            return {
                'feed': marshal(posts_feed, schema.postdata)
            }, 200


@cache.cached(300, key_prefix='article')
@home.doc(
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
@home.route('/homearticle/<id>')
class homeArticle(Resource):
    def get(self, id):
        language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
        try:
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
            saved = []
        except:
            user = None
        if request.args:
            if id:
                lang = request.args.get('lang', None)
                current_lang = Language.query.filter_by(code=lang).first()
                posts_feed = Posts.query.filter_by(uuid=id).first()
                #trans=Translated.query.filter(and_(Translated.post_id==posts_feed.id,Translated.language_id==current_lang.id)).first()
                user1 = Users.query.filter_by(id=posts_feed.author).first()
                saves = Save.query.filter_by(post_id=posts_feed.id).count()
                report = Report.query.filter_by(post_id=posts_feed.id).count()
                count_claps = posts_feed.No__claps()
                if posts_feed.paid == True:
                    p = 1
                else:
                    p = 0
                if user:
                    return {
                        "results": {
                            "status": p,
                            "lang": lang,
                            "shouts": count_claps,
                            "saves": saves,
                            "report": report,
                            'translated_feed': marshal(posts_feed, schema.postdata)
                        }
                    }, 200


@cache.cached(300, key_prefix='article')
@home.doc(
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
@home.route('/article/<id>')
class Article(Resource):
    def get(self, id):
        language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
        try:
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            user = Users.query.filter_by(uuid=data['uuid']).first()
        except:
            user = None
        if request.args:
            if id:
                lang = request.args.get('lang', None)
                current_lang = Language.query.filter_by(code=lang).first()
                posts_feed = Posts.query.filter_by(uuid=id).first()
                
                if posts_feed == None:
                    return {
                    'status': 6,
                    'res': 'article not found'
                    }, 404
                user1 = Users.query.filter_by(id=posts_feed.author).first()
                saves = Save.query.filter_by(post_id=posts_feed.id).count()
                report = Report.query.filter_by(post_id=posts_feed.id).count()
                translated_feed = Translated.query.filter(and_(
                    Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                count_claps = posts_feed.No__claps()
                if user is not None:
                    dona = Post_Access.query.filter(
                        and_(Post_Access.user == user.id, Post_Access.post == posts_feed.id)).first()
                    if dona:
                        d = True
                    else:
                        d = False
                    if user1.id == user.id:
                        if translated_feed:
                            return {
                                "results": {
                                    "status": 4,
                                    "lang": lang,
                                    "shouts": count_claps,
                                    "saves": saves,
                                    "report": report,
                                    'translated_feed': marshal(translated_feed, schema.lang_post)
                                }
                            }, 200
                        else:
                            current_lang = Language.query.filter_by(
                                id=posts_feed.orig_lang).first()
                            translated_feed = Translated.query.filter(and_(
                                Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                            return {
                                "results": {
                                    "status": 5,
                                    "lang": lang,
                                    "original_lang": current_lang.code,
                                    "shouts": count_claps,
                                    "saves": saves,
                                    "report": report,
                                    'translated_feed': marshal(translated_feed, schema.lang_post),
                                    'res': "This post can't been translated"
                                }
                            }, 200
                    if posts_feed.donation_id != None and posts_feed.subs_only == True:
                        follow = user.is_following(user1)
                        if follow:
                            if translated_feed:
                                return {
                                    "results": {
                                        "status": 5,
                                        "lang": lang,
                                        "shouts": count_claps,
                                        "saves": saves,
                                        "report": report,
                                        'uuid': user1.uuid,
                                        'donated': d,
                                        'translated_feed': marshal(translated_feed, schema.lang_post)
                                    }
                                }, 200
                            else:
                                current_lang = Language.query.filter_by(
                                    id=posts_feed.orig_lang).first()
                                translated_feed = Translated.query.filter(and_(
                                    Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                                return {
                                    "results": {
                                        "status": 5,
                                        "lang": lang,
                                        "original_lang": current_lang.code,
                                        "shouts": count_claps,
                                        "saves": saves,
                                        "report": report,
                                        'uuid': user1.uuid,
                                        'donated': d,
                                        'translated_feed': marshal(translated_feed, schema.lang_post),
                                        'res': "This post can't been translated"
                                    }
                                }, 200
                        else:
                            return {
                                "status": 2,
                                "uuid": user1.uuid,
                                'uploader_data': [marshal(user1, schema.users_dat1)],
                                "res": "Please subscribe to have access to this post"
                            }, 200
                    if posts_feed.donation_id != None:
                        if translated_feed:
                            return {
                                "results": {
                                    "status": 5,
                                    "lang": lang,
                                    "shouts": count_claps,
                                    "saves": saves,
                                    "report": report,
                                    'uuid': user1.uuid,
                                    'donated': d,
                                    'translated_feed': marshal(translated_feed, schema.lang_post)
                                }
                            }, 200
                        else:
                            current_lang = Language.query.filter_by(
                                id=posts_feed.orig_lang).first()
                            translated_feed = Translated.query.filter(and_(
                                Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                            return {
                                "results": {
                                    "status": 5,
                                    "lang": lang,
                                    "original_lang": current_lang.code,
                                    "shouts": count_claps,
                                    "saves": saves,
                                    "report": report,
                                    'uuid': user1.uuid,
                                    'donated': d,
                                    'translated_feed': marshal(translated_feed, schema.lang_post),
                                    'res': "This post can't been translated"
                                }
                            }, 200
                    if posts_feed.subs_only == True:
                        follow = user.is_following(user1)
                        if follow:
                            if translated_feed:
                                return {
                                    "results": {
                                        "status": 0,
                                        "lang": lang,
                                        "shouts": count_claps,
                                        "saves": saves,
                                        "report": report,
                                        'translated_feed': marshal(translated_feed, schema.lang_post)
                                    }
                                }, 200
                            else:
                                current_lang = Language.query.filter_by(
                                    id=posts_feed.orig_lang).first()
                                translated_feed = Translated.query.filter(and_(
                                    Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                                return {
                                    "results": {
                                        "status": 0,
                                        "lang": lang,
                                        "original_lang": current_lang.code,
                                        "shouts": count_claps,
                                        "saves": saves,
                                        "report": report,
                                        'translated_feed': marshal(translated_feed, schema.lang_post),
                                        'res': "This post can't been translated"
                                    }
                                }, 200
                        else:
                            return {
                                "status": 2,
                                "uuid": user1.uuid,
                                'uploader_data': [marshal(user1, schema.users_dat1)],
                                "res": "Please subscribe to have access to this post"
                            }, 200

                    elif posts_feed.paid == True:
                        access = Post_Access.query.filter(
                            and_(Post_Access.user == user.id, Post_Access.post == posts_feed.id)).first()
                        if access:
                            if translated_feed:
                                return {
                                    "results": {
                                        "status": 0,
                                        "saves": saves,
                                        "report": report,
                                        "lang": lang,
                                        "shouts": count_claps,
                                        'translated_feed': marshal(translated_feed, schema.lang_post)
                                    }
                                }, 200
                            else:
                                current_lang = Language.query.filter_by(
                                    id=posts_feed.orig_lang).first()
                                translated_feed = Translated.query.filter(and_(
                                    Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                                return {
                                    "results": {
                                        "status": 0,
                                        "lang": lang,
                                        "original_lang": current_lang.code,
                                        "shouts": count_claps,
                                        "saves": saves,
                                        "report": report,
                                        'translated_feed': marshal(translated_feed, schema.lang_post),
                                        'res': "This post can't been translated"
                                    }
                                }, 200
                        else:
                            return {
                                "status": 1,
                                "uuid": user1.uuid,
                                'uploader_data': [marshal(user1, schema.users_dat1)],
                                "res": "Please pay for post"
                            }, 200
                    else:
                        if translated_feed:
                            return {
                                "results": {
                                    "status": 0,
                                    "lang": lang,
                                    "shouts": count_claps,
                                    "saves": saves,
                                    "report": report,
                                    "user_bio":user1.bio,
                                    'translated_feed': marshal(translated_feed, schema.lang_post)
                                }
                            }, 200
                        else:
                            current_lang = Language.query.filter_by(
                                id=posts_feed.orig_lang).first()
                            translated_feed = Translated.query.filter(and_(
                                Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                            return {
                                "results": {
                                    "status": 0,
                                    "lang": lang,
                                    "original_lang": current_lang.code,
                                    "shouts": count_claps,
                                    "saves": saves,
                                    "report": report,
                                    "user_bio":user1.bio,
                                    'translated_feed': marshal(translated_feed, schema.lang_post),
                                    'res': "This post can't been translated"
                                }
                            }, 200

                if posts_feed.subs_only == True:
                    return {
                        "status": 2,
                        "uuid": user1.uuid,
                        'uploader_data': [marshal(user1, schema.users_dat1)],
                        "res": "Please login and Subscribe"
                    }, 200

                if posts_feed.paid == True:
                    return {
                        "status": 1,
                        "uuid": user1.uuid,
                        'uploader_data': [marshal(user1, schema.users_dat1)],
                        "res": "Please login and pay for post"
                    }, 200
                if posts_feed.donation_id != None:
                    if translated_feed:
                        return {
                            "results": {
                                "status": 5,
                                "lang": lang,
                                "shouts": count_claps,
                                "saves": saves,
                                "report": report,
                                'uuid': user1.uuid,
                                'donated': True,
                                'translated_feed': marshal(translated_feed, schema.lang_post)
                            }
                        }, 200
                    else:
                        current_lang = Language.query.filter_by(
                            id=posts_feed.orig_lang).first()
                        translated_feed = Translated.query.filter(and_(
                            Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                        return {
                            "results": {
                                "status": 5,
                                "lang": lang,
                                "original_lang": current_lang.code,
                                "shouts": count_claps,
                                "saves": saves,
                                "report": report,
                                'uuid': user1.uuid,
                                'donated': True,
                                'translated_feed': marshal(translated_feed, schema.lang_post),
                                'res': "This post can't been translated"
                            }
                        }, 200
                else:
                    if translated_feed:
                        return {
                            "results": {
                                "status": 0,
                                "lang": lang,
                                "shouts": count_claps,
                                "saves": saves,
                                "report": report,
                                "user_bio":user1.bio,
                                'translated_feed': marshal(translated_feed, schema.lang_post)
                            }
                        }, 200
                    else:
                        current_lang = Language.query.filter_by(
                            id=posts_feed.orig_lang).first()
                        translated_feed = Translated.query.filter(and_(
                            Translated.post_id == posts_feed.id, Translated.language_id == current_lang.id)).first()
                        return {
                            "results": {
                                "status": 0,
                                "lang": lang,
                                "original_lang": current_lang.code,
                                "shouts": count_claps,
                                "saves": saves,
                                "report": report,
                                "user_bio":user1.bio,
                                'translated_feed': marshal(translated_feed, schema.lang_post),
                                'res': "This post can't been translated"
                            }
                        }, 200
            else:
                return {
                    'status': 6,
                    'res': 'article not found'
                }, 404
        else:
            posts_feed = Posts.query.filter_by(uuid=id).first()
            return {
                'feed': marshal(posts_feed, schema.postdata)
            }, 200
# if posts is unpaid and not for subs,shld he pay for post


@cache.cached(300, key_prefix='Report')
@home.doc(
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
@home.route('/reportpost/')
class Report_post_(Resource):
    @home.expect(schema.Reported_post)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post = Posts.query.filter_by(uuid=req_data['post_id']).first()
        lan = Reporttype(content="Fake news")
        lan1 = Reporttype(content="Vulgar Language")
        lan2 = Reporttype(content="Bad Translation")
        lan3 = Reporttype(content="Copyright")
        lan4 = Reporttype(content="Others")
        db.session.add(lan)
        db.session.add(lan1)
        db.session.add(lan2)
        db.session.add(lan3)
        db.session.add(lan4)
        db.session.commit()
        typo = [1, 2, 3, 4]
        rep = req_data['type']
        Length = len(req_data['type'])

        if user is None:
            return{
                "status": 0,
                "res": "Fail"
            }

        if post:
            if req_data['reason'] is None:
                for i in typo:
                    for a in rep:
                        if i == a:
                            Report_sent = Report(
                                reporter=user.id, post_id=post.id, user_reported=post.author, rtype=a)
                            db.session.add(Report_sent)
                            db.session.commit()
                return{
                    "status": 1,
                    "res": "Post has been reported"
                }
            if req_data['reason'] is not None:
                if Length == 1:
                    Report_sent = Report(
                        reason=req_data['reason'], reporter=user.id, post_id=post.id, user_reported=post.author, rtype=5)
                    db.session.add(Report_sent)
                    db.session.commit()
                    return{
                        "status": 1,
                        "res": "Post has been reported"
                    }
                if Length > 1:
                    Report_sent = Report(
                        reason=req_data['reason'], reporter=user.id, post_id=post.id, user_reported=post.author, rtype=5)
                    db.session.add(Report_sent)
                    db.session.commit()
                    for i in typo:
                        for a in rep:
                            if i == a:
                                Report_sent = Report(
                                    reporter=user.id, post_id=post.id, user_reported=post.author, rtype=a)
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

        else:
            return{
                "status": 0,
                "res": "Fail"
            }
            # fff


@cache.cached(300, key_prefix='all_saves')
@home.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page'},
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
@home.route('/Save/')
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
                    desc(Save.id)).paginate(int(start), int(count), False).items
                if user_saves:
                    return {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next,
                        "previous": previous,
                        "results": marshal(user_saves, schema.saved)
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

    @home.expect(schema.saves_post)
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
            return{
                "status": 1,
                "res": "deleted"
            }
        else:
            return{
                "status": 0,
                "res": "Fail"
            }

    @home.expect(schema.saves_post)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post = Posts.query.filter_by(uuid=req_data['Post_id']).first()
        Saves = Save.query.filter(
            and_(Save.user_id == user.id, Save.post_id == post.id)).first()
        if Saves:
            db.session.delete(Saves)
            db.session.commit()
            return{
                "status": 0,
                "res": "Post has  been unsaved"
            }
        if post:
            save = Save(user.id, post.id)
            db.session.add(save)
            db.session.commit()
            return{
                "status": 1,
                "res": "Post has been saved"
            }, 200

        else:
            return{
                "status": 0,
                "res": "Fail"
            }


@cache.cached(300, key_prefix='all_recents')
@home.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page'},
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
@home.route('/post/recent')
class recent_post(Resource):
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
            user = 1
            if user:
                user_saves = Posts.query.order_by(desc(Posts.id)).paginate(
                    int(start), int(count), False).items
                if user_saves:
                    return {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next,
                        "previous": previous,
                        "results": marshal(user_saves, schema.postdata)
                    }, 200
                else:
                    return{
                        "status": 0,
                        "res": "No posts"
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


@message.doc(
    security='KEY',
    params={'id': 'ID of the post'},
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
@message.route('/message/<user>')
class Message(Resource):
    @token_required
    @message.marshal_with(schema.homedata)
    def get(self):
        return {}, 200


@cache.cached(300, key_prefix='Not_interested')
@home.doc(
    security='KEY',
    params={'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page'},
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
@home.route('/post/notinterested')
class notinterested(Resource):
    @home.expect(schema.Not_Interested)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post = Posts.query.filter_by(uuid=req_data['uuid']).first()
        if post.not_interested(user) is None:
            post.is_not_interested(user)

            return{
                "status": 1,
                "res": "Post has been added to noninterested"
            }, 200
        else:
            return{
                "status": 0,
                "res": "Post was already set into notinterested"
            }, 200
