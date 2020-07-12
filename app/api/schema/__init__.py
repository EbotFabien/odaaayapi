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
    'phonenumber': fields.String(required=True, description="Users phone number"),
})

signupdata = apisec.model('Signup', {
    'username': fields.String(required=True, description="The username for the application"),
    'phonenumber': fields.String(required=True, description="Users phone number")
})
signupdataemail= apisec.model('signup',{
    'username': fields.String(required=True, description="The username for the application"),
    'password': fields.String(required=True, description="Users password"),
    'Email': fields.String(required=True, description="Users Email")
})
verifyemail= apisec.model('verify',{
    'verification_code': fields.String(required=True, description="The username for the application"),
    'Email': fields.String(required=True, description="Users Email")
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

send_verification = apisec.model('send_verification', {
    'code': fields.String(required=True, description="code sent to user from server"),
    'type': fields.String(required=True, description="phone, email or both")
})
