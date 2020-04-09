from flask_restplus import Namespace, Resource, fields
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session
from app.models import Users,Posts,Comment
from flask import current_app as app
from app import db


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

comment = Namespace('/api/comment', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/v1/')


apiinfo = comment.model('Info', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

logindata = comment.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

verifydata = comment.model('Verify', {
    'username': fields.String(required=True),
    'code': fields.String(required=True)
})

creationdata = comment.model('Create', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'bio': fields.String(required=True)
})
commentcreation =comment.model('Create',{
    'post_id': fields.String(required=True),
    'content': fields.String(required=True),
    'comment_type': fields.String(required=True),
})    

@comment.doc(
    security='KEY',
    params={ 'postid': 'Specify the id of the post' },
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
@comment.route('/comment')
class Data(Resource):
    @comment.marshal_with(apiinfo)
    def get(self):
        return {}, 200
    @token_required
    @comment.expect(commentcreation)
    def post(self):
        if request.args.get('postid'):
            post_id=request.args.get('postid')
        elif request.args.get('postid') is None:
            post_id=Posts.query.get(req_data['post_id'])
        if post_id is None:
            return {'res':'fail'},400
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if  post_id:
            new_comment=Comment(user,'1', post_id, req_data['content'], req_data['comment_type'])
            db.session.add(new_comment)
            db.session.commit()
            return{'res':'success'},200
        else:
            return {'res':'fail'},400
        
    @token_required
    @comment.expect(logindata)
    def put(self):
        return {}, 200
    @token_required
    @comment.expect(logindata)
    def patch(self):
        return {}, 200
    @token_required
    @comment.marshal_with(apiinfo)
    def delete(self):
        return {}, 200

@comment.route('/comment/<word>')
class Searchcomment(Resource):
    @comment.marshal_with(apiinfo)
    def get(self):
        return {}, 200
    @token_required
    @comment.expect(logindata)
    def post(self, username):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if user:
            return {}, 200

    @token_required
    @comment.expect(logindata)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        #if 
        #elif user:
        #    return {}, 200
        return {}, 200
    @token_required
    @comment.expect(logindata)
    def patch(self):
        return {}, 200
    @token_required
    @comment.marshal_with(apiinfo)
    def delete(self):
        return {}, 200