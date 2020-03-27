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

homedata = apisec.model('Home', {
    'user': fields.String(required=True),
    'uuid': fields.String(required=True),
    'exp': fields.String(required=True),
    'iat': fields.String(required=True)
})