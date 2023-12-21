from wtforms import Form, StringField, EmailField, PasswordField, validators

# Login form
class Login(Form):
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])


# Signup form
class Signup(Form):
    first_name = StringField("First Name", [validators.DataRequired()])
    last_name = StringField("Last Name", [validators.DataRequired()])
    email = EmailField("Email", [validators.DataRequired()])
    username = StringField("Username", [validators.DataRequired()])