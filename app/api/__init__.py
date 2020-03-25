from flask import Blueprint
from app.services import Mailer
from flask_restplus import Api, Resource, fields, reqparse
from flask import Blueprint, render_template, abort, request, session
from flask_cors import CORS
from functools import wraps
from flask import current_app as app
from datetime import datetime, timedelta
from app import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
import jwt, uuid, os
from .v1 import user, info, token, search, post
from app import ma
from app.models import User, Language, Save, Setting, Message, Comment, \
    Subcomment, Channel, Post, Postarb, Posten, Postfr, Posthau, Postpor, \
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
description='', authorizations=authorizations)
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

home = apisec.namespace('/api/home/[user]', \
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
    @login.expect(schema.logindata)
    def post(self):
        login_data = request.get_json()
        user = User.query.filter_by(username=login_data['username']).first()
        if user is None or not user.verify_password(login_data['password']):
            return {},404   
        else:
            if user.verify_password(login_data['password']):
                token = jwt.encode({
                    'user': user.username,
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
    @signup.expect(schema.signupdata)
    def post(self):
        signup_data = request.get_json()
        exuser = User.query.filter_by(username=signup_data['username']).first()
        if signup_data and exuser is None:
            user = User(signup_data['username'], signup_data['email'], signup_data['password'], '')
            db.session.add(user)
            db.session.commit()
            return {}, 200
        else:
            return {},404

@home.doc(
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
@home.route('/home/<user>')
class Home(Resource):
    @token_required
    @home.marshal_with(schema.homedata)
    def get(self):
        return {}, 200       