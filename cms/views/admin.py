# coding=utf-8
from flask import Blueprint
from flask import Response
from flask import render_template
from flask import request
from flask import url_for
from flask_login import login_required, current_user

from cms.extentions import rbac
from cms.models import db
from cms.models.account import User
from cms.models.log import Log

admin_app = Blueprint('admin', __name__, url_prefix='/cmsadmin')


@admin_app.route("/index", methods=['GET'])
@rbac.allow(['superuser', 'manager'], methods=['GET'])
@login_required
def index():
    return render_template('cmsadmin/index.html')


@admin_app.route("/js/navtab.js", methods=['GET'])
@rbac.allow(['anonymous'], methods=['GET'])
def getnavtabjs():
    image = file("cms/static/js/navtab.js")
    resp = Response(image, mimetype="text/javascript")
    return resp


@admin_app.route("/copyright", methods=['GET'])
@rbac.allow(['superuser'], methods=['GET'])
def copyright():
    Log(
        user_id=current_user.id,
        type='operation',
        level='danger',
        file='none',
        module='admin',
        view_func='copyright',
        method=request.method,
        args='none',
        ip=request.remote_addr
    ).save()
    return render_template('cmsadmin/copyright.html')


@admin_app.route("/log/operation/<int:page>", methods=['GET'])
@rbac.allow(['superuser', 'manager'], methods=['GET'])
def operationlog(page=1):
    if current_user.get_role() == u"超级管理员":
        opagination = Log.query.filter_by(type='operation').order_by(db.desc(Log.id)).paginate(1, 8)
        opage = opagination.pages

        print opage > page
        if opage >= page:
            opagination = Log.query.filter_by(type='operation').order_by(db.desc(Log.id)).paginate(page, 8)
        oposts = opagination.items
        for log in oposts:
            log.username = User.query.filter_by(id=log.user_id).first().loginname
        return render_template('cmsadmin/operation.html', ologs=oposts, opages=opage)
    else:
        logs = Log.query.filter_by(user_id=current_user.get_id())
        allpage = ""
        return render_template('cmsadmin/operation.html', logs=logs, pages=allpage)


@admin_app.route("/log/login/<int:page>", methods=['GET'])
@rbac.allow(['superuser', 'manager'], methods=['GET'])
def loginlog(page=1):
    if current_user.get_role() == u"超级管理员":
        lpagination = Log.query.filter_by(type='login').order_by(db.desc(Log.id)).paginate(1, 8)
        lpage = lpagination.pages
        print lpage > page
        if lpage > page:
            lpagination = Log.query.filter_by(type='login').order_by(db.desc(Log.id)).paginate(page, 8)
        lposts = lpagination.items
        for log in lposts:
            log.username = User.query.filter_by(id=log.user_id).first().loginname
        return render_template('cmsadmin/logininfo.html', llogs=lposts, lpages=lpage)
    else:
        logs = Log.query.filter_by(user_id=current_user.get_id())
        allpage = ""
        return render_template('cmsadmin/logininfo.html', logs=logs, pages=allpage)
