from .. import apisec
from flask_restplus import fields

appinfo = apisec.model('Info', {
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
verifydata = apisec.model('Verify', {
    'username': fields.String(required=True),
    'code': fields.String(required=True)
})
creationdata = apisec.model('Create', {
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'bio': fields.String(required=True)
})