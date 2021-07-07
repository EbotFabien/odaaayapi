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
import json, shortuuid
import jwt, uuid, os
from flask import current_app as app
from sqlalchemy import func,or_,and_
import re
from app.services import mail
from .v1 import user, info, token, search, post
from app.models import Report, Users, Language, Save, Setting, \
         Posttype, Rating, Ratingtype
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
apisec.add_namespace(search)



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
    # Limiting the user request to localy prevent DDoSing
    # @limiter.limit("1/hour")
    @login.expect(schema.full_login)
    def post(self):
        app.logger.info('User login with user_name')
        count=5
        req_data = request.get_json()
        phone_login=req_data['phone_login']
        if phone_login == False :
            email=req_data['email'] or None
            password=req_data['password'] or None
            user = Users.query.filter_by(email=email).first()
            if user : 
                if user.verified_email == True:
                    if user.verify_password(password):
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
                        }, 200

                
                    else:
                        if user.tries < count:
                            user.tries +=1
                            db.session.commit()
                            return {'res': 'Your Password is wrong '}, 401
                        if user.tries >= count:
                            user.verified_email=False
                            db.session.commit()
                            return {'res': 'Reset your Password '}, 401
                else:
                    return {'status': 4,'res': 'user is  not verified'}, 401

            else:
                return {'res': 'User does not exist '}, 401
            
        
        if phone_login == True:
                number=req_data['phone'] or None
                code=req_data['code'] or None
                user1 = Users.query.filter_by(phone=number).first()
                if user1:
                    if code is None:
                        verification_code=phone.generate_code()
                        user1.code = verification_code
                        user1.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                        db.session.commit()
                        phone.send_confirmation_code(number,verification_code)
                        return {
                            'status': 1,
                            'res': 'verification sms sent'
                            }, 200
                    
                    if code:
                        if (str(user1.code) == str(code)) and not (datetime.utcnow() > user1.code_expires_in):
                            token = jwt.encode({
                                'user': user1.username,
                                'uuid': user1.uuid,
                                'exp': datetime.utcnow() + timedelta(days=30),
                                'iat': datetime.utcnow()
                            },
                            app.config.get('SECRET_KEY'),
                            algorithm='HS256')
                            return {
                                'status': 1,
                                'res':'success',
                                'token': str(token)
                                }, 200
                        
                        if code:
                            if (str(user1.code) == str(code)) and not (datetime.utcnow() > user1.code_expires_in):
                                user1.verified_phone=True
                                user1.tries =0
                                db.session.commit()
                                token = jwt.encode({
                                    'user': user1.username,
                                    'uuid': user1.uuid,
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
                                if user1.tries < count:
                                    user1.tries +=1
                                    db.session.commit()
                                    return {'res': 'verification fail make sure code is not more than 5 mins old '}, 401

                                if user1.tries >= count:
                                    user1.verified_phone=False
                                    db.session.commit()
                                    return {'res': 'Reset your code '}, 401
                    else:
                        return {'res': 'Your account has been blocked'}, 401
                else:
                    return {'res': 'User does not exist'}, 401

    

@login.doc(
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
@login.route('/auth/check_reset')
class _check_reset(Resource):
    @login.expect(schema.check_pass)
    def post(self):
        req_data = request.get_json()
        email=req_data['email']
        password=req_data['password']
        #code=req_data['code']
        check_email =Users.query.filter_by(email=email).first()
        if check_email:#.code == int(code):
            check_email.passwordhash(password)
            check_email.tries = 0
            user.verified_email=True
            db.session.commit()
            return{
                    'status':1,
                    'res':'code has been reset',
                    
                },200
        else:
            return{
                    'status':0,
                    'res':'code is not same',
                    
                },400

@login.doc(
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
@login.route('/auth/checkresetcode')
class _check_reset(Resource):
    @login.expect(schema.check_code)
    def post(self):
        req_data = request.get_json()
        email=req_data['email']
        code=req_data['code']
        check_email =Users.query.filter_by(email=email).first()
        if check_email.code == int(code) and not (datetime.utcnow() > check_email.code_expires_in):
            check_email.tries = 0
            user.verified_email=True
            db.session.commit()
            return{
                    'status':1,
                    'res':'code has been reset',
                    
                },200
        else:
            return{
                    'status':0,
                    'res':'code is not same or expired',
                    
                },400

@login.doc(
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
@login.route('/auth/reset_code')
class _reset_code(Resource):
    @login.expect(schema.reset_pass)
    def post(self):
        req_data = request.get_json()
        email=req_data['email']
        phone_num=req_data['number']
        email1 =Users.query.filter_by(email=email).first()
        phon=Users.query.filter_by(phone=phone_num).first()
        code_sent=int(phone.generate_code())
        regex1 = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        regex2 = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        if re.search(regex1,str(email)) or re.search(regex2,str(email)):
                email1.code=code_sent
                email1.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                db.session.commit()
                mail.send_email(app,[email1.email],code_sent)
                return{
                        'status':1,
                        'res':'Mail sent',
                        
                    },200
        if  phon:
            phone.send_confirmation_code(phone_num)
            return{
                    'status':1,
                    'res':'Phone_code sent',
                        
                    },200
        else:
            return{
                    "status":0,
                    "res":"Fail"
                },400
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
    @limiter.limit("10/hour")
    @signup.expect(schema.signupdataemail)
    def post(self):
        signup_data = request.get_json()
        if signup_data:
            email = signup_data['email'] or None 
            username = signup_data['user_name'] or None 
            password = signup_data['password'] or None
            phone_number = signup_data['phone_number'] or None

            if email and username and password is not None:
                user = Users.query.filter_by(email=email).first() #filter by user handle
            
                if user :
                    if user.verified_email == False:
                        verification_code = phone.generate_code()
                        user.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                        user.code = verification_code
                        mail.send_email(app,[user.email],verification_code)
                        return { 
                            'res':'user already exist,verification code sent',
                            'status': 0
                        }, 200
                    else:
                        return { 
                            'res':'user already exist',
                            'status': 3
                        }, 200
                else:
                    verification_code = phone.generate_code()

                    if verification_code:
                        newuser = Users(username,str(uuid.uuid4()),True, signup_data['email'])
                        newuser.code = verification_code
                        newuser.passwordhash(password)
                        newuser.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                        db.session.add(newuser)
                        db.session.commit()
                        #send code to email
                        mail.send_email(app,[signup_data['email']],verification_code) #check this
                        return {
                            'res': 'success',
                            'user_name':username,
                            'email': signup_data['email'],
                            'status': 1
                        }, 200
                    else:
                        return {
                            'status': 0,
                            'res':'error'
                        }, 201
            if phone_number is not None:
                user = Users.query.filter_by(phone=phone_number).first()
                if user:
                    return { 
                        'res':'user already exist',
                        'status': 0
                    }, 200
                else:
                    verification_code=phone.generate_code()
                    newuser = Users(str(phone_number),str(uuid.uuid4()),True, str(phone_number),phone_number)
                    db.session.commit()
                    newuser.code = verification_code
                    newuser.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                    db.session.add(newuser)
                    db.session.commit()
                    phone.send_confirmation_code(phone_number,verification_code)
                    return {
                        'status': 1,
                        'Phone':phone_number,
                        'res': 'verification sms sent'
                        }, 200
            if email and username and password and phone_number is not None:
                user = Users.query.filter_by(email=email).first()
                if user:
                    return { 
                        'res':'user already exist',
                        'status': 0
                    }, 200
                else:
                    verification_code=phone.generate_code()
                    newuser = Users(user_name,str(uuid.uuid4()),False, email,phone_number)
                    db.session.commit()
                    newuser.code = verification_code
                    newuser.passwordhash(password)
                    newuser.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                    db.session.commit()
                    phone.send_confirmation_code(phone_number,verification_code)
                    mail.send_email(app,[signup_data['email']],verification_code) #check this
                    return {
                        'status': 1,
                        'user_name':user_name,
                        'email':email,
                        'Phone':phone_number,
                        'res': 'verification sms  and email sent'
                        }, 200
        else:
            return {
                'status': 0,
                'res': 'No data'
            },201

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
class Resetpassword(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("10/hour")
    @signup.expect(schema.resetpassword)
    def post(self):
        signup_data = request.get_json()
        if signup_data:
            email = signup_data['email'] 
            check=Users.query.filter_by(email=email).first()
            if check:
                verification_code = phone.generate_code()
                check.code = verification_code
                check.code_expires_in = datetime.utcnow() + timedelta(minutes=5)
                db.session.commit()
                mail.send_email(app,[email],verification_code)
                return {
                'status': 1,
                'res': 'email has been sent'
                },200
            else:
                return {
                'status': 0,
                'res': 'user not found'
                },201
@signup.route('/auth/email_verification')
class email_verification(Resource):
    # Limiting the user request to localy prevent DDoSing
    @limiter.limit("10/hour")
    @signup.expect(schema.verifyemail)
    def post(self):
        signup_data = request.get_json()
        email = signup_data['email']
        exuser = Users.query.filter_by(email=email).first()
        if exuser:
            if exuser.code == int(signup_data['code']) and not (datetime.utcnow() > exuser.code_expires_in):
                exuser.verified_email = True
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
            language_dict = {'en', 'es','ar', 'pt', 'sw', 'fr', 'ha'}
            for i in language_dict:
                if i == lang:
                    current_lang = Language.query.filter_by(code=i).first()
                    posts_feed = Translated.query.filter_by(language_id=current_lang.id).order_by(func.random()).paginate(int(start), int(count), False)
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
            'id': 'Article id',
            'lang':'Language'},
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
            language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
            for i in language_dict:
                if i == lang:
                    current_lang = Language.query.filter_by(code=i).first()
                    posts_feed = Translated.query.filter_by(language_id=current_lang.id).join(Posts).order_by(func.random()).filter(Posts.post_type==2).paginate(int(start), int(count), False)
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
            language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
            for i in language_dict:
                if i == lang:
                    current_lang = Language.query.filter_by(code=i).first()
                    posts_feed = Translated.query.filter_by(language_id=current_lang.id).join(Posts).order_by(func.random()).filter(Posts.thumb_url != None).paginate(int(start), int(count), False)
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
            language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
            for i in language_dict:
                if i == lang:
                    current_lang = Language.query.filter_by(code=i).first()
                    posts_feed = Translated.query.filter_by(language_id=current_lang.id).join(Posts).order_by(func.random()).filter(Posts.thumb_url != None).paginate(int(start), int(count), False)
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
        language_dict = {'en', 'es', 'ar', 'pt', 'sw', 'fr', 'ha'}
        if request.args:
            if id:
                lang  = request.args.get('lang', None)
                current_lang = Language.query.filter_by(code=lang).first()
                posts_feed = Posts.query.filter_by(uuid = id).first()
                translated_feed = Translated.query.filter_by(post_id= posts_feed.id).first()
                return {
                    "results": {
                        "lang": lang,
                        'translated_feed':marshal(translated_feed, schema.postdata),
                        'article': marshal(posts_feed, schema.postdata)
                    }
                }, 200
            else:
                return {
                    'status': 0,
                    'res': 'article not found'
                }, 404
        else:
            posts_feed = Posts.query.filter_by(uuid = id).first()
            return {
                'feed': marshal(posts_feed, schema.postdata)
            }, 200 

        

@home.route('/reportpost/')
class Report_post_(Resource):
    @home.expect(schema.Report_post)   
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post= Posts.query.filter_by(uuid=req_data['post_id']).first()
  
        if user is None:
            return{
                    "status":0,
                    "res":"Fail"
                }

        if post:
            Report_sent=Report(req_data['reason'],user.email,user.id,post.id,post.uploader_id,req_data['type'][0])
            db.session.add(Report_sent)
            db.session.commit()
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

@home.route('/Save/')
class save_post(Resource): 
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
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
                        "results": marshal(user_saves,schema.saved)
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

    @home.expect(schema.saves_post) 
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

    @home.expect(schema.saves_post)   
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

