# coding:utf-8
import datetime
import time

from flask import Flask, request, render_template, session, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import data_required
from flask_sqlalchemy import SQLAlchemy
from UVweaver import dosth
from locate_ip_addr import check_ip_location, check_my_ip

app = Flask(__name__)


app.config['SECRET_KEY'] = 'hard_to_guess_string'  # 防止CSRF
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1123@192.168.0.99/myflaskapp'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 新版sqlalchemy不加会提示
db = SQLAlchemy(app)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

# todo 下面db.Integer和db.INTEGER能产生相同的效果吗?


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    user = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


class Mylog(db.Model):
    __tablename__ = 'mylog'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    ipaddr = db.Column(db.String(64))
    ipinfo = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    # 网页表格
    name = StringField('What is your name?', validators=[data_required()])
    accept_tos = BooleanField(
        'I accept the TOS',
        validators=[
            data_required()],
        default='checked')
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():  # 首页用来测试新技术
    # FUNCTION ipaddress and ipinfo Save to MYSQLDATABASE
    ipaddr = request.remote_addr
    ipinfo = check_ip_location(ipaddr)
    db.session.add(
        Mylog(
            time=datetime.datetime.now(),
            ipaddr=ipaddr,
            ipinfo=ipinfo))

    # FUNCTION NameForm
    form = NameForm()
    # if commit
    if form.validate_on_submit() and form.accept_tos:
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=str(form.name.data))
            db.session.add(user)

        # FUNCTION flash
        if form.name.data != session.get('name') and session.get('name'):
            flash('It seems you have changed your name!')
        # Session remenber name
        session['name'] = form.name.data
        form.name.data = ''

        # redirect to avoid pop_up_window when refresh this page
        return redirect(url_for('index'), 302)

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        ipaddr=ipaddr,
        ipinfo=ipinfo,
        current_time=datetime.datetime.utcnow())


@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():  # 这个用来做积累页面
    if session.get('name') == 'ZL':
        return redirect('/ftp')
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        return redirect(url_for('mainpage'), 302)
    ipaddr = request.remote_addr
    ipinfo = check_ip_location(ipaddr)
    return render_template(
        'mainpage.html',
        form=form,
        name=session.get('name'),
        ipaddr=ipaddr,
        ipinfo=ipinfo,
        current_time=datetime.datetime.utcnow())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/uv')
def uv_weaver():
    return dosth()


# todo 这里要处理一个比较久的怎么弄？？

@app.route('/ftp')
def ftp():
    if session.get('name') == 'ZL':
        ipaddr = check_my_ip()
        return redirect('ftp://zl:12345@%s:21/' % ipaddr)
    else:
        return render_template('500.html')


if __name__ == '__main__':
    manager.run()
