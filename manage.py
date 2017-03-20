# -*- coding: utf-8 -*-
#!/usr/bin/env python

from flask.ext.script import Manager, Server

from cms.app import create_app
from cms.extentions import db

application = create_app('cms')
manager = Manager(application)
manager.add_command("runserver",
        Server(host="127.0.0.1", port=5000, use_debugger=application.config['DEBUG']))

@manager.shell
def make_shell_context():
    """Create a python CLI.

    return: Default import object
    type: `Dict`
    """
    return dict(app=application,
                db=db)


if __name__ == '__main__':
    manager.run()