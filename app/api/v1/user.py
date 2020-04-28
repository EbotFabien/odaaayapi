from flask_restplus import Namespace, Resource, fields,marshal
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session
from app.models import Users,followers
from flask import current_app as app
from app import db, cache, logging

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
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'number': fields.String(required=True),
})
updateuser = user.model('Update',{
    'user_id':fields.String(required=True),
    'username': fields.String(required=True),
    'email':fields.String(required=True),
    'number':fields.String(required=True),
})
deleteuser = user.model('deleteuser',{
    'user_id':fields.String(required=True)
})
Postfollowed = user.model('Postfollowed',{
    'id': fields.Integer(required=True),
    'title':fields.String(required=True),
    'uploader_id' : fields.Integer(required=True),
    
})
fanbase =user.model('Fanbase',{
    'subject':fields.String(required=True),  
})

@user.doc(
    security='KEY',
    params={ 'username': 'Specify the username associated with the person',
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
        username = request.args.get('username', None)
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if username == user.username: 
            # get list of blocked users to make sure they don't see profile information.
            return{
                "results":marshal(user,userdata)
                }
        else:
            return {'res': 'User not found'}, 404
       
    @token_required
    @user.expect(updateuser)
    def post(self):
        return {}, 200
    @token_required
    @user.expect(updateuser)
    def put(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token,app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        if req_data['username'] and req_data['email'] is None:
            return {'res':'fail'}, 404  

        if req_data['user_id'] == user.id:
            user.username = req_data['username']
            user.email = req_data['email']
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
        if req_data['username'] and req_data['email'] is None:
            return {'res':'fail'}, 404  

        if req_data['user_id'] == user.id:
            user.username = req_data['username']
            user.email = req_data['email']
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
    params={ 'username': 'Specify the username associated with the person',
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
    #@user.marshal_with(fanbase)
    #@user.expect(fanbase)
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
        if fan_base == 'post':
            return {
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(posts,Postfollowed)
            }, 200
               # print(posts)
        if fanbase == 'following':
            return {'res':'success'}, 200
        if fanbase == 'followers':
            return {'res':'success'}, 200
       
        
       

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
@user.route('/user/prefs')
class Userprefs(Resource):
    @user.marshal_with(userinfo)
    def get(self):
        return {}, 200
    @token_required
    @user.expect(userinfo)
    def post(self, username):
        return {}, 200