from flask_restplus import Namespace, Resource, fields
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session


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


apiinfo = user.model('Info', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

logindata = user.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

verifydata = user.model('Verify', {
    'username': fields.String(required=True),
    'code': fields.String(required=True)
})

creationdata = user.model('Create', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'bio': fields.String(required=True)
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
@user.route('/user/<username>')
class Data(Resource):
    @user.marshal_with(apiinfo)
    def get(self):
        return {}, 200
    @token_required
    @user.expect(logindata)
    def post(self, username):
        return {}, 200
    @token_required
    @user.expect(logindata)
    def put(self):
        return {}, 200
    @token_required
    @user.expect(logindata)
    def patch(self):
        return {}, 200
    @token_required
    @user.marshal_with(apiinfo)
    def delete(self):
        return {}, 200