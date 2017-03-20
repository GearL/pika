from flask import Blueprint
from flask import render_template

from cms.extentions import rbac
from cms.models.article import Article

article_app = Blueprint('article', __name__, url_prefix='/article')


@article_app.route('/<string:category>/list', methods=['GET'])
@rbac.allow(['anonymous'], methods=['GET'])
def alllist(category):
    articles = Article.query.all()
    return render_template('articles/list.html', articles=articles)


@article_app.route('/mlist', methods=['GET'])
@rbac.allow(['superuser', 'manager'], methods=['GET'])
def adminlist():
    articles = Article.query.all()
    return render_template('articles/mlist.html', articles=articles)


@article_app.route('/category', methods=['GET'])
@rbac.allow(['superuser', 'manager'], methods=['GET'])
def category():
    articles = Article.query.all()
    return render_template('articles/mlist.html', articles=articles)

