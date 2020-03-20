from flask import Blueprint
from app.services import Mailer
from flask_restplus import Api, Resource, fields, reqparse
from flask import Blueprint, render_template, abort, request, session
from flask_cors import CORS
from functools import wraps
from flask import current_app as app
from datetime import datetime
from datetime import  timedelta
from app.models import User
from app import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
import jwt, uuid, os


# API security
authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'API-KEY'
    }
}

api = Blueprint('api', __name__, template_folder = '../templates')
apisec = Api( app=api, doc='/docs', version='1.0', title='News', \
description='', authorizations=authorizations)
from . import schemas
CORS(api, resources={r"/api/*": {"origins": "*"}})

uploader = apisec.parser()
uploader.add_argument('file', location='files', type=FileStorage, required=True, help="You must parse a file")
uploader.add_argument('name', location='form', type=str, required=True, help="Name cannot be blank")

info = apisec.namespace('/api/', \
    description='This namespace contains all the information about our API.', \
    path='/v1/')

tokens = apisec.namespace('/api/tokens', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
        To get this authorization, please contact out I.T Team ', \
    path='/v1/')

login = apisec.namespace('/api/login', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
        To get this authorization, please contact out I.T Team ', \
    path='/v1/')

user = apisec.namespace('/api/user', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

post = apisec.namespace('/api/post', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/private/')


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

@info.deprecated
@info.route('/')
class Data(Resource):
    @info.marshal_with(schemas.apiinfo)
    def get(self):
        app = {
            'name':'News',
            'version': 1.0,
            'date': datetime.utcnow(),
            'author': 'Leslie Etubo T, E. Fabien, Samuel Klein, Marc.',
            'description': 'This is an API to serve information to clients'
        }, 200
        return app

@tokens.doc(
    security='KEY',
    params={ 'username': 'Specify the username associated with the person' },
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
@tokens.route('/token')
class Data(Resource):
    @tokens.marshal_with(schemas.logindata)
    def post(self):
        data = request.get_json()
        if data is not None:
            user = User.query.filter((User.username == data['username'].lower()) | (User.email == data['username'].lower())).first()
            if user is not None:
                if user.verified:
                    if user.vericount <= 5:
                        if user.verify_password(data['password']):
                            user.vericount = 0
                            db.session.add(user)
                            db.session.commit()
                            authtoken = jwt.encode(
                                {
                                    'user': user.uuid,
                                    'email': user.email,
                                    'exp': datetime.utcnow() + timedelta(days=30),
                                    'iat': datetime.utcnow()
                                },
                                app.config.get('SECRET_KEY'),
                                algorithm='HS256'
                            )
                            return {
                                'result': 'Welcome '+ user.username,
                                'token': str(authtoken),
                                'status': 1
                            }, 201
                        else:
                            user.vericount += 1
                            db.session.add(user)
                            db.session.commit()
                            return {
                                'result': 'Please check credential',
                                'status': 0
                            }, 401
                    else:
                        return {
                            'result': 'User account has been blocked please change password',
                            'status': 0
                        }, 401
                else:
                    return {
                        'result': 'This account is not verified',
                        'status': 0
                    }, 401
            else:
                return {
                    'result': 'User or password incorrect',
                    'status': 0
                }, 404
        else:
            return {
                'result': 'Invalid arguments',
                'status': 0
            }, 401
    
    def get(self):
        return {}, 200

    def put(self):
        return {}, 200

    def patch(self):
        return {}, 200
    
    def delete(self):
        return {}, 200

@user.doc(
    security='KEY',
    params={ 'username': 'Specify the username associated with the person' },
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
@user.route('/user/<username>')
class Data(Resource):
    @user.marshal_with(schemas.apiinfo)
    def get(self):
        return {}, 200
    @token_required
    @tokens.expect(schemas.logindata)
    def post(self, username):
        return {}, 200
    @token_required
    @tokens.expect(schemas.logindata)
    def put(self):
        return {}, 200
    @token_required
    @tokens.expect(schemas.logindata)
    def patch(self):
        return {}, 200
    @token_required
    @user.marshal_with(schemas.apiinfo)
    def delete(self):
        return {}, 200