import string
import random
import shelve
import hashlib
import os
from flask import current_app
from werkzeug.utils import secure_filename
from flask_mail import Message

from Customer import Customer
from Admin import Admin


# Functions
# Generate otp
def generate_otp(length):
    digits = string.digits
    otp = ''.join(random.choices(digits, k=length))

    print("otp = " + otp)

    return otp


# Send email
def send_email(mail, subject, sender, recipients, body=None, html=None):
    try:
        if not isinstance(recipients, list):
            recipients = [recipients]

        msg = Message(subject, sender=sender, recipients=recipients)

        if body:
            msg.body = body
        elif html:
            msg.html = html

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error occurred while sending email: {str(e)}")
        return False


# Get user (customer/ admin) object from username/ email, returns False when no such account found
def get_user_object(user_id=None, username=None, email=None):
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

    if user_id in customers_dict.keys():
        return customers_dict.get(user_id)
    elif user_id in admins_dict.keys():
        return admins_dict.get(user_id)

    for customer in customers_dict.values():
        if (username and username == customer.get_username()) or (email and email == customer.get_email()):
            return customer

    for admin in admins_dict.values():
        if (username and username == admin.get_username()) or (email and email == admin.get_email()):
            return admin

    return False


# Get account type (customer/ admin) from user_object, user_id
def get_account_type(user_object=None, user_id=None):
    if user_object:
        if isinstance(user_object, Customer):
            return "customer"
        elif isinstance(user_object, Admin):
            return "admin"

    elif user_id:
        if int(user_id[0:3]) in range(100, 500):
            return "customer"
        elif int(user_id[0:3]) in range(501, 999):
            return "admin"


# Compare passwords
def compare_passwords(account_type, user_id, password):
    actual_password = ""
    # Hash given password
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Retrieve stored hashed password
    db = shelve.open("user_accounts.db", "c")
    if account_type == "customer":
        actual_password = db["Customers"][user_id].get_password()
    elif account_type == "admin":
        actual_password = db["Admins"][user_id].get_password()

    print("actual pass = " + str(actual_password) + ", hashed pass = " + str(hashed_password))
    return hashed_password == actual_password


# Unique data function (for username, email)
def is_unique_data(username=None, email=None):
    existing_data = []
    if username or email:
        attribute_name = "username" if username else "email"
        data = username or email

    db = shelve.open("user_accounts.db", "c")
    if "Customers" in db:
        existing_data += [object.get_cust_data().get(attribute_name) for object in db["Customers"].values()]
    if "Admins" in db:
        existing_data += [object.get_admin_data().get(attribute_name) for object in db["Admins"].values()]

    print("existing data = " + str(existing_data))

    db.close()

    return data not in existing_data


# Allowed file
def is_allowed_file(file_item):
    filename = secure_filename(file_item.filename)
    # Check whether allowed extension
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_IMAGE_FILE_EXTENSIONS"]


# Delete file (if file exists, returns filepath, else returns False)
def delete_file(account_type, file_category, filename_without_extension, possible_extensions):
    for extension in possible_extensions:
        existing_filename = f"{filename_without_extension}.{extension}"
        existing_file_path = os.path.join("static", "uploads", account_type, file_category, existing_filename)
        try:
            os.remove(existing_file_path)
            print(f"File {existing_filename} in {existing_file_path} has been removed successfully!")
            return existing_file_path
        except FileNotFoundError:
            print("Didn't work")
            pass
    return False

