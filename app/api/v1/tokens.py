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
                data = jwt.decode(token, app.config.get('SECRET_KEY'),algorithms='HS256')
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

token = Namespace('/api/token', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
        To get this authorization, please contact out I.T Team ', \
    path='/v1/')


apiinfo = token.model('Info', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

logindata = token.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

verifydata = token.model('Verify', {
    'username': fields.String(required=True),
    'code': fields.String(required=True)
})

creationdata = token.model('Create', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'bio': fields.String(required=True)
})
    

@token.doc(
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
@token.route('/token')
class Token(Resource):
    @token.marshal_with(apiinfo)
    def get(self):
        return {}, 200
    @token_required
    @token.expect(logindata)
    def post(self, username):
        data = request.get_json()
        return {}, 200
    @token_required
    @token.expect(logindata)
    def put(self):
        return {}, 200
    @token_required
    @token.expect(logindata)
    def patch(self):
        return {}, 200
    @token_required
    @token.marshal_with(apiinfo)
    def delete(self):
        return {}, 200