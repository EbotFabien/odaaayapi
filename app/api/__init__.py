from flask import Blueprint
from app.services import Mailer
from flask_restplus import Api, Resource, fields, reqparse
from flask import Blueprint, render_template, abort, request, session
from flask_cors import CORS
from functools import wraps
from flask import current_app as app
from datetime import datetime
from datetime import  timedelta
from app.models import User
from app import db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
import jwt, uuid, os
from .v1 import user, info, token, search, post


# API security
authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'API-KEY'
    }
}

api = Blueprint('api', __name__, template_folder = '../templates')
apisec = Api( app=api, doc='/docs', version='1.0', title='News API.', \
description='', authorizations=authorizations)
CORS(api, resources={r"/api/*": {"origins": "*"}})

uploader = apisec.parser()
uploader.add_argument('file', location='files', type=FileStorage, required=True, help="You must parse a file")
uploader.add_argument('name', location='form', type=str, required=True, help="Name cannot be blank")

apisec.add_namespace(info)
apisec.add_namespace(user)
apisec.add_namespace(token)
apisec.add_namespace(post)
apisec.add_namespace(search)

login = apisec.namespace('/api/login', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
        To get this authorization, please contact out I.T Team ', \
    path='/v1/')

post = apisec.namespace('/api/post', \
    description= "All routes under this section of the documentation are the open routes bots can perform CRUD action \
    on the application.", \
    path = '/private/')
