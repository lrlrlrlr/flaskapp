from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField
from wtforms.validators import data_required


class NameForm(FlaskForm):
    # 网页表格
    name=StringField('What is your name?',validators=[data_required()])
    accept_tos=BooleanField(
        'I accept the TOS',
        validators=[
            data_required()],
        default='checked')
    submit=SubmitField('Submit')
