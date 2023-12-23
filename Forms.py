from wtforms import Form, StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, Email
import shelve

# Custom validator functions
# Password complexity validator
def password_complexity(form, field):
    password = field.data
    error_list = []
    
    if len(password) < 8:
        error_list.append("Password must be at least 8 characters long")

    if not any(char.islower() for char in password):
        error_list.append("Password must contain at least one lowercase letter")

    if not any(char.isupper() for char in password):
        error_list.append("Password must contain at least one uppercase letter")

    if not any(char in "!@#$%^&*()_+-=[]{}|;':\",.<>/?" for char in password):
        error_list.append("Password must contain at least one symbol")

    if error_list:
        raise ValidationError("; ".join(error_list))


# Unique username validator
def unique_username(form, field):
    username = field.data
    customers_dict = {}
    usernames_list = []

    # Retrieve data in shelve db
    try:
        db = shelve.open("customer.db", "c")

        try:
            customers_dict = db["Customers"]

            # Retrieve usernames from data dict
            for customer in customers_dict.values():
                cust_username = customer.get_username()
                usernames_list.append(cust_username)

            # Check whether username exists
            if username in usernames_list:
                raise ValidationError("Username is already in use")
        except KeyError:
            pass
    except Exception as e:
        # Display error messages
        print(f"Error accessing database: {e}")
        raise ValidationError("An error occurred while checking for username availability, please try again later")
    else:
        if db:
            db.close()


# Username exists validator
def username_exist(form, field):
    pass


# Correct password validator
def correct_password(form, field):
    pass


# Signup Form (Base stage)
class BaseSignUpForm(Form):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired(), Length(min=4, message="Username must be at least 4 characters long"), unique_username])
    email = StringField("Email", validators=[DataRequired(), Email(granular_message=True, check_deliverability=True)])
    submit = SubmitField("SEND")


# OTP Form
class OTPForm(Form):
    otp = StringField("One Time Pin", validators=[DataRequired()])


# Password Form (For Signup only - Set Password stage)
class PasswordForm(Form):
    password = PasswordField("Password", validators=[DataRequired(), password_complexity])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])


class LoginForm(Form):
    username = StringField("Username", validators=[DataRequired(), username_exist])
    password = PasswordField("Password", validators=[DataRequired(), correct_password])
