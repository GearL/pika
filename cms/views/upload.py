import os

from flask import Blueprint, request, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename

from cms.extentions import rbac
from cms.settings import UPLOAD_FOLDER

upload_app = Blueprint('upload', __name__, url_prefix='/upload')


@upload_app.route('/file', methods=['GET', 'POST'])
@rbac.allow(['superuser', 'manager'], methods=['GET', 'POST'])
@login_required
def upload():
    if 'file' in request.files:
        f = request.files['file']
        fname = secure_filename(f.filename)
        f.save(os.path.join('cms', UPLOAD_FOLDER, fname))
        return jsonify(
            success=True,
            fileurl=os.path.join(UPLOAD_FOLDER, fname)
        )
    else:
        return jsonify(
            success=False
        )