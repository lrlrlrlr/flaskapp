from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import hashlib
from flask import request

from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User'         :(Permission.FOLLOW |
                             Permission.COMMENT |
                             Permission.WRITE_ARTICLES, True),
            'Moderator'    :(Permission.FOLLOW |
                             Permission.COMMENT |
                             Permission.WRITE_ARTICLES |
                             Permission.MODERATE_COMMENTS, False),
            'Administrator':(0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    #todo 下面db.Interger如果改成db.INTERGER还是一样的吗?
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        '''9.2: 定义默认的用户角色'''
        super(User, self).__init__(**kwargs)#todo 这句super什么意思???
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        '''拒绝访问明文密码'''
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        '''生成哈希密码'''
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        '''验证哈希密码'''
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        '''生成确认token'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'confirm':self.id})

    def confirm(self, token):
        '''校验确认token'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        '''生成重置密码token'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'reset':self.id})

    def reset_password(self, token, new_password):
        '''校验重置密码token'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        '''生成重置邮箱token'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'change_email':self.id,
            'new_email'   :new_email})

    def change_email(self, token):
        '''校验重置邮箱token'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        '''9.3: 角色验证'''
        return self.role is not None and\
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        '''9.3: 角色验证'''
        return self.can(Permission.ADMINISTER)

    def ping(self):
        '''10.1: 刷新用户最后访问时间'''
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url='https://secure.gravatar.com/avatar'
        else:
            url='http://www.gravatar.com/avatar'
        hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,
                                                                     rating=rating)


    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    '''9.3: 角色验证'''

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Mylog(db.Model):
    __tablename__ = 'mylog'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    ipaddr = db.Column(db.String(64))
    ipinfo = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
