from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField, ValidationError, TextAreaField, SelectField
from wtforms.validators import data_required, Length, Email, Regexp
from flask_pagedown.fields import PageDownField

from ..models import Role, User


class NameForm(FlaskForm):
    # 网页表格
    name = StringField('What is your name?', validators=[data_required()])
    accept_tos = BooleanField(
        'I accept the TOS',
        validators=[
            data_required()],
        default='checked')
    submit = SubmitField('Submit')


class UVweaverForm(FlaskForm):
    # uvweaver用来填写短链
    short_url_raw = StringField('短链（多个用逗号隔开）', validators=[data_required(), Length(1, 2000)])
    count = IntegerField('每个要刷多少UV（1~20000）', validators=[data_required()])
    submit = SubmitField('Go')

    def validate_count(self, field):
        if field.data >= 1 and field.data <= 20000:
            pass
        else:
            raise ValidationError('范围1~20000')

    def validate_short_url_raw(self, field):
        '''检查短链的格式:空格,长度'''
        if ' ' in field.data:
            raise ValidationError('短链里面有空格,请仔细检查!')
        for short_url in field.data.split(','):
            if type(short_url) == str and len(short_url) != 7:
                raise ValidationError('短链:{}长度不对!长度只能为7!'.format(short_url))


class ShorturlquerierForm(FlaskForm):
    # 批量查询短链
    short_url_list_raw = StringField('短链,多个用逗号分隔（如rUvIrmu,EjuU3q6）', validators=[data_required()])
    start_date = StringField('输入开始日期(如20170901)', validators=[data_required(), Length(8, 8)])
    end_date = StringField('输入结束日期(如20170901)', validators=[data_required(), Length(8, 8)])
    submit = SubmitField('Check')

    def validate_short_url_list_raw(self, field):
        '''检查短链的格式:空格,长度'''
        if ' ' in field.data:
            raise ValidationError('短链里面有空格,请仔细检查!')
        for short_url in field.data.split(','):
            if type(short_url) == str and len(short_url) != 7:
                raise ValidationError('短链:{}长度不对!长度只能为7!'.format(short_url))

    def validate_end_date(self, field):
        '''校验日期:结束日期必须在开始日期之后'''
        if int(field.data) < int(self.start_date.data):
            raise ValidationError('结束日期必须在开始日期之后!')


class EditProfileForm(FlaskForm):
    # 编辑用户资料表单
    real_name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    # 管理员编辑用户资料表单
    email = StringField('Email', validators=[data_required(), Length(1, 64), Email()])
    username = StringField('User name',
                           validators=[data_required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                              'Usernames must have only '
                                                                              'letters, numbers, '
                                                                              'dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    '''发表博文表单'''
    body = PageDownField("What's on your mind?", validators=[data_required()])
    submit = SubmitField('Submit')
