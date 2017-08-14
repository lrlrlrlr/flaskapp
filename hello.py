from flask import Flask, request, render_template, session, url_for, redirect, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import data_required

import datetime
from locate_ip_addr import check_ip_location
from UVweaver import dosth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard_to_guess_string'  # 防止CSRF
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
basedir


class NameForm(FlaskForm):
    # 网页表格
    name = StringField('What is your name?', validators=[data_required()])
    accept_tos = BooleanField('I accept the TOS', validators=[data_required()], default='checked')
    submit = SubmitField('Submit')



@app.route('/', methods=['GET', 'POST'])
def index():  # 首页用来测试新技术
    form = NameForm()
    # FUNCTION NameForm
    if form.validate_on_submit() and form.accept_tos:
        # FUNCTION flash
        if form.name.data != session.get('name') and session.get('name'):
            flash('It seems you have changed your name!')
        # Session remenber name
        session['name'] = form.name.data
        form.name.data = ''
        # redirect to avoid pop_up_window when refresh this page
        return redirect(url_for('index'), 302)
    # FUNCTION ipaddress and ipinfo
    ipaddr = request.remote_addr
    ipinfo = check_ip_location(ipaddr)
    
    return render_template('index.html', form=form, name=session.get('name'), ipaddr=ipaddr, ipinfo=ipinfo,
                           current_time=datetime.datetime.utcnow())


@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():  # 这个用来做积累页面
    form = NameForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        return redirect(url_for('mainpage'), 302)
    ipaddr = request.remote_addr
    ipinfo = check_ip_location(ipaddr)
    return render_template('mainpage.html', form=form, name=session.get('name'), ipaddr=ipaddr, ipinfo=ipinfo,
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

if __name__ == '__main__':
    manager.run()
