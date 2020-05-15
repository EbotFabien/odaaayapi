from flask_restplus import Namespace, Resource, fields, marshal
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session
from flask import current_app as app
from app.models import Users, Channels, subs, Posts
from app import db, cache, logging
import json


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

post = Namespace('/api/post', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
        To get this authorization, please contact out I.T Team ', \
    path='/v1/')

postcreationdata = post.model('postcreationdata', {
    'title': fields.String(required=True),
    'channel': fields.Integer(required=True),
    'type': fields.String(required=True),
    'content': fields.String(required=True)
})

Updatedata = post.model('Updatedata',{
    'id':  fields.String(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True)
})

deletedata =post.model('deletedata',{
    'id':fields.String(required=True)
})
    
postdata = post.model('postreturndata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'channel_id': fields.Integer(required=True),
    'uploader': fields.String(required=True),
    'content': fields.String(required=True),
    'uploader_date': fields.DateTime(required=True)
})

multiplepost = post.model('',{
    "start": fields.Integer(required=True),
    "limit": fields.Integer(required=True),
    "count": fields.Integer(required=True),
    "next": fields.String(required=True),
    "previous": fields.String(required=True),
    "results": fields.List(fields.Nested(postdata))
})


postreq = post.model('postreq', {
    'arg': fields.String(required=True),
    'all': fields.Boolean(required=True),
    'channel': fields.Integer(required=True),
    'arg_type': fields.String(required=True),
})


@post.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page' },
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
@post.route('/post')

class Post(Resource):
    @token_required
    @cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            # Still to fix the next and previous WRT Sqlalchemy
            next = "/api/v1/post?start="+start+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start="+start+"&limit="+limit+"&count="+count
            posts = Posts.query.order_by(Posts.uploader_date.desc()).paginate(int(start), int(count), False).items
            return {
                "start": start,
                "limit": limit,
                "count": count,
                "next": next,
                "previous": previous,
                "results": marshal(posts, postdata)
            }, 200
        else:
            posts = Posts.query.order_by(Posts.uploader_date.desc()).all()
            return marshal(posts, postdata), 200

    @token_required
    @post.expect(Updatedata)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post_id=Posts.query.get(req_data['id'])
        if req_data['content'] is None:
            return {'res':'fail'}, 404
        elif user and post_id:
            post_id.title= req_data['title']
            post_id.content=req_data['content']
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404
        
    @token_required
    @post.expect(deletedata)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post_id=Posts.query.get(req_data['id'])
        if user and post_id:
            db.session.delete(post_id)
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404
    
    @token_required
    @post.expect(Updatedata)
    def patch(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        post_id=Posts.query.get(req_data['id'])
        if user and post_id:
            post_id.title= req_data['title']
            post_id.content=req_data['content']
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404
              
    @token_required
    @post.expect(postcreationdata)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        channel = Channels.query.filter_by(id=req_data['channel']).first()
        if user.subscribed(channel) is None:
            return {'res':'You are not subscribed to this channel'}, 404
        if req_data['channel'] is None:
            return {'res':'fail'}, 404
        elif user.subscribed(channel) and user:
            if req_data['type'] is None:
                req_data['type']="Text"
            new_post = Posts(user.id, req_data['title'], req_data['channel'], req_data['type'], req_data['content'], user.id)
            db.session.add(new_post)
            db.session.commit()
           # new_post.launch_translation_task('translate_posts', user.id, 'Translating  post ...')
            #db.session.commit()
            return {'res':'success'}, 200
        else:
            return {'res':'fail'}, 404
   
    
