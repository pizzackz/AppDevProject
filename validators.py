import shelve
from flask import session, flash
from wtforms import ValidationError


# Check whether otp is correct
def is_correct_otp(otp):
    stored_otp = session.get("create_customer", None).get("otp")

    if otp == stored_otp:
        return True
    else:
        flash("Invalid OTP! Please try again")
        return False


# Custom validator functions for Forms.py
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


# Unique data validator (for username, email)
def unique_data(form, field):
    data = field.data
    field_name = field.name
    
    db = shelve.open("user_accounts.db", "c")
    if "Customers" in db:
        customers_dict = db["Customers"]

        for customer in customers_dict.values():
            if not customer.is_unique_data(data, field_name):
                raise ValidationError(f"{field_name.capitalize()} is already in use")

    db.close()


# Data exists validator (for username, email)
def data_exist(form, field):
    data_exist = False
    data = field.data
    field_name = field.name
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
            data_exist = True
            return

    for admin in admins_dict.values():
        if not admin.is_unique_data(data, field_name):
            data_exist = True
            return

    if not data_exist:
        raise ValidationError(f"No account exists with this {field_name.capitalize()}")

