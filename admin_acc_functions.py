import shelve
import hashlib
import random
from flask import session
from Admin import Admin
from __init__ import get_user_object


# Create Admin
def create_admin(first_name, last_name, username, email, password):
    account_exists = False
    # Hash 1st 4 char of username & add random number in front to get user_id
    hashed_username = hashlib.sha256(username[0:3].encode("utf-8")).hexdigest()
    user_id = f"{random.randint(501, 999)}{hashed_username}"

    # Hash password
    hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Access database to store admin account details
    admins_dict = {}
    db = shelve.open("user_accounts.db", "c")

    if "Admins" in db:
        admins_dict = db["Admins"]
    else:
        db["Admins"] = admins_dict
    
    for admin in admins_dict.values():
        if admin.get_username() == user_id:
            account_exists = True

    if account_exists:
        print(f"Admin account {username} already exists")
        db.close()
        return

    admin = Admin(user_id, first_name, last_name, username, email, hashed_password)

    admins_dict[user_id] = admin
    db["Admins"] = admins_dict
    print(f"Admin account {user_id:.10s} is created")

    db.close()


# Update Admin
def update_admin(first_name, last_name, username, email, password):
    pass


# Delete Admin
def delete_admin(username):
    admin_object = get_user_object(username)
    admin_id = ""

    # Access database to delete admin account
    admins_dict = {}
    db = shelve.open("user_accounts.db", "c")

    if "Admins" in db:
        admins_dict = db["Admins"]
    else:
        print("No admin accounts currently")
        return

    if admin_object == False:
        print("No such admin account")
        return
    else:
        admin_id = admin_object.get_user_id()

    admins_dict.pop(admin_id, None)
    print(f"Admin account {admin_id:.10s} is deleted")

    db["Admins"] = admins_dict
    db.close()

