from flask_restplus import Namespace, Resource, fields,marshal
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session
from app.models import Users, followers, Setting,Channels,Message,Reaction,Comment
from flask import current_app as app
from app import db, cache, logging
from sqlalchemy import or_,and_

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
userdata = user.model('Profile', {
    'id': fields.Integer(required=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'uuid': fields.String(required=True),
    'user_number': fields.String(required=True),
    'verified': fields.Boolean(required=True),
    'user_visibility': fields.Boolean(required=True)
})
update_settings = user.model('Full_settings',{
    'user_id' :fields.Integer(required=True),
    'username':  fields.String(required=True),
    'email': fields.String(required=True),
    'uuid': fields.String(required=True),
    'user_number': fields.String(required=True),
    'verified': fields.Boolean(required=True),
    'user_visibility': fields.Boolean(required=True),
    'setting_id':fields.Integer(required=True),
    'language_id': fields.Integer(required=True),
    'theme': fields.String(required=True),
    'post': fields.Boolean(required=True),
    'saves': fields.Boolean(required=True),
    'channel': fields.Boolean(required=True),
    'comments': fields.Boolean(required=True),
    'messages': fields.Boolean(required=True),
    'N_S_F_W': fields.Boolean(required=True),
    
})
user_prefs = user.model('Preference', {
    'id': fields.Integer(required=True),
    'language_id': fields.Integer(required=True),
    'users_id': fields.Integer(required=True),
    'theme': fields.String(required=True),
    'post': fields.Boolean(required=True),
    'saves': fields.Boolean(required=True),
    'channel': fields.Boolean(required=True),
    'comments': fields.Boolean(required=True),
    'messages': fields.Boolean(required=True),
    'N_S_F_W': fields.Boolean(required=True),
})
updateuser = user.model('Update',{
    'user_id':fields.String(required=True),
    'username': fields.String(required=True),
    'email':fields.String(required=False),
    'number':fields.String(required=False),
    'user_visibility':fields.String(required=False),
})
deleteuser = user.model('deleteuser',{
    'user_id':fields.String(required=True)
})
Postfollowed = user.model('Postfollowed',{
    'id': fields.Integer(required=True),
    'title':fields.String(required=True),
    'uploader_id' : fields.Integer(required=True),
    
})
following_followers = user.model('following',{
    'id':fields.Integer(required=True),
    'username':fields.String(required=True)
})
fanbase =user.model('Fanbase',{
    'subject':fields.String(required=True),  
})
user_notify = user.model('notify',{
    'channel_id':fields.String(required=True)
})
user_messaging =  user.model('messaging',{
    'recipient_id':fields.String(required=True),
    'content':fields.String(required=True)

})
user_name = user.model('user_clap',{
    'id':fields.Integer(required=True),
    'username':fields.String(required=True),
})
messagedata = user.model('message_data',{
    'sender__name':fields.List(fields.Nested(user_name)),
    'timestamp':fields.String(required=True),
    'recipient__name':fields.List(fields.Nested(user_name)),
    'body':fields.String(required=True)
})
messagedata1 =  user.model('message_data1',{
    'sender__name':fields.List(fields.Nested(user_name)),
    'timestamp':fields.String(required=True),
    'recipient__name':fields.List(fields.Nested(user_name)),
})
reaction =  user.model('reaction',{
    'reaction':fields.String(required=True),
    'comment':fields.String(required=True)
})

@user.doc(
    security='KEY',
    params={ 'user_id': 'Specify the user_id associated with the person',
             'fan_base':'Specify if you need followers,followed or post',
             'start': 'Value to start from ',
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
@user.route('/user')
class Data(Resource):
    @token_required
    #@user.marshal_with(userinfo)
    def get(self):
        user_id = request.args.get('user_id', None)
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if user.id: 
            return{
                "results":marshal(user,userdata)
                }, 200
        if user_id:
            user_check = Users.query.get(int(user_id))
            if user_check.is_blocking(user):
                return {'res': 'User not found'}, 404
            if user_check :
                return{
                    "results":marshal(user_check,following_followers)# we use this model because it gives us the structure we need
                }, 200
        else:
            return {'res': 'User not found'}, 404

    @token_required
    def post(self):
        pass 
    
    @token_required
    @user.expect(updateuser)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if req_data['username']  is None:
            return {'res':'fail'}, 404  

        if req_data['user_id'] == user.id:
            user.username = req_data['username']
            user.email = req_data['email']
            user.user_visibility = req_data['user_visibility']
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404

    @token_required
    @user.expect(updateuser)
    def patch(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if req_data['username']  is None:
            return {'res':'fail'}, 404  

        if req_data['user_id'] == user.id:
            user.username = req_data['username']
            user.email = req_data['email']
            user.user_visibility = req_data['user_visibility']
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404
    @token_required
    @user.expect(deleteuser)
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if req_data['user_id'] == user.id:
            db.session.delete(user)
            db.session.commit()
            return {'res':'success'}, 200
        else:
              return {'res':'fail'}, 404
    
@user.doc(
    security='KEY',
    params={ 'user_id': 'Specify the user_id associated with the person',
             'fan_base':'Specify if you need followers,followed or post',
             'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page'
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
@user.route('/user/following')
class User_following(Resource):
    @token_required
    #@cache.cached(300, key_prefix='all_followers&following')
    def get(self):  
        if request.args:
            fan_base =  request.args.get('fan_base')
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
        previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
        user= Users.query.filter_by(uuid=data['uuid']).first()
        posts=user.followed_posts().paginate(int(start),int(count), False).items
        following=user.has_followed().paginate(int(start),int(count), False).items
        followers=user.followers().paginate(int(start),int(count),False).items
        if fan_base == 'post':
            return {
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(posts,Postfollowed)
            }, 200
    
        if fan_base == 'following':
            return {
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(following,following_followers)
            }, 200
        if fan_base == 'followers':
            return {
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(followers,following_followers)
            }, 200
       
        
       

    @token_required
    @user.expect(deleteuser)#This is the following route but we will use the deleteuser model since we just need the user ID        
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        user_to_follow =Users.query.get(req_data['user_id'])
        if user_to_follow is None :
            return {'res':'fail'}, 404
        if user_to_follow:
            user.follow(user_to_follow)
            db.session.commit()
            return{'res':'success'},200
        else:
            return {'res':'fail'},404
    @token_required
    @user.expect(deleteuser)#This is the following route but we will use the deleteuser model since we just need the user ID        
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        user_to_unfollow =Users.query.get(req_data['user_id'])
        if user_to_unfollow is None :
            return {'res':'fail'}, 404
        if user.is_following(user_to_unfollow) is None:
            return {'res':'fail'}, 404
        if user.is_following(user_to_unfollow):
            user.unfollow(user_to_unfollow)
            db.session.commit()
            return{'res':'success'},200
        else:
            return {'res':'fail'},404

@user.route('/user/Block')
class User_Block(Resource):
    def get(self):
        if request.args:
            user_id = request.args.get('user_id')
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
        previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
        user= Users.query.filter_by(uuid=data['uuid']).first()
        following=user.has_blocked().paginate(int(start),int(count), False).items
        if user_id == user.id:
            return {
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(following,following_followers)#we are using this model because it helps though it is the following model
            }, 200
        else:
            return {'res':'fail'},404
        
    @token_required
    @user.expect(deleteuser)#This is the block user route but we will use the deleteuser model since we just need the user ID        
    def post(self, username):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        user_to_block =Users.query.get(req_data['user_id'])
        if user_to_block is None:
            return {'res':'fail'},404
        if user_to_block:
            user.block(user_to_block)
            db.session.commit()
            return{'res':'success'},200
        else:
            return {'res':'fail'},404
    def delete(self, username):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        user_to_unblock = Users.query.get(req_data['user_id'])
        if user_to_unblock is None:
            return {'res':'fail'},404
        if user_to_unblock:
            user.unblock(user_to_unblock)
            db.session.commit()
            return{'res':'success'},200
        else:
            return{'res':'fail'},404

@user.doc(
    security='KEY',
    params={ 'user_id': 'Specify the user_id associated with the person' },
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
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        if token:
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user = Users.query.filter_by(uuid=data['uuid']).first()
            user_settings = Setting.query.filter_by(users_id=user.id).first()
            return {
                "user": marshal(user, userdata),
                "user_prefs": marshal(user_settings, user_prefs)
                }, 200
        else:
           return {

           }, 200 

    @token_required
    @user.expect(update_settings)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        user_settings = Setting.query.filter_by(users_id=user.id).first()

        if req_data['user_id'] == user.id:
            user.username = req_data['username']
            user.email = req_data['email']
            user.user_visibility = req_data['user_visibility']
            db.session.commit()
            return {
                "status":1,
                "res":"User_data updated"
            }, 200
        else:
            return {
                "status":0,
                "res":"You not User"
            }, 200
        if user_settings:
            user_settings.language_id = req_data['language']
            user_settings.theme = req_data['theme']
            user_settings.post = req_data['post']
            user_settings.messages = req_data['messages']
            user_settings.channel = req_data['channel']
            user_settings.saves = req_data['saves']
            user_settings.comments =req_data['comment'] 
            user_settings.users_id =req_data['users'] 
            db.session.commit()
            return {
                "status":1,
                "res":"User_settings updated"
            }, 200


@user.doc(
    security='KEY',
    params={ 'user_id': 'Specify the user_id associated with the person' },
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
@user.route('/user/notification')
class Usernotify(Resource):
    @token_required
    @user.expect(user_notify)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        channel =Channels.query.filter_by(id= int(req_data['channel_id'])).first()
        print(channel.id)
        if channel.subscribed(user) is None:
            return {
                "status":0,
                "res":"You not subscribed to this channel"
            }, 200
        else:
            user.add_notification(channel)
            db.session.commit()
            #sur pause


@user.doc(
    security='KEY',
    params={ 'user_id': 'Specify the user_id associated with the person',
             'start': 'Value to start from ',
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
@user.route('/user/user_messages')
class Usermessage(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if user:
            messages = Message.query.filter(or_(Message.sender_id == user.id , Message.recipient_id == user.id)).distinct().all()
            return{
            "results":marshal(messages,messagedata1)
        }, 200
        else:
            return{
                "status":0,
                "res":"This user does not exist"
            }
        
    @token_required
    @user.expect(user_messaging)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        content =req_data['content']
        sender = Users.query.filter_by(uuid=data['uuid']).first()
        receiver = Users.query.filter_by(id=req_data['recipient_id']).first()
        
        if sender and receiver:
            msg = Message(author=sender, recipient=receiver,body=content)
            db.session.add(msg)
            db.session.commit()
            return {
                "status":1,
                "res":"Message sent"
            }, 200
        else:
            return {
                "status":0,
                "res":"Users are not found"
            }, 404
#delete later


@user.doc(
    security='KEY',
    params={ 'user_id_2': 'Specify the user_id associated with the person',
             'start': 'Value to start from ',
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
@user.route('/user/message_conversation')
class Usermessage_sender(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        user_2= Users.query.filter_by(id=user2).first()
        if user:
            messages = Message.query.filter(and_(or_(Message.sender_id == user_2.id , Message.recipient_id == user_2.id) ,or_(Message.sender_id == user.id , Message.recipient_id == user.id))).all()

            return{
                "results":marshal(messages,messagedata)
            }, 200
        else:
            return{
                "status":0,
                "res":"This user does not exist"
            }
        
@user.doc(
    security='KEY',
    params={ 'user_id': 'Specify the user_id associated with the person',
             'start': 'Value to start from ',
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
@user.route('/user/reaction')
class User_reaction(Resource):
    @token_required
    @user.expect(reaction)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        reaction = req_data['reaction']
        user = Users.query.filter_by(uuid=data['uuid']).first()
        comment = Comment.query.filter_by(id=req_data['comment']).first()

        if user:
            if comment:
                if reaction == ":smile:" :
                    Reactions =Reaction(comment.id,reaction)
                    db.session.add(Reactions)
                    db.session.commit()
                    return{
                        "status":1,
                        "res":"smile reaction posted"
                    }
                if reaction == ":angry:":
                    Reactions =Reaction(comment.id,reaction)
                    db.session.add(Reactions)
                    db.session.commit()
                    return{
                        "status":1,
                        "res":"anger reaction posted"
                    }
                if reaction == ":disappointed_relieved:":
                    Reactions =Reaction(comment.id,reaction)
                    db.session.add(Reactions)
                    db.session.commit()
                    return{
                        "status":1,
                        "res":"sad reaction posted"
                    }
                else:
                     return{
                        "status":1,
                        "res":"this reaction is not  available"
                    }
            else:
                return{
                    "status":0,
                    "res":"comment not found"
                }
                
        else:
            return{
                "status":0,
                "res":"Users are not found"
            }
            #getmethod
            #deletemethod