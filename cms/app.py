# -*- coding: utf-8 -*-
# !/usr/bin/env python
from flask import Flask
from flask import render_template

from cms.extentions import setup_database
from cms.extentions import setup_login_manager
from cms.extentions import setup_rbac
from cms.views.account import account_app
from cms.views.admin import admin_app
from cms.views.article import article_app
from cms.views.upload import upload_app


def create_app(import_name=None, config=None):
    app = Flask(import_name or __name__)

    app.config.from_object('cms.settings')

    if isinstance(config, dict):
        app.config.update(config)
    elif config:
        app.config.from_pyfile(os.path.abspath(config))

    if app.config.get('SENTRY_ON', False):
        from raven.contrib.flask import Sentry
        sentry = Sentry(app)

    setup_database(app)
    setup_login_manager(app)
    setup_rbac(app)

    setup_error_pages(app)

    app.register_blueprint(article_app)
    app.register_blueprint(account_app)
    app.register_blueprint(admin_app)
    app.register_blueprint(upload_app)
    #app.register_blueprint(resource_app)
    #app.register_blueprint(discuss_app)

    return app


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
