from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField,IntegerField,ValidationError,TextAreaField
from wtforms.validators import data_required,Length


class NameForm(FlaskForm):
    # 网页表格
    name=StringField('What is your name?',validators=[data_required()])
    accept_tos=BooleanField(
        'I accept the TOS',
        validators=[
            data_required()],
        default='checked')
    submit=SubmitField('Submit')


class UVweaverForm(FlaskForm):
    #uvweaver用来填写短链
    short_url_raw=StringField('短链（多个用逗号隔开）',validators=[data_required(),Length(1,2000)])
    count=IntegerField('每个要刷多少UV（1~20000）',validators=[data_required()])
    submit=SubmitField('Go')

    def validate_count(self,field):
        if field.data>=1 and field.data<=20000:
            pass
        else:
            raise ValidationError('范围1~20000')


class ShorturlcheckForm(FlaskForm):
    #批量查询短链
    short_url_list_raw = StringField('短链,多个用逗号分隔（如rUvIrmu,EjuU3q6）', validators=[data_required()])
    start_date=StringField('输入开始日期(如20170101)',validators=[data_required()])
    end_date=StringField('输入开始日期(如20170101)',validators=[data_required()])
    submit=SubmitField('Check')


class EditProfileForm(FlaskForm):
    #编辑用户资料表单
    real_name=StringField('Real name',validators=[Length(0,64)])
    location=StringField('Location',validators=[Length(0,64)])
    about_me=TextAreaField('About me')
    submit=SubmitField('Submit')
