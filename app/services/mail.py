from threading import Thread
from flask import current_app,url_for
from flask_mail import Message
from app import mail



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
        print(True)

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
            print(True)
        else:
            Thread(target=send_async_email,
                args=(current_app._get_current_object(), msg)).start()


def Report(sender_u,text_body):
    Thread(target=_user_,
            args=(current_app._get_current_object(), sender_u,text_body)).start()


def invitation_email(token,email,sender,r):
    msg = Message('You have been invited to oodaay',
                  sender=sender,
                  recipients=[email])
    
    msg.body = f''' To join odaay,visit the following link:
                {r}
     
                if you did not make this request then simply ignore this email and no changes will be made
                '''
    mail.send(msg)

def verify_email(email,r):
    msg = Message('Verify your  odaaay account',
                  sender='noreply@demo.com',
                  recipients=[email])
    
    msg.body = f''' To Verify your odaaay account,visit the following link:
                {r}
     
                if you did not make this request then simply ignore this email and no changes will be made
                '''
    mail.send(msg)

    
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