# coding=utf-8
from flask import redirect, url_for, Blueprint, jsonify
from flask import render_template
from flask import request

from cms.extentions.rbac import rbac
from cms.forms.account import SignInForm, SignUpForm
from flask_login import login_user, current_user, logout_user, login_required

from cms.models.account import User, Role

account_app = Blueprint('account', __name__, url_prefix='/cmsadmin')


@account_app.route("/signin", methods=['GET', 'POST'])
@rbac.allow(['anonymous'], ['GET', 'POST'])
def signin():
    #if not current_user.is_anonymous():
        #return redirect(url_for('index'))

    form = SignUpForm()

    if form.validate_on_submit():
        loginname = request.form['loginname'].strip()
        passwd = request.form['passwd'].strip()
        is_remember = request.form['remember'].strip()
        user = User.query.authenticate(loginname,passwd)

        if user:
            login_user(user, remember=is_remember, force=True)
            return jsonify(
                success=True,
                redirect_url = url_for('index')
            )
        else:
            return jsonify(
                success = False,
                messages = "用户名或密码错误，请重新登陆"
            )

    if form.errors:
        return jsonify(success=False, errors=True, messages=form.errors)

    return render_template('admin/login.html', form=form)



@account_app.route("/signup", methods=['GET', 'POST'])
def signup():
    pass


@account_app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@account_app.route("/index", methods=['GET'])
@login_required
@rbac.allow(['superuser', 'manager'], methods=['GET'])
def index():
    return render_template('admin/index.html')
