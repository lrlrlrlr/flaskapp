from threading import Thread

from flask import render_template,current_app
from flask_mail import Message

from . import mail


def send_async_email(app,msg):#异步发送邮件
    with app.app_context():
        mail.send(msg)


def send_mail(to,subject,template,**kwargs):
    app=current_app._get_current_object()#注意这里~~~
    msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,
                recipients=[to])
    msg.body=render_template(template+'.txt',**kwargs)
    msg.html=render_template(template+'.html',**kwargs)
    thr=Thread(target=send_async_email,args=(app,msg,))#异步发送邮件
    thr.start()#异步发送邮件
    return thr#异步发送邮件
