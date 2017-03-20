# -*- coding: utf-8 -*-
import urllib
from datetime import datetime
from hashlib import md5, sha256
from uuid import uuid4

from flask_rbac import RoleMixin, UserMixin
from flask.ext.sqlalchemy import BaseQuery

from cms.models import db, ModelMixin


class UserQuery(BaseQuery):
    def authenticate(self, loginname, raw_passwd):
        user = self.filter(User.loginname == loginname).first()
        if user and user.check_password(raw_passwd):
            return user
        return None


roles_parents = db.Table(
    'roles_parents',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('parent_id', db.Integer, db.ForeignKey('role.id'))
)

users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Role(ModelMixin, RoleMixin, db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    parents = db.relationship(
        'Role',
        secondary=roles_parents,
        primaryjoin=(id == roles_parents.c.role_id),
        secondaryjoin=(id == roles_parents.c.parent_id),
        backref=db.backref('children', lazy='dynamic')
    )
    users = db.relationship('User', secondary=users_roles,
                            backref=db.backref('roles', lazy='dynamic'))

    def __init__(self, name):
        RoleMixin.__init__(self)
        self.name = name

    def add_parent(self, parent):
        # You don't need to add this role to parent's children set,
        # relationship between roles would do this work automatically
        self.parents.append(parent)

    def add_parents(self, *parents):
        for parent in parents:
            self.add_parent(parent)

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()



class User(ModelMixin, UserMixin, db.Model):
    """Model of user."""

    __tablename__ = 'user'
    query_class = UserQuery
    USER_STATE_VALUES = ('normal', 'frozen', 'deleted', 'unactivated')
    USER_STATE_TEXTS = ('Normal', 'Frozen',
                        'Deleted', 'Unactivated')

    id = db.Column(db.Integer, primary_key=True)
    loginname = db.Column(db.String(30), nullable=False)
    hashed_password = db.Column(db.String(64))
    nickname = db.Column(db.String(16), unique=True)
    email = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(11), nullable=True)
    qq = db.Column(db.String(15), nullable=True)
    avatar = db.Column(db.String(250))
    create_date = db.Column(db.DateTime, default=datetime.now())
    salt = db.Column(db.String(32), nullable=False)
    state = db.Column(db.Enum(*USER_STATE_VALUES), default='normal')

    def __init__(self, **kwargs):
        self.salt = uuid4().hex

        if 'loginname' in kwargs:
            loginname = kwargs.pop('loginname')
            self.loginname = loginname.lower()

        if 'passwd' in kwargs:
            raw_passwd = kwargs.pop('passwd')
            self.change_password(raw_passwd)

        if 'nickname' in kwargs:
            nickname = kwargs.pop('nickname')
            self.nickname = nickname.lower()

        db.Model.__init__(self, **kwargs)

    def __unicode__(self):
        return self.loginname

    def __repr__(self):
        return "<User: %s>" % self.loginname

    def change_password(self, raw_passwd):
        self.salt = uuid4().hex
        self.hashed_password = self._hash_password(self.salt, raw_passwd)

    def check_password(self, raw_passwd):
        _hashed_password = self._hash_password(self.salt, raw_passwd)
        return self.hashed_password == _hashed_password

    def has_email(self):
        return not self.email is None

    def check_email(self, email):
        return self.email == email

    def is_active(self):
        return self.state == 'normal'

    def is_anonymous(self):
        return self.nickname is None

    def get_id(self):
        return self.id

    def get_role(self):
        if self.roles[0].name == u"superuser":
            return u"超级管理员"
        elif self.roles[0].name == u"manager":
            return u"管理员"

    def jsonify(self):
        return {
            'id' : self.id,
            'loginname' : self.loginname,
            'nickname' : self.nickname,
            'email' : self.email,
            'qq' : self.qq,
            'phone' : self.phone,
            'create_date' : self.create_date,
            'state' : self.state
        }

    def is_authenticated(self):
        return self.state in ('normal', 'unactivated')

    def active(self):
        self.state = 'normal'

    def get_avatar(self, size=70):
        if self.avatar:
            return self.avatar

        if not self.email:
            self.email = 'None'
        URL_PATTERN = "http://www.gravatar.com/avatar/%s?%s"
        gravatar_url = URL_PATTERN % (md5(self.email.lower()).hexdigest(),
                                      urllib.urlencode({'s': str(size)}))
        return gravatar_url

    def set_avatar(self, avatar_url):
        self.avatar = avatar_url

    @staticmethod
    def _hash_password(salt, password):
        hashed = sha256()
        hashed.update("<%s|%s>" % (salt, password))
        return hashed.hexdigest()
