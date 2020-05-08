from flask_mail import Message
from app import mail
import jwt, uuid, os
from flask import current_app as app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from twilio.rest import Client
import random
from rq import get_current_job
from app import db
from app.models import Task,Users
from threading import Thread


class Mailer:
    
    def send_email(self, subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
        token = user.get_reset_token()
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body + f'''{url_for('users.reset_token',token=token,_external=True)}'''
        msg.html = html_body
        if attachments:
            for attachment in attachments:
                msg.attach(*attachment)
        if sync:
            mail.send(msg)
        else:
            Thread(target=send_async_email,
                args=(app._get_current_object(), msg)).start()

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(app.config['SECRET_KEY'],expiration)
        data = jwt.decode(token, app.config.get('SECRET_KEY'))
        user= Users.query.filter_by(uuid=data['uuid']).first()
        return s.dumps({'user_id':user.id}).decode('utf-8')

    def confirm_token(self, token):
        serializer = Serializer(app.config['SECRET_KEY'])
        try:
           user_id = s.loads(token) ['user_id']
        except:
            return False
        return Users.query.get(user_id)

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

class Tasker:

    def _set_task_progress(self, progress):
        job = get_current_job()
        if job:
            job.meta['progress'] = progress
            job.save_meta()
            task = Task.query.get(job.get_id())
            task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                        'progress': progress})
            if progress >= 100:
                task.complete = True
            db.session.commit()