from wtforms import Form, StringField, PasswordField, FileField, TextAreaField
from wtforms.validators import Email, DataRequired, Length
from validators import unique_data, password_complexity, data_exist, otp_validator


# Signup Form (Base stage)
class BaseSignUpForm(Form):
    first_name = StringField("First Name", render_kw={"placeholder": "John"})
    last_name = StringField("Last Name", render_kw={"placeholder": "Doe"})
    username = StringField("Username", validators=[unique_data], render_kw={"placeholder": "JohnDoe1"})
    email = StringField("Email", validators=[Email(granular_message=True, check_deliverability=True), unique_data], render_kw={"placeholder": "user@xyz.com"})


# OTP Form
class OTPForm(Form):
    otp = StringField("One Time Pin", validators=[otp_validator], render_kw={"placeholder": "OTP"})


# Password Form (For Signup only - Set Password stage)
class PasswordForm(Form):
    password = PasswordField("Password", validators=[password_complexity], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", render_kw={"placeholder": "Confirm Password"})


# Login Form
class LoginForm(Form):
    username = StringField("Username", render_kw={"placeholder": "JohnDoe1"})
    password = PasswordField("Password", render_kw={"placeholder": "Password"})


# Email Form (to allow reset of password in login page)
class EmailForm(Form):
    email = StringField("Email", validators=[Email(granular_message=True, check_deliverability=True), data_exist], render_kw={"placeholder": "user@xyz.com"})


# Reset Password Form (Login - Reset Password action)
class ResetPasswordForm(Form):
    password = PasswordField("New Password", validators=[password_complexity], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", render_kw={"placeholder": "Confirm Password"})


# Account Details Form
class AccountDetailsForm(Form):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    display_name = StringField("Display Name")
    email = StringField("Email Address", validators=[Email(granular_message=True, check_deliverability=True)])


# OTP Form to verify email after trying to change email address
class OTPForm2(Form):
    otp = StringField("One Time Pin", validators=[otp_validator], render_kw={"placeholder": "OTP"})


# Reset Password Form (Edit user profile - Reset Password action)
class ResetPasswordForm2(Form):
    password = PasswordField("New Password", validators=[password_complexity], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", render_kw={"placeholder": "Confirm Password"})


# Create Admin Form
class CreateAdminForm(Form):
    username = StringField("Username", validators=[unique_data], render_kw={"placeholder": "JohnDoe1"})
    first_name = StringField("First Name", render_kw={"placeholder": "John"})
    last_name = StringField("Last Name", render_kw={"placeholder": "Doe"})
    email = StringField("Email Address", validators=[Email(granular_message=True, check_deliverability=True), unique_data], render_kw={"placeholder": "user@xyz.com"})
    password = PasswordField("Password", validators=[password_complexity], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField("Confirm Password", render_kw={"placeholder": "Confirm Password"})


# Update Admin Form
class UpdateAdminForm(Form):
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    display_name = StringField("Display Name")
    email = StringField("Email Address", validators=[Email(granular_message=True, check_deliverability=True)])


# Search Customer Form (Customer Database - Admin View)
class SearchCustomerForm(Form):
    username = StringField("Enter Customer's Username", render_kw={"placeholder": "JohnDoe1"})


# Change Profile Picture Form (Edit Profile - Customer & Admin)
class FileForm(Form):
    file = FileField("File")


# Display Customer Account Details Form (Customer Database - Retrieve Customer - Admin View)
class AccountDetailsForm2(Form):
    first_name = StringField("First Name", render_kw={"disabled": True})
    last_name = StringField("Last Name", render_kw={"disabled": True})
    display_name = StringField("Display Name", render_kw={"disabled": True})
    email = StringField("Email Address", render_kw={"disabled": True})


# Lock Details Form (Customer Database - Lock Customer - Admin View)
class LockCustomerAccountForm(Form):
    reason = TextAreaField("Reason for locking", render_kw={"placeholder": "Enter Reason"})

class CreateRecipeForm(Form):
    name = StringField("Name", validators=[DataRequired(), Length(max=255)], render_kw={"class": "form-control"})
    ingredients = StringField("Ingredients", validators=[DataRequired()], render_kw={"class": "form-control"})
    instructions = TextAreaField("Instructions", validators=[DataRequired()], render_kw={"class": "form-control"})
    picture = FileField("Picture", render_kw={"class": "form-control", "accept": "image/*"})
    
class createArticle(Form):
    category = StringField('Category', [Length(min=1, max=150), DataRequired()])
    title = StringField('Article Title', [Length(min=1, max=150), DataRequired()])
    image = FileField('Upload Image')
    description = TextAreaField('Description', [DataRequired()])

class comment_sec(Form):
    title = StringField('Username', [Length(min=1, max=150), DataRequired()])
    image = FileField('Profile picture')
    description = TextAreaField('Description', [DataRequired()])