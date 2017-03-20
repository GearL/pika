#-*- coding: utf-8 -*-
# Settings for cmd
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://goldenlau:goldenlau@127.0.0.1:3306/cms'
RBAC_USE_WHITE = True
WTF_CSRF_SECRET_KEY = 'pikacms@author:goldenlau'
SECRET_KEY = 'pikacms@author:goldenlau'
UPLOAD_FOLDER = 'static/Uploads'
