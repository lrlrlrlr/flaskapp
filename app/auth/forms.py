from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo

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
