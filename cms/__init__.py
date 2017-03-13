# -*- coding: utf-8 -*-
# !/usr/bin/env python

from flask import Flask
from flask import render_template
from flask_login import LoginManager

from cms import models
from cms.extentions.rbac import setup_rbac
from cms.models import db
from cms.models.account import User
from cms.views import account, menu, article
from cms.views.account import account_app

login_manager = LoginManager()

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


def setup_login_manager(app):
    login_manager.init_app(app)


def setup_database(app):
    db.init_app(app)


def setup_error_pages(app):
    @app.errorhandler(403)
    def page_not_found(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allow(error):
        return render_template('errors/405.html'), 405

app = Flask(__name__)

app.config.from_object('config')

setup_database(app)
setup_login_manager(app)
setup_rbac(app)

setup_error_pages(app)

#app.register_blueprint(master_app)
app.register_blueprint(account_app)
#app.register_blueprint(admin_app)
#app.register_blueprint(course_app)
#app.register_blueprint(resource_app)
#app.register_blueprint(discuss_app)