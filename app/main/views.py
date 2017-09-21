import datetime
from flask import redirect, url_for, flash, request, session
from flask import render_template, abort
from flask_login import login_required, current_user

from . import main
from .forms import UVweaverForm, EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..decorators import admin_required
from ..locate_ip_addr import check_ip_location
from ..models import Mylog, User, Post, Permission


@main.before_app_first_request
def before_request():
    '''用户第一次访问网站的时候记录ip,并查询用户所在地'''
    ipaddr = request.remote_addr
    ipinfo = check_ip_location(ipaddr)
    db.session.add(Mylog(time=datetime.datetime.now(), ipaddr=ipaddr, ipinfo=ipinfo))
    # 把ip地址和位置保存到session,免得每次要用的时候都去查询
    session['ipaddr'] = ipaddr
    if ipinfo:
        session['ipinfo'] = ipinfo


@main.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    # Get ipaddress and location about this session.
    ipaddr = session.get('ipaddr')
    ipinfo = session.get('ipinfo')
    # UVweaver功能逻辑
    form = UVweaverForm()
    if form.validate_on_submit():
        try:
            short_url_list = form.short_url_raw.data.split(',')
        except:
            flash('Invalid short_url!')
        else:
            from app.main.wo.uv_weaver import main_async
            main_async(short_url_list, form.count.data)
            flash('已提交任务：短链%s，刷%s个。正在执行...' % (short_url_list, form.count.data))
            pass

        return redirect(url_for('.mainpage'), 302)
    return render_template('mainpage.html', form=form, ipaddr=ipaddr, ipinfo=ipinfo,
                           current_time=datetime.datetime.utcnow())


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', form=form, posts=posts)


@main.route('/testmail/<mailaddr>')
def welcome(mailaddr):
    from flask_mail import Message
    from .. import mail
    msg = Message('这是一封测试邮件Header', recipients=[str(mailaddr)])
    msg.body = '这是一封测试邮件 bodyer'
    msg.html = '这是一封测试邮件 htmler'
    mail.send(msg)
    return 'Hello world!' + mailaddr


@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@main.route('/short_url_querier', methods=['GET', 'POST'])
def short_url_querier():
    '''短链批量查询'''
    from .forms import ShorturlquerierForm
    form = ShorturlquerierForm()

    if form.validate_on_submit():
        from .wo.short_url_querier import shorturl_platform
        shorturl_list = list(form.short_url_list_raw.data.split(','))
        starttime = form.start_date.data
        endtime = form.end_date.data
        platform = shorturl_platform(short_url_list=shorturl_list, starttime=starttime, endtime=endtime)
        results = platform.check()
        return render_template('short_url_querier.html', form=form, results=results)
    # 默认日期
    form.start_date.data = (datetime.date.today() - datetime.timedelta(8)).strftime('%Y%m%d')
    form.end_date.data = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y%m%d')
    return render_template('short_url_querier.html', form=form)


@main.route('/txt')
def text():
    '''下载文件方法  http://gccmx.blog.51cto.com/479381/1733021'''
    from flask import make_response
    content = "long text"
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=myfilename.txt"
    return response


@main.route('/user/<username>')
def user(username):
    '''显示个人资料'''
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''修改个人资料'''
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.real_name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', username=current_user.username))
    form.real_name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    '''管理员修改任意用户资料'''
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role.data = form.role.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been update.')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form)
