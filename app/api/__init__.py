from flask import Blueprint, url_for
from app.services import Mailer, Phoner
from flask_restplus import Api, Resource, fields, reqparse, marshal
from flask import Blueprint, render_template, abort, request, session
from flask_cors import CORS
from functools import wraps
from flask import current_app as app
from datetime import datetime, timedelta
from app import db, limiter, cache
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
import jwt, uuid, os
from flask import current_app as app
from .v1 import user, info, token, search, post, comment, channel
from app.models import Users, Channels, subs, Language, Save, Setting, Message, Comment, \
    Subcomment,  Posts, Postarb, Posten, Postfr, Posthau, Postpor, \
        Postsw, Posttype, Rating, Ratingtype

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
apisec = Api( app=api, doc='/docs', version='1.4', title='News API.', \
description='This documentation contains all routes to access the lirivi API. \nSome routes require authorization and can only be gotten \
    from the lirivi company', license='../LICENSE', license_url='www.lirivi.com', contact='leslie.etubo@gmail.com', authorizations=authorizations)
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

verify = apisec.namespace('/api/verify', \
    description= "Handles user verification by email or phone\
    on the application.", \
    path = '/v1/')

message = apisec.namespace('/api/mesage/user*', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

 

@login.doc(
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
class Login(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("1/hour")
    @login.expect(schema.logindata)
    def post(self):
        app.logger.info('User login in')
        login_data = request.get_json()
        user = Users.query.filter_by(username=login_data['username']).first()
        if user is None or not user.verify_password(login_data['password']):
            return {'res':'User not Found'},404   
        else:
            if user.verify_password(login_data['password']):
                token = jwt.encode({
                    'user': user.username,
                    'uuid': user.uuid,
                    'exp': datetime.utcnow() + timedelta(days=30),
                    'iat': datetime.utcnow()
                },
                app.config.get('SECRET_KEY'),
                algorithm='HS256')
                return {'token': str(token)}, 200
            return {},404 

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
class Signup(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("10/hour")
    @signup.expect(schema.signupdata)
    def post(self):
        signup_data = request.get_json()
        exuser = Users.query.filter_by(username=signup_data['username']).first()
        if signup_data:
            if exuser:
                return {'res':'user already exist'}, 200
            else:
                user = Users(signup_data['username'], signup_data['email'], signup_data['password'], '')
                db.session.add(user)
                db.session.commit()
                return {}, 201
            return {}, 200
        else:
            return {},404


# Home still requires paginated queries for user's phone not to load forever
@cache.cached(300, key_prefix='all_home_posts')
@home.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page' },
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
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        # user getting data for their home screen
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            # Still to fix the next and previous WRT Sqlalchemy
            posts_trending = Posts.query.order_by(Posts.id.desc()).paginate(int(start), int(count), False)
            posts_feed = Posts.query.order_by(Posts.id.desc()).paginate(int(start), int(count), False)
            posts_discover = Posts.query.order_by(Posts.id.desc()).paginate(int(start), int(count), False)
            next_url = url_for('api./api/home_home', start=posts_trending.next_num, limit=int(limit), count=int(count)) if posts_trending.has_next else None 
            previous = url_for('api./api/home_home', start=posts_trending.prev_num, limit=int(limit), count=int(count)) if posts_trending.has_prev else None 
            return {
                "start": start,
                "limit": limit,
                "count": count,
                "next": next_url,
                "previous": previous,
                "results": {
                    'trending': marshal(posts_trending.items, schema.postdata),
                    'feed': marshal(posts_feed.items, schema.postdata),
                    'discover': marshal(posts_discover.items, schema.postdata)
                }
            }, 200
        else:
            posts_trending = Posts.query.limit(10).all()
            posts_feed = Posts.query.limit(10).all()
            posts_discover = Posts.query.limit(10).all()
            return {
                'trending': marshal(posts_trending, schema.postdata),
                'feed': marshal(posts_feed, schema.postdata),
                'discover': marshal(posts_discover, schema.postdata)
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

@verify.doc( 
    security='KEY',
    params={ 'phonenumber': 'ID of the post',
            'auth_type': 'Method of authentication e.g phone, email, both',
            'id':'Id of authenticator' },
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
@verify.route('/verify')
class verify(Resource):
    @verify.expect(schema.send_verification)
    def post(self):
        verification_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data["uuid"]).first()
        codedata =  verification_data['code']
        if verification_data:
            if  verification_data["type"] == "phone":
                if str(user.code) == str(codedata):
                    if user.code_expires_in < datetime.utcnow():
                        return {
                            'result': 'Code expired',
                            'status': 0
                        }, 401
                    else:
                        user.phone_verification= True
                        db.session.commit()
                        return {
                            'result': 'User phone verified',
                            'status': 1
                        }, 200
                else:
                    return {
                        'result': 'Verification Failed',
                        'status': 0
                    }, 500
            elif schema.send_verification["type"] == "email":
                pass # Classic fill email verification.
            elif schema.send_verification["type"] == "both":
                user.phone_verification= True
                db.session.commit()
                return {
                    'result': 'User phone verified',
                    'status': 1
                }, 200
            else:
                return {
                    'result': 'Verification Failed',
                    'status': 0
                }, 500
        else:
            return {
                'result': 'No verification data available',
                'status': 0
            }, 500

    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data["uuid"]).first()
        if request.args:
            if request.args.get('auth_type') == 'phone':
                number  = request.args.get('phonenumber', None)
                authtype = request.args.get('auth_type', None)
                user.user_number = number
                phone = Phoner()
                user.code = phone.send_confirmation_code(number)
                user.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                db.session.commit()
                if authtype == 'phone':
                    return {
                        'result': 'Sms sent',
                        'status': 1
                    }, 200
                elif authtype == 'email':
                    return {
                        'result': 'Mail sent',
                        'status': 1
                    }, 200
            elif request.args.get('auth_type') == 'email':
                pass
            else:
                pass
        else:
            return {
                'result': 'No args available in request',
                'status': 0
            }, 401