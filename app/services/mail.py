from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(recipients, text_body,
               attachments=None, sync=False):
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

def Report(sender_u,text_body):
    msg = Message(subject="Report", sender=sender_u, recipients=current_app.config['ADMINS'][0])
    msg.body = text_body
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