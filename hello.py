# coding:utf-8
import datetime
import os
from threading import Thread

from flask import Flask,request,render_template,session,url_for,redirect,flash
from flask_bootstrap import Bootstrap
from flask_mail import Mail,Message
from flask_migrate import MigrateCommand,Migrate
from flask_moment import Moment
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField
from wtforms.validators import data_required

from locate_ip_addr import check_ip_location,check_my_ip

app=Flask(__name__)

app.config['SECRET_KEY']='hard_to_guess_string'  # 防止CSRF
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///C:/Users/Administrator/Documents/GitHub/flaskapp/DATA.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False  # 新版sqlalchemy不加会提示
app.config['MAIL_SERVER']='smtp.xinxidawang.xyz'
app.config['MAIL_PORT']=465
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME') or 'admin@xinxidawang.xyz'
app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER']='admin@xinxidawang.xyz'
app.config['FLASKY_MAIL_SUBJECT_PREFIX']='[Flasky]'
app.config['FLASKY_ADMIN']=os.environ.get('FLASKY_ADMIN') or 'admin@xinxidawang.xyz'
# app.config['FLASKY_MAIL_SENDER']='Flasky Admin <admin@xinxidawang.com>'

db=SQLAlchemy(app)
manager=Manager(app)
bootstrap=Bootstrap(app)
moment=Moment(app)
migrate=Migrate(app,db)
manager.add_command('db',MigrateCommand)
mail=Mail(app)


# todo 下面db.Integer和db.INTEGER能产生相同的效果吗?


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


class NameForm(FlaskForm):
    # 网页表格
    name=StringField('What is your name?',validators=[data_required()])
    accept_tos=BooleanField(
        'I accept the TOS',
        validators=[
            data_required()],
        default='checked')
    submit=SubmitField('Submit')


@app.route('/',methods=['GET','POST'])
def index():  # 首页用来测试新技术
    # FUNCTION ipaddress and ipinfo Save to MYSQLDATABASE
    ipaddr=request.remote_addr
    ipinfo=check_ip_location(ipaddr)
    db.session.add(
        Mylog(
            time=datetime.datetime.now(),
            ipaddr=ipaddr,
            ipinfo=ipinfo))

    # FUNCTION NameForm
    form=NameForm()
    # if commit
    if form.validate_on_submit() and form.accept_tos:
        user=User.query.filter_by(username=form.name.data).first()
        if user is None:
            user=User(username=str(form.name.data))
            db.session.add(user)
            #sendmail if it's a new username(not in database)!
            send_mail(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
        # FUNCTION flash
        if form.name.data!=session.get('name') and session.get('name'):
            flash('It seems you have changed your name!')
        # Session remenber name
        session['name']=form.name.data
        form.name.data=''

        # redirect to avoid pop_up_window when refresh this page
        return redirect(url_for('index'),302)

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        ipaddr=ipaddr,
        ipinfo=ipinfo,
        current_time=datetime.datetime.utcnow())


@app.route('/mainpage',methods=['GET','POST'])
def mainpage():  # 这个用来做积累页面
    if session.get('name')=='ZL':
        return redirect('/ftp')
    form=NameForm()
    if form.validate_on_submit():
        session['name']=form.name.data
        return redirect(url_for('mainpage'),302)
    ipaddr=request.remote_addr
    ipinfo=check_ip_location(ipaddr)
    return render_template(
        'mainpage.html',
        form=form,
        name=session.get('name'),
        ipaddr=ipaddr,
        ipinfo=ipinfo,
        current_time=datetime.datetime.utcnow())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500


@app.route('/ftp')
def ftp():
    if session.get('name')=='ZL':
        ipaddr=check_my_ip()
        return redirect('ftp://zl:12345@%s:21/'%ipaddr)
    else:
        return render_template('500.html')


def send_mail(to,subject,template,**kwargs):
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
                recipients=[to])
    msg.body=render_template(template+'.txt',**kwargs)
    msg.html=render_template(template+'.html',**kwargs)
    thr=Thread(target=send_async_email,args=(app,msg,))#异步发送邮件
    thr.start()#异步发送邮件
    return thr#异步发送邮件


def send_async_email(app,msg):#异步发送邮件
    with app.app_context():
        mail.send(msg)


@app.route('/testmail')
def welcome():
    msg=Message('这是一封测试邮件Header',recipients=['17098903020@163.com'])
    msg.body='这是一封测试邮件 bodyer'
    msg.html='这是一封测试邮件 htmler'
    mail.send(msg)
    return 'Hello world!'


if __name__=='__main__':
    manager.run()
