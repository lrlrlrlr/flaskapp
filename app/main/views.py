import datetime

from flask import render_template
from flask import session,redirect,url_for,flash,request,current_app

from . import main
from .forms import UVweaverForm
from .. import db
from ..email import send_mail
from ..locate_ip_addr import check_ip_location
from ..models import Mylog,User

from flask_login import login_required

@main.route('/mainpage',methods=['GET','POST'])
def mainpage():
    # FUNCTION ipaddress and ipinfo Save to MYSQLDATABASE
    ipaddr=request.remote_addr
    ipinfo=check_ip_location(ipaddr)
    db.session.add(
        Mylog(
            time=datetime.datetime.now(),
            ipaddr=ipaddr,
            ipinfo=ipinfo))

    # FUNCTION NameForm
    form=UVweaverForm()
    # if commit
    if form.validate_on_submit():
            # redirect to avoid pop_up_window when refresh this page
            try:
                short_url_list=form.short_url_raw.data.split(',')
            except:
                flash('Invalid short_url!')
            else:
                #do something....

                from .UV_Weaver import main_async
                main_async(short_url_list,form.count.data)
                flash('已提交任务：短链%s，刷%s个。正在执行...'%(short_url_list,form.count.data))
                pass


            return redirect(url_for('.mainpage'),302)
    return render_template('mainpage.html',form=form,ipaddr=ipaddr,ipinfo=ipinfo,
                           current_time=datetime.datetime.utcnow())


@main.route('/',methods=['GET','POST'])
def index():  # 首页用来测试新技术
    ipaddr=request.remote_addr
    ipinfo=check_ip_location(ipaddr)
    db.session.add(Mylog(time=datetime.datetime.now(),ipaddr=ipaddr,ipinfo=ipinfo))
    return render_template('index.html')


@main.route('/testmail')
def welcome():
    from flask_mail import Message
    from .. import mail
    msg=Message('这是一封测试邮件Header',recipients=['17098903020@163.com'])
    msg.body='这是一封测试邮件 bodyer'
    msg.html='这是一封测试邮件 htmler'
    mail.send(msg)
    return 'Hello world!'


@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'

