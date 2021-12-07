########################################################
# This file contains all search routes and sub routes  #
# You can can add more routes to this file  if need be #
########################################################
# Make sure you don't mess it up.

from flask_restplus import Namespace, Resource, fields, marshal
import jwt, uuid, os
from functools import wraps 
from flask import abort, request, session
from datetime import datetime
from app.models import Posts,Translated


# Preparing the Namespace of the search routes to add to main api file
search = Namespace('/api/search', \
    description='This namespace contains all the search capabilities of the API, it involve the search for post, users \
        and other entities.', \
    path='/v1/')

post_= search.model('post_', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'uuid': fields.String(required=True),
    'user_name': fields.String(required=True),
    'post_type': fields.Integer(required=True),
    'post_url': fields.String(required=True),
    'audio_url': fields.String(required=True),
    'video_url': fields.String(required=True),
    'created_on': fields.DateTime(required=True),
    'thumb_url': fields.String(required=False),
    'tags': fields.String(required=True),
    'price': fields.Float(required=True),
})

postdata = search.model('postreturndata', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'content': fields.String(required=True),
    'fullcontent':fields.String(required=True),
    'posts': fields.List(fields.Nested(post_)),
})


@search.doc(
    security='KEY',
    params={ 'keyword': 'search keyword'},
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
@search.route('/search')
class Searchlist(Resource):
    #@search.marshal_with(postdata)
    def get(self):
        keyword = request.args.get('keyword')
        # results = Posts.query.msearch(keyword,fields=['title'],limit=20).filter(...)
        # or
        # results = Posts.query.filter(...).msearch(keyword,fields=['title'],limit=20).filter(...)
        # elasticsearch
        # keyword = "title:book AND content:read"
        # more syntax please visit https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html
        #results = Posts.query.msearch(keyword,limit=20).all()
        results1 = Translated.query.msearch(keyword,limit=20).all()
        return  {
                        "results": marshal(results1,postdata)
                }, 200
    
