# -*- coding: utf-8 -*-
import urllib
from datetime import datetime
from hashlib import md5, sha256
from uuid import uuid4

from flask_rbac import RoleMixin, UserMixin
from flask.ext.sqlalchemy import BaseQuery

from cms.models import db


class ModelMixin(object):

    @classmethod
    def paginate(self, page, per_page=20, error_out=True, order_by=None,
                 filters=[], with_deleted=False):
        """A proxy method to return `per_page` items from page `page`.
        If there is `state` attribute in class and `with_deleted` is `False`
        it will filter out which was `state != 'deleted'`.
        If items were not found it will abort with 404.
        Example::
            User(BaseModel):
                id = BaseModel.Column(BaseModel.Integer, primary_key=True)
                name = BaseModel.Column(BaseModel.String(20))
            User.paginate(page=1, per_page=3)
        Returns an :class:`Pagination` object.
        :param page: Page to show.
        :param per_page: Sepcify how many items in a page.
        :param error_out: If `False`, disable abort with 404.
        :param filters: A list that the query wile filter.
        :param with_deleted: If True, it will not filter `state != 'deleted'`
        """
        query = self.query

        if hasattr(self, 'state') and not with_deleted:
            query = query.filter(self.state != 'deleted')

        for filte in filters:
            query = query.filter(filte)

        if not order_by is None:
            query = query.order_by(order_by)

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=error_out
        )

        return pagination

    def save(self, commit=True):
        """Proxy method of saving object to database"""
        db.session.add(self)
        if commit:
            db.session.commit()

    def edit(self, form_data, commit=True):
        """Edit object from `form_data`.
        :param form_data: Data to save in object.
        :param commit: If `commit` is `True`
                       it will commit to database immediately
                       after editing object.
        """
        for key, value in form_data.iteritems():
            setattr(self, key, value)

        db.session.add(self)

        if commit:
            db.session.commit()

    def delete(self, commit=True):
        """Delete object from database.
        :param commit: Commit to database immediately
        """
        if hasattr(self, 'state'):
            self.state = 'deleted'
        else:
            db.session.delete(self)

        if commit:
            db.session.commit()

class UserQuery(BaseQuery):
    def authenticate(self, username, raw_passwd):
        user = self.filter(User.username == username).first()
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
            username = kwargs.pop('username')
            self.username = username.lower()

        if 'passwd' in kwargs:
            raw_passwd = kwargs.pop('passwd')
            self.change_password(raw_passwd)

        if 'nickname' in kwargs:
            nickname = kwargs.pop('nickname')
            self.nickname = nickname.lower()

        db.Model.__init__(self, **kwargs)

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return "<User: %s>" % self.loginname

    def change_password(self, raw_passwd):
        self.salt = uuid4().hex
        self.hashed_password = self._hash_password(self.salt, raw_passwd)

    def check_password(self, raw_passwd):
        _hashed_password = self._hash_password(self.salt, raw_passwd)
        return self.hashed_password == _hashed_password

    def is_active(self):
        return self.state == 'normal'

    def get_id(self):
        return self.id

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

    @staticmethod
    def _hash_password(salt, password):
        hashed = sha256()
        hashed.update("<%s|%s>" % (salt, password))
        return hashed.hexdigest()
