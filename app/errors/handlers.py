from flask import  request,Blueprint
from flask import current_app as app
from app import db,api
from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
#from app.errors import errors
#from app.api.errors import error_response as api_error_response




def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']

@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return 'bad request!', 400

@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return 'bad request!', 404
    


@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_bad_request(e):
    return 'Internal server error', 500
