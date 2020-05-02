from flask_mail import Message
from app import mail
from flask import current_app as app
from itsdangerous import URLSafeTimedSerializer
from twilio.rest import Client
import random


class Mailer:
    def send_email(to, subject, template):
        msg = Message(
            subject,
            recipients=[to],
            html=template,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)

    def generate_confirmation_token(email):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


    def confirm_token(token, expiration=3600):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=app.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )
        except:
            return False
        return email

class Phoner:
    
    def generate_code(self):
        return str(random.randrange(100000, 999999))

    def send_sms(self, to_number, body):
        message = '''Your News app verification code is :\n '''+body
        account_sid = app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = app.config.get('TWILIO_AUTH_TOKEN')
        twilio_number = app.config.get('TWILIO_NUMBER')
        client = Client(account_sid, auth_token)
        client.api.messages.create(to_number,
                            from_=twilio_number,
                            body=message)

    def send_confirmation_code(self, to_number):
        verification_code = self.generate_code()
        self.send_sms(to_number, verification_code)
        return verification_code