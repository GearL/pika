from datetime import datetime

from cms.models import db, ModelMixin


class Log(ModelMixin, db.Model):
    TYPE_TEXT = ('login', 'operation')
    LEVEL = ('danger', 'warn', 'normal')
    type = db.Column(db.Enum(*TYPE_TEXT))
    level = db.Column(db.Enum(*LEVEL))
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DATETIME, default=datetime.now())
    file = db.Column(db.String(250), default='none')
    module = db.Column(db.String(50))
    view_func = db.Column(db.String(50))
    method = db.Column(db.String(6))
    args = db.Column(db.String(250))
    ip = db.Column(db.String(30))
    user = db.relationship('User', backref=db.backref('logs', lazy='dynamic'),
                           uselist=False)