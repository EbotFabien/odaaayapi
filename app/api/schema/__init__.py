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
