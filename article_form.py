from wtforms import Form, StringField, FileField, TextAreaField, validators
from datetime import *

class createArticle(Form):
    category = StringField('Category', [validators.Length(min=1, max=150), validators.DataRequired()])
    title = StringField('Article Title', [validators.Length(min=1, max=150), validators.DataRequired()])
    image = FileField('Upload Image')
    description = TextAreaField('Description', [validators.DataRequired()])


class comment_sec(Form):
    title = StringField('Username', [validators.Length(min=1, max=150), validators.DataRequired()])
    image = FileField('Profile picture')
    description = TextAreaField('Description', [validators.DataRequired()])


