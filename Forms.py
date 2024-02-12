from wtforms import Form, StringField, PasswordField, FileField, TextAreaField, IntegerField, SelectField, DecimalField
from wtforms.validators import Email, DataRequired, Length, NumberRange
from validators import unique_data, password_complexity, data_exist, otp_validator, six_digit_postal_code_validator, phone_number_validator, card_number_validator, card_expiry_validator


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


class CreateCartForm(Form):
    name = StringField('Name', [Length(min=1, max=150), DataRequired()], render_kw={'readonly': True})
    product_id_field = StringField('Product_id', [Length(min=1, max=150), DataRequired()], render_kw={'readonly': True})
    qty = IntegerField('Quantity', [DataRequired(), NumberRange(1)])
    price = StringField('Price', [Length(min=1, max=150), DataRequired()], render_kw={'readonly': True})


class CreateDeliveryInfoForm(Form):
    fname = StringField('Name', [Length(min=1, max=150), DataRequired()], render_kw={"placeholder": "John Doe"})
    address = StringField('Address', [Length(min=1, max=150), DataRequired()], render_kw={"placeholder": "123 ABC Street"})
    postal = StringField('Postal Code', [six_digit_postal_code_validator, DataRequired()], render_kw={"placeholder": "123456"})
    phone = StringField('Phone', [phone_number_validator, DataRequired()], render_kw={"placeholder": "9123 4567"})
    card_type = StringField('Card Type', [Length(min=1, max=150), DataRequired()], render_kw={"placeholder": "Master Card"})
    card_name = StringField('Name on Card', [Length(min=1, max=150), DataRequired()], render_kw={"placeholder": "John Doe"})
    card_num = StringField('Card Number', [DataRequired(), card_number_validator], render_kw={"placeholder": "1234-5678-9012-3456"})
    card_exp = StringField('Expiration Date', [DataRequired(), card_expiry_validator], render_kw={"placeholder": "MM/YY"})
    card_cvc = IntegerField('CVC', [NumberRange(100, 999), DataRequired()], render_kw={"placeholder": "123"})


class CustomerFeedbackForm(Form):
    name = StringField('Your Name', render_kw={"disabled": True})
    category = SelectField('Category', choices=[("product", "Product"), ("website", "Website"), ("delivery", "Delivery"), ("others", "Others")])
    rating = DecimalField('Overall Satisfaction', [NumberRange(min=1, max=5)])
    comment = TextAreaField('Feedback', [DataRequired()])


class createMenu(Form):
    name = StringField('Name Of Dish', [Length(min=1, max=150), DataRequired()])
    description = TextAreaField('Description', [DataRequired()])
    quantity = IntegerField('Quantity', [DataRequired()])
    price = DecimalField('Price', [DataRequired()])
    image = FileField('Upload Image')


class updateMenu(Form):
    name = StringField('Name Of Dish')
    description = TextAreaField('Description')
    quantity = IntegerField('Quantity')
    price = DecimalField('Price')
    image = FileField('Change Image')

