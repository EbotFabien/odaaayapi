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
    'username': fields.String(required=False, description="The username for the application"),
    'phonenumber': fields.String(required=True, description="Users phone number")
})
signupdataemail= apisec.model('signup',{
    'email': fields.String(required=True, description="Users Email")
})
verifyemail= apisec.model('verify',{
    'verification_code': fields.String(required=True, description="The username for the application"),
    'Email': fields.String(required=True, description="Users Email")
})
channeldata = apisec.model('channel',{
    'id': fields.Integer(required=True),
    'name': fields.String(required=True, description="name of channel"),
    'description': fields.String(required=True, description="description of channel"),
    'profile_pic': fields.String(required=True, description="profile pic"),
    'background': fields.String(required=True, description="background image"),
    'css': fields.String(required=True, description="css to style channel page"),
    'desc_en': fields.String(required=True, description="description in english"),
    'desc_es': fields.String(required=True, description="description in spanish"),
    'desc_ar': fields.String(required=True, description="description in arabic"),
    'desc_pt': fields.String(required=True, description="description in portuguese"),
    'desc_fr': fields.String(required=True, description="description in french"),
    'desc_sw': fields.String(required=True, description="description in swahili"),
    'desc_ha': fields.String(required=True, description="description in hausa"),
    'moderator': fields.String(required=True, description="Moderator id")
})

postdata = apisec.model('postreturndata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'uuid': fields.String(required=True),
    'uploader': fields.String(required=True),
    'content': fields.String(required=True),
    'uploader_date': fields.DateTime(required=True),
    'thumb_url': fields.String(required=False)
})

lang_post = apisec.model('trans_post', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True),
    'language_id': fields.Integer(required=True),
    'posts': fields.List(fields.Nested(postdata))
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
