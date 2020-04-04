from app.api import apisec
from flask_restplus import Namespace, Resource, fields

apiinfo = apisec.model('Info', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

logindata = apisec.model('Login', {
    'username': fields.String(required=True, description="Username you registered in the application"),
    'password': fields.String(required=True, description="Password for the user above")
})

signupdata = apisec.model('Signup', {
    'username': fields.String(required=True, description="The username for the application"),
    'email': fields.String(required=True, description="Users email for the application"),
    'password': fields.String(required=True, description="Password of the user")
})

postdata = apisec.model('postreturndata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'channel_id': fields.Integer(required=True),
    'uploader': fields.String(required=True),
    'content': fields.String(required=True),
    'uploader_date': fields.DateTime(required=True)
})

trendingdata = apisec.inherit('trending', postdata, {})

feeddata = apisec.model('feed', postdata, {})

discoverdata = apisec.model('discover', postdata, {})

homedata = apisec.model('Home', {
    'trending': fields.List(fields.Nested(trendingdata)),
    'feed': fields.List(fields.Nested(feeddata)),
    'discover': fields.List(fields.Nested(discoverdata))
})
