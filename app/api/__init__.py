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
from .v1 import user, info, token, search, post


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


login = apisec.namespace('/api/login', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
    To get this authorization, please contact out I.T Team ', \
    path='/v1/')

home = apisec.namespace('/api/home/[user]', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

@login.doc(
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
@login.route('/login')
class Login(Resource):
    @token_required
    @login.expect(schema.logindata)
    def post(self):
        return {}, 200

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