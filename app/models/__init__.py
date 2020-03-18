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
    uuid = db.Column(db.String, unique=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    ip_addr = db.Column(db.String)
    verified = db.Column(db.Boolean)
    verified_on = db.Column(db.DateTime)
    vericount = db.Column(db.Integer, default=0)
    bio = db.Column(db.String)
    datecreated = db.Column(db.DateTime)
    profile_pic = db.Column(db.String)
    
    
    def __init__(self, username, email, password_hash, ip_addr, \
    datecreated, verified, bio, profile_pic):
        self.username = username
        self.uuid = uuid.uuid4().hex
        self.email = email
        self.password_hash =  generate_password_hash(password_hash)
        self.ip_addr = ip_addr
        self.verified = verified
        self.verified_on = datetime.utcnow()
        self.datecreated = datecreated
        self.bio = bio
        self.profile_pic = profile_pic
        self.vericount = 0

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
    name = db.Column(db.String, nullable=False)
    
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.name

