# This file contains the models of the code. The database in use doesn't matter
# just insert the new model and properly link the model as on the ERD then you will be good to go.
# After linking, * Run flask Migrate to use Alembic module to migrate the data without destroying your
# Data in the Database. This file should not be messed with if you donno know what you are doing.

from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import redis
import rq
from flask import current_app as app
from time import time
import json

channel_langs = db.Table('channel_langs',
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id'), primary_key=True),
    db.Column('language_id', db.Integer, db.ForeignKey('language.id'), primary_key=True)
)
subs = db.Table('subs',
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id'), primary_key=True),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)
followers = db.Table('followers',
    db.Column('follower_id',db.Integer,db.ForeignKey('users.id')),
    db.Column('followed_id',db.Integer,db.ForeignKey('users.id')),
)
blocking = db.Table('Blocked',
    db.Column('blocker_id',db.Integer,db.ForeignKey('users.id')),
    db.Column('blocked_id',db.Integer,db.ForeignKey('users.id')),
)
sub_moderator = db.Table('sub_moderator',
    db.Column('channel_id',db.Integer,db.ForeignKey('channels.id')),
    db.Column('sub_moderator_id',db.Integer,db.ForeignKey('users.id')),
    
)
# The user table will store user all user data, passwords will not be stored
# This is for confidentiality purposes. Take note when adding a model for
# vulnerability.
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable=False)
    uuid = db.Column(db.String, nullable=False)
    user_number = db.Column(db.String, nullable=True)
    user_visibility = db.Column(db.Boolean, nullable=False, default=True)
    user_saves = db.relationship('Save', backref="save", lazy=True )
    user_ratings = db.relationship('Rating', backref = "userrating", lazy = True)
    user_setting = db.relationship('Setting', backref = "usersetting", lazy = True)
    code = db.Column(db.Integer)
    posts = db.relationship('Posts', backref='author', lazy='dynamic')
    code_expires_in = db.Column(db.DateTime)
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')
    #subs = db.relationship('Channels', secondary=subs, lazy='subquery',
    #    backref=db.backref('subscribers', lazy=True))
    
    followed = db.relationship(
        'Users', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    #subs = db.relationship(
    #    'Users', secondary=subs,
    #    primaryjoin=(subs.c.channel_id == Channels.id),
    #    secondaryjoin=(subs.c.users_id == id),
    #    backref=db.backref('subscribers', lazy='dynamic'), lazy='dynamic')    
    blocked = db.relationship(
        'Users', secondary=blocking,
        primaryjoin=(blocking.c.blocker_id == id),
        secondaryjoin=(blocking.c.blocked_id == id),
        backref=db.backref('blocking',lazy='dynamic'),lazy='dynamic')
        
    def __init__(self, username, number, user_visibility):
        self.username = username
        self.uuid = str(uuid.uuid4())
        self.user_number = number
        self.user_visibility = user_visibility

    def __repr__(self):
        return '<User %r>' % self.username

    def is_blocking(self,user):
        return self.blocked.filter(
            blocking.c.blocked_id == user.id).count() > 0

    def block(self,user):
        if not self.is_blocking(user):
            self.blocked.append(user)

    def unblock(self,user):
        if self.is_blocking(user):
            self.blocked.append(user)

    def has_blocked(self):
        return Users.query.join(
            blocking,(blocking.c.blocked_id == Users.id)).filter(
                blocking.c.blocker_id == self.id)
                  
    def is_following(self,user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        followed = Posts.query.join(
            followers,(followers.c.followed_id == Posts.uploader_id)).filter(
                followers.c.follower_id == self.id)        
        own= Posts.query.filter_by(uploader_id=self.id)
        return followed.union(own).order_by(Posts.uploader_date.desc())

    def has_followed(self):
        return Users.query.join(
            followers,(followers.c.followed_id == Users.id)).filter(
                followers.c.follower_id == self.id)

    def followers(self):
        return Users.query.join(
            followers,(followers.c.follower_id == Users.id)).filter(
                followers.c.followed_id == self.id)

        
    def is_moderator(self):
        return Users.query.join(
            Channels,(Channels.moderator == Users.id)).filter(
                Channels.moderator == self.id).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def verify_phone(self, phone):
        return check_password_hash(self.user_number, phone)

    def add_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = app.task_queue.enqueue('app.services.task.' + name, self.id, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description, user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()


class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    complete = db.Column(db.Boolean, default=False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def get_data(self):
        return json.loads(str(self.payload_json))

class Channels(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    profile_pic = db.Column(db.String)
    background = db.Column(db.String)
    css = db.Column(db.String)
    desc_en = db.Column(db.String)
    desc_es = db.Column(db.String)
    desc_ar = db.Column(db.String)
    desc_pt = db.Column(db.String)
    desc_fr = db.Column(db.String)
    desc_sw = db.Column(db.String)
    desc_ha = db.Column(db.String)
    moderator = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    sub_moderator = db.relationship('Users', secondary=sub_moderator,
        primaryjoin=(sub_moderator.c.channel_id == id),
        secondaryjoin=(sub_moderator.c.sub_moderator_id == Users.id),
        backref=db.backref('sub_mod', lazy='dynamic'),lazy='dynamic')
    subs = db.relationship(
        'Users', secondary=subs,
        primaryjoin=(subs.c.channel_id == id),
        secondaryjoin=(subs.c.users_id == Users.id),
        backref=db.backref('subscribers', lazy='dynamic'), lazy='dynamic') 
    def subscribed(self,user):
        return  self.query.join(
            subs,(subs.c.channel_id == self.id )).filter(
                subs.c.users_id == user.id).first()
    def add_sub(self,user):
        if not self.subscribed(user):
            self.subs.append(user)
            
    def remove_sub(self,user):
        if  self.subscribed(user):
            self.subs.remove(user)

    def is_sub_mod(self,user):
        return self.sub_moderator.filter(
            sub_moderator.c.sub_moderator_id == user.id).count() > 0
    def add_sub_mod(self,user):
        if not self.is_sub_mod(user):
            self.sub_moderator.append(user)
    def remove_sub_mod(self,user):
        if not self.is_sub_mod(user):
            self.sub_moderator.remove(user)
   # def modify_sub(self,user):
    #    return self.sub_moderator.filter(
    #        sub_moderator.c.sub_moderator_id == user.id).first()# == new_id

    def __init__(self, name, description, profile_pic, background, user, css):
        self.name = name
        self.profile_pic = profile_pic
        self.background = background
        self.description = description
        self.moderator = user
        self.css = css

    def __repr__(self):
        return'<Channels>%r' %self.name 

class Save(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __init__(self, user, content):
        self.user = user
        self.content = content

    def __repr__(self):
        return '<Save %r>' % self.id

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False) 
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(50), nullable=False)

    def __init__(self, language, users, theme):
        self.language = language
        self.theme = theme
        self.users = users
    def __repr__(self):
        return '<Setting %r>' % self.id

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ratingtype = db.Column(db.Integer, db.ForeignKey('ratingtype.id'), nullable = False)
    rater = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable= False)

    def __init__(self, ratingtype, rater,post):
        self.post = post
        self.rater = rater
        self.ratingtype = ratingtype

    def __repr__(self):
        return '<Rating>%r' %self.id


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    uploader = db.Column(db.String)
    uploader_date = db.Column(db.DateTime, nullable=False)
    post_type = db.Column(db.Integer, db.ForeignKey('posttype.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ratings_id = db.relationship('Rating', backref='rating', lazy = True)
    comments_id = db.relationship('Comment', backref='postcomment', lazy = True)
    esposts = db.relationship('Postes', backref='spanish_posts', lazy='dynamic')
    enposts = db.relationship('Posten', backref='english_posts', lazy='dynamic')
    ptposts = db.relationship('Postpor', backref='portuguese_posts', lazy='dynamic')
    swposts = db.relationship('Postsw', backref='swahili_posts', lazy='dynamic')
    haposts = db.relationship('Posthau', backref='hausa_posts', lazy='dynamic')
    arposts = db.relationship('Postarb', backref='arabic_posts', lazy='dynamic')
    frposts = db.relationship('Postfr', backref='french_posts', lazy='dynamic')
    picture_url =db.Column(db.String)
    video_url =db.Column(db.String)

    def __init__(self, uploader, title, channel, posttype, content, uploader_id,picture_url=None,video_url=None):
        self.content = content
        self.title = title
        self.uploader_id = uploader
        self.channel_id = channel
        self.post_type = posttype
        self.uploader = Users.query.filter_by(id=uploader_id).first().username
        self.uploader_date = datetime.utcnow()
        self.picture_url = picture_url
        self.video_url = video_url
    
    def launch_translation_task(self, name, userid, descr):
        rq_job = app.task_queue.enqueue('app.services.task.' + name, self.id, userid)
        task = Task(id=rq_job.get_id(), name=name, user_id=userid, description=descr)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def __repr__(self):
        return '<Post>%r' %self.title

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    comment_type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    #language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable= False)
    public =db.Column(db.Boolean, nullable= False, default=True)

    def __init__(self, language, user, post, content, comment_type,public):
        self.content = content
        self.user_id = user
        self.post_id = post
        #self.language_id = language
        self.comment_type = comment_type
        self.public = public

    def __repr__(self):
        return '<Comment>%r' %self.content


class Subcomment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    subcomment_type = db.Column(db.String, nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    public =db.Column(db.Boolean, nullable= False, default=True)

    def __init__(self, content, user, comment,comtype,public=True):
        self.content = content
        self.user = user
        self.comment = comment
        self.subcomment_type = comtype
        self.public = public
        
    def __repr__(self):
        return '<Subcomment>%r' %self.content

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    settings = db.relationship('Setting', backref='setting', lazy=True)
    lang_type = db.Column(db.String(30), nullable=False)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(40), nullable=False)

    def __init__(self, name, code, comments):
        self.comments = comments
        self.code = code
        self.name = name
    def __repr__(self):
        return '<Language>%r' %self.name

class Posttype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Posttype>%r' %self.id

class Ratingtype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Ratingtype>%r' %self.id

class Postarb(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

class Posten(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

class Postpor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

class Postfr(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
    
    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

class Posthau(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang 

class Postsw(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang 

class Postes(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

