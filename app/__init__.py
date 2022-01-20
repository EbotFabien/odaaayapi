import os
from flask import Flask, Response, send_file, request, jsonify
from werkzeug.utils import redirect
from config import config
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_script import Manager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_caching import Cache
import flask_monitoringdashboard as dashboard
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_matomo import *
from werkzeug.http import HTTP_STATUS_CODES
import werkzeug
from redis import Redis
import rq, json, stripe
import requests as rqs
import rq_dashboard
from flask_googletrans import translator
from flask_msearch import Search


bycrypt = Bcrypt()
db = SQLAlchemy()
search = Search(db=db)
mail = Mail()
basedir= os.path.abspath(os.path.dirname(__file__))
cache = Cache(config={'CACHE_TYPE': 'simple'})
#dashboard.config.init_from(file=os.path.join(basedir, '../config.cfg'))
limiter = Limiter(key_func=get_remote_address)

SERVER_NAME = 'Google Web Server v0.1.0'

class localFlask(Flask):
    def process_response(self, response):
        #Every response will be processed here first
        response.headers['server'] = SERVER_NAME
        super(localFlask, self).process_response(response)
        return(response)

def createapp(configname):
    app = localFlask(__name__)
    app.config.from_object(config[configname])
    CORS(app, resources=r'/api/*')
    bycrypt.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    #dashboard.bind(app)
    limiter.init_app(app)
    app.ts = translator(app)
    search.init_app(app)
    #matomo = Matomo(app, matomo_url="http://192.168.43.40/matomo",
    #            id_site=1, token_auth="1c3e081497f195c446f8c430236a507b")
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    stripe.api_key = app.config['STRIPE_KEY_SEC']
    app.task_queue = rq.Queue('newsapp-tasks', connection=app.redis)
    

    from .api import api as api_blueprint
    from app import models
    from app.google import authenticate

    
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(rq_dashboard.blueprint, url_prefix='/rq')
    app.register_blueprint(authenticate,url_prefix='/google')
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/')
    def index():
        return "Hello from Odaaay-app"

    @app.route('/file/<name>')
    def filename(name):
        return send_file('./static/files/'+str(name), attachment_filename=str(name))

    @app.route('/create-checkout-session', methods=['POST'])
    def create_checkout_session():
        data = json.loads(request.data)
        try:
            # See https://stripe.com/docs/api/checkout/sessions/create
            # for additional parameters to pass.
            # {CHECKOUT_SESSION_ID} is a string literal; do not change it!
            # the actual Session ID is returned in the query parameter when your customer
            # is redirected to the success page.
            checkout_session = stripe.checkout.Session.create(
                success_url="https://example.com/success.html?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://example.com/canceled.html",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[
                    {
                        "price": data['priceId'],
                        # For metered billing, do not pass quantity
                        "quantity": 1
                    }
                ],
            )
            return jsonify({'sessionId': checkout_session['id']})
        except Exception as e:
            return jsonify({'error': {'message': str(e)}}), 400

    @app.route('/create-stripe-account-login', methods=['POST','GET'])
    def createLogin():
        login = stripe.Account.create_login_link(
            "acct_1HtsAu2SfJ6AP0v7",
        )
        return { 
            'login': login,
        }
    @app.route('/create-stripe-account', methods=['POST','GET'])
    def create_account():
        account = stripe.Account.create(
            type='express',
            country= 'US',
            email= 'chupimpim@odaaay.com'
        )
        account_links = stripe.AccountLink.create(
            account= account.id,
            refresh_url= 'https://example.com/reauth',
            return_url= 'https://example.com/return',
            type='account_onboarding',
        )
        return { 
            'onboarding': account_links,
        }

    @app.route('/debug-sentry')
    def trigger_error():
        division_by_zero = 1 / 0

    @app.errorhandler(werkzeug.exceptions.BadRequest)
    def handle_bad_request(e):
        return 'bad request!', 400

    @app.errorhandler(werkzeug.exceptions.NotFound)
    def handle_bad_request(e):
        return 'Not Found!', 404
        
    @app.errorhandler(werkzeug.exceptions.InternalServerError)
    def handle_bad_request(e):
        return 'Internal server error', 500

    return app


