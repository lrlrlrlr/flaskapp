import datetime

from flask import render_template
from flask import session,redirect,url_for,flash,request,current_app

from . import main
from .forms import NameForm
from .. import db
from ..email import send_mail
from ..locate_ip_addr import check_ip_location
from ..models import Mylog,User


# @main.route('/',methods=['GET','POST'])
# def index():
#     form=NameForm()
#     if form.validate_on_submit():
#         # ...
#         session['name']=form.name.data
#         return redirect(url_for('.index'))
#     return render_template('index.html',
#                            form=form,name=session.get('name'),
#                            known=session.get('known',False),
#                            current_time=datetime.datetime.utcnow())

#todo 这下面还要改~~~~~~~~~~~~~
@main.route('/',methods=['GET','POST'])
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
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.name.data).first()
        if user is None:
            user=User(username=str(form.name.data))
            db.session.add(user)
            #sendmail if it's a new username(not in database)!
            send_mail(current_app.config['FLASK_ADMIN'],'New User','mail/new_user',
                      user=user)#todo 这第一个参数要改成类似app.config['FLASKY_ADMIN']
            # FUNCTION flash
        if form.name.data!=session.get('name'):
            flash('It seems you have changed your name!')
            # Session remenber name
            session['name']=form.name.data
            form.name.data=''

            # redirect to avoid pop_up_window when refresh this page
            return redirect(url_for('.index'),302)
    return render_template('index.html',form=form,name=session.get('name'),ipaddr=ipaddr,ipinfo=ipinfo,
                           current_time=datetime.datetime.utcnow())

    #
    # @main.route('/mainpage',methods=['GET','POST'])
    # def mainpage():  # 这个用来做积累页面
    #     if session.get('name')=='ZL':
    #         return redirect('/ftp')
    #     form=NameForm()
    #     if form.validate_on_submit():
    #         session['name']=form.name.data
    #         return redirect(url_for('.mainpage'),302)
    #     ipaddr=request.remote_addr
    #     ipinfo=check_ip_location(ipaddr)
    #     return render_template(
    #         'mainpage.html',
    #         form=form,
    #         name=session.get('name'),
    #         ipaddr=ipaddr,
    #         ipinfo=ipinfo,
    #         current_time=datetime.datetime.utcnow())
    #
    #
    # @main.route('/ftp')
    # def ftp():
    #     if session.get('name')=='ZL':
    #         ipaddr=check_my_ip()
    #         return redirect('ftp://zl:12345@%s:21/'%ipaddr)
    #     else:
    #         return render_template('500.html')
    #


@main.route('/testmail')
def welcome():
    from flask_mail import Message
    from .. import mail
    msg=Message('这是一封测试邮件Header',recipients=['17098903020@163.com'])
    msg.body='这是一封测试邮件 bodyer'
    msg.html='这是一封测试邮件 htmler'
    mail.send(msg)
    return 'Hello world!'
