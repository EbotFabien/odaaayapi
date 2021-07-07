from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os, json
from flask_cors import CORS
from functools import wraps
import requests as rqs
from flask import abort, request, session,Blueprint
from app.models import Users, followers, Setting,Notification,clap,Save,Posts
from flask import current_app as app
from app import db, cache, logging
from sqlalchemy import or_, and_, distinct, func
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import werkzeug
import colorgram
import requests
from datetime import datetime, timedelta
import json
from app.services import mail,phone

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

api = Blueprint('api',__name__, template_folder='../templates')
user1=Api( app=api, doc='/docs',version='1.4',title='News API.',\
description='', authorizations=authorizations)
#from app.api import schema
CORS(api, resources={r"/api/*": {"origins": "*"}})

uploader = user1.parser()
uploader.add_argument('file', location='files', type=FileStorage, required=False, help="You must parse a file")
uploader.add_argument('name', location='form', type=str, required=False, help="Name cannot be blank")

user = user1.namespace('/api/user', \
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

COnfirminvitation= user.model('COnfirminvitation',{
    'uuid':fields.String(required=True, description="Users uuid"),
    'user_name': fields.String(required=False, description="Users Name"),
    'email': fields.String(required=False, description="Users Email"),
    'password':fields.String(required=False, description="Password"),
    'phone_number':fields.String(required=False, description="Phone Number"),
})

sinvitation= user.model('sinvitation',{
    'email': fields.String(required=False, description="invitee Email")
})
userdata = user.model('Profile', {
    'id': fields.Integer(required=True),
    'username': fields.String(required=True),
    'profile_picture': fields.String(required=True),
    'email': fields.String(required=True),
    'uuid': fields.String(required=True),
    'bio': fields.String(required=False),
    'user_number': fields.String(required=True),
    'verified': fields.Boolean(required=True),
    'user_visibility': fields.Boolean(required=True)
})
postsdata = user.model('postsdata',{
    'id': fields.Integer(required=True),
    'title': fields.String(required=True)
})

saved = user.model('saved', {
    'id': fields.Integer(required=True),
    'user_id': fields.String(required=True),
    'post___data': fields.List(fields.Nested(postsdata))
})

notification_ =user.model('notification_',{
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'user_id': fields.String(required=True),
    'seen': fields.String(required=True),
    'timestamp': fields.String(required=True),
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
    'N_S_F_W': fields.Boolean(required=True),
    
})
user_prefs = user.model('Preference', {
    'id': fields.Integer(required=True),
    'language_id': fields.Integer(required=True),
    'users_id': fields.Integer(required=True),
    'theme': fields.String(required=True),
    'post': fields.Boolean(required=True),
    'saves': fields.Boolean(required=True),
    'N_S_F_W': fields.Boolean(required=True),
})
updateuser = user.model('Update',{
    'user_id':fields.String(required=True),
    'username': fields.String(required=True),
    'email':fields.String(required=False),
    'number':fields.String(required=False),
    'profile_picture':fields.String(required=False),
    'user_visibility':fields.String(required=False),
})
User_R_data = user.model('User_R_data',{
    'username': fields.String(required=True),
    'email':fields.String(required=False),
    'number':fields.String(required=False),
    'bio':fields.String(required=False),
    'uuid':fields.String(required=False),
    'profile_picture':fields.String(required=False),
    'user_visibility':fields.String(required=False),
})
deleteuser = user.model('deleteuser',{
    'uuid':fields.String(required=True)
})
Postfollowed = user.model('Postfollowed',{
    'id': fields.Integer(required=True),
    'title':fields.String(required=True),
    'uploader_id' : fields.Integer(required=True),
    
})
following_followers = user.model('following',{
    'username': fields.String(required=True),
    'profile_picture': fields.String(required=True),
    'uuid': fields.String(required=True),
    'bio': fields.String(required=False),
})
fanbase =user.model('Fanbase',{
    'subject':fields.String(required=True),  
})
user_notify = user.model('notify',{
    'channel_id':fields.String(required=True)
})
user_messaging =  user.model('messaging',{
    'uuid':fields.String(required=True),
    'content':fields.String(required=True)

})
user_name = user.model('user_clap',{
    'id':fields.Integer(required=True),
    'username':fields.String(required=True),
})


ip_data = user.model('address',{
    'address':fields.String(required=True)
})
Notification_seen = user.model('Notification_seen',{
    'notification_id':fields.String(required=True)
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
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        if fan_base == 'post':
            posts=user.followed_posts() 
            return {
                "results":marshal(posts,Postfollowed)
            }, 200
    
        if fan_base == 'following':
            following=user.has_followed()
            return {
                "results":marshal(following,following_followers)
            }, 200
        if fan_base == 'followers':
            followers=user.is_followers()
            return {
                "results":marshal(followers,following_followers)
            }, 200

    @token_required
    @user.expect(deleteuser)#This is the following route but we will use the deleteuser model since we just need the user ID        
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        user_to_follow =Users.query.filter_by(uuid=req_data['uuid']).first()
        if user_to_follow is None :
            return {'status': 0,'res':'fail'}, 200
        if user_to_follow:
            user.follow(user_to_follow)
            db.session.commit()
            return{'status': 1, 'res':'success'},200
        else:
            return {'status': 0, 'res':'fail'},200
    @token_required
    @user.expect(deleteuser)#This is the following route but we will use the deleteuser model since we just need the user ID        
    def delete(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        user_to_unfollow =Users.query.filter_by(uuid=req_data['uuid']).first()
        if user_to_unfollow is None :
            return {'status': 0, 'res':'faila'}, 200
        if user.is_following(user_to_unfollow) is None:
            return {'status': 0, 'res':'fails'}, 200
        if user.is_following(user_to_unfollow):
            user.unfollow(user_to_unfollow)
            db.session.commit()
            return{'status': 1, 'res':'success'},200
        else:
            return {'status': 0, 'res':user_to_unfollow.id},200

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
        user_to_block =Users.query.filter_by(uuid=req_data['uuid']).first()
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
        user_to_unblock = Users.query.filter_by(uuid=req_data['uuid']).first()
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
            user.N_S_F_W =req_data['N_S_F_W']
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
            user_settings.saves = req_data['saves']
            user_settings.users_id =req_data['users'] 
            db.session.commit()
            return {
                "status":1,
                "res":"User_settings updated"
            }, 200






        


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
@user.route('/user/ip_addressdata')
class User_ip_address(Resource):
     #@token_required
    @user.expect(ip_data)
    def post(self):
        req_data = request.get_json()
       # token = request.headers['API-KEY']
        #data = jwt.decode(token, app.config.get('SECRET_KEY'))
        ip_address = req_data['address']
       # user = Users.query.filter_by(uuid=data['uuid']).first()
        ip_info="http://ip-api.com/json/"+ip_address 
        if ip_address:
            response=rqs.get(ip_info)
            return{
                'status':1,
                'res': json.loads(response.content)
            }
        else:
            return{
                'status':0,
                'res':"input IP"
            }


#test
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
@user.route('/user/profilepic')
class User_upload_profile_pic(Resource):
    @token_required
    @user.expect(uploader)
    def post(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        args = uploader.parse_args()
        if user and  args['file'] is not None: 

            if args['file'].mimetype == 'image/jpeg':
                name = args['name']
                orig_name = secure_filename(args['file'].filename)
                file = args['file']
                destination = os.path.join(app.config.get('UPLOAD_FOLDER'),'profilepic/' ,user.uuid)
                if not os.path.exists(destination):
                    os.makedirs(destination)
                profilepic_ = '%s%s' % (destination+'/', orig_name)
                file.save(profilepic_)
                user.profile_picture ='/profilepic/'+user.uuid+'/'+orig_name
                db.session.commit()
                colors = colorgram.extract(profilepic_, 3)

                first_color = colors[0]
                RGB=first_color.rgb
                return {
                    'status':1,
                    'res':'picture uploaded',
                    'pic':RGB
                }
            if args['file'].mimetype == 'image/png':
                name = args['name']
                orig_name = secure_filename(args['file'].filename)
                file = args['file']
                destination = os.path.join(app.config.get('UPLOAD_FOLDER'),'profilepic/' ,user.uuid)
                if not os.path.exists(destination):
                    os.makedirs(destination)
                profilepic_ = '%s%s' % (destination+'/', orig_name)
                file.save(profilepic_)
                user.profile_picture ='/profilepic/'+user.uuid+'/'+orig_name
                db.session.commit()
                colors = colorgram.extract(profilepic_, 3)

                first_color = colors[0]
                RGB=first_color.rgb
                return {
                    'status':1,
                    'res':'picture uploaded',
                    'pic':RGB
                }
            else:
                return{
                    'status':0,
                    'res':'please put image format'
                }
        else:
            return{
                'status':0,
                'res':"user doesn't exist"
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
@user.route('/user/Randomusers')
class User_Random(Resource):
     def get(self):
        if request.args:
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
            next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
            previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
            channel = Users.query.order_by(func.random()).paginate(int(start),int(count), False).items
            return{
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(channel,User_R_data)
            }, 200
        else:
            return{
                "res":"return request",
                "status":0,
                
            }, 404


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
@user.route('/user/Notification')
class Seen_Notification(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
            previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
            user = Users.query.filter_by(uuid=data['uuid']).first()
            notification= Notification.query.filter_by(user_id=user.id).paginate(int(start),int(count), False).items
            return{
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(notification,notification_)
            }, 200
        else:
            return{
                "res":"return request",
                "status":0,
                
            }, 404
    @token_required
    @user.expect(Notification_seen)
    def post(self):
        token = request.headers['API-KEY']
        req_data = request.get_json()
        notification=req_data['notification_id']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        notification= Notification.query.filter_by(id=notification).first()

        if user and notification:
            notification.seen = True
            db.session.commit()
        else:
            return{
                "res":"failed",
                "status":0,
                
            }, 404


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
@user.route('/user/invitation')
class  Invitation(Resource):
    @token_required
    def get(self):
        token =  request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        if data is None:
            return{
                'status':'0',
                'res':'This token has expired'
            },400
        else:
            user = Users.query.filter_by(uuid=data['uuid']).first()
            return{
                'status':'1',
                'user':user.username,
                'uuid':user.uuid,
                'res':'Your token is valid'
            },200

    @token_required#check the data sent
    @user.expect(sinvitation)
    def post(self):
        token = request.headers['API-KEY']
        req_data = request.get_json()
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        email= req_data['email']
        
        if user and email:
            token = jwt.encode({
                'uuid': user.uuid,
                'exp': datetime.utcnow() + timedelta(minutes=60), 
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256')
            r="http://localhost:3000/en/invitation?token="+str(token)
            mail.invitation_email(token,email,user.email,r)
            return{
                'token':str(token),
                'res':'Invitation_sent'
            },200

        else:
           return{
                'status':'0',
                'res':'You are not a user'
            },400 

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
@user.route('/user/confirminvitation')
class  confirminvitation(Resource):
    @user.expect(COnfirminvitation)
    def post(self):
        signup_data = request.get_json()
        user1 = Users.query.filter_by(uuid=signup_data['uuid']).first()
        if signup_data and user1:
            email = signup_data['email'] or None
            username = signup_data['user_name'] or None
            password = signup_data['password'] or None
            phone_number = signup_data['phone_number'] or None

            if email and username and password is not None:
                user = Users.query.filter_by(email=email).first() #filter by user handle
            
                if user:
                    return { 
                        'res':'user already exist',
                        'status': 0
                    }, 200
                else:
                    verification_code = phone.generate_code()

                    if verification_code:
                        newuser = Users(username,str(uuid.uuid4()),False, signup_data['email'])
                        newuser.code = verification_code
                        newuser.passwordhash(password)
                        newuser.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                        db.session.add(newuser)
                        db.session.commit()
                        newuser.follow(user1)
                        db.session.commit()
                        #send code to email
                        mail.send_email(app,[signup_data['email']],verification_code) #check this
                        return {
                            'res': 'success',
                            'user_name':username,
                            'email': signup_data['email'],
                            'status': 1
                        }, 200
                    else:
                        return {
                            'status': 0,
                            'res':'error'
                        }, 201
            if phone_number is not None:
                user = Users.query.filter_by(phone=phone_number).first()
                if user:
                    return { 
                        'res':'user already exist',
                        'status': 0
                    }, 200
                else:
                    verification_code=phone.generate_code()
                    newuser = Users(str(phone_number),str(uuid.uuid4()),True, str(phone_number),phone_number)
                    db.session.commit()
                    newuser.code = verification_code
                    newuser.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                    db.session.add(newuser)
                    db.session.commit()
                    newuser.follow(user1)
                    db.session.commit()
                    phone.send_confirmation_code(phone_number,verification_code)
                    return {
                        'status': 1,
                        'Phone':phone_number,
                        'res': 'verification sms sent'
                        }, 200
            if email and username and password and phone_number is not None:
                user = Users.query.filter_by(email=email).first()
                if user:
                    return { 
                        'res':'user already exist',
                        'status': 0
                    }, 200
                else:
                    verification_code=phone.generate_code()
                    newuser = Users(user_name,str(uuid.uuid4()),True, email,phone_number)
                    db.session.commit()
                    newuser.code = verification_code
                    newuser.passwordhash(password)
                    newuser.code_expires_in = datetime.utcnow() + timedelta(minutes=2)
                    db.session.commit()
                    newuser.follow(user1)
                    db.session.commit()
                    phone.send_confirmation_code(phone_number,verification_code)
                    mail.send_email(app,[signup_data['email']],verification_code) #check this
                    return {
                        'status': 1,
                        'user_name':user_name,
                        'email':email,
                        'Phone':phone_number,
                        'res': 'verification sms  and email sent'
                        }, 200
        else:
            return {
                'status': 0,
                'res': 'No data'
            },201

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
@user.route('/user/No_claps')
class  No_claps_(Resource):
    @token_required
    def get(self):
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()

        if user:
            number =user.No_claps()
            return{
                    'number of claps':number,
                    
                },200

        else:
            return{
                    "status":0,
                    "res":"Fail"
                },400



@user.doc(
    security='KEY',
    params={ 
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
@user.route('/user/savings')
class  No_savings(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
            previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
            user = Users.query.filter_by(uuid=data['uuid']).first()
            saves=Save.query.filter_by(user_id=user.id).paginate(int(start),int(count), False).items
            if saves:
                return{
                    "start":start,
                    "limit":limit,
                    "count":count,
                    "next":next,
                    "previous":previous,
                    'number of saves':count,
                    "results":marshal(saves,saved)
                            
                },200

            else:
                return{
                        "status":0,
                        "res":"Fail"
                    },400

@user.doc(
    security='KEY',
    params={ 
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
@user.route('/user/posts')
class  Posts_(Resource):
    @token_required
    def get(self):
        if request.args:
            token = request.headers['API-KEY']
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
            previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
            user = Users.query.filter_by(uuid=data['uuid']).first()
            posts=Posts.query.filter_by(author=user.id).paginate(int(start),int(count), False).items
            if posts:
                return{
                    "start":start,
                    "limit":limit,
                    "count":count,
                    "next":next,
                    "previous":previous,
                    'number of saves':count,
                    "results":marshal(posts,postsdata)
                            
                },200

            else:
                return{
                        "status":0,
                        "res":"Fail"
                    },400



