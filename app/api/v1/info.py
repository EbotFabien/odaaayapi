from flask_restplus import Namespace, Resource, fields
import jwt, uuid, os
from functools import wraps
from flask import abort, request, session
from datetime import datetime


info = Namespace('/api/', \
    description='This namespace contains all the information about our API.', \
    path='/v1/')


apiinfo = info.model('Info', {
    'name': fields.String,
    'version': fields.Integer,
    'date': fields.String,
    'author': fields.String,
    'description': fields.String
})

@info.deprecated
@info.route('/')
class Info(Resource):
    @info.marshal_with(apiinfo)
    def get(self):
        app = {
            'name':'News',
            'version': 1.0,
            'date': datetime.utcnow(),
            'author': 'Leslie Etubo T, E. Fabien, Samuel Klein, Marc.',
            'description': 'This is an API to serve information to clients'
        }, 200
        return app
