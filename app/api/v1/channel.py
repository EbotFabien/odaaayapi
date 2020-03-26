from flask_restplus import Namespace, Resource, fields
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session
from app.models import Users, Channel, subs
from app import db
from flask import current_app as app


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

channel = Namespace('/api/channel', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')



creationdata = channel.model('Create', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'bio': fields.String(required=True)
})

okresponse = channel.model('Okresponse', {
    'res': fields.String(required=True),
})

channelcreationdata = channel.model('ChannelCreationData', {
    'name': fields.String(required=True),
    'profile_pic': fields.String(required=True),
    'description': fields.String(required=True),
    'background': fields.String(),
    'css': fields.String()
})
    

@channel.doc(
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
@channel.route('/channel')
class Data(Resource):
    @channel.marshal_with(okresponse)
    def get(self):
        return {}, 200
    @token_required
    @channel.expect(channelcreationdata)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        channels = Channel.query.filter_by(name=req_data['name']).first()
        if user:
            if channels is None:
                new_channel = Channel(req_data['name'],req_data['description'], req_data['profile_pic'], \
                req_data['background'], user.id, req_data['css'])
                db.session.add(new_channel)
                db.session.commit()
            else:
                return {'res':'Channel already exist'}, 404
            return {'res':'success'}, 200
        else:
            return {'res':'fail'}, 404
    
    @token_required
    def put(self):
        return {}, 200
    @token_required
    def patch(self):
        return {}, 200
    @token_required
    def delete(self):
        return {}, 200