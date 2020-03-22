# This file contains the models of the code. The database in use doesn't matter
# just insert the new model and properly link the model as on the ERD then you will be good to go.
# After linking, * Run flask Migrate to use Alembic module to migrate the data without destroying your
# Data in the Database. This file should not be messed with if you donno know what you are doing.

from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import os
import base64



# The user table will store user all user data, passwords will not be stored
# This is for confidentiality purposes. Take note when adding a model for
# vulnerability.
class User (db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    user_saves = db.relationship('Save', backref="save", lazy=True )
    #user_channels = "many to many"
    user_messages = db.relationship('Message',backref = "message", lazy = True)
    user_comments = db.relationship('Comment',backref="comment", lazy = True)
    user_subcomments = db.relationship('Subcomment',backref = "subcomment", lazy = True)
    user_posts = db.relationship('Post',backref = "post", lazy = True)
    user_ratings = db.relationship('Rating', backref = "rating", lazy = True)
    user_number = db.Column(db.String(50), nullable=False)
    
    
    def __init__(self, username, email, password_hash, saves, channels, setting, messages, comments, subcomments, posts, ratings, number):
        self.username = username
        self.email = email
        self.password_hash =  generate_password_hash(password_hash)
        self.saves = saves
        self.channels = channels
        self.posts = posts
        self.ratings = ratings
        self.setting = setting
        self.number = number
        self.messages = messages
        self.comments = comments

    def __repr__(self):
        return '<User %r>' % self.username
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Save (db.Model):
    __tablename__ = "Save"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return '<Save %r>' % self.id

class Setting(db.Model):
    __tablename__ = "Setting"
    id = db.Column(db.Integer, primary_key = True)
    language_id = db.Column(db.Integer,db.ForeignKey('Language.id'), nullable=False) 
    users_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    theme = db.Column(db.String(50), nullable=False)

    def __init__(self, language, users, theme):
        self.language = language
        self.theme = theme
        self.users = users
    def __repr__(self):
        return '<Setting %r>' % self.id

class Message (db.Model):
    __tablename__ ="Message"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('User.id'), nullable=False)

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return '<Message %r>' %self.id

class Language(db.Model):
    __tablename__="Language"
    id = db.Column(db.Integer, primary_key=True)
    settings_id = db.relationship('Setting', backref='setting', lazy=True)
    comments_id = db.relationship('Comment', backref='comment', lazy=True)
    type = db.Column(db.String(30), nullable=False)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(40), nullable=False)

    def __init__(self, name, code, comments, settings):
        self.settings = settings
        self.comments = comments
        self.code = code
        self.name = name
    def __repr__(self):
        return '<Language>%r' %self.name

class Comment(db.Model):
    __tablename__="Comment"
    id = db.Column(db.Integer, primary_key=True)
    subcomments_id = db.relationship(db.Integer,backref='subcomment', lazy=True)
    language_id = db.Column(db.Integer, db.ForeignKey('Language.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    content = db.Column(db.String(250), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    postsw_id = db.Column(db.Integer, db.ForeignKey('Postsw.id'), nullable= False)
    postarb_id = db.Column(db.Integer, db.ForeignKey('Postarb.id'), nullable= False)
    posten_id = db.Column(db.Integer, db.ForeignKey('Posten.id'), nullable= False)
    postpor_id = db.Column(db.Integer, db.ForeignKey('Postpor.id'), nullable= False) 
    postfr_id = db.Column(db.Integer, db.ForeignKey('Postfr.id'), nullable= False)
    posthau_id = db.Column(db.Integer, db.ForeignKey('Posthau.id'), nullable= False) 
    

    def __init__(self, subcomments, language, user,content):
        self.content = content
        self.user = user
        self.subcomments = subcomments
        self.language = language
        self.type = type

    def __repr__(self):
        return '<Comment>%r' %self.content

class Subcomment (db.Model):
    __tablename__="Subcomment"
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('Comment.id'),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    content = db.Column(db.String(250), nullable=False)
    type = db.Column(db.String(250), nullable=False)

    def __init__(self, content, user, comment,type):
        self.content = content
        self.user = user
        self.comment = comment
        self.type = type

    def __repr__(self):
        return '<Subcomment>%r' %self.content

UsersChannels = db.table('UsersChannel', 
db.Column('channel_id', db.Integer, db.ForeignKey('Channel.id'), primary_key=True),
db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True))

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    users_id = db.relationship('User', secondary = UsersChannels, lazy = 'subqery', backref = db.backref('channel', lazy =True)) 
    posts_id = db.relationship('Post', backref='post', lazy = True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(250))
    profile_pic = db.Column(db.String(250))
    background = db.Column(db.String(250))

    def __init__(self, name, description, profile_pic, background, users, posts):
        self.users = users
        self.name = name
        self.profile_pic = profile_pic
        self.background = background
        self.posts = posts

    def __repr__(self):
        return'<Channel>%r' %self.name

class Posttype (db.Model):
    __tablename__="Posttype"
    id = db.Column(db.Integer, primary_key=True)
    posts_id = db.relationship(db.Integer, backref='post', lazy= True)

    def __init__(self, posts):
        self.posts = posts

    def __repr__(self):
        return '<Posttype>%r' %self.id


class Ratingtype(db.Model):
    __tablename__="Ratingtype"
    id = db.Column(db.Integer, primary_key=True)
    ratings_id = db.relationship(db.Integer, backref='rating', lazy=True)

    def __init__(self, ratings):
        self.ratings = ratings
    def __repr__(self):
        return '<Ratingtype>%r' %self.id

class Rating(db.Model):
    __tablename__="Rating"
    id = db.Column(db.Integer, primary_key=True)
    ratingtype = db.Column(db.Integer, db.ForeignKey('Ratingtype.id'), nullable = False)
    rater = db.Column(db.Integer, db.ForeignKey('User.id'), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('Post.id'), nullable= False)

    def __init__(self, ratingtype, rater,post):
        self.post = post
        self.rater = rater
        self.ratingtype = ratingtype
    def __repr__(self):
        return '<Rating>%r' %self.id
     
class Post(db.Model):
    __tablename__="Post"
    id = db.Column(db.Integer, primary_key=True)
    ratings_id = db.relationship('Rating', backref='rating', lazy = True)
    channel_id = db.Column(db.Integer, db.ForeignKey('Channel.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    title = db.Column(db.String(250))
    content = db.Column(db.String(250))
    #uploader_date = db.Column(db.datetime) no take datetime values
    # many to many 
    """postsws_id = 
    postarbs_id =
    postens_id = 
    postpors_id = 
    postfrs_id = 
    posthaus_id ="""

    def __init__(self, ratings, uploader, title, content, uploader_date):

        self.content = content
        self.title = title
        self.ratings = ratings
        self.uploader_date = uploader_date
        self.uploader = uploader
    
    def __repr__(self):
        return '<Post>%r' %self.title


class Postarb (Post):
    __tablename__ ="Postarb"
    comments_id = db.relationship('Comment', backref='comment', lazy = True)
    #posts = db.Column(db.Po)

class Posten (Post):
    __tablename__ ="Posten"
    comments_id = db.relationship('Comment', backref='comment', lazy = True)
    #posts = db.Column(db.Po

class Postpor (Post):
    __tablename__ ="Postpor"
    comments_id = db.relationship('Comment', backref='comment', lazy = True)
    #posts_id = db.Column(db.Po

class Postfr (Post):
    __tablename__ ="Postfr"
    comments_id = db.relationship('Comment', backref='comment', lazy = True)
    #posts = db.Column(db.Po

class Posthau (Post):
    __tablename__ ="Posthau"
    comments_id = db.relationship('Comment', backref='comment', lazy = True)
    #posts = db.Column(db.Po