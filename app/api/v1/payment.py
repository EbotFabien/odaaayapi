from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals
from operator import pos

from flask_restplus import Namespace, Resource, fields, marshal,Api
import jwt, uuid, os
from flask_cors import CORS
from functools import wraps

from sqlalchemy.sql.base import NO_ARG
from app.services import mail
from flask import abort, request,redirect, session,Blueprint,jsonify
from flask import current_app as app
import numpy as np
from app.models import Save ,Subs, Users,Post_Access, Posts, Language,Translated,Report,Notification,Posttype,Account
from app import db, cache, logging, createapp
import json
from tqdm import tqdm
from werkzeug.datastructures import FileStorage
import requests
from bs4 import BeautifulSoup
import bleach
import json
from sqlalchemy import or_,and_,func

import stripe
from flask import current_app as app
from config import Config

#with app.app_context().push():
stripe.api_key = Config.stripe_secret_key


endpoint_secret = 'whsec_oN3IGfm2oUjOzAJ9bgAySwpfNx4yR8gZ'

authorizations = {
    'KEY': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'API-KEY'
    }
}

# The token decorator to protect my routes
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'API-KEY' in request.headers:
            token = request.headers['API-KEY']
            try:
                data = jwt.decode(token, app.config.get('SECRET_KEY'))
            except:
                return {'message': 'Token is invalid.'}, 403
        if not token:
            return {'message': 'Token is missing or not found.'}, 401
        if data:
            pass
        return f(*args, **kwargs)
    return decorated

api = Blueprint('api',__name__, template_folder='../templates')
payment1=Api( app=api, doc='/docs',version='1.4',title='News API.',\
description='', authorizations=authorizations)
#from app.api import schema  'channel': fields.List(fields.String(required=True)),
CORS(api, resources={r"/api/*": {"origins": "*"}})


payment = payment1.namespace('/api/payment', \
    description='This contains routes for core app data access. Authorization is required for each of the calls. \
        To get this authorization, please contact out I.T Team ', \
    path='/v1/')


paymenttype =payment.model('paymenttype',{
    'type':  fields.String(required=True),
    'price':fields.Integer(required=False),
    'lang' : fields.String(required=True)
})

portal =payment.model('portal',{
    'type':fields.Boolean(required=True),
    'lang':fields.String(required=True)

})

paymentbuy =payment.model('paymentbuy',{
    'type':  fields.String(required=True),
    'uuid': fields.String(required=True),
    'post_uuid':fields.String(required=False),
    'lang':fields.String(required=True)
})

@payment.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
            },
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
@payment.route('/register')

class Payment(Resource):
    @payment.expect(paymenttype)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        Type= req_data['type'] 
        lan=req_data['lang']
        if Type == "all":
            acc_=Account.query.filter_by(user=user.id).first()
            if acc_ is None:
                user.paid=True
                product = stripe.Product.create(
                    name=user.username.lower()+"subscription",
                )
                usd= req_data['price'] 
                user.product_id=product['id']
                price = stripe.Price.create(
                    product=product['id'],
                    unit_amount=usd*100,
                    currency='usd',
                    recurring={
                        'interval': 'month',
                    },
                )
                user.price=float(usd)
                user.price_id=price["id"]
                account_ = stripe.Account.create(
                type='express',
                )
                acc=Account(user=user.id,account_id=account_['id'])
                db.session.add(acc)
                account_links = stripe.AccountLink.create(
                account=account_['id'],
                refresh_url='https://odaaay.co/api/v1/refresh2/'+str(user.id)+'/'+lan,
                return_url='https://odaaay.co/'+lan+'/profile',#profilepage
                type='account_onboarding',
                )
                db.session.commit()
                return {
                    'status': 1,
                    'res': 'success',
                    'link': account_links['url'],
                }, 200
            if acc_ and user.paid == False:
                user.paid=True
                product = stripe.Product.create(
                    name=user.username.lower()+"subscription",
                )
                usd= req_data['price'] 
                user.product_id=product['id']
                price = stripe.Price.create(
                    product=product['id'],
                    unit_amount=usd*100,
                    currency='usd',
                    recurring={
                        'interval': 'month',
                    },
                )
                user.price=float(usd)
                user.price_id=price["id"]
                db.session.commit()
                return {
                    'status': 2,
                    'res': 'You have created a subscription account ',
                }, 200

            else:
                return {
                    'status': 0,
                    'res': 'you already have an account',
                }, 200
        
        if Type == "post":
            acc_=Account.query.filter_by(user=user.id).first()
            if acc_ is None:
                account_ = stripe.Account.create(
                    type='express',
                    )
                acc=Account(user=user.id,account_id=account_['id'])
                db.session.add(acc)
                account_links = stripe.AccountLink.create(
                account=account_['id'],
                refresh_url='https://odaaay.co/api/v1/refresh2/'+str(user.id)+'/'+lan,#refreshurl
                return_url='https://odaaay.co/'+lan+'/profile',#where?profile
                type='account_onboarding',
                )
                db.session.commit()
                
                return {
                    'status': 1,
                    'res': 'success',
                    'link': account_links['url'],
                }, 200
            else:
                return {
                    'status': 0,
                    'res': 'you already have an account',
                }, 200
        #option for when account is but not subs



@payment.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
            },
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
@payment.route('/buy')

class buy(Resource):
    @payment.expect(paymentbuy)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        Type= req_data['type']
        lan=req_data['lang']
        seller=Users.query.filter_by(uuid=req_data['uuid']).first()
        acc=Account.query.filter_by(user=seller.id).first()

        if Type == "subs":
            if seller.paid==True:
                session = stripe.checkout.Session.create(
                        customer=user.customer_id,
                        mode="subscription",
                        payment_method_types=['card'],
                        line_items=[{
                            'price': seller.price_id,
                            'quantity': 1,
                        }],
                        subscription_data={
                            'application_fee_percent': 10,
                            'transfer_data': {
                            'destination': acc.account_id,
                            },
                        },
                        success_url='https://odaaay.co/'+lan,#redirect to  seller page
                        cancel_url='https://odaaay.co/'+lan,#3 home
                    )
                    
                
                return {
                    'status': 1,
                    'res': 'success',
                    'link': session['url'],
                }, 200
        if Type == "post":
            post=Posts.query.filter_by(uuid=req_data['post_uuid']).first()
            session = stripe.checkout.Session.create(
                customer=user.customer_id,
                client_reference_id=post.product_id,
                mode="payment",
                payment_method_types=['card','alipay'],
                line_items=[{
                    'price':post.price_id,
                    'quantity': 1,
                }],
                payment_intent_data={
                    'application_fee_amount': 123,#fee
                    'transfer_data': {
                    'destination': acc.account_id,
                    },
                },
                success_url='https://odaaay.co/'+lan+'/article/'+req_data['post_uuid'],# open posts
                cancel_url='https://odaaay.co/'+lan,#home page
            )
        
            return {
                    'status': 1,
                    'res': 'success',
                    'link': session['url'],
                }, 200

        #payment for donation


@payment.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
            },
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
@payment.route('/portal')

class Portal(Resource):
    @payment.expect(portal)
    @token_required
    def post(self):
        req_data = request.get_json()
        token = request.headers['API-KEY']
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user = Users.query.filter_by(uuid=data['uuid']).first()
        Type= req_data['type']
        lan=req_data['lang']
        acc=Account.query.filter_by(user=user.id).first()

        if Type == True:
            if acc.valid == True:
                link=stripe.Account.create_login_link(
                    acc.account_id,
                    )
                link=link['url']
                return {
                    'status': 1,
                    'res': 'success',
                    'link': link,
                }, 200
            if acc.valid == False:
                return {
                    'status': 0,
                    'res': 'pass refresh link,user has not finish on boarding',
                }, 200

            #prime redirects the user to refresh if acc.valid==False


        if Type == False:
            session = stripe.billing_portal.Session.create(
            customer=user.customer_id,
            return_url='https://odaaay.co/'+lan+'/profile',#profile page
            )
            link=session.url
            return {
                'status': 1,
                'res': 'success',
                'link': link,
            }, 200

@payment.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
            },
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
@payment.route('/refresh/<id>/<lan>')

class refresh(Resource):
    def get(self,id,lan):
        user = Users.query.filter_by(uuid=id).first()
        account = Account.query.filter_by(user=user.id).first()
        account_links = stripe.AccountLink.create(
                account=account.account_id,    
                refresh_url='https://odaaay.co/api/v1/refresh2/'+str(user.id)+'/'+lan,
                return_url='https://odaaay.co/'+lan+'/profile',
                type='account_onboarding',
                )

        return {
                'status': 1,
                'res': 'success',
                'link': account_links['url'],
            }, 200

@payment.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
            },
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
@payment.route('/refresh2/<id>/<lan>')

class refresh1(Resource):
    def get(self,id,lan):
        user = Users.query.filter_by(uuid=id).first()
        account = Account.query.filter_by(user=user.id).first()
        account_links = stripe.AccountLink.create(
                account=account.account_id,    
                refresh_url='https://odaaay.co/api/v1/refresh2/'+str(user.id)+'/'+lan,
                return_url='https://odaaay.co/'+lan+'/profile',
                type='account_onboarding',
                )

        return redirect(account_links['url'])

@payment.doc(
    security='KEY',
    params={ 'start': 'Value to start from ',
            'limit': 'Total limit of the query',
            'count': 'Number results per page',
            'lang' : 'Language'
            },
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
@payment.route('/webhook')
class hook(Resource):
    def post(self):
        event = None
        payload = request.data
        a=json.loads(payload)
        requet=json.dumps(a)
        sig_header = request.headers['STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            #raise e
            return  {
                'status': 1,
                'res': 'success',
            }, 200

        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            #raise e
            return  {
                'status': 3,
                'res': 'success',
            }, 200

        # Handle the event
        if event['type'] == "invoice.paid":#follow
            subscription_schedule = event['data']['object']
            customer=subscription_schedule.customer
            subscription=subscription_schedule.lines['data'][0].subscription
            product_=subscription_schedule.lines['data'][0]['plan'].product
            client=Users.query.filter_by(customer_id=customer).first()
            product=Users.query.filter_by(product_id=product_).first()
            if client and product:
                client.follow(product)
                db.session.commit()
                sub=Subs(user_sub=client.id,product_user=product.id,sub_id=subscription)
                db.session.add(sub)
                db.session.commit()

        if event['type'] == "checkout.session.completed":#pay post
            subscription_schedule = event['data']['object']
            if subscription_schedule.mode=="payment":
                client=Users.query.filter_by(customer_id=subscription_schedule.customer).first()
                user=Posts.query.filter_by(product_id=subscription_schedule.client_reference_id).first()
                post_done=Post_Access(user=client.id,post=user.id)
                db.session.add(post_done)
                db.session.commit()




        # ... handle other event types
        if event['type'] == "customer.subscription.updated":#unfollow
            subscription_schedule = event['data']['object']
            product=Subs.query.filter(and_(Subs.sub_id==subscription_schedule.id,Subs.valid==True)).first()
            if product is not None:
                client=Users.query.filter_by(id=product.user_sub).first()
                product=Users.query.filter_by(id=product.product_user).first()
                client.unfollow(product)
                product.valid=False
                db.session.commit()
        
        if event['type'] == "account.updated":#account verified
            subscription_schedule = event['data']['object']
            account=Account.query.filter_by(account_id=subscription_schedule['id']).first()
            account.valid=True#cheeck
            db.session.commit()
        else:
            print('Unhandled event type {}'.format(event['type']))

        return jsonify(success=True)
