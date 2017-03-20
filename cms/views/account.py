# coding=utf-8
from flask import redirect, url_for, Blueprint, jsonify
from flask import render_template
from flask import request

from cms.extentions.rbac import rbac
from cms.forms.account import SignInForm, SignUpForm, ChangePasswdForm, \
                              ReSetPasswdForm, DetailForm
from flask_login import login_user, current_user, logout_user, \
                        login_required

from cms.models.account import User, Role
from cms.models.log import Log

account_app = Blueprint('account', __name__, url_prefix='/account')


def checkloginname(loginname):
    if User.query.filter_by(loginname=loginname).first():
        return jsonify(
            success=False,
            message="用户已存在"
        )
    return "ok"


def is_ajax(req):
    return not req.headers.get('X-Requested-With') is None





@account_app.route("/signin", methods=['GET', 'POST'])
@rbac.allow(['anonymous'], ['GET', 'POST'])
def signin():
    if not current_user.is_anonymous():
        return redirect(url_for('admin.index'))

    form = SignInForm()

    if form.validate_on_submit():
        loginname = request.form['loginname'].strip()
        passwd = request.form['passwd'].strip()
        is_remember = False
        if 'remember' in request.form:
            is_remember = request.form['remember']
        user = User.query.authenticate(loginname, passwd)
        print request.remote_addr
        if user:
            if not user.is_active():
                Log(
                    user_id=user.get_id(),
                    module='account',
                    view_func='signin',
                    method=request.method,
                    args="%s sign in failed" % user.loginname,
                    ip=request.remote_addr,
                ).save()
                return jsonify(
                    success=False,
                    messages="用户已被暂停使用,请联系管理员"
                )
            login_user(user, remember=is_remember, force=True)
            Log(
                user_id=user.get_id(),
                type='login',
                level='normal',
                module='account',
                view_func='signin',
                method=request.method,
                args="%s sign in success" % user.loginname,
                ip=request.remote_addr,
            ).save()
            return jsonify(
                success=True,
                message="登录成功",
                redirect_url=url_for('admin.index')
            )
        else:
            user = User.query.filter_by(loginname=loginname).first()
            if user:
                Log(
                    user_id=user.get_id(),
                    type='login',
                    level='warn',
                    module='account',
                    view_func='signin',
                    method=request.method,
                    args="%s sign in failded" % loginname,
                    ip=request.remote_addr,
                ).save()
            return jsonify(
                success=False,
                messages="用户名或密码错误，请重新登陆"
            )

    if form.errors:
        return jsonify(success=False, errors=True, messages=form.errors)

    return render_template('cmsadmin/account/login.html', form=form)


@account_app.route("/signup", methods=['GET', 'POST'])
@rbac.allow(['anonymous'], ['GET', 'POST'])
def signup():
    if not current_user.is_anonymous():
        return redirect(url_for('admin.index'))

    form = SignUpForm()

    if form.validate_on_submit():
        loginname = request.form['loginname'].strip()
        passwd = request.form['passwd'].strip()
        nickname = request.form['nickname']

        if not checkloginname(loginname) == "ok":
            return checkloginname(loginname)

        anonymous = Role.query.filter_by(name='anonymous').first()

        user = User(
            loginname=loginname,
            nickname=nickname,
            passwd=passwd
        )
        user.roles.append(anonymous)

        user.save()
        return jsonify(
            success=True,
            messages='注册成功',
            redirect_url=url_for('admin.index')
        )

    if form.errors:
        return jsonify(
            success=False,
            errors=True,
            messages=form.errors
        )
    return render_template('cmsadmin/account/signup.html', form=form)


@account_app.route("/logout", methods=['GET'])
@rbac.allow(['anonymous'], ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.signin'))


@account_app.route("/list", methods=['GET'])
@rbac.allow(['superuser'], methods=['GET'])
@login_required
def account_list():
    userall = User.query.all()

    Log(
        user_id=current_user.get_id(),
        type='operation',
        level='normal',
        module='account',
        view_func='account_detail',
        method=request.method,
        args='none',
        ip=request.remote_addr,
    ).save()

    if userall:
        user_all = {}
        for user in userall:
            userjson = user.jsonify()
            user_all[user.get_id()] = userjson
        return render_template('cmsadmin/account/list.html', users=user_all)


@account_app.route("/detail", methods=['GET', 'POST'])
@rbac.allow(['superuser', 'manager'], methods=['GET', 'POST'])
@login_required
def account_detail():
    form = DetailForm()
    args = ''
    print request
    for a in request.form:
        args += a+'='+request.form[a]+" "

    Log(
        user_id=current_user.get_id(),
        type='operation',
        level='normal',
        module='account',
        view_func='account_detail',
        method=request.method,
        args=args,
        ip=request.remote_addr,
    ).save()

    if request.method == "GET":
        userjson = current_user.jsonify()
        userjson['role_name'] = current_user.get_role()
        return render_template(
            'cmsadmin/account/personInfo.html',
            detail=userjson,
            form=form
        )
    elif request.method == "POST":
        if 'phone' in request.form:
            phone = request.form['phone']
            current_user.phone = phone
        if 'qq' in request.form:
            qq = request.form['qq']
            current_user.qq = qq
        if 'email' in request.form:
            email = request.form['email']
            current_user.email = email
        current_user.save()
        return jsonify(
            success=True
        )



@account_app.route("/addmanager/<int:id>", methods=['GET'])
@rbac.allow(['superuser'], methods=['GET'])
@login_required
def add_manager(id):
    user = User.query.filter_by(id=id).first()
    if user:
        manager = Role.query.filter_by(name='manager').first()
        user.roles.append(manager)
        user.save()
        return jsonify(
            success=True
        )
    return jsonify(
        success=False,
        message="用户不存在"
    )


@account_app.route("/delete/<int:id>", methods=['GET'])
@rbac.allow(['superuser'], methods=['GET'])
@login_required
def deleteuser(id):
    user = User.query.filter_by(id=id).first()
    if user:
        user.state = "deleted"
        user.save()
        return jsonify(
            success=True
        )
    return jsonify(
        success=False,
        message="用户不存在"
    )


@account_app.route("/reactive/<int:id>", methods=['GET'])
@rbac.allow(['superuser'], methods=['GET'])
@login_required
def reactive(id):
    user = User.query.filter_by(id=id).first()
    if user:
        user.active()
        user.save()
        return jsonify(
            success=True
        )
    return jsonify(
        success=False,
        message="用户不存在"
    )


@account_app.route("/passwd", methods=['GET', 'POST'])
@rbac.allow(['superuser', 'manager'], methods=['GET', 'POST'])
@login_required
def changepasswd():
    user = current_user
    form = ChangePasswdForm()

    if form.validate_on_submit():
        passwd = request.form['passwd'].strip()
        newpasswd = request.form['newpasswd'].strip()
        if user.check_password(passwd):
            user.change_password(newpasswd)
            user.save()
            return jsonify(
                success=True,
                message="修改密码成功，请重新登陆",
                redirect_url=url_for('account.logout')
            )
        return jsonify(
            success=False,
            message="原密码不正确，请重新输入"
        )
    if form.errors:

        return jsonify(
            success=False,
            errors=True,
            message=form.errors
        )
    return render_template('cmsadmin/account/changepwd.html', form=form)


@account_app.route("/resetpasswd", methods=['GET', 'POST'])
@rbac.allow(['superuser', 'manager'], methods=['GET', 'POST'])
@login_required
def resetpasswd():
    user = current_user
    form = ReSetPasswdForm()

    if form.validate_on_submit():
        email = request.form['email'].strip()
        newpasswd = request.form['newpasswd'].strip()
        if user.has_email():
            if user.check_email(email):
                user.change_password(newpasswd)
                user.save()
                return jsonify(
                    success=True,
                    message="修改密码成功，请重新登陆",
                    redirect_url=url_for('account.logout')
                )
            return jsonify(
                success=False,
                message="邮箱不正确，请重新输入"
            )
        else:
            return jsonify(
                success=False,
                message="邮箱未设置，请联系超级管理员重置密码"
            )
    if form.errors:
        return jsonify(
            success=False,
            errors=True,
            message=form.errors
        )
    return render_template('cmsadmin/account/resetpasswd.html', form=form)


@account_app.route("/resetpasswd/<int:id>", methods=['POST'])
@rbac.allow(['superuser'], methods=['POST'])
@login_required
def resetpwd(id):
    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify(
            success=False,
            message="没有这个用户"
        )
    newpasswd = request.form['newpasswd'].strip()

    user.change_password(newpasswd)
    user.save()
    return jsonify(
        success=True,
        message="修改密码成功"
    )


@account_app.route("/setavatar", methods=['POST'])
@rbac.allow(['superuser', 'manager'], methods=['POST'])
@login_required
def setavatar():
    user = current_user
    newavatar = request.form.get('newavatar',user.get_avatar())
    print newavatar
    user.set_avatar(newavatar)
    user.save()
    return jsonify(
        success=True,
        message="修改成功"
    )

