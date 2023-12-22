from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email

# Complete all validations with inclusion of database

# Signup Form (Base stage)
class BaseSignUpForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired(), Length(min=4, message="Username must be at least 4 characters long")])
    email = StringField("Email", validators=[DataRequired(), Email(granular_message=True, check_deliverability=True)])
    submit = SubmitField("SEND")