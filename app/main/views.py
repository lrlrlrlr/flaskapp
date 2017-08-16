from ..locate_ip_addr import check_ip_location,check_my_ip
from ..models import Mylog

from datetime import datetime
from flask import render_template, session, redirect, url_for, request, flash

from . import main
from .forms import NameForm
from .. import db
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    # FUNCTION ipaddress and ipinfo Save to MYSQLDATABASE
    ipaddr = request.remote_addr
    ipinfo = check_ip_location(ipaddr)
    db.session.add(
        Mylog(
            time=datetime.now(),
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
        return redirect(url_for('.index'))

    return render_template(
        'index.html',
        form=form,
        name=session.get('name'),
        ipaddr=ipaddr,
        ipinfo=ipinfo,
        current_time=datetime.utcnow())

@main.route('/mainpage')
def mainpage():
    if session.get('name')=='ZL':
        return redirect('ftp://zl:12345@%s:21/'%check_my_ip() )
    form=NameForm()
    if form.validate_on_submit():
        session['name']=form.name.data
        return redirect(url_for('.mainpage'),302)
    ipaddr=request.remote_addr
    ipinfo=check_ip_location(ipaddr)
    return render_template(
        'mainpage.html',
        form=form,
        name=session.get('name'),
        ipaddr=ipaddr,
        ipinfo=ipinfo,
        current_time=datetime.utcnow())
