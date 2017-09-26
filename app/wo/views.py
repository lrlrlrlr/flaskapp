import datetime
from flask import redirect, url_for, flash
from flask import render_template

from app.wo.short_url_querier import shorturl_platform
from app.wo.uv_weaver import main_async
from . import wo
from .forms import ShorturlquerierForm
from .forms import UVweaverForm


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
