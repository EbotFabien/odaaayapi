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
import json, shortuuid, bleach
from markdown import markdown
from werkzeug.utils import secure_filename

channel_langs = db.Table('channel_langs',
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id'), primary_key=True),
    db.Column('language_id', db.Integer, db.ForeignKey('language.id'), primary_key=True)
)
postchannel = db.Table('postchannel',
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
)
subs = db.Table('subs',
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id'), primary_key=True),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('notif', db.Boolean, default=True),

)
followers = db.Table('followers',
    db.Column('follower_id',db.Integer,db.ForeignKey('users.id')),
    db.Column('followed_id',db.Integer,db.ForeignKey('users.id')),
)
blocking = db.Table('Blocked',
    db.Column('blocker_id',db.Integer,db.ForeignKey('users.id')),
    db.Column('blocked_id',db.Integer,db.ForeignKey('users.id')),
)
clap = db.Table('clap',
    db.Column('clap_id',db.Integer,autoincrement=True, primary_key = True),
    db.Column('user_id',db.Integer,db.ForeignKey('users.id'),primary_key=True),
    db.Column('post_id',db.Integer,db.ForeignKey('posts.id'), primary_key=True)
)
shout = db.Table('shout',
    db.Column('shout_id',db.Integer,autoincrement=True, primary_key = True),
    db.Column('user_id',db.Integer,db.ForeignKey('users.id'),primary_key=True),
    db.Column('comment_id',db.Integer,db.ForeignKey('comment.id'), primary_key=True)
)
sub_moderator = db.Table('sub_moderator',
    db.Column('channel_id',db.Integer,db.ForeignKey('channels.id')),
    db.Column('sub_moderator_id',db.Integer,db.ForeignKey('users.id'))
)
# The user table will store user all user data, passwords will not be stored
# This is for confidentiality purposes. Take note when adding a model for
# vulnerability.


class Reaction(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    comment = db.Column(db.Integer, db.ForeignKey('comment.id'))
    reaction = db.Column(db.String, nullable=False)

    def __init__(self, comment,reaction):
        self.comment = comment
        self.reaction = reaction

    def __repr__(self):
        return '<Reaction {}>'.format(self.reaction)
        
class Users(db.Model):
    __searchable__ = ['username']
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120),unique=True, nullable=True)
    password_hash = db.Column(db.String(256),nullable=True)
    uuid = db.Column(db.String, nullable=False)
    user_number = db.Column(db.Integer, nullable=True)
    #user_handle = db.Column(db.String, nullable=False)
    #profile_picture =  db.Column(db.String, nullable=True)
    user_visibility = db.Column(db.Boolean, nullable=False, default=True)
    verified = db.Column(db.Boolean, nullable=False, default=False)
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
    

    followed = db.relationship(
        'Users', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
        
    subs =  db.relationship(
        'Channels', secondary=subs,
        primaryjoin=(subs.c.users_id == id),
        backref=db.backref('notify', lazy='dynamic'), lazy='dynamic')

   

    blocked = db.relationship(
        'Users', secondary=blocking,
        primaryjoin=(blocking.c.blocker_id == id),
        secondaryjoin=(blocking.c.blocked_id == id),
        backref=db.backref('blocking',lazy='dynamic'), lazy='dynamic')
        
    def __init__(self, username,user_visibility,email=None,number=None):
        self.username = username
        self.uuid = str(uuid.uuid4())
        self.user_number = number
        #self.user_handle = user_handle
        #self.profile_picture = profile_picture
        self.user_visibility = user_visibility
        self.email =email


    def __repr__(self):
        return '<User %r>' % self.username

    def notified(self,channel):
        user=  self.query.join(
            subs,( subs.c.users_id == self.id))

        return user.filter(subs.c.notif == True).all()

    def add_notification(self,channel):
        if not self.notified(channel):
            notif =db.session.query(subs).filter(subs.c.users_id == self.id).first()
            notif.notif = True 

    def remove_notification(self,channel):
        if self.notified(channel):
            self.subs.append('False')

    def is_blocking(self, user):
        return self.blocked.filter(
            blocking.c.blocked_id == user.id).count() > 0

    def block(self,user):
        if not self.is_blocking(user):
            self.blocked.append(user)

    def unblock(self,user):#check this line
        if self.is_blocking(user):
            self.blocked.remove(user)

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
    
    def channel_sub_moderators(self):
        return Channels.query.join(
            sub_moderator,(sub_moderator.c.channel_id == Channels.id)).filter(
                sub_moderator.c.sub_moderator_id == self.id).order_by(Channels.id.desc())
        #own= Channels.query.filter_by(user_id=user)
        #return followed.union(own)

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

    def get_channels(self):
        return Channels.query.join(
            subs,(subs.c.users_id == self.id)).filter(
                subs.c.channel_id == Channels.id).all() 


    
    def passwordhash(self, password_taken):
        self.password_hash = generate_password_hash(password_taken)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def verify_phone(self, phone):
        return check_password_hash(self.user_number, phone)

    #def add_notification(self, name, data):
      #  self.notifications.filter_by(name=name).delete()
      #  n = Notification(name=name, payload_json=json.dumps(data), user=self)
      #  db.session.add(n)
      #  return n

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
    
    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

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



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def __init__(self, name, user):
        self.name = name
        self.user_id = user
        

    def get_data(self):
        return json.loads(str(self.payload_json))

class Channels(db.Model):
    __searchable__ = ['name', 'description', 'desc_en', 'desc_es', 'desc_fr', 'desc_pt', 'desc_ar', 'desc_sw', 'desc_ha']
    id = db.Column(db.Integer, primary_key=True)
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
        backref=db.backref('get_subscribers', lazy='dynamic'), lazy='dynamic')

    postchannel = db.relationship(
        'Posts',secondary=postchannel,
        primaryjoin=(postchannel.c.channel_id == id),
        backref=db.backref('channelpost', lazy='dynamic'), lazy='dynamic')

    
    def subscribed(self,user):
        return  self.query.join(
            subs,(subs.c.channel_id == self.id )).filter(
                subs.c.users_id == user.id).first()

            
    def haspost(self,post):
        return  self.query.join(
            postchannel,(postchannel.c.channel_id == self.id )).filter(
                postchannel.c.post_id == post.id).first()

    def add_sub(self,user):
        if not self.subscribed(user):
            self.subs.append(user)

    def add_post(self, post):
        if not self.haspost(post):
            self.postchannel.append(post)
            
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



class Setting(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False) 
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(50), nullable=False)
    post = db.Column(db.Boolean, nullable=False, default=False)
    comments = db.Column(db.Boolean, nullable=False, default=False)
    saves = db.Column(db.Boolean, nullable=False, default=False)
    channel = db.Column(db.Boolean, nullable=False, default=False)
    messages = db.Column(db.Boolean, nullable=False, default=False)
    N_S_F_W = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, language, users, theme, post, messages, channel, saves, comment):
        self.language_id = language
        self.theme = theme
        self.post = post
        self.messages = messages
        self.channel = channel
        self.saves = saves
        self.comments = comment
        self.users_id = users

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
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    uuid = db.Column(db.String)
    content = db.Column(db.Text)
    uploader = db.Column(db.String)
    post_url = db.Column(db.String)
    thumb_url = db.Column(db.String)
    orig_lang = db.Column(db.Integer, db.ForeignKey('language.id'), default=1)
    uploader_date = db.Column(db.DateTime, nullable=False)
    post_type = db.Column(db.Integer, db.ForeignKey('posttype.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ratings_id = db.relationship('Rating', backref='rating', lazy = True)
    comments_id = db.relationship('Comment', backref='postcomment', lazy = True)
    picture_url =db.Column(db.String)
    video_url =db.Column(db.String)
    postchannel = db.relationship(
        'Channels',secondary=postchannel,
        primaryjoin=(postchannel.c.post_id == id),
        secondaryjoin=(postchannel.c.channel_id == Channels.id),
        backref=db.backref('post_channel', lazy='dynamic'), lazy='dynamic')
    clap = db.relationship(
        'Users',secondary=clap,
        primaryjoin=(clap.c.post_id == id),
        secondaryjoin=(clap.c.user_id == Users.id),
        backref=db.backref('clap', lazy='dynamic'), lazy='dynamic')
    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'video', 'audio', 'hr']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def post_is_channel(self,channel):
        return self.query.join(
            postchannel,(postchannel.c.post_id == self.id)).filter(
                postchannel.c.channel_id == channel.id).first()

    def has_clapped(self,user):
        return self.query.join(
            clap,(clap.c.post_id == self.id)).filter(
            clap.c.user_id == user.id).first()

    def add_clap(self,user):
        if not self.has_clapped(user):
            self.clap.append(user)

    def remove_clap(self,user):
        if  self.has_clapped(user):
            self.clap.remove(user)

    def add_post(self,channel):
        if not self.post_is_channel(channel):
            self.postchannel.append(channel)

    def remove_post(self,channel):
        if self.post_is_channel(channel):
            self.postchannel.remove(channel)

    def __init__(self, uploader, title, posttype, content, lang, uploader_id, picture_url=None, video_url=None, thumb_url=None):
        self.content = content
        self.title = title
        self.uuid = secure_filename(title)+'_'+shortuuid.uuid()
        self.uploader_id = uploader
        self.post_type = posttype
        self.orig_lang = lang
        self.thumb_url = thumb_url
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

    def get_post_channels(self):
        return Channels.query.join(
            postchannel,(postchannel.c.post_id == self.id)).filter(
                postchannel.c.channel_id == Channels.id).all()

    def __repr__(self):
        return '<Post>%r' %self.title

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

class Comment(db.Model):

    _N = 6

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    comment_type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow, index=True)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable= False)
    public =db.Column(db.Boolean, nullable= False, default=True)
    path = db.Column(db.Text, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    post__data = db.relationship("Posts", 
        primaryjoin=(post_id == Posts.id),
        backref=db.backref('post_data', uselist=False), uselist=False)
    replies = db.relationship(
        'Comment', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic')
    shout =db.relationship(
        'Users',secondary=shout,
        primaryjoin=(shout.c.comment_id == id),
        secondaryjoin=(shout.c.user_id == Users.id),
        backref=db.backref('shout', lazy='dynamic'), lazy='dynamic')

    def has_shouted(self,user):
        return self.query.join(
            shout,(shout.c.comment_id == self.id)).filter(
            shout.c.user_id == user.id).first()

    def add_shout(self,user):
        if not self.has_shouted(user):
            self.shout.append(user)

    def remove_shout(self,user):
        if  self.has_shouted(user):
            self.shout.remove(user)
            
    def __init__(self, language, user, post, content, comment_type, public,parent_id=None):
        self.content = content
        self.user_id = user
        self.post_id = post
        self.language_id = language
        self.comment_type = comment_type
        self.public = public 
        self.parent_id = parent_id
        

    def __repr__(self):
        return '<Comment>%r' %self.content

    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self.id, self._N)
        db.session.commit()
        

    def level(self):
        return len(self.path) // self._N - 1

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
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
    posts = db.relationship('Posts', backref=db.backref('postarb', lazy='dynamic'))

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

class Posten(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
    posts = db.relationship('Posts', backref=db.backref('posten', lazy='dynamic'))

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

class Postpor(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
    posts = db.relationship('Posts', backref=db.backref('postpor', lazy='dynamic'))

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

class Postfr(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
    posts = db.relationship('Posts', backref=db.backref('postfr', lazy='dynamic'))
    
    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang

class Posthau(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
    posts = db.relationship('Posts', backref=db.backref('posthau', lazy='dynamic'))

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang 

class Postsw(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
    posts = db.relationship('Posts', backref=db.backref('postsw', lazy='dynamic'))

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang 

class Postes(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    title = db.Column(db.String(250), nullable = False, unique=True)
    content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
    posts = db.relationship('Posts', backref=db.backref('postes', lazy='dynamic'))

    def __init__(self, id, title, content, lang):
        self.id = id
        self.title = title
        self.content= content
        self.language_id = lang
 
class Save(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id =db.Column(db.Integer,db.ForeignKey('posts.id'),nullable=False)
    post___data=db.relationship('Posts', 
        primaryjoin=(post_id == Posts.id),
        backref=db.backref('postsdat_a', uselist=False), uselist=False)
    def __init__(self, user, content,post):
        self.user_id = user
        self.content = content
        self.post_id = post

    def __repr__(self):
        return '<Save %r>' % self.id

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender__name = db.relationship("Users", 
        primaryjoin=(sender_id == Users.id),
        backref=db.backref('sender_name', uselist=False), uselist=False)
    recipient__name = db.relationship("Users", 
        primaryjoin=(recipient_id == Users.id),
        backref=db.backref('recipient_name', uselist=False), uselist=False)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)
    
