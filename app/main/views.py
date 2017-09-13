import datetime

from flask import redirect,url_for,flash,request
from flask import render_template,abort
from flask_login import login_required,current_user

from . import main
from .forms import UVweaverForm,EditProfileForm
from .. import db
from ..locate_ip_addr import check_ip_location
from ..models import Mylog,User


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

            from app.main.wo.UV_Weaver import main_async
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


@main.route('/testmail/<mailaddr>')
def welcome(mailaddr):
    from flask_mail import Message
    from .. import mail
    msg=Message('这是一封测试邮件Header',recipients=[str(mailaddr)])
    msg.body='这是一封测试邮件 bodyer'
    msg.html='这是一封测试邮件 htmler'
    mail.send(msg)
    return 'Hello world!'+mailaddr


@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@main.route('/short_url_checker',methods=['GET','POST'])
def short_url_checker():
    '''短链批量查询'''
    from .forms import ShorturlcheckForm
    form=ShorturlcheckForm()

    if form.validate_on_submit():
        from .wo.short_url_checker import shorturl_platform
        shorturl_list=list(form.short_url_list_raw.data.split(','))
        starttime=form.start_date.data
        endtime=form.end_date.data

        platform=shorturl_platform(short_url_list=shorturl_list,starttime=starttime,endtime=endtime)
        result=platform.check()
        return render_template('short_url_checker.html',form=form,result=result)
        #todo 学会datatable之后要优化这里的数据展示

    return render_template('short_url_checker.html',form=form)


@main.route('/txt')
def text():
    '''下载文件方法  http://gccmx.blog.51cto.com/479381/1733021'''
    from flask import make_response
    content="long text"
    response=make_response(content)
    response.headers["Content-Disposition"]="attachment; filename=myfilename.txt"
    return response


@main.route('/user/<username>')
def user(username):
    '''显示个人资料'''
    user=User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html',user=user)


@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    '''修改个人资料'''
    form=EditProfileForm()
    if form.validate_on_submit():
        current_user.name=form.real_name.data
        current_user.location=form.location.data
        current_user.about_me=form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('main.user',username=current_user.username))
    form.real_name.data=current_user.name
    form.location.data=current_user.location
    form.about_me.data=current_user.about_me
    return render_template('edit_profile.html',form=form)
