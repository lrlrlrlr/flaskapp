from flask import redirect,request,url_for,flash
from flask import render_template
from flask_login import current_user,login_required
from flask_login import login_user,logout_user

from . import auth
from .forms import LoginForm,RegisterForm,ChangePasswordForm,ResetPasswordRequestForm,ResetPasswordForm
from .. import db
from ..email import send_mail
from ..models import User


@auth.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html',form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register',methods=['GET','POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user=User(email=form.email.data,username=form.username.data,password=form.username.data)
        db.session.add(user)
        db.session.commit()

        token=user.generate_confirmation_token()
        send_mail(user.email,'Confirm Your Account','auth/email/confirm',user=user,token=token)
        flash('A confirmation has been sent to you by email!')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account! Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated\
            and not current_user.confirmed\
            and request.endpoint[:5]!='auth.'\
            and request.endpoint!='static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_mail(current_user.email,'Confirm Your Account','auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
    form=ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password=form.newpassword.data
            flash('Your password has been updated!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password! Please check!')

    return render_template('auth/changepassword.html',form=form)


@auth.route('/reset',methods=['GET','POST'])
def password_reset_request():
    '''请求重设密码界面'''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form=ResetPasswordRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            token=user.generate_reset_token()
            send_mail(form.email.data,'Reset your account','auth/email/reset_password',user=user,token=token,
                      next=request.args.get('next'))
            flash('An email with instructions to reset your password has been sent to you.')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid email!')
    return render_template('auth/reset.html',form=form)


@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
    '''重设密码'''
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form=ResetPasswordForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email!')
            return redirect(url_for('main.index'))
        if user.reset_password(token=token,new_password=form.new_password.data):
            flash('Your password has been reset!')
            return redirect(url_for('auth.login'))
        else:
            flash('Certification has been expired!')
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html',form=form)
