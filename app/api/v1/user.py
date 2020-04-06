from flask_restplus import Namespace, Resource, fields
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session
from app.models import Users

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

user = Namespace('/api/user', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')

userinfo = user.model('Profile', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

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
@user.route('/user')
class Data(Resource):
    @token_required
    @user.marshal_with(userinfo)
    def get(self):
        username = request.args.get('username', None)
        if username:
            user =  Users.query.filter_by(username=username).first()
            # get list of blocked users to make sure they don't see profile information.
            if user is None:
                return {'res': 'User not found'}, 404
        else:
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user = Users.query.filter_by(uuid=data['uuid']).first()
        return user, 200
    @token_required
    @user.expect(userinfo)
    def post(self, username):
        return {}, 200
    @token_required
    @user.expect(userinfo)
    def put(self):
        return {}, 200
    @token_required
    @user.expect(userinfo)
    def patch(self):
        return {}, 200
    @token_required
    @user.marshal_with(userinfo)
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
@user.route('/user/prefs')
class Userprefs(Resource):
    @user.marshal_with(userinfo)
    def get(self):
        return {}, 200
    @token_required
    @user.expect(userinfo)
    def post(self, username):
        return {}, 200