from flask_restplus import Namespace, Resource, fields,marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps
from flask import abort, request, session,Blueprint
from app.models import Users,Posts,Comment,Channels, subs
from flask import current_app as app
from app import db,cache
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import werkzeug

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
comment1=Api( app=api, doc='/docs',version='1.4',title='News API.',\
description='', authorizations=authorizations)
#from app.api import schema
CORS(api, resources={r"/api/*": {"origins": "*"}})

uploader = comment1.parser()
uploader.add_argument('file', location='files', type=FileStorage, required=True, help="You must parse a file")
uploader.add_argument('name', location='form', type=str, required=True, help="Name cannot be blank")



comment = comment1.namespace('/api/comment', \
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
commentupdate =comment.model('Update',{
    'Comment_id':fields.String(required=True),
    'post_id': fields.String(required=True),
    'content': fields.String(required=True),
})  
commentdelete =comment.model('Update',{
    'Comment_id':fields.String(required=True),
    'post_id': fields.String(required=True),
})  
commentdata =comment.model('commentdata',{
    'user_id':fields.String(required=True),
    'post_id':fields.String(required=True),
    'content':fields.String(required=True),
    'path':fields.String(required=True),
    
})




@comment.doc(
    security='KEY',
    params={ 'postid': 'Specify the id of the post',
             'start': 'Value to start from ',
             'limit': 'Total limit of the query',
             'count': 'Number results per page',
             'file':'The file is an mp3',
             'content':'Specify if it is text or audio',
             'comment_type':'Specify the type of comment',
             'Parent_id':'Specify parent_id if present'
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
@comment.route('/comment')
class Data(Resource):
    @token_required
    @cache.cached(300, key_prefix='all_Comments')
    #@comment.marshal_with(apiinfo)
    def get(self):
        if request.args:
            start = request.args.get('start',None)
            limit = request.args.get('limit',None)
            count = request.args.get('count',None)
            next = "/api/v1/comment?"+start+"&limit="+limit+"&count="+count
            previous = "api/v1/comment?start="+start+"&limit"+limit+"&count="+count
            comment = Comment.query.filter_by(Comment.public == True).order_by(Comment.path).paginate(int(start),int(count), False).items
            for comments in comment:
                print( comments.path)
            return{
                "start":start,
                "limit":limit,
                "count":count,
                "next":next,
                "previous":previous,
                "results":marshal(comment,commentdata)
            }, 200
        else:
            comment =Comment.query.all()
            return marshal(comment,commentdata),200
    @token_required
    #@comment.expect(commentcreation)
    @comment.expect(uploader)
    def post(self):
        post_id=request.args.get('postid')
        comment_type=request.args.get('comment_type')
        content =request.args.get('content')
        parent_id =request.args.get('Parent_id')
        if post_id is None:
            return {'res':'fail'},400
        token = request.headers['API-KEY']
        args = uploader.parse_args()
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        post_id_real=Posts.query.get(int(post_id))
        
        if comment_type == "audio":
            if post_id and  args['file'] is not None: 
                if args['file'].mimetype == 'audio/mpeg':
                    name = args['name']
                    orig_name = secure_filename(args['file'].filename)
                    file = args['file']
                    destination = os.path.join(app.config.get('UPLOAD_FOLDER'),'comments/' ,user.uuid)
                    if not os.path.exists(destination):
                        os.makedirs(destination)
                    audiofile = '%s%s' % (destination+'/', orig_name)
                    file.save(audiofile)
                    if parent_id is None :
                        new_comment=Comment(int(1),user.id, post_id,'/comments/'+user.uuid+'/'+orig_name, 'audio',True)
                        new_comment.save()
                    else:
                        new_comment=Comment(int(1),user.id, post_id,'/comments/'+user.uuid+'/'+orig_name, 'audio',True,parent_id=parent_id)
                        new_comment.save()
                        
                    return{'res':new_comment.id},200
                if args['file'].mimetype == 'picture/jpeg':
                    return {'res':'This is a picture'}
            else:
                return {'res':'fail'},400
        if comment_type == "text":       
            if  content and post_id:
                if parent_id is None :
                    new_comment=Comment(int(1),user.id, post_id, content, comment_type,public=True)
                    new_comment.save()
                else:
                    new_comment=Comment(int(1),user.id, post_id,"This is insane", 'text',True,parent_id=parent_id)
                    new_comment.save()
                return{'res':'success'},200
            else:
                return {'res':'fail'},400
        
    @token_required
    @comment.expect(commentupdate)
    def put(self):
        req_data = request.get_json()
        if request.args.get('postid'):
            post_id=request.args.get('postid')
        elif request.args.get('postid') is None:
            post_id=Posts.query.get(req_data['post_id'])
        if post_id is None:
            return{'res':'fail'},400
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        comment=Comment.query.get(req_data['Comment_id'])
    
        if req_data['content'] is None:
            return{'res':'fail'}, 404
        if post_id and comment:
            if user.id  == comment.user_id:
                comment.content = req_data['content']
                db.session.commit()
            return {'res':'success'}, 200
        else:
            return {'res':'fail'},404

    @token_required
    @comment.expect(commentupdate)
    def patch(self):
        req_data = request.get_json()
        if request.args.get('postid'):
            post_id=request.args.get('postid')
        elif request.args.get('postid') is None:
            post_id=Posts.query.get(req_data['post_id'])
        if post_id is None:
            return{'res':'fail'},400
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        comment=Comment.query.get(req_data['Comment_id'])
        if req_data['content'] is None:
            return{'res':'fail'}, 404
        if post_id and comment:
            if user.id == comment.user_id: 
                comment.content = req_data['content']
                db.session.commit()
            return {'res':'success'}, 200
        else:
            return {'res':'fail'},404
        #return {}, 200
    @token_required
    @comment.expect(commentupdate)
    def delete(self):
        req_data = request.get_json()
        if request.args.get('postid'):
            post_id=request.args.get('postid')
        elif request.args.get('postid') is None:
            post_id=Posts.query.get(req_data['post_id'])
        if post_id is None:
            return{'res':'fail'},400
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        comment=Comment.query.get(req_data['Comment_id'])
        if post_id and comment:
            if user.id == comment.user_id:
                comment.public = False
                db.session.commit()
            return {'res':'success'}, 200
        else:
            return {'res':'fail'},404
        #return {}, 200
        #return {}, 200


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


@comment.doc(
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
@comment.route('/comment/userComment')
class UsersComment(Resource):
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
            comments1 = Comment.query.filter_by(user_id=user.id).first()
            if comments1:
                if user.id == comments1.user_id :
                    comments = Comment.query.filter_by(and_(user_id = comments1.user_id) , (Comment.public == True)).order_by(Comment.path).paginate(int(start), int(count), False).items
                    return {
                        "start": start,
                        "limit": limit,
                        "count": count,
                        "next": next,
                        "previous": previous,
                        "results": marshal(comments, commentdata)
                    }, 200
                else : 
                    return{
                        "status":0,
                        "res":"User does not have post"
                    }
            else:
                 return{
                        "status":0,
                        "res":"User does not have Comments"
                    }
        else:
            return{
                    "status":0,
                    "res":"No request found"
                }

    
