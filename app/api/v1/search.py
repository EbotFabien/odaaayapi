########################################################
# This file contains all search routes and sub routes  #
# You can can add more routes to this file  if need be #
########################################################
# Make sure you don't mess it up.

from flask_restplus import Namespace, Resource, fields
import jwt, uuid, os
from functools import wraps 
from flask import abort, request, session
from datetime import datetime


# Preparing the Namespace of the search routes to add to main api file
search = Namespace('/api/search', \
    description='This namespace contains all the search capabilities of the API, it involve the search for post, users \
        and other entities.', \
    path='/v1/')


@search.route('/search')
class Searchlist(Resource):
    def get(self):
        return {}, 200
