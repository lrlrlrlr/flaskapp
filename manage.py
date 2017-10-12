#!/usr/bin/env python3
# coding:utf-8

import os

from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager, Shell

from app import create_app, db
from app.models import User, Role, Mylog, Post, Longurl, UrlCounter

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)


# 自动导入那个啥,每次调试的时候省的手动输入from xx import db这样的命令了
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Mylog=Mylog, Post=Post, Longurl=Longurl, UrlCounter=UrlCounter)


manager.add_command('shell', Shell(make_context=make_shell_context))

# 导入db命令
manager.add_command('db', MigrateCommand)


# 导入unittest命令
@manager.command
def test():
    '''run the unit tests.'''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
