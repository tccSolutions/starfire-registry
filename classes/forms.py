import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, HiddenField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


class AddPostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    created_by = StringField('created_by', validators=[DataRequired()])
    body = CKEditorField('post', validators=[DataRequired()])
    date = datetime.date.today()


class ReplyPost(FlaskForm):
    created_by = StringField('created_by', validators=[DataRequired()])
    body = CKEditorField('post', validators=[DataRequired()])
    date = datetime.date.today()
    post_id = HiddenField('post_id', validators=[DataRequired()])
