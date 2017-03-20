# coding=utf-8
from flask.ext.wtf import FlaskForm, validators
from wtforms import HiddenField, StringField, IntegerField


class menu(FlaskForm):
    mid = HiddenField()
    mname = StringField(
        validators=[
            validators.DataRequired(),
            validators.length(min=2, max=16)
        ]
    )
    type = IntegerField(
        validators=[
            validators.DataRequired()
        ]
    )
    query_id = IntegerField(
        validators=[
            validators.DataRequired()
        ]
    )
    father_mid = HiddenField()  # 区分二级目录归在哪个一级目录下
    url = StringField(
        validators=[
            validators.DataRequired()
        ]
    )