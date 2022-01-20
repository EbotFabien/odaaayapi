from flask import  request,Blueprint, url_for, session, request, jsonify
from flask import current_app as app
from app import db,api
from flask import jsonify
from config import Config
from flask_oauthlib.client import OAuth
import ssl
from app.google import authenticate
from app.models import Users

oauth = OAuth(app)

google = oauth.remote_app(
        'google',
        consumer_key=Config.GOOGLE_ID,
        consumer_secret=Config.GOOGLE_SECRET,
        request_token_params={
            'scope': ['email','profile']
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )

@authenticate.route('/google')
    def login():
        return google.authorize(callback=url_for('authenticate.authorized', _external=True))
    
@authenticate.route('/google/authorized')
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
        link='https://odaaay.co/'+me.data['locale']
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
            #return jsonify({"data": me.data,"token":session['google_token']})
            return redirect(link)
        else:
            user=Users(me.data['given_name'],str(uuid.uuid4()),True,email=me.data['email'])
            db.session.add(user)
            user.picture=me.data['picture']
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
            return redirect(link)

@google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')
