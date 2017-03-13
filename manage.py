# -*- coding: utf-8 -*-
#!/usr/bin/env python

from flask.ext.script import Manager, Server
from cms import models, app

manager = Manager(app)
manager.add_command("runserver",
        Server(host="127.0.0.1", port=5000, use_debugger=app.config['DEBUG']))

@manager.shell
def make_shell_context():
    """Create a python CLI.

    return: Default import object
    type: `Dict`
    """
    return dict(app=app,
                db=models.db)


if __name__ == '__main__':
    manager.run()