import shelve
import hashlib
from wtforms import ValidationError
from flask import current_app


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
                raise ValidationError(f"Please use another {field_name.capitalize()}")
    
    if "Admins" in db:
        admins_dict = db["Admins"]

        for admin in admins_dict.values():
            if not admin.is_unique_data(data, field_name):
                raise ValidationError(f"Please use another {field_name.capitalize()}")

    db.close()


# Data exists validator (for username, email)
def data_exist(form, field):
    data_exist = False
    data = field.data
    field_name = field.name

    # Hash given data if field is password
    if "password" in field_name:
        data = hashlib.sha256(data.encode("utf-8")).hexdigest()

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
