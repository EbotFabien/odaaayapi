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

info = apisec.namespace('Information', \
description='This namespace contains all the information about our API.', \
path='/')

core = apisec.namespace('Data access', \
description='This contains data for the user and content belonging to the \
application to be shared. The android and iOS application will make calls from \
these endpoints. Tokens will be the method of security with two tokens, a  \
refresh token ( 30 days span ) and a normal token ( 7 days ) ', \
path='/')


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

@core.doc(security='KEY')
@core.route('/login')
class Data(Resource):
    @core.expect(schemas.logindata)
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

@info.doc(security='KEY')
@info.route('/info')
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