# -*- coding: utf-8 -*-
from datetime import datetime

from cms.models import db


class Menu(db.Model):

    __tablename__ = 'menu'
    CATEGORY_STATE_VALUES=['normal', 'deleted']
    mid = db.Column(db.Integer, primary_key=True)
    mname = db.Column(db.String(16))
    type = db.Column(db.Integer,default=1)  #默认为1，1为一级目录，2为二级目录，不支持更高级目录
    query_id = db.Column(db.Integer,default=0)
    father_mid = db.Column(db.Integer, default=0)  #区分二级目录归在哪个一级目录下
    url = db.Column(db.String(50))
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    state = db.Column(db.Enum(*CATEGORY_STATE_VALUES), default='normal')

    def __str__(self):
        return "%s" % self.mname

    def __repr__(self):
        return "<Category %s>" % self.mname

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()

    def jsonify(self):
        return {
            'mid' : self.mid,
            'mname' : self.mname,
            'type' : self.type,
            'query_id' : self.query_id,
            'father_mid' : self.father_mid,
            'url' : self.url
        }
