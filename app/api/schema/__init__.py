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
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

signupdata = apisec.model('Signup', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

trendingdata = apisec.model('trending',{

})

feeddata = apisec.model('feed',{
    
})

discoverdata = apisec.model('discover',{
    
})

homedata = apisec.model('Home', {
    'trending': fields.List(fields.Nested(trendingdata)),
    'feed': fields.List(fields.Nested(feeddata)),
    'discover': fields.List(fields.Nested(discoverdata))
})
