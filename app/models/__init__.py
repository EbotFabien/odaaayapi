# This file contains the models of the code. The database in use doesn't matter
# just insert the new model and properly link the model as on the ERD then you will be good to go.
# After linking, * Run flask Migrate to use Alembic module to migrate the data without destroying your
# Data in the Database. This file should not be messed with if you donno know what you are doing.

from app import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime, timedelta
from sqlalchemy import ForeignKeyConstraint, ForeignKey, UniqueConstraint
import json
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from time import time
import json
import shortuuid
import bleach
from markdown import markdown
from werkzeug.utils import secure_filename
import rq
import redis


Not_Interested = db.Table('Not_Interested',
                          db.Column('user_id', db.Integer,
                                    db.ForeignKey('users.id')),
                          db.Column('post_id', db.Integer,
                                    db.ForeignKey('posts.id'))
                          )


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('users.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('users.id')),
                     )

blocking = db.Table('Blocked',
                    db.Column('blocker_id', db.Integer,
                              db.ForeignKey('users.id')),
                    db.Column('blocked_id', db.Integer,
                              db.ForeignKey('users.id')),
                    )

clap = db.Table('clap',
                db.Column('clap_id', db.Integer,
                          autoincrement=True, primary_key=True),
                db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
                )


# The user table will store user all user data, passwords will not be stored
# This is for confidentiality purposes. Take note when adding a model for
# vulnerability.

shorty = shortuuid.uuid()


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #settings = db.relationship('Setting', backref='setting', lazy=True)
    lang_type = db.Column(db.String(30), nullable=False)
    code = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return '<Language>%r' % self.name


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return '<Category>%r' % self.name


class Users(db.Model):
    __searchable__ = ['username', 'handle', 'country']
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)  # unique True
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    uuid = db.Column(db.String(60), nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.String(350), nullable=True)
    picture = db.Column(db.String(120), nullable=True)
    background = db.Column(db.String(120), nullable=True)
    country = db.Column(db.String(120), nullable=True)
    user_visibility = db.Column(db.Boolean, nullable=False, default=True)
    user_ratings = db.relationship('Rating', backref="userrating", lazy=True)
    #user_setting = db.relationship('Setting', backref = "usersetting", lazy = True)
    language_id = db.Column(
        db.Integer, db.ForeignKey('language.id'), nullable=True)
    handle = db.Column(db.String(120), nullable=True)
    code_expires_in = db.Column(db.DateTime)
    verified_email = db.Column(db.Boolean, nullable=False, default=False)
    verified_phone = db.Column(db.Boolean, nullable=False, default=False)
    tries = db.Column(db.Integer, default=0)
    created_on = db.Column(db.DateTime)
    rescue = db.Column(db.String)
    product_id = db.Column(db.String)
    customer_id = db.Column(db.String)
    price_id = db.Column(db.String)
    price = db.Column(db.Float)
    paid = db.Column(db.Boolean, default=False)

    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic')
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    Lang = db.relationship(
        'Language',
        primaryjoin=(language_id == Language.id),
        backref=db.backref('Lang_',  uselist=False), uselist=False)

    followed = db.relationship(
        'Users', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    blocked = db.relationship(
        'Users', secondary=blocking,
        primaryjoin=(blocking.c.blocker_id == id),
        secondaryjoin=(blocking.c.blocked_id == id),
        backref=db.backref('blocking', lazy='dynamic'), lazy='dynamic')

    claps = db.relationship(
        'Posts', secondary=clap,
        primaryjoin=(clap.c.user_id == id),
        backref=db.backref('clap_no', lazy='dynamic'), lazy='dynamic')

    def __init__(self, username, uuid, user_visibility, email=None, number=None):
        self.username = username
        self.uuid = uuid
        self.phone = number
        #self.picture = profile_picture
        self.user_visibility = user_visibility
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

    def No_claps(self):
        return self.clap.filter(clap.c.user_id == self.id).count()

    def is_blocking(self, user):
        return self.blocked.filter(
            blocking.c.blocked_id == user.id).count() > 0

    def block(self, user):
        if not self.is_blocking(user):
            self.blocked.append(user)

    def unblock(self, user):  # check this line
        if self.is_blocking(user):
            self.blocked.remove(user)

    def has_blocked(self):
        return Users.query.join(
            blocking, (blocking.c.blocked_id == Users.id)).filter(
                blocking.c.blocker_id == self.id)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def followed_posts(self):
        followed = Posts.query.join(
            followers, (followers.c.followed_id == Posts.uploader_id)).filter(
                followers.c.follower_id == self.id)
        own = Posts.query.filter_by(uploader_id=self.id)
        return followed.union(own).order_by(Posts.uploader_date.desc())

    def has_followed(self):
        return Users.query.join(
            followers, (followers.c.followed_id == Users.id)).filter(
                followers.c.follower_id == self.id).all()

    def is_followers(self):
        use = Users.query.join(
            followers, (followers.c.follower_id == Users.id)).filter(
                followers.c.followed_id == self.id).all()
        follow = list()
        for i in use:
            follow.append(i.id)
        return follow

    def is_followersd(self):
        return Users.query.join(
            followers, (followers.c.follower_id == Users.id)).filter(
                followers.c.followed_id == self.id).all()

    def passwordhash(self, password_taken):
        self.password_hash = generate_password_hash(password_taken)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def verify_phone(self, phone):
        return check_password_hash(self.user_number, phone)

    def add_prog_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n

    def launch_task(self, name, description, *args, **kwargs):
        rq_job = app.task_queue.enqueue(
            'app.services.task.' + name, self.id, *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name,
                    description=description, user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def get_reset_token(self, expire_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expire_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)

# class Postsummary(db.Model):
 #   id = db.Column(db.Integer, primary_key = True)
  #  post_id =db.Column(db.Integer,db.ForeignKey('posts.id'),nullable=False)
  #  content = db.Column(db.String)
  #  language_id = db.Column(db.Integer,db.ForeignKey('language.id'), nullable=False)
  #  status = db.Column(db.String)
  #  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

   # def __repr__(self):
    #    return '<Postsummary %r>' % self.id


class Subs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_sub = db.Column(db.Integer, db.ForeignKey('users.id'))
    sub_id = db.Column(db.String(60))
    valid = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<Subs %r>' % self.id


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    account_id = db.Column(db.String(60))
    valid = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Account %r>' % self.id


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


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey(
        'language.id'), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(50), nullable=False)
    N_S_F_W = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, language, users, theme):
        self.language_id = language
        self.theme = theme
        self.users_id = users

    def __repr__(self):
        return '<Setting %r>' % self.id


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ratingtype = db.Column(db.Integer, db.ForeignKey(
        'ratingtype.id'), nullable=False)
    rater = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    def __init__(self, ratingtype, rater, post):
        self.post_id = post
        self.rater = rater
        self.ratingtype = ratingtype

    def __repr__(self):
        return '<Rating>%r' % self.id


class Posts(db.Model):
    __searchable__ = ['title', 'text_content',
                      'created_on', 'user_name', 'price', 'tags']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10000))
    uuid = db.Column(db.String(1000000))  # check
    description = db.Column(db.String(10000))
    post_url = db.Column(db.String(10000))
    thumb_url = db.Column(db.String(10000))
    text_content = db.Column(db.Text)
    picture_url = db.Column(db.String(10000))
    audio_url = db.Column(db.String(10000))
    video_url = db.Column(db.String(10000))
    Country = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey('category.id'), nullable=True)
    translate = db.Column(db.Boolean, nullable=False, default=False)
    summarize = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_name = db.Column(db.String(10000))
    donation_id = db.Column(db.String())
    product_id = db.Column(db.String())
    price_id = db.Column(db.String())
    price = db.Column(db.Float())
    mini = db.Column(db.Float())
    maxi = db.Column(db.Float())
    subs_only = db.Column(db.Boolean, default=False)
    nsfw = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)
    visibility = db.Column(db.Boolean, default=True)
    tags = db.Column(db.Text)
    post_type = db.Column(db.Integer, db.ForeignKey(
        'posttype.id'), nullable=False)
    orig_lang = db.Column(db.Integer, db.ForeignKey('language.id'), default=1)
    ratings = db.relationship('Rating', backref='rating', lazy=True)

    # summarized = db.relationship('Postsummary',
    #   primaryjoin=(id == Postsummary.post_id),
    #  backref='summarized', lazy='dynamic')

    clap = db.relationship(
        'Users', secondary=clap,
        primaryjoin=(clap.c.post_id == id),
        secondaryjoin=(clap.c.user_id == Users.id),
        backref=db.backref('clap', lazy='dynamic'), lazy='dynamic')

    Not_Interested = db.relationship(
        'Users', secondary=Not_Interested,
        primaryjoin=(Not_Interested.c.post_id == id),
        secondaryjoin=(Not_Interested.c.user_id == Users.id),
        backref=db.backref('no_interest', lazy='dynamic'), lazy='dynamic')

    uploader_data = db.relationship("Users",
                                    primaryjoin=(author == Users.id),
                                    backref=db.backref('uploader__data',  uselist=False),  uselist=False)

    # Save = db.relationship(
    # 'Users',secondary=Save,
    #primaryjoin=(Save.c.post_id == id),
    #secondaryjoin=(Save.c.user_id == Users.id),
    # backref=db.backref('Save', lazy='dynamic'), lazy='dynamic')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'video', 'audio', 'hr']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def has_clapped(self, user):
        return self.query.join(
            clap, (clap.c.post_id == self.id)).filter(
            clap.c.user_id == user.id).first()

    def not_interested(self, user):
        return self.query.join(
            Not_Interested, (Not_Interested.c.post_id == self.id)).filter(
            Not_Interested.c.user_id == user.id).first()

    def is_not_interested(self, user):
        if not self.not_interested(user):
            self.Not_Interested.append(user)

    def remove_not_interested(self, user):
        if self.not_interested(user):
            self.Not_Interested.remove(user)

    def No__claps(self):
        return self.clap.filter(clap.c.post_id == self.id).count()

    def add_clap(self, user):
        if not self.has_clapped(user):
            self.clap.append(user)

    def remove_clap(self, user):
        if self.has_clapped(user):
            self.clap.remove(user)

    def __init__(self, uploader, title, posttype, content, lang, post_url=None, video_url=None, thumb_url=None):
        self.text_content = content
        self.title = title
        self.uuid = secure_filename(title)+'_'+shorty[0:3]
        self.author = uploader
        self.post_type = posttype
        self.orig_lang = lang
        self.thumb_url = thumb_url
        #self.uploader = Users.query.filter_by(id=uploader_id).first().username
        #elf.uploader_date = datetime.utcnow()
        self.post_url = post_url
        self.video_url = video_url

    def launch_translation_task(self, name, userid,descr):
        with app.app_context():
            rq_job = app.task_queue.enqueue(
                'app.services.task.' + name, self.id,userid)
        task = Task(id=rq_job.get_id(), name=name,
                    user_id=userid, description=descr)
        db.session.add(task)
        db.session.commit()
        return task

    def launch_summary_task(self, name, userid, descr):
        with app.app_context():
            rq_job = app.task_queue.enqueue(
                'app.services.task.' + name, self.id,userid)
        task = Task(id=rq_job.get_id(), name=name,
                    user_id=userid, description=descr)
        db.session.add(task)
        db.session.commit()
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(user=self, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, user=self,
                                    complete=False).first()

    def __repr__(self):
        return '<Post>%r' % self.title


class Post_Access(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    post = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_data = db.relationship("Users",
                                primaryjoin=(user == Users.id),
                                backref=db.backref('uploader__data_',  uselist=False),  uselist=False)
    post_data = db.relationship("Posts",
                                primaryjoin=(post == Posts.id),
                                backref=db.backref('_uploader__data',  uselist=False),  uselist=False)

    def __repr__(self):
        return '<Post_Access %r>' % self.id


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    post = db.Column(db.Integer, db.ForeignKey('posts.id'))
    tags = db.Column(db.String)

    def __repr__(self):
        return '<Tags %r>' % self.id


class Translated(db.Model):
    __searchable__ = ['title', 'fullcontent',
                      'tags', 'timestamp', 'user', 'category']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    content = db.Column(db.String, nullable=False)
    fullcontent = db.Column(db.String, nullable=False)
    user = db.Column(db.String)
    category = db.Column(db.String)
    language_id = db.Column(db.Integer, db.ForeignKey(
        'language.id'), nullable=False)
    category_id = db.Column(
        db.Integer, db.ForeignKey('category.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    tags = db.Column(db.Text)
    status = db.Column(db.String)
    visibility = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    posts = db.relationship('Posts',
                            primaryjoin=(post_id == Posts.id),
                            backref='translations', uselist=False)

    def __repr__(self):
        return '<Translated %r>' % self.id


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    seen = db.Column(db.Boolean, nullable=False, default=False)
    created_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    payload_json = db.Column(db.Text)
    user_data = db.relationship("Users",
                                primaryjoin=(user_id == Users.id),
                                backref=db.backref('uploader__dat_a_',  uselist=False),  uselist=False)
    post_data = db.relationship("Posts",
                                primaryjoin=(post_id == Posts.id),
                                backref=db.backref('_uploader__dat_a',  uselist=False),  uselist=False)

    def __init__(self, name, user, post):
        self.name = name
        self.user_id = user
        self.post_id = post

    def get_data(self):
        return json.loads(str(self.payload_json))

    def __repr__(self):
        return '<Notification %r>' % self.id


class Posttype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Posttype>%r' % self.id


class Ratingtype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Ratingtype>%r' % self.id


class Reporttype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Reporttype>%r' % self.id


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String)
    reporter = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_reported = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    rtype = db.Column(db.Integer, db.ForeignKey(
        'reporttype.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Report %r>' % self.id


class Save(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    post___data = db.relationship('Posts',
                                  primaryjoin=(post_id == Posts.id),
                                  backref=db.backref('postsdat_a', uselist=False), uselist=False)

    def __init__(self, user, post):
        self.user_id = user
        self.post_id = post

    def __repr__(self):
        return '<Save %r>' % self.id


class country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    code = db.Column(db.String)

    def __repr__(self):
        return '<country>%r' % self.id


class app_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return '<app_history>%r' % self.id


class billing_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String)
    task = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return '<billing_history>%r' % self.id
