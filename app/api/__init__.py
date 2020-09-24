from flask import Blueprint, url_for
from app.services import mail, phone
from flask_restplus import Api, Resource, fields, reqparse, marshal
from flask import Blueprint, render_template, abort, request, session
from flask_cors import CORS
from functools import wraps
from tqdm import tqdm
from flask import current_app as app
from datetime import datetime, timedelta
from app import db, limiter, cache,bycrypt
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import werkzeug
import jwt, uuid, os
from flask import current_app as app
from sqlalchemy import func
from .v1 import user, info, token, search, post, comment, channel
from app.models import Users, Channels, subs, Language, Save, Setting, Message, Comment, \
    Posts, Postarb, Posten, Postfr, Posthau, Postpor, \
        Postsw, Postes, Posttype, Rating, Ratingtype, postchannel

# API security
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

api = Blueprint('api', __name__, template_folder = '../templates')
apisec = Api( app=api, doc='/docs', version='1.9.0', title='Odaaay API.', \
    description='This documentation contains all routes to access the Odaaay API. \npip install googletransSome routes require authorization and can only be gotten \
    from the odaaay company', license='../LICENSE', license_url='www.odaaay.com', contact='leslie.etubo@gmail.com', authorizations=authorizations)
CORS(api, resources={r"/api/*": {"origins": "*"}})

from . import schema
uploader = apisec.parser()
uploader.add_argument('file', location='files', type=FileStorage, required=True, help="You must parse a file")
uploader.add_argument('name', location='form', type=str, required=True, help="Name cannot be blank")

apisec.add_namespace(info)
apisec.add_namespace(user)
apisec.add_namespace(token)
apisec.add_namespace(post)
apisec.add_namespace(channel)
apisec.add_namespace(search)
apisec.add_namespace(comment)


login = apisec.namespace('/api/auth', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ', \
    path='/v1/')

signup = apisec.namespace('/api/auth', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ', \
    path='/v1/')

home = apisec.namespace('/api/home', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

message = apisec.namespace('/api/mesage/user*', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

 

@login.doc(
    params={ 
            'phone': 'User phone number',
            'code': 'verification code'},

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
@login.route('/auth/phone_login')
class Login(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("1/hour")
    def post(self):
        app.logger.info('User login in')
        if request.args:
            number = request.args.get('phone', None)
            code = request.args.get('code', None)
            user = Users.query.filter_by(user_number=number).first()
            if user is not None:
                if code:
                    if (str(user.code) == str(code)) and not (datetime.utcnow() > user.code_expires_in):
                        token = jwt.encode({
                            'user': user.username,
                            'uuid': user.uuid,
                            'exp': datetime.utcnow() + timedelta(days=30),
                            'iat': datetime.utcnow()
                        },
                        app.config.get('SECRET_KEY'),
                        algorithm='HS256')
                        return {
                            'status': 1,
                            'res': 'success',
                            'token': str(token)
                        }, 200
                    else:
                        return {
                            'status': 0,
                            'res': 'verification fail make sure code is not more than 5 mins old'
                            }, 200
                else:
                    verification_code = '123456'
                    user.code = verification_code
                    user.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                    #db.session.add(newuser)
                    db.session.commit()
                    # phone.send_confirmation_code(request.args.get('phone', None))
                    return {
                        'status': 1,
                        'res': 'verification sms sent'
                        }, 201
            else:
                return {
                    'status': 0,
                    'res': 'user does not exist sign up'
                    },200
        else:
           return {
               'status': 0,
               'res': 'Invalid request'
               }, 500

@login.doc(
    params={
            'username':'Username',
            'password': 'password'},

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
@login.route('/auth/email_login')
class Login_email(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("1/hour")
    def post(self):
        app.logger.info('User login with user_name')
        data = request.get_json()
        if data:
            user_name = data['username']
            password = data['password']
            user = Users.query.filter_by(username=user_name).first()
            if user :
                if password:
                    if user.verify_password(password) and user.verified == True:
                        token = jwt.encode({
                            'user': user.username,
                            'uuid': user.uuid,
                            'iat': datetime.utcnow()
                        },
                        app.config.get('SECRET_KEY'),
                        algorithm='HS256')
                        string_token = str(token)
                        return {
                            'status': 1,
                            'res': 'success',
                            'token': string_token
                        }, 201
                    else:
                        return {'res': 'Your Password is wrong or you not verified'}, 401
                else:
                    default_password = '123456'
                    user.password = default_password
                    db.session.commit()
                    return {'res': 're_enter password'}, 301
            else:
                return {'res': 'User does not exist'}, 401
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
@signup.route('/auth/phone_signup')
class Signup(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("10/hour")
    @signup.expect(schema.signupdata)
    def post(self):
        signup_data = request.get_json()
        number = signup_data['phonenumber']
        exuser = Users.query.filter_by(user_number=number).first() #filter also by userhandle
        if signup_data:
            if exuser:
                return { 
                    'res':'user already exist',
                    'status':0
                }, 200
            else:
                number = signup_data['phonenumber']
                verification_code = '123456'
                # phone.send_confirmation_code(number)
                if verification_code:
                    newuser = Users('', True, number=int(signup_data['phonenumber']))
                    newuser.code = verification_code
                    newuser.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                    db.session.add(newuser)
                    db.session.commit()
                    return {
                        'status': 1,
                        'res': 'success',
                        'phone': signup_data['phonenumber']
                    }, 200
                else:
                    return {
                        'status': 0,
                        'results':'error'
                    }, 201
        else:
            return {
                'status': 0,
                'results':'error'
            },201

@signup.route('/auth/email_signup')
class Signup_email(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("10/hour")
    @signup.expect(schema.signupdataemail)
    def post(self):
        signup_data = request.get_json()
        email = signup_data['email']
        
        user = Users.query.filter_by(email=email).first() #filter by user handle
        if signup_data:
            if user:
                return { 
                    'res':'user already exist',
                    'status': 0
                }, 200
            else:
                email = signup_data['email']
                verification_code = '123456'

                if verification_code:
                    newuser = Users('', True, signup_data['email'])
                    newuser.code = verification_code
                    newuser.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                    db.session.add(newuser)
                    db.session.commit()
                    #send code to email
                    mail.send_email([signup_data['email']],verification_code) 
                    return {
                        'res': 'success',
                        'email': signup_data['email'],
                        'status': 1
                    }, 200
                else:
                    return {
                        'status': 0,
                        'res':'error'
                    }, 201
        else:
            return {
                'status': 0,
                'res': 'No data'
            },201

@signup.route('/auth/email_verification')
class email_verification(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("10/hour")
    @signup.expect(schema.verifyemail)
    def post(self):
        signup_data = request.get_json()
        email = signup_data['Email']
        exuser = Users.query.filter_by(email=email).first()
        if exuser:
            if exuser.code == int(signup_data['verification_code']) and not (datetime.utcnow() > exuser.code_expires_in):
                exuser.verified = True
                db.session.commit()
                return {
                        'res': "user is verified",
                        'status': 1
                    }, 200
            else:
                return {
                    'res': "user code wrong or expired",
                    'status': 0
                }, 200
        else:
            return {
                    'res': 'User doesnt exist',
                    'status': 1
                }, 200
# Home still requires paginated queries for user's phone not to load forever
@cache.cached(300, key_prefix='all_home_posts')
@home.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'lang': 'i18n',
            'count': 'Number results per page',
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
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', None)
            post_type = request.args.get('ptype', '1')
            # Still to fix the next and previous WRT Sqlalchemy
            language_dict = {'en': Posten, 'es': Postes, 'ar': Postarb, 'pt': Postpor, 'sw': Postsw, 'fr': Postfr, 'ha': Posthau}
            for i in language_dict:
                if i == lang:
                    table = language_dict.get(i)
                    posts_feed = table.query.order_by(func.random()).paginate(int(start), int(count), False)
                    total = (posts_feed.total/int(count))
                    next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(limit), count=int(count)) if posts_feed.has_next else None 
                    previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(limit), count=int(count)) if posts_feed.has_prev else None 
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

@cache.cached(300, key_prefix='all_video_posts')
@home.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
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
@home.route('/video')
class Videos(Resource): 
    def get(self):
        # user getting data for their home screen
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', None)
            post_type = request.args.get('ptype', '1')
            # Still to fix the next and previous WRT Sqlalchemy
            language_dict = {'en': Posten, 'es': Postes, 'ar': Postarb, 'pt': Postpor, 'sw': Postsw, 'fr': Postfr, 'ha': Posthau}
            for i in language_dict:
                if i == lang:
                    table = language_dict.get(i)
                    posts_feed = table.query.join(Posts).order_by(func.random()).filter(Posts.post_type==2).paginate(int(start), int(count), False)
                    total = (posts_feed.total/int(count))
                    next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(limit), count=int(count)) if posts_feed.has_next else None 
                    previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(limit), count=int(count)) if posts_feed.has_prev else None 
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
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', None)
            post_type = request.args.get('ptype', '1')
            # Still to fix the next and previous WRT Sqlalchemy
            language_dict = {'en': Posten, 'es': Postes, 'ar': Postarb, 'pt': Postpor, 'sw': Postsw, 'fr': Postfr, 'ha': Posthau}
            for i in language_dict:
                if i == lang:
                    table = language_dict.get(i)
                    posts_feed = table.query.join(Posts).order_by(func.random()).filter(Posts.thumb_url != None).paginate(int(start), int(count), False)
                    total = (posts_feed.total/int(count))
                    next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(limit), count=int(count)) if posts_feed.has_next else None 
                    previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(limit), count=int(count)) if posts_feed.has_prev else None 
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

@home.route('/related')
class Related(Resource):
    def get(self):
        # user getting data for their home screen
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            lang = request.args.get('lang', None)
            post_type = request.args.get('ptype', '1')
            # Still to fix the next and previous WRT Sqlalchemy
            language_dict = {'en': Posten, 'es': Postes, 'ar': Postarb, 'pt': Postpor, 'sw': Postsw, 'fr': Postfr, 'ha': Posthau}
            for i in language_dict:
                if i == lang:
                    table = language_dict.get(i)
                    posts_feed = table.query.join(Posts).order_by(func.random()).filter(Posts.post_type==1, Posts.thumb_url != None).paginate(int(start), int(count), False)
                    total = (posts_feed.total/int(count))
                    next_url = url_for('api./api/home_home', start=posts_feed.next_num, limit=int(limit), count=int(count)) if posts_feed.has_next else None 
                    previous = url_for('api./api/home_home', start=posts_feed.prev_num, limit=int(limit), count=int(count)) if posts_feed.has_prev else None 
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

@home.route('/article/<id>')
class Article(Resource):
    def get(self, id):
        if id:
            posts_feed = Posts.query.filter_by(uuid = id).first()
            channels = posts_feed.get_post_channels()
            return {
                "results": {
                    'article': marshal(posts_feed, schema.postdata),
                    'channels': marshal(channels, schema.channeldata)
                }
            }, 200
        else:
            return {
                'status': 0,
                'res': 'article not found'
            }, 404

@home.route('/summary/<id>')
class Aticle(Resource):
    def get(self, id):
        # user getting data for their home screen
        language_dict = {'en': Posten, 'es': Postes, 'ar': Postarb, 'pt': Postpor, 'sw': Postsw, 'fr': Postfr, 'ha': Posthau}
        if request.args:
            lang  = request.args.get('lang', None)
            table = language_dict.get(lang)
            orig_post = Posts.query.filter_by(uuid = id).first()
            posts_feed = table.query.filter_by(id = orig_post.id).first()
            return {
                "lang": lang,
                "results": {
                    'article': marshal(posts_feed, schema.postdata)
                }
            }, 200
        else:
            posts_feed = Posts.query.filter_by(uuid = id).first()
            return {
                'feed': marshal(posts_feed, schema.postdata)
            }, 200     

@message.doc(
    security='KEY',
    params={ 'id': 'ID of the post' },
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

