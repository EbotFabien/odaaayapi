from twilio.rest import Client
from flask import current_app as app
import random
from config import Config

account_sid = Config.TWILIO_ACCOUNT_SID
auth_token = Config.TWILIO_AUTH_TOKEN
services = Config.TWILIO_SERVICE
client = Client(account_sid, auth_token)

def generate_code():
    return str(random.randrange(100000, 999999))

def send_sms(to_number, body):
    message = '''Your News app verification code is :\n '''+body
    account_sid = app.config.get('TWILIO_ACCOUNT_SID')
    auth_token = app.config.get('TWILIO_AUTH_TOKEN')
    twilio_number = app.config.get('TWILIO_NUMBER')
    client = Client(account_sid, auth_token)
    client.api.messages.create(to_number,
                        from_=twilio_number,
                        body=message)

def sendverification(unumber):
    verification = client.verify \
                    .services(services) \
                    .verifications \
                    .create(to= str(unumber), channel='sms')
    return verification

def checkverification(unumber, ucode):
    verification_check = client.verify \
                        .services(services) \
                        .verification_checks \
                        .create(to= str(unumber), code=str(ucode))
    return verification_check
    
def send_confirmation_code(to_number,verification_code):
    send_sms(to_number, verification_code)
    return verification_code

