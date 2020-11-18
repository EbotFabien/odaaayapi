from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def user(app,text_body,receiver_u):
        with app.app_context():
            msg = Message(subject="Report", sender=current_app.config['ADMINS'][0], recipients=receiver_u)
            msg.body =text_body
            mail.send(msg)

def user_(app,sender_u,text_body,receiver_u):
        with app.app_context():
            msg = Message(subject="Report", sender=sender_u, recipients=receiver_u)
            msg.body =text_body
            mail.send(msg)

def _user_(app,sender_u,text_body):
        with app.app_context():
            msg = Message(subject="Report", sender=sender_u, recipients=current_app.config['ADMINS'][0])
            msg.body =text_body
            mail.send(msg)             

def send_email(app, recipients, text_body,
               attachments=None, sync=False):
    with app.app_context():
        msg = Message(subject="verification", sender="noreply@demo.com", recipients=recipients)
        msg.body = text_body
        #msg.html = html_body
        if attachments:
            for attachment in attachments:
                msg.attach(*attachment)
        if sync:
            mail.send(msg)
        else:
            Thread(target=send_async_email,
                args=(current_app._get_current_object(), msg)).start()

<<<<<<< HEAD
def Report(app, sender_u,text_body):
    with app.app_context():
        msg = Message(subject="Report", sender=sender_u, recipients=app.config['ADMINS'][0])
        msg.body = text_body
        mail.send(msg)  

def Invitation(app, receiver_u,text_body,sender_u):
    with app.app_context():
        msg = Message(subject="Report", sender=app.config['ADMINS'][0], recipients=receiver_u)
        msg.body =text_body
        mail.send(msg) 
=======
def invitation(receiver_u,text_body):

    Thread(target=user,
            args=(current_app._get_current_object(),text_body,receiver_u)).start()

def Invitation(receiver_u,text_body,sender_u):

    Thread(target=user_,
            args=(current_app._get_current_object(), sender_u,text_body,receiver_u)).start()

def Report(sender_u,text_body):
    Thread(target=_user_,
            args=(current_app._get_current_object(), sender_u,text_body)).start()


     
>>>>>>> 1a71d2130e2be40ff14c5172f19ba2482f7947ed
    
'''
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
'''