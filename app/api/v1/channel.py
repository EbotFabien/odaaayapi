from flask_restplus import Namespace, Resource, fields, marshal
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session
from app.models import Users, Channels, subs
from app import db
from flask import current_app as app
from  sqlalchemy.sql.expression import func


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

channel_view = channel.model('channel_view', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'profile_pic': fields.String(required=True),
    'background': fields.String(required=True)
})
channel_R_data = channel.model('channel_R_data', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'description': fields.String(required=True),
    'profile_pic': fields.String(required=True),
    'background': fields.String(required=True)
})

channeldata = channel.model('channelreturndata',{
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'description': fields.String(required=True)
})

channel_post =channel.model('channel_post',{
    'id': fields.Integer(required=True),
    'title':fields.String(required=True),
    'uuid':fields.String(required=True),
    'uploader':fields.String(required=True),
    'uploader_date':fields.String(required=True)
})

channel_post_final = channel.model('channel_post_final',{
    'postchannel': fields.List(fields.Nested(channel_post))
})

channel_list = channel.model('channel_list', {
    'channel': fields.List(fields.Nested(channel_view))
})


channelcreationdata = channel.model('ChannelCreationData', {
    'name': fields.String(required=True),
    'profile_pic': fields.String(required=True),
    'description': fields.String(required=True),
    'background': fields.String(),
    'css': fields.String()
})
channel_sub_moderator = channel.model('channel_sub_moderator',{
    'channel_id': fields.String(required=True),
    'user_id': fields.Integer(required=True),
})
channel_subscribe = channel.model('channel_subscribe',{
    'channel_id': fields.Integer(required=True)
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
    @channel.marshal_with(channel_view)
    @token_required 
    def get(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        channel = user.get_channels()
        return channel, 200
    @token_required
    @channel.expect(channelcreationdata)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        channels = Channels.query.filter_by(name=req_data['name']).first()
        channel_user = Channels.query.filter_by(moderator=user.id).first()
        if user:
            if channel_user:
                 return {'res':'user already has channel'}, 404
            if channels is None:
                new_channel = Channels(req_data['name'],req_data['description'], req_data['profile_pic'], \
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


@channel.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
              },
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

@channel.route('/channel/random')
class random(Resource):
    def get(self):
        if request.args:
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
            next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
            previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
            channel = Channels.query.order_by(func.random()).paginate(int(start),int(count), False).items
            return{
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(channel,channel_R_data)
            }, 200
        else:
            return{
                "res":"return request",
                "status":0,
                
            }, 404
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
@channel.route('/channel/add_sub_moderator')
class sub(Resource):
    @channel.marshal_with(okresponse)
    def get(self):
        return {}, 200
    @token_required
    @channel.expect(channel_sub_moderator)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        sub_Mod=Users.query.filter_by(id=req_data['user_id']).first()
        #user_admin = user.is_moderator()
        #if user_admin is None:
        #    return {'res':user.id}, 200
        #else:
        moderator_check = Channels.query.filter_by(moderator=user.id).first()
        channel = Channels.query.filter_by(id=req_data['channel_id']).first()
        if sub_Mod.subscribed(channel) is None:
            return {'res':'The user is not  subscribed to this channel'}, 404
        if  moderator_check.moderator == sub_Mod.id :
            return{'res':'Moderator cannot be sub Moderator'}
        if moderator_check.id == channel.id  :
            channel.add_sub_mod(sub_Mod)
            db.session.commit()
            return {'res':'You have created a sub moderator '}, 200
        else:
            return {'res':'You have not a sub moderator of this channel'}, 404
    @token_required
    @channel.expect(channel_sub_moderator)
    def put(self):
        return {}, 200
    @token_required
    def patch(self):
        return {}, 200
    @token_required
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        sub_Mod=Users.query.filter_by(id=req_data['user_id']).first()
        moderator_check = Channels.query.filter_by(moderator=user.id).first()
        channel = Channels.query.filter_by(id=req_data['channel_id']).first()
        if moderator_check.id == channel.id :
            channel.remove_sub_mod(sub_Mod)
            db.session.commit()
            return {'res':'You are now a sub moderator '}, 200
        else:
            return {'res':'you are not a moderator of this channel'}, 404

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
@channel.route('/channel/subscribe')
class sub_channel(Resource):
    @channel.marshal_with(okresponse)
    def get(self):
        return {}, 200
    @token_required
    @channel.expect(channel_subscribe)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        channel = Channels.query.filter_by(id=req_data['channel_id']).first()
        if user is None:
            return {
                'status': 0,
                'res':'fail'
            }, 404
        if  user and channel :
            channel.add_sub(user)
            db.session.commit()
            return{
                'status': 1,
                'res':'success'
            }
        else:
            return {
                'status': 0,
                'res':'You have not subscribed'
            }, 404
    @token_required
    @channel.expect()
    def put(self):
        return {}, 200
    @token_required
    def patch(self):
        return {}, 200
    @token_required
    @channel.expect(channel_subscribe)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        channel = Channels.query.filter_by(id=req_data['channel_id']).first()
        if user is None:
            return {'status': 0, 'res':'fail'}, 404
        if  user and channel :
            channel.remove_sub(user)
            db.session.commit()
            return{'status': 1,
            'res':'success'}
        else:
            return {'status': 0, 'res':'You have not subscribed'}, 404


@channel.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            },
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
@channel.route('/channel/user_is_Moderator')
class user_is_moderator(Resource):
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            moderator_check = Channels.query.filter_by(moderator=user.id).first()
            if moderator_check:
                channel = Channels.query.filter_by(moderator=user.id).order_by(Channels.id.desc()).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(channel, channeldata)
                }, 200
            else :
                return{
                    "status":0,
                    "res":"User is not a moderator of any channel"
                }
        else:
            return{
                    "status":0,
                    "res":"No request found"
                }

@channel.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            },
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
@channel.route('/channel/user_is_sub_Moderator')
class user_is_sub_moderator(Resource):
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            channel_sub = user.channel_sub_moderators()
            if channel_sub :
                channel_sub_moderators =user.channel_sub_moderators().paginate(int(start),int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(channel_sub_moderators, channeldata)
                }, 200
            else :
                return{
                    "status":0,
                    "res":"User is not a moderator of any channel"
                }
        else:
            return{
                    "status":0,
                    "res":"No request found"
                }
                

@channel.doc(
    security='KEY',
    params={'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'channel_id':'Input Channel ID'
            },
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
@channel.route('/channel/all_Post')
class ALL_channels_post(Resource):
    @token_required
    #@cache.cached(300, key_prefix='all_posts')
    def get(self):
        if request.args:
            start  = request.args.get('start', None)
            limit  = request.args.get('limit', None)
            count = request.args.get('count', None)
            channel=request.args.get('channel_id')
            next = "/api/v1/post?start="+str(int(start)+1)+"&limit="+limit+"&count="+count
            previous = "/api/v1/post?start="+str(int(start)-1)+"&limit="+limit+"&count="+count
            token = request.headers['API-KEY']
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user= Users.query.filter_by(uuid=data['uuid']).first()
            channels=Channels.query.filter_by(id=channel).first()
            if channels:
                channelspost=Channels.query.filter_by(id=channel).order_by(Channels.id.desc()).paginate(int(start), int(count), False).items
                return {
                    "start": start,
                    "limit": limit,
                    "count": count,
                    "next": next,
                    "previous": previous,
                    "results": marshal(channelspost, channel_post_final)
                }, 200
            else :
                return{
                    "status":0,
                    "res":"Channel does not exist"
                }
        else:
            return{
                    "status":0,
                    "res":"No request found"
                }