from flask import Blueprint
from flask import render_template
from flask.ext.login import login_required

from cms.extentions import rbac
from cms.models.menu import Menu

menu_app = Blueprint('menu', __name__, url_prefix='/menu')


@menu_app.route("list", methods=['GET'])
@rbac.allow(['superuser', 'manager'], ['GET'])
@login_required
def menulist():
    first_menu = Menu.query.filter_by(type=1).order_by('query_id')
    menu_list = {}
    menu_first_list = {}
    for menu in first_menu:
        menu_json = menu.jsonify()
        second_menu = Menu.query.filter_by(type=2).order_by('query_id')
        menu_json['second_menu'] = second_menu
        menu_first_list[menu_json.query_id] = menu_json
    return render_template('cmsadmin/menu/menu.html')
