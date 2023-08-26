import os
from flask import Flask, Response, send_file, request, jsonify, url_for, session,make_response
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
from flask_oauthlib.client import OAuth
import ssl
import jwt, uuid
from datetime import timedelta,datetime,timezone
from config import Config
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_compress import Compress
#from flask_socketio import SocketIO

bycrypt = Bcrypt()
compress = Compress()
db = SQLAlchemy()

search = Search(db=db)
#socketio = SocketIO(cors_allowed_origins='*')

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
    with app.app_context():
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "http://127.0.0.1:5000")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
    app.config.from_object(config[configname])
    CORS(app, resources=r'/api/*')
    bycrypt.init_app(app)
    db.init_app(app)
    #socketio.init_app(app)
    compress.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    
    oauth = OAuth(app)
    
    #dashboard.bind(app)
    limiter.init_app(app)
    app.ts = translator(app)
    search.init_app(app)
    #matomo = Matomo(app, matomo_url="http://192.168.43.40/matomo",
    #            id_site=1, token_auth="1c3e081497f195c446f8c430236a507b")
    app.redis = Redis.from_url(app.config.get('REDIS_URL'))
    stripe.api_key = Config.stripe_secret_key
    app.task_queue = rq.Queue('newsapp-tasks', connection=app.redis)

    sentry_sdk.init(
        dsn="https://076148b85ca74c93b2c9ab0e07c2bd24@o1249285.ingest.sentry.io/6409744",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0

    )
   

    google = oauth.remote_app(
        'google',
        consumer_key=app.config['GOOGLE_ID'],
        consumer_secret=app.config['GOOGLE_SECRET'],
        request_token_params={
            'scope': ['email','profile']
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )
    

    from .api import api as api_blueprint
    from app import models
    from app.models import Users
    #from app.errors.handlers import errors

    
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(rq_dashboard.blueprint, url_prefix='/rq')
    #app.register_blueprint(errors)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app)
    

    @app.route('/')
    def index():
        return "Hello from Odaaay-app"
    @app.route('/google')
    def login():
        return google.authorize(callback=url_for('authorized', _external=True))
    
    @app.route('/google/last')
    def login_last():
        return google.authorize(callback=url_for('authorized_L', _external=True))

    @app.route('/google/authorized/last')
    def authorized_L():
        ssl._create_default_https_context = ssl._create_unverified_context
        resp = google.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        session['google_token'] = (resp['access_token'], '')
        me = google.get('userinfo')
        user=Users.query.filter_by(email=me.data['email']).first()
        link='https://odaaay.com/'+me.data['locale'][0:2]+'/login'
        
        if user:
            token = jwt.encode({
                'user': user.username,
                'uuid': user.uuid,
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256')
            session['google'] = token
            if user.customer_id == None:
                customer = stripe.Customer.create(
                    email=user.email,#see if phone number can be used
                    payment_method='pm_card_visa',
                    invoice_settings={
                        'default_payment_method': 'pm_card_visa',
                    },
                )
                user.customer_id=customer['id']
                user.verified_email = True
                user.user_visibility = True
                db.session.commit()
            #return jsonify({"data": me.data,"token":session['google_token']})
            data={
                'token':token,
                'uuid':user.uuid,
                'id':user.id,
                'name':user.username,
                'profile_picture':user.picture ,
                'email':user.email,
                'background':user.background,
                'handle':user.handle,
            }
            return {'results':data},200
            #return redirect(link+str('?token=')+str(token)+str('&uuid=')+str(user.uuid))
        else:
            user=Users(me.data['given_name'],str(uuid.uuid4()),True,email=me.data['email'])
            db.session.add(user)
            user.picture=me.data['picture']
            db.session.commit()
            if user.customer_id == None:
                customer = stripe.Customer.create(
                    email=user.email,#see if phone number can be used
                    payment_method='pm_card_visa',
                    invoice_settings={
                        'default_payment_method': 'pm_card_visa',
                    },
                )
                user.customer_id=customer['id']
                user.verified_email = True
                user.user_visibility = True
                db.session.commit()
            token = jwt.encode({
                'user': user.username,
                'uuid': user.uuid,
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256')
            session['google'] = token
            data={
                'token':token,
                'uuid':user.uuid,
                'id':user.id,
                'name':user.username,
                'profile_picture':user.picture ,
                'email':user.email,
                'background':user.background,
                'handle':user.handle,
            }
            return {'results':data},200
            #return redirect(link+str('?token=')+str(token)+str('&uuid=')+str(user.uuid))
        
    @app.route('/google/authorized')
    def authorized():
        ssl._create_default_https_context = ssl._create_unverified_context
        resp = google.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        session['google_token'] = (resp['access_token'], '')
        me = google.get('userinfo')
        user=Users.query.filter_by(email=me.data['email']).first()
        link='https://odaaay.com/'+me.data['locale'][0:2]+'/login'
        
        if user:
            token = jwt.encode({
                'user': user.username,
                'uuid': user.uuid,
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256')
            session['google'] = token
            if user.customer_id == None:
                customer = stripe.Customer.create(
                    email=user.email,#see if phone number can be used
                    payment_method='pm_card_visa',
                    invoice_settings={
                        'default_payment_method': 'pm_card_visa',
                    },
                )
                user.customer_id=customer['id']
                user.verified_email = True
                user.user_visibility = True
                db.session.commit()
            #return jsonify({"data": me.data,"token":session['google_token']})
            #return redirect(link+str('?token=')+str(token)+str('&uuid=')+str(user.uuid))
            data={
                'uuid':user.uuid,
                'id':user.id,
                'name':user.username,
                'profile_picture':user.picture ,
                'email':user.email,
                'background':user.background,
                'handle':user.handle,
            }
            return {'status': 1,
                        'res': 'success',
                        'uuid': user.uuid,
                        'token': str(token),
                        'data':data
                    },200
        
        else:
            user=Users(me.data['given_name'],str(uuid.uuid4()),True,email=me.data['email'])
            db.session.add(user)
            user.picture=me.data['picture']
            db.session.commit()
            if user.customer_id == None:
                customer = stripe.Customer.create(
                    email=user.email,#see if phone number can be used
                    payment_method='pm_card_visa',
                    invoice_settings={
                        'default_payment_method': 'pm_card_visa',
                    },
                )
                user.customer_id=customer['id']
                user.verified_email = True
                user.user_visibility = True
                db.session.commit()
            token = jwt.encode({
                'user': user.username,
                'uuid': user.uuid,
                'exp': datetime.utcnow() + timedelta(days=30),
                'iat': datetime.utcnow()
            },
            app.config.get('SECRET_KEY'),
            algorithm='HS256')
            session['google'] = token
            
            data={
                'uuid':user.uuid,
                'id':user.id,
                'name':user.username,
                'profile_picture':user.picture ,
                'email':user.email,
                'background':user.background,
                'handle':user.handle,
            }
            return {'status': 1,
                        'res': 'success',
                        'uuid': user.uuid,
                        'token': str(token),
                        'data':data
                    },200
            #return redirect(link+str('?token=')+str(token)+str('&uuid=')+str(user.uuid))

    @google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')
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


