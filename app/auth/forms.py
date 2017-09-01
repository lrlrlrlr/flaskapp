from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo
from flask_login import current_user
from ..models import User

'''
wtforms.validator里面都是用于判断文本输入框的内容..
Length(a,b) 限制输入框文本长度
Email() 限制输入框只能输入email
Regexp 正则..
EqualTo(target,message=..) 用于校验两个输入框内容是否相同

'''


class LoginForm(FlaskForm):
    '''登录表单'''
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember_me=BooleanField('Keep me logged in')
    submit=SubmitField('Log In')


class RegisterForm(FlaskForm):
    '''注册表单'''
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username=StringField('Username',validators=[DataRequired(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                                                                   'Usernames must have only letters, '
                                                                                   'numbers, dots or underscores')])
    password=PasswordField('Password',validators=[DataRequired(),EqualTo('password2',message='Passwords must match.')])
    password2=PasswordField('Confirm Password',validators=[DataRequired()])
    submit=SubmitField('Register')

    def validate_email(self,field):
        '''自定义验证函数,确保email不重复'''
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self,field):
        '''自定义验证函数,确保username不重复'''
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ChangePasswordForm(FlaskForm):
    '''改密码表单'''
    old_password=PasswordField('Your Old Password',validators=[DataRequired()])
    newpassword=PasswordField('Input Your New Password',
                              validators=[DataRequired(),EqualTo('newpassword2',message='Passwords must match.')])
    newpassword2=PasswordField('Confirm Your New Password',validators=[DataRequired()])
    submit=SubmitField('Update Password')
    #
    # def validate_old_password(self,field):
    #     '''验证旧密码'''
    #     if current_user.verify_password(field.data) is False:
    #         raise ValidationError('Old password invalid.')


class ResetPasswordRequestForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    submit=SubmitField('Reset Password')


class ResetPasswordForm(FlaskForm):
    email=StringField('Input Your Email',validators=[DataRequired(),Length(1,64),Email()])
    new_password=PasswordField('Input Your New Password',
                               validators=[DataRequired(),EqualTo('new_password2',message='Passwords must match.')])
    new_password2=PasswordField('Confirm Your New Password',validators=[DataRequired()])
    submit=SubmitField('Reset Password')
