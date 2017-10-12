import datetime

from flask import redirect, url_for, flash, abort, request
from flask import render_template

from app.wo.short_url_querier import shorturl_platform
from app.wo.uv_weaver import main_async
from . import wo
from .forms import ShorturlquerierForm, UVweaverForm, LongurlForm
from .sina_short_url import SinaShortUrl
from .. import db
from ..models import Longurl, UrlCounter


@wo.route('/short_url_querier', methods=['GET', 'POST'])
def short_url_querier():
    '''短链批量查询'''
    form = ShorturlquerierForm()

    if form.validate_on_submit():
        shorturl_list = list(form.short_url_list_raw.data.split(','))
        starttime = form.start_date.data
        endtime = form.end_date.data
        platform = shorturl_platform(short_url_list=shorturl_list, starttime=starttime, endtime=endtime)
        results = platform.check()
        return render_template('wo/short_url_querier.html', form=form, results=results)
    # 默认日期
    form.start_date.data = (datetime.date.today() - datetime.timedelta(8)).strftime('%Y%m%d')
    form.end_date.data = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y%m%d')
    return render_template('wo/short_url_querier.html', form=form)


@wo.route('/uv_weaver', methods=['GET', 'POST'])
def uv_weaver():
    # UVweaver功能逻辑
    form = UVweaverForm()
    if form.validate_on_submit():
        try:
            short_url_list = form.short_url_raw.data.split(',')
        except:
            flash('Invalid short_url!')
        else:
            main_async(short_url_list, form.count.data)
            flash('已提交任务：短链%s，刷%s个。正在执行...' % (short_url_list, form.count.data))
            pass

        return redirect(url_for('wo.uv_weaver'), 302)
    return render_template('wo/uv_weaver.html', form=form)


@wo.route('/long_url/<id>')
def url_redirect(id):
    longurl = Longurl.query.filter_by(id=id).first()

    if longurl:
        ipaddr = request.remote_addr
        ua = request.headers.get('User-Agent')
        db.session.add(UrlCounter(time=datetime.datetime.now(), url=longurl.url, ipaddr=ipaddr, ua=ua))
        return redirect(longurl.url)
    else:
        return abort(404)


@wo.route('/short_url_generator', methods=['GET', 'POST'])
def short_url_generator():
    form = LongurlForm()
    if form.validate_on_submit():
        # 先看看数据库里是否有该url
        url_exist = Longurl.query.filter_by(url=form.long_url.data).first()
        if url_exist:
            # TODO 这里要判断是否生成了短链,如果没生成,则生成
            flash('该长链已生成短链:{}'.format(url_exist.short_url))
            redirect(url_for('wo.short_url_generator'))
        # 如果没有重复数据则开始生成短链

        # 这里要先保存提交,以生成id--链接
        db.session.add(Longurl(url=form.long_url.data))
        db.session.commit()
        id = Longurl.query.filter_by(url=form.long_url.data).first().id

        sina = SinaShortUrl()
        result = sina.generator('http://xinxidawang.xyz/wo/long_url/{}'.format(id))
        if result:
            short_url = result

            # 保存
            db.session.add(Longurl(url=form.long_url.data, short_url=short_url))
            db.session.commit()

            flash('成功!短链:{}'.format(short_url))
        redirect(url_for('wo.short_url_generator'))

    # TODO 这里结果的呈现还没实现
    results = None
    # results=Longurl.query.order_by(Longurl.id).all()
    return render_template('wo/short_url_generator.html', form=form, results=results)
