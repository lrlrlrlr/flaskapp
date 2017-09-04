from flask import redirect, request, url_for, flash
from flask import render_template
from flask_login import current_user, login_required
from flask_login import login_user, logout_user

from . import auth
from .forms import LoginForm, RegisterForm, ChangePasswordForm, ResetPasswordRequestForm, ResetPasswordForm,\
    ChangeEmailRequestForm
from .. import db
from ..email import send_mail
from ..models import User

from ..decorators import admin_required,permission_required
from ..models import Permission


@auth.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return 'For administrators!'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''登录界面'''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    '''登出界面'''
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    '''注册界面'''
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.username.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email, 'Confirm Your Account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation has been sent to you by email!')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    '''确认邮箱地址界面'''
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account! Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    '''如果用户已登录+未确认邮箱地址，则强制要求确认地址'''
    if current_user.is_authenticated\
            and not current_user.confirmed\
            and request.endpoint[:5] != 'auth.'\
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    '''未验证邮箱提示界面'''
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    '''重新发送验证邮箱邮件'''
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, 'Confirm Your Account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    '''修改密码界面'''
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.newpassword.data
            flash('Your password has been updated!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password! Please check!')

    return render_template('auth/changepassword.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    '''请求重设密码界面'''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_mail(form.email.data, 'Reset your account', 'auth/email/reset_password', user=user, token=token,
                      next=request.args.get('next'))
            flash('An email with instructions to reset your password has been sent to you.')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid email!')
    return render_template('auth/reset.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    '''重设密码界面'''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email!')
            return redirect(url_for('main.index'))
        if user.reset_password(token=token, new_password=form.new_password.data):
            flash('Your password has been reset!')
            return redirect(url_for('auth.login'))
        else:
            flash('Certification has been expired!')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    '''请求重设邮箱地址界面'''
    form = ChangeEmailRequestForm()

    if form.validate_on_submit():
        token = current_user.generate_email_change_token(form.new_email.data)
        send_mail(form.new_email.data, 'Change Email', 'auth/email/change_email', user=current_user.username,
                  token=token)
        flash('A email has been sent to your new email address!')
        return redirect(url_for('main.index'))

    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    '''重设邮箱地址界面'''
    if current_user.change_email(token):
        flash('Your email has been changed!')
        return redirect(url_for('main.index'))
    else:
        flash('Fail to change your email address, please retry.')
        return redirect(url_for('main.index'))
