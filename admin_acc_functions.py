import shelve
import hashlib
import random
from Admin import Admin
from functions import get_user_object


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


# Update Admin Details
def update_admin_details(user_id, first_name=None, last_name=None, display_name=None, email=None, password=None):
    # Open db to store data
    db = shelve.open("user_accounts.db", "c")
    admins_dict = db["Admins"]
    admin = admins_dict.get(user_id)

    # Update first_name of customer
    if first_name:
        admin.set_first_name(first_name)
        print(f"Admin account f{user_id:10s}'s first name updated")
    
    # Update last_name of customer
    if last_name:
        admin.set_display_name(last_name)
        print(f"Admin account f{user_id:10s}'s last name updated")
        
    # Update display_name of customer
    if display_name:
        admin.set_display_name(display_name)
        print(f"Admin account f{user_id:10s}'s display name updated")

    # Update email of customer
    if email:
        admin.set_email(email)
        print(f"Admin account f{user_id:10s}'s email updated")
    
    # Update password of customer
    if password:
        admin.set_password(password)
        print(f"Admin account f{user_id:10s}'s password updated")

    db["Admins"] = admins_dict

    db.close()


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