from flask_sqlalchemy import SQLAlchemy
from enum import Enum
import datetime
import json

from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import DeclarativeMeta

from superform.utils import str_converter


# ADRI standardize
class State(Enum):
    INCOMPLETE = -1     # draft
    NOT_VALIDATED = 0    # waiting to be reviewed by a moderator
    VALIDATED = 1       # validated by a moderator
    PUBLISHED = 2       # archived
    REFUSED = 3         # refused by the moderation, must be reworked or deleted
    OLD_VERSION = 4


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    # TEAM2: Google calendar
    gcal_cred = db.Column(db.String(2147483647), nullable=True)
    # TEAM2: Google calendar
    posts = db.relationship("Post", backref="user", lazy=True)
    authorizations = db.relationship("Authorization", backref="user", lazy=True)

    def __repr__(self):
        return '<User {}>'.format(repr(self.id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.String(80), db.ForeignKey("user.id"), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    link_url = db.Column(db.Text)
    image_url = db.Column(db.Text)
    date_from = db.Column(db.DateTime)
    date_until = db.Column(db.DateTime)

    publishings = db.relationship("Publishing", backref="post", lazy=True)

    __table_args__ = ({"sqlite_autoincrement": True},)

    def __repr__(self):
        return '<Post {}>'.format(repr(self.id))

    def is_a_record(self):
        if len(self.publishings) == 0:
            return False
        else:
            # check if all the publications from a post are archived
            for pub in self.publishings:
                if pub.state != 2:
                    # state 2 is archived.
                    return False
            return True


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in vars(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    if data.__class__ == datetime.datetime:
                        fields[field] = str_converter(data)
                    else:
                        json.dumps(data)  # this will fail on non-encodable values, like other classes
                        fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields
        return json.JSONEncoder.default(self, obj)


class Publishing(db.Model):
    publishing_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    num_version = db.Column(db.Integer, nullable=False, default=1)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    # TEAM2: Stat module
    user_id = db.Column(db.String(80), db.ForeignKey("user.id"), nullable=False)
    # TEAM2: Stat module
    channel_id = db.Column(db.Integer, db.ForeignKey("channel.id"), nullable=False)
    state = db.Column(db.Integer, nullable=False, default=-1)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    link_url = db.Column(db.Text)
    image_url = db.Column(db.Text)
    date_from = db.Column(db.DateTime)
    date_until = db.Column(db.DateTime)
    
    UniqueConstraint(num_version, post_id, channel_id, name='unicity_publishing_numvers')
    __table_args__ = ({"sqlite_autoincrement": True},)

    def __repr__(self):
        return '<Publishing {} ({} {})>'.format(repr(self.publishing_id), repr(self.post_id), repr(self.channel_id))

    def get_author(self):
        return db.session.query(Post).get(self.post_id).user_id

    def get_chan_module(self):  # Return the name of the plugin used by the publication
        chn = db.session.query(Channel).get(self.channel_id).module
        return chn[18:]


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(100), nullable=False)
    config = db.Column(db.Text, nullable=False)
    count = db.Column(db.Integer, default=0)

    publishings = db.relationship("Publishing", cascade="all, delete-orphan", backref="channel", lazy=True)
    authorizations = db.relationship("Authorization", cascade="all, delete", backref="channel", lazy=True)

    __table_args__ = ({"sqlite_autoincrement": True},)

    def __repr__(self):
        return '<Channel {}>'.format(repr(self.id))


class Authorization(db.Model):
    user_id = db.Column(db.String(80), db.ForeignKey("user.id"), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey("channel.id"), nullable=False)
    permission = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.PrimaryKeyConstraint('user_id', 'channel_id'),)

    def __repr__(self):
        return '<Authorization {} {}>'.format(repr(self.user_id), repr(self.channel_id))


class Comment(db.Model):
    publishing_id = db.Column(db.Integer, db.ForeignKey("publishing.publishing_id"), primary_key=True, nullable=False)
    user_comment = db.Column(db.Text, nullable=True)
    moderator_comment = db.Column(db.Text, nullable=True)
    date_moderator_comment = db.Column(db.Text, nullable=True)
    date_user_comment = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return '<Comment {}>'.format(repr(self.publishing_id))

    __table_args__ = (db.PrimaryKeyConstraint('publishing_id'),)


class Permission(Enum):
    AUTHOR = 1
    MODERATOR = 2
