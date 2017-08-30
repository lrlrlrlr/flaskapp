from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app



class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin,db.Model):
    #todo 下面db.Interger如果改成db.INTERGER还是一样的吗?
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    confirmed=db.Column(db.Boolean,default=False)

    @property
    def password(self):
        '''拒绝访问明文密码'''
        raise AttributeError('password is not a readabel attribute.')

    @password.setter
    def password(self, password):
        '''生成哈希密码'''
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        '''验证哈希密码'''
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self,expiration=3600):
        '''生成确认token'''
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({
                           'confirm':self.id})

    def confirm(self,token):
        '''确认'''
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return False
        if data.get('confirm')!=self.id:
            return False
        self.confirmed=True
        db.session.add(self)
        return True


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
