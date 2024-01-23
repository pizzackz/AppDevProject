from wtforms import Form, StringField, FileField, TextAreaField, validators, DecimalField, ValidationError

class createMenu(Form):
    name = StringField('Name Of Dish', [validators.Length(min=1, max=150), validators.DataRequired()])
    description = TextAreaField('Description', [validators.DataRequired()])
    price = DecimalField('Price', [validators.DataRequired()])
    image = FileField('Upload Image')