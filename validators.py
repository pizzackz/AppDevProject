import shelve
from werkzeug.security import generate_password_hash
from wtforms import ValidationError
import re


# Custom validator functions for Forms.py
# Password complexity validator
def password_complexity(form, field):
    password = field.data

    if len(password) < 8:
        raise ValidationError("Please enter at least 8 characters")

    if not any(char.islower() for char in password):
        raise ValidationError("Please enter at least one lowercase letter")

    if not any(char.isupper() for char in password):
        raise ValidationError("Please enter at least one uppercase letter")

    if not any(char in "!@#$%^&*()_+-=[]{}|;':\",.<>/?" for char in password):
        raise ValidationError("Please enter at least one symbol")


# Unique data validator (for username, email)
def unique_data(form, field):
    data = field.data
    field_name = field.name

    db = shelve.open("user_accounts.db", "c")
    if "Customers" in db:
        customers_dict = db["Customers"]

        for customer in customers_dict.values():
            if not customer.is_unique_data(data, field_name):
                raise ValidationError(f"{field_name.capitalize()} already in use. Try another")

    if "Admins" in db:
        admins_dict = db["Admins"]

        for admin in admins_dict.values():
            if not admin.is_unique_data(data, field_name):
                raise ValidationError(f"{field_name.capitalize()} already in use. Try another")

    db.close()


# Data exists validator (for username, email)
def data_exist(form, field):
    data_exist = False
    data = field.data
    field_name = field.name

    # Hash given data if field is password
    if "password" in field_name:
        data = generate_password_hash(data, salt_length=8)

    customers_dict = {}
    admins_dict = {}

    db = shelve.open("user_accounts.db", "c")

    if "Customers" in db:
        customers_dict = db["Customers"]
    else:
        db["Customers"] = customers_dict

    if "Admins" in db:
        admins_dict = db["Admins"]
    else:
        db["Admins"] = admins_dict

    db.close()

    for customer in customers_dict.values():
        if not customer.is_unique_data(data, field_name):
            return

    for admin in admins_dict.values():
        if not admin.is_unique_data(data, field_name):
            return

    if not data_exist:
        raise ValidationError(f"Please enter a registered {field_name.capitalize()}")


# 6 digit OTP specific validator
def otp_validator(form, field):
    otp = field.data

    if len(otp) != 6:
        raise ValidationError("Please enter exactly 6 digits")

    try:
        otp = int(otp)
    except ValueError:
        raise ValidationError("Please enter only numbers")


def six_digit_postal_code_validator(form, field):
    if len(field.data) != 6:
        raise ValidationError("Please enter a valid 6-digit postal code.")
    if field.data == "000000":
        raise ValidationError("Please enter a valid 6-digit postal code.")
    try:
        field.data = int(field.data)
    except ValueError:
        raise ValidationError("Please enter a valid 6-digit postal code.")


def phone_number_validator(form, field):
    pattern = r"^(8|9)\d{3} \d{4}$"
    field_data_str = str(field.data)  # Ensure data is a string
    if not re.match(pattern, field_data_str):
        raise ValidationError("Please enter a valid phone number in the format 8/9XXX XXXX.")


def card_number_validator(form, field):
    pattern = r"^\d{4}-\d{4}-\d{4}-\d{4}$"
    field_data_str = str(field.data)  # Ensure data is a string
    if not re.match(pattern, field_data_str):
        raise ValidationError("Please enter a valid card number in the format XXXX-XXXX-XXXX-XXXX.")


def card_expiry_validator(form, field):
    pattern = r"^\d{2}/\d{2}$"
    field_data_str = str(field.data)  # Ensure data is a string
    if not re.match(pattern, field_data_str):
        raise ValidationError("Please enter a valid expiry date in the format MM/YY.")

    # Extract month and year components from the expiry date
    expiry_month, expiry_year = map(int, field_data_str.split('/'))

    # Check if the expiry date is before 02/24
    print(expiry_year, expiry_month)
    if expiry_year < 24 or expiry_year > 31 or expiry_month == 0 or expiry_month > 13:
        raise ValidationError("Please enter a valid expiry date after 02/24 and before 12/30.")
