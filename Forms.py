from wtforms import Form, StringField, SubmitField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, Email
import shelve
from validators import unique_data, password_complexity, data_exist

# Signup Form (Base stage)
class BaseSignUpForm(Form):
    first_name = StringField("First Name", validators=[DataRequired()], render_kw={"placeholder": "First Name"})
    last_name = StringField("Last Name", validators=[DataRequired()], render_kw={"placeholder": "Last Name"})
    username = StringField("Username", validators=[DataRequired(), unique_data], render_kw={"placeholder": "Username"})
    email = StringField("Email", validators=[DataRequired(), Email(granular_message=True, check_deliverability=True), unique_data], render_kw={"placeholder": "Email"})


# OTP Form
class OTPForm(Form):
    otp = StringField("One Time Pin", validators=[DataRequired()], render_kw={"placeholder": "OTP"})


# Password Form (For Signup only - Set Password stage)
class PasswordForm(Form):
    password = PasswordField("Password", validators=[DataRequired(), password_complexity], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()], render_kw={"placeholder": "Confirm Password"})


# Login Form
class LoginForm(Form):
    username = StringField("Username", validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})


# Email Form (to allow reset of password in login page)
class EmailForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email(granular_message=True, check_deliverability=True), data_exist], render_kw={"placeholder": "Email"})


# Reset Password Form (Login - Reset Password action)
class ResetPasswordForm(Form):
    password = PasswordField("New Password", validators=[DataRequired(), password_complexity], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()], render_kw={"placeholder": "Confirm Password"})
