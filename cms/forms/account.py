# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField
from wtforms import validators


class SignInForm(Form):
    loginname = StringField(
        label='loginname',
        description='6~30 characters',
        validators=[
            validators.InputRequired(),
            validators.length(min=4, max=16)
        ]
    )
    passwd = StringField(
        label='passwd',
        description='6~30 characters',
        validators=[
            validators.InputRequired(),
            validators.length(min=6, max=16)
         ]
    )
    remember = BooleanField('remember me')

class SignUpForm(Form):
    loginname = StringField('loginname', [validators.length(min=4, max=16)])
    nickname = StringField('nickname', [validators.length(min=4, max=24)])
    passwd = PasswordField('passwd', [validators.DataRequired(), validators.length(min=6, max=16)])
    confirm_passwd = PasswordField('confirm_passwd', [validators.DataRequired(), validators.length(min=6, max=16)])
