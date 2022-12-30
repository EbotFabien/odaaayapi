from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os, json
from flask_cors import CORS
from functools import wraps
import requests as rqs
from flask import abort, request, session,Blueprint
from app.models import Users, followers, Setting,Notification,clap,Save,Posts,Language,Translated,Subs,Account
from flask import current_app as app
from app import db, cache, logging, createapp
from sqlalchemy import or_, and_, distinct, func
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import werkzeug
import colorgram
import requests
from datetime import datetime, timedelta
import json
from app.services import mail,phone
import stripe
from flask import current_app as app

from config import Config
import base64
import os.path
from os import path
from werkzeug.utils import redirect
import cloudinary
import cloudinary.uploader
from sqlalchemy import func,or_, and_, desc, asc




cloudinary.config(
    cloud_name="odaaay",
    api_key="893419336671437",
    api_secret="lIGoIkb5l7vZGpcD-k18Py49nGQ"
)


#with app.app_context().push():
stripe.api_key = Config.stripe_secret_key

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

langdata= user.model('langdata',{
    'code': fields.String(required=True)
})

userdata = user.model('userdata', {
    'id': fields.Integer(required=True),
    'username': fields.String(required=True),
    'picture': fields.String(required=True),
    'email': fields.String(required=True),
    'country':fields.String(required=True),
    'uuid': fields.String(required=True),
    'bio': fields.String(required=False),
    'rescue':fields.String(required=False),
    'background': fields.String(required=False),
    'Lang':fields.List(fields.Nested(langdata)),
    'phone': fields.String(required=True),
    'handle':fields.String(required=True),
    'verified': fields.Boolean(required=True),
    'user_visibility': fields.Boolean(required=True)
})

postsdata = user.model('postsdata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'uuid': fields.String(required=True),
    'author': fields.Integer(required=True),
    'user_name': fields.String(required=True),
    'post_type': fields.Integer(required=True),
    'text_content': fields.String(required=True),
    'post_url': fields.String(required=True),
    'audio_url': fields.String(required=True),
    'video_url': fields.String(required=True),
    'created_on': fields.DateTime(required=True),
    'thumb_url': fields.String(required=False),
    'tags': fields.String(required=True),
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
    'type':  fields.String(required=True),
    'username':  fields.String(required=False),
    'email': fields.String(required=False),
    'phone': fields.String(required=False),
    'newphone':fields.String(required=False),
    'language_id': fields.String(required=False),
    'bio': fields.String(required=False),
    'country':fields.String(required=False),
    'handle':fields.String(required=False),
    'code':fields.String(required=False),
    'user_visibility': fields.Boolean(required=False)
    
})
user_prefs = user.model('Preference', {
    'id': fields.Integer(required=True),
    'language_id': fields.Integer(required=True),#fix data for language,so as to pass code
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
    'picture': fields.String(required=True),
    'user_visibility':fields.String(required=False),
})
User_R_data = user.model('User_R_data',{
    'username': fields.String(required=True),
    'email':fields.String(required=False),
    'number':fields.String(required=False),
    'bio':fields.String(required=False),
    'uuid':fields.String(required=False),
    'picture': fields.String(required=True),
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
    'picture': fields.String(required=True),
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
uploaderdata = user.model('uploaderdata',{
    'file':fields.String(required=True),
    'name':fields.String(required=True),
})

ip_data = user.model('address',{
    'address':fields.String(required=False)
})
Notification_seen = user.model('Notification_seen',{
    'notification_id':fields.String(required=True)
})

lang_post = user.model('lang_post', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True),
    'fullcontent':fields.String(required=True),
    'language_id': fields.Integer(required=True),
    'tags': fields.String(required=True),
    'posts': fields.List(fields.Nested(postsdata)),
})


@user.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
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
@user.route('/backdrop')

class backdrop(Resource):
    @token_required
    @user.expect(uploader)
    def post(self):
        args = uploader.parse_args()
        destination = Config.UPLOAD_FOLDER_MEDIA
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        File=args['file']
        Name=args['name']
        if File.mimetype == "image/jpeg" :
            fila=os.path.join(destination,str(data['uuid']),'backdrop')#,Name)
            if os.path.isdir(fila) == False:
                os.makedirs(fila)
            fil=os.path.join(fila,Name)#,Name)
            File.save(fil)
            upload_result = cloudinary.uploader.upload(args)
            user.background=upload_result["secure_url"]#str(data['uuid'])+"/backdrop/"+Name
            db.session.commit()
            return {
                    "status":1,
                    "res":"back drop was uploaded",
                    }, 200
                    
        if File.mimetype == "image/jpg" :
            fila=os.path.join(destination,str(data['uuid']),'post')#,Name)
            if os.path.isdir(fila) == False:
                os.makedirs(fila)
            fil=os.path.join(fila,Name)#,Name)
            File.save(fil)
            upload_result = cloudinary.uploader.upload('https://odaaay.com/api/static/files/'+str(data['uuid'])+"/backdrop/"+Name)
            user.background=upload_result["secure_url"]#str(data['uuid'])+"/backdrop/"+Name
            db.session.commit()
            return {
                    "status":1,
                    "res":"back drop was uploaded",
                    }, 200
        else:
            return {
                    "status":0,
                    "res":"Put a Jpeg file",
                    }, 200


@user.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
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
@user.route('/user/upload')

class Uplu(Resource):
    @token_required
    @user.expect(uploaderdata)
    def post(self):
        args = request.get_json()
        destination = Config.UPLOAD_FOLDER_MEDIA
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        File=args['file']
        Name=args['name']

        
        if File:
            if Name.lower() =="jpeg":
                ex=user.username+".jpeg"
            if Name.lower() =="jpg":
                ex=user.username+".jpg"
            if Name.lower() =="png":
                ex=user.username+".png"
            pa=str(data['uuid'])+"/"+'profile'
            fila=os.path.join(destination,pa)
            if path.exists(fila) == False:
                os.makedirs(fila)
            fil=os.path.join(fila,ex)
            if path.exists(fil) == True:
                os.remove(fil)
            with open(fil, 'wb') as image_file:
                image_file.write(base64.b64decode(File))
                upload_result = cloudinary.uploader.upload('https://odaaay.com/api/static/files/'+str(data['uuid'])+"/profile/"+ex)
            user.picture=upload_result["secure_url"]#str(data['uuid'])+"/profile/"+ex
            db.session.commit()
            return {
                    "status":1,
                    "res":"profile pic uploaded",
                    }, 200
        else:
            return {
                    "status":0,
                    "res":"Put a Jpeg file",
                    }, 200


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
            followers=user.is_followersd()
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
            if  user_to_follow.paid == True:
                sub=Subs.query.filter(and_(Subs.product_user==user_to_follow.id,Subs.user_sub==user.id,Subs.valid==True)).first()
                if sub is None:
                    return {'status': 0,
                     'res':'please pay subscription',
                     'uuid':req_data['uuid'],
                     },200
                else:
                    return{'status': 1, 'res':'You have sub already'},200
            else:
                user.follow(user_to_follow)# here   
                db.session.commit()
                mail.subscription_message(user_to_follow.picture,user_to_follow.username)
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
            if user_to_unfollow.paid==True:
                product=Subs.query.filter(and_(Subs.user_sub==user.id,Subs.product_user==user.id,Subs.valid==True)).first()
                if product:
                    stripe.Subscription.modify(
                    product.sub_id,
                    cancel_at_period_end=True
                    )
                    return{'status': 1, 'res':'success'},200
                else:
                    return {'status': 0, 'res':'fail'},400
            else:
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
            acc_=Account.query.filter_by(user=user.id).first()
            if acc_ == None:
                status_=0
                status=0
            if acc_ != None: 
                if acc_.valid == True:
                    status=2
                if acc_.valid == False:
                    status=1
                if acc_.valid == True and user.paid == True :
                    status_=2
                if acc_.valid == False and user.paid == True :
                    status_=1
                if acc_ and user.paid == False :
                    status_=3
            return {
                "post_payment":status,
                "account_payment":status_,
                "user": marshal(user, userdata)
                }, 200
        else:
           return {

           }, 200 

    @token_required
    @user.expect(update_settings)
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()

        
        if req_data['type'] =='settings':
            lang=req_data['language_id'] or None
            language= Language.query.filter_by(code=lang).first()
            user.username=req_data['username'] or None
            user.email=req_data['email'] or None
            user.country=req_data['country'] or None
            user.language_id=language.id
            user.handle=req_data['handle'] or None
            user.bio =req_data['bio'] or None
            
            #backgroundpicture
            db.session.commit()
            return {
                    "status":1,
                    "res":"User_data updated"
                }, 200 
        if req_data['type'] =='security':
            ph =req_data['phone'] or None
            ph = "".join(ph.split())
            NP=req_data['newphone'] or None
            if user.phone == ph :
                try:
                    phone.sendverification(NP)
                    return {
                                'status': 1,
                                'res': 'verification sms sent'
                            }, 200
                except:
                    return {
                        'status': 0,
                        'res':'This phone number cannot receive a code,please use rescue number',
                        }, 400

            else:
                return {
                    "status":0,
                    "res":"This phone number doesn't belong to this user"
                }, 400 
        if req_data['type'] =='deactivate':
            #visi=req_data['user_visibility'] or None
            link='https://odaaay.com/api/v1/user/confirm_delete/'+str(user.uuid)
            mail.delete_account(user.email,link)
            db.session.commit()
            return {
                    'status': 1,
                    'res':'success',
                    }, 200


        if req_data['type'] =='code':
            code=req_data['code'] or None
            NP=req_data['newphone'] or None
            NP = "".join(NP.split())
            if code is not None:
                check=phone.checkverification(NP,code)
                if check.status == "approved":
                    user.phone=NP
                    user.verified_phone=True
                    user.tries =0
                    db.session.commit()
                    return {
                        'status': 1,
                        'res':'success',
                        }, 200
                else:
                    return {
                        'status': 0,
                        'res':'This phone number cannot receive a code,please use rescue number',
                        }, 400

            else:
                return {
                "status":0,
                "res":"No code"
            }, 400
        if req_data['type'] =='rescue':
            uu=str(uuid.uuid4())
            user.rescue=uu
            db.session.commit()
            return {
                    'status': 1,
                    'res':'success',
                    }, 200
        else:
            return {
                "status":0
            }, 400
        

        


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
        if ip_address == None:
            return{
                'status':0,
                'res':"input IP"
            }
       # user = Users.query.filter_by(uuid=data['uuid']).first()
        ip_info="http://ip-api.com/json/"+ip_address 
        if ip_address != None:
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
@user.route('/user/confirm_delete/<uuid>')
class User_confirm_delete(Resource):

    def get(self,uuid):
        user = Users.query.filter_by(uuid=uuid).first()
        
        if user:
            user.user_visibility=False
            user.verified_phone=False
            user.verified_email = False
            db.session.commit()
            language=Language.query.filter_by(id=user.language_id).first()
            link='https://odaaay.com/'+str(language.code)+'/delete-account?delete=true'
            mail.account_deleted(user.email)
            return redirect (link)

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
                user.picture ='/profilepic/'+user.uuid+'/'+orig_name
                db.session.commit()
                #colors = colorgram.extract(profilepic_, 3)

                #first_color = colors[0]
                #RGB=first_color.rgb
                return {
                    'status':1,
                    'res':'picture uploaded'
                    #'pic':RGB
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
                user.picture ='/profilepic/'+user.uuid+'/'+orig_name
                db.session.commit()
                #colors = colorgram.extract(profilepic_, 3)

                #first_color = colors[0]
                #RGB=first_color.rgb
                return {
                    'status':1,
                    'res':'picture uploaded'
                    #'pic':RGB
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
@user.route('/user/Randomusers')
class User_Random(Resource):
     @token_required
     def get(self):
        if request.args:
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
            next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
            previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
            token = request.headers['API-KEY']
            req_data = request.get_json()
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            user = Users.query.filter_by(uuid=data['uuid']).first()
            channel = Users.query.filter_by(user_visibility=True).order_by(func.random()).paginate(int(start),int(count), False).items
            followed =[]
            latest=[]
            followers=user.has_followed()
            for i in channel:
                for j in followers:
                    if i.id == j.id :
                        followed.append(i.id)
                        channel.remove(i)

            for i in channel:
                if i.id == user.id:
                    channel.remove(i)                
            return{
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "followed":followed,
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
             'lang': 'i18n',
             'fil':'type',
             'type':'savings or posts',
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
            fil = request.args.get('fil',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
            lang = request.args.get('lang', None)
            Type = request.args.get('type', None)
            language_dict = {'en', 'es','ar', 'pt', 'sw', 'fr', 'ha'}
            data = jwt.decode(token, app.config.get('SECRET_KEY'))
            next = "/api/v1/posts?"+start+"&limit="+limit+"&count="+count
            previous = "api/v1/posts?start="+start+"&limit"+limit+"&count="+count
            user = Users.query.filter_by(uuid=data['uuid']).first()
            for i in language_dict:
                if i == lang:
                    current_lang = Language.query.filter_by(code=i).first()
                    posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(
                                        Posts,(Posts.id == Translated.post_id)).filter(
                                            Posts.author==user.id)
                    if fil == 'new':
                        posts_feed =posts_feeds.order_by(asc(Posts.created_on)).paginate(int(start), int(count), False)
                    if fil == 'old':
                        posts_feed =posts_feeds.order_by(desc(Posts.created_on)).paginate(int(start), int(count), False)
                    if fil == 'random':
                        posts_feed =posts_feeds.order_by(func.random()).paginate(int(start), int(count), False)
                    else:
                        posts_feed =posts_feeds.order_by(func.random()).paginate(int(start), int(count), False)
                    total = (posts_feed.total/int(count))
                    if Type == "savings":
                        if posts_feed:
                            savess=[]
                            user_saves=Save.query.filter_by(user_id=user.id).order_by(Save.id.desc()).all()
                            user_posts= Translated.query.filter_by(language_id=current_lang.id).join(
                                        Save,(Save.post_id == Translated.post_id)).filter(
                                            Save.user_id==user.id).paginate(int(start), int(count), False).items 
                            return{
                                "start":start,
                                "limit":limit,
                                "count":count,
                                "next":next,
                                "previous":previous,
                                "results":marshal(user_posts,lang_post)
                                        
                            },200

                        else:
                            return{
                                    "status":0,
                                    "res":"Fail"
                                },400

                    if Type == "posts":

                        if posts_feed:
                            return{
                                "start":start,
                                "limit":limit,
                                "count":count,
                                "next":next,
                                "total":total,
                                "previous":previous,
                                "results":marshal(posts_feed.items,lang_post)
                                        
                            },200

                        else:
                            return{
                                    "status":0,
                                    "res":"Fail"
                                },400



@user.doc(
    security='KEY',
    params={ 'uuid': 'Specify the uuid associated with the person',
             'start': 'Value to start from ',
             'lang': 'i18n',
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
@user.route('/profile')
class Data(Resource):
    @token_required
    #@user.marshal_with(userinfo)
    def get(self):
        user_id = request.args.get('uuid')
        lang = request.args.get('lang', None)
        start = request.args.get('start',None)
        limit = request.args.get('limit',None)
        count = request.args.get('count',None)
        language_dict = {'en', 'es','ar', 'pt', 'sw', 'fr', 'ha'}
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        next = "/api/v1/profile?"+start+"&limit="+limit+"&count="+count
        previous = "api/v1/profile?start="+start+"&limit"+limit+"&count="+count
        user2 = Users.query.filter_by(uuid=user_id).first()
        if user:
            for i in language_dict:
                    if i == lang:
                        current_lang = Language.query.filter_by(code=i).first()
                        posts_feeds = Translated.query.filter_by(language_id=current_lang.id).join(
                                        Posts,(Posts.id == Translated.post_id)).filter(
                                            Posts.author==user2.id)
                        posts_feed =posts_feeds.order_by(func.random()).paginate(int(start), int(count), False)
                        total = (posts_feed.total/int(count))
                        if user != user2:
                            if user.is_following(user2) > 0:
                                follow=True
                            else:
                                follow=False
                        else:
                            follow=False
                        if posts_feed:
                                return{
                                    "start":start,
                                    "limit":limit,
                                    "count":count,
                                    "next":next,
                                    "total":total,
                                    "previous":previous,
                                    "follow":follow,
                                    "user_data":marshal(user2,userdata),
                                    "results":marshal(posts_feed.items,lang_post)
                                },200

                        else:
                            return{
                                    "status":0,
                                    "res":"Fail"
                                },400

        else: 
            return{
                    "status":0,
                    "res":"User doesn't exist"
                }, 200