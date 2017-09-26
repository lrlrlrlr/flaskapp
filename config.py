import os

basedir=os.path.abspath(os.path.dirname(__file__))

# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///C:/Users/Administrator/Documents/GitHub/flaskapp/DATA.db'
# app.config['FLASKY_MAIL_SENDER']='Flasky Admin <admin@xinxidawang.com>'


import os

basedir=os.path.abspath(os.path.dirname(__file__))


class Config:
    '''通用config'''
    #防止CSRF
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    SQLALCHEMY_TRACK_MODIFICATIONS=False  # 新版sqlalchemy不加会提示

    MAIL_SERVER='smtp.xinxidawang.xyz'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME') or 'admin@xinxidawang.xyz'
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER='admin@xinxidawang.xyz'
    FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
    FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN') or 'admin@xinxidawang.xyz'
    FLASKY_POSTS_PER_PAGE = os.environ.get('FLASKY_POSTS_PER_PAGE') or 20
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    '''子类config,可单独配置'''
    DEBUG=True

    SQLALCHEMY_DATABASE_URI=os.environ.get('DEV_DATABASE_URL') or\
                            'sqlite:///'+os.path.join(basedir,'data-dev.sqlite')


class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL') or\
                            'sqlite:///'+os.path.join(basedir,'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or\
                            'sqlite:///'+os.path.join(basedir,'data.sqlite')


config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}

'''
如果想调用当前config的某个值：
from flask import current_app
current_app.config['sth']
'''
