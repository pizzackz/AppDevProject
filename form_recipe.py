from wtforms import Form, StringField, FileField, TextAreaField
from wtforms.validators import DataRequired, Length

class CreateRecipeForm(Form):
    name = StringField("Name", validators=[DataRequired(), Length(max=255)], render_kw={"class": "form-control"})
    ingredients = StringField("Ingredients", validators=[DataRequired()], render_kw={"class": "form-control"})
    instructions = TextAreaField("Instructions", validators=[DataRequired()], render_kw={"class": "form-control"})
    picture = FileField("Picture", render_kw={"class": "form-control", "accept": "image/*"})