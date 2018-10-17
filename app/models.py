from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin  # Methods for User model to make it compatible with flask login
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    """Mixin to synchronise changes made in database with Elasticsearch db via improving SQLAlchemy methods"""

    @classmethod
    def search(cls, expression, page, per_page):
        """
        Search some text via Elasticsearch and return SQLAlchemy query to get corresponding SQLAlchemy objects

        :param expression: text to search
        :param page: which page of results should we get back
        :param per_page: how many posts per page with results there should be
        :return: SQLAlchemy query to get SQLAlchemy objects according to Elasticsearch resulting list of ids
        """

        # Query to Elasticsearch to find elements containing given text
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0

        # Make list of tuples to denote order of ids returned from Elasticsearch by their relevance to text in
        # search query
        when = [(ids, i) for i, ids in enumerate(ids)]

        # First we filter out ids from db table so that there left only these that exist in list of ids returned by
        # Elasticsearch; then we sort corresponding ids from table according their order in Elasticsearch resulting list
        return cls.query.filter(cls.id.in_(ids)).order_by(db.case(when, value=cls.id)), total

        # More about ordering via case construct here:
        # https://stackoverflow.com/questions/6332043/sql-order-by-multiple-values-in-specific-order/6332081#6332081
        # and here:
        # https://docs.sqlalchemy.org/en/latest/core/sqlelement.html#sqlalchemy.sql.expression.case

    @classmethod
    def before_commit(cls, session):
        """
        Save changes to a new attribute because they won't be available after the session is committed
        :param session: I guess current db session but actually this is Miguel Grinberg's code so I am not sure
        :return: None
        """
        session._changes = {
            'add': [obj for obj in session.new if isinstance(obj, cls)],
            'update': [obj for obj in session.dirty if isinstance(obj, cls)],
            'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
        }

    @classmethod
    def after_commit(cls, session):

        """
        add accepted changes in database to Elasticsearch
        :param session: I guess current db session but actually this is Miguel Grinberg's code so I am not sure
        :return: None
        """
        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            remove_from_index(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        """
        a simple helper method that you can use to refresh an index
        with all the data from the relational side
        :return: None
        """
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


# Note that I am not declaring this table as a model, like I did for the users and posts tables. Since this is an
# auxiliary table that has no data other than the foreign keys, I created it without an associated model class.
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(280))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Get link for user's avatar. Create new is user doesn't have one.
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=robohash&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    # Get posts of people this user follows along with own posts of the user
    def get_followed_posts(self):
        # Get others' posts
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        # Get own posts
        own = Post.query.filter_by(user_id=self.id)
        # Merge them and sort by date
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, current_app.config['SECRET_KEY'],
                          algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithm=['HS256'])['reset_password']
            # You don't need to check expiration manually - it is being checked automatically
        except:
            return
        return User.query.get(user_id)


class Post(SearchableMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))
    __searcheable__ = ['body']

    def __repr__(self):
        return f'<Post {self.body}>'


# These set up
# the event handlers that are invoked before and after each commit.
db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
