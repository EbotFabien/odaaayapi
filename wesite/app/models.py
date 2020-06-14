from app import db
from datetime import datetime, timedelta
import uuid

class Posts(db.Model):
    __searchable__ = ['uuid', 'description', 'pubdate', 'link']
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.String, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, nullable=False)
    pubdate = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String, nullable=False)
    source_desc = db.Column(db.String, nullable=False)
    thumb= db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __init__(self, title, description, link, pubdate, source, source_desc, thumb):
        self.uuid = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate
        self.source = source
        self.source_desc = source_desc
        self.thumb = thumb

    def __repr__(self):
        return '<Post>%r' %self.uuid

class Summary(db.Model):
    __searchable__ = ['content']
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    posts = db.relationship('Posts', backref='post', lazy=True)

    def __init__(self, content, post):
        self.content = content
        self.post_id = post

    def __repr__(self):
        return '<Summary>%r' %self.content