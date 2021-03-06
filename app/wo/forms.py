from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, ValidationError
from wtforms.validators import data_required, Length, url


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


class LongurlForm(FlaskForm):
    # 用户输入长链接,用于生成短链接,或者用于查询短链的点击效果
    long_url = StringField('请输入长链接(如http://www.qq.com)', validators=[data_required(), url()])
    submit = SubmitField('生成/查询')

    def validate_long_url(self, field):
        '''
        这里涉及到url这个validator的bug:添加长链接的时候,链接末端加入空格无法判断出来。
        e.g.： 在long_url表单里填写"http://wotvnews.17wo.cn/wovideo/video/first?groupId=1502435723099&resourceId=44  ",后面有空格也不会报错
        '''
        if field.data[-1].isspace():
            raise ValidationError('链接末端不能是空格!')
