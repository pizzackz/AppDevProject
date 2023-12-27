import string
import random
import shelve
import hashlib
import uuid
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
def get_user_object(username=None, email=None):
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
        if (username and username == customer.get_username()) or (email and email == customer.get_email()):
            return customer

    for admin in admins_dict.values():
        if (username and username == admin.get_username()) or (email and email == admin.get_email()):
            return admin

    return False


# Get account type (customer/ admin) from user_object
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
    
    return hashed_password == actual_password


# Generate unique tokens
def generate_unique_token(user_id=None):
    base_token = str(uuid.uuid4())

    if user_id:
        token = f"{user_id}_{base_token}"
    else:
        token = base_token

    return token.replace("-", "")
