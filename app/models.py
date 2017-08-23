from . import db


class Role(db.Model):
    __tablename__='roles'

    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    user=db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>'%self.name


class User(db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))


class Mylog(db.Model):
    __tablename__='mylog'
    id=db.Column(db.Integer,primary_key=True)
    time=db.Column(db.DateTime)
    ipaddr=db.Column(db.String(64))
    ipinfo=db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>'%self.username
