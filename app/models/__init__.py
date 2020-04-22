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
from flask import current_app


subs = db.Table('subs',
    db.Column('channel_id', db.Integer, db.ForeignKey('channels.id'), primary_key=True),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)
followers = db.Table('followers',
    db.Column('follower_id',db.Integer,db.ForeignKey('users.id')),
    db.Column('followed_id',db.Integer,db.ForeignKey('users.id'))
)
# The user table will store user all user data, passwords will not be stored
# This is for confidentiality purposes. Take note when adding a model for
# vulnerability.
# ****** channel.subsciber.append(user), then commit()
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    password_hash = db.Column(db.String, nullable=False)
    uuid = db.Column(db.String, nullable=False)
    user_number = db.Column(db.String, nullable=True)
    user_saves = db.relationship('Save', backref="save", lazy=True )
    user_messages = db.relationship('Message',backref = "message", lazy = True)
    user_ratings = db.relationship('Rating', backref = "userrating", lazy = True)
    user_setting = db.relationship('Setting', backref = "usersetting", lazy = True)
    subs = db.relationship('Channels', secondary=subs, lazy='subquery',
        backref=db.backref('subscribers', lazy=True))
    followed = db.relationship(
        'Users', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def __init__(self, username, email, password_hash, number):
        self.username = username
        self.email = email
        self.uuid = str(uuid.uuid4())
        self.password_hash =  generate_password_hash(password_hash)
        self.user_number = number

    def __repr__(self):
        return '<User %r>' % self.username
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue('app.tasks.' + name, self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
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
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100



class Channels(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    profile_pic = db.Column(db.String)
    background = db.Column(db.String)
    css = db.Column(db.String) 
    moderator = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


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

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return '<Message %r>' %self.id

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

    def __init__(self, uploader, title, channel, posttype, content, uploader_id):
        self.content = content
        self.title = title
        self.uploader_id = uploader
        self.channel_id = channel
        self.post_type = posttype
        self.uploader = Users.query.filter_by(id=uploader_id).first().username
        self.uploader_date = datetime.utcnow()
    
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

    def __init__(self, content, user, comment,comtype):
        self.content = content
        self.user = user
        self.comment = comment
        self.subcomment_type = comtype

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

class Postarb(Posts):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    arb_title = db.Column(db.String(250), nullable = False, unique=True)
    arb_content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False) 

class Posten(Posts):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    en_title = db.Column(db.String(250), nullable = False, unique=True)
    en_content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False) 

class Postpor(Posts):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    por_title = db.Column(db.String(250), nullable = False, unique=True)
    por_content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False) 

class Postfr(Posts):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    fr_title = db.Column(db.String(250), nullable = False, unique=True)
    fr_content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False) 

class Posthau(Posts):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    hau_title = db.Column(db.String(250), nullable = False, unique=True)
    hau_content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False) 

class Postsw(Posts):
    id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    sw_title = db.Column(db.String(250), nullable = False, unique=True)
    sw_content = db.Column(db.String, nullable = False, unique=True)
    language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False) 

