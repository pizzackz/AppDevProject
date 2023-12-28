from wtforms import Form, StringField, PasswordField, FileField
from wtforms.validators import DataRequired, Email
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


# Account Details Form
class AccountDetailsForm(Form):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    display_name = StringField("Display Name", validators=[DataRequired()])
    email = StringField("Email Address", render_kw={"disabled": True})
    # profile_picture = FileField('Profile Picture', validators=[])


# Change Email Form (to allow customer to change email address)
class ChangeEmailForm(Form):
    email = StringField("New Email", validators=[DataRequired(), Email(granular_message=True, check_deliverability=True)], render_kw={"placeholder": "New Email Address"})


# Reset Password Form (Edit cust profile - Reset Password action)
class ResetPasswordForm2(Form):
    password = PasswordField("New Password", validators=[DataRequired(), password_complexity], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()], render_kw={"placeholder": "Confirm Password"})