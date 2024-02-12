import shelve
import random
import hashlib
from datetime import datetime
from Customer import Customer
from werkzeug.security import generate_password_hash


# Create Customer
def create_customer(session_data, hashed_password):
    # Get all account details
    first_name = session_data.get("first_name")
    last_name = session_data.get("last_name")
    username = session_data.get("username")
    email = session_data.get("email")
    last_online = session_data.get("last_online")

    # Hash 1st 4 char of username & add random number in front to get user_id
    hashed_username = hashlib.sha256(username[0:3].encode("utf-8")).hexdigest()[0:9]
    user_id = f"{random.randint(100, 500)}{hashed_username}"
    print("user_id = " + user_id)

    # Access database to store customer account details
    customers_dict = {}

    db = shelve.open("user_accounts.db", "c")
    if "Customers" in db:
        customers_dict = db["Customers"]
    else:
        db["Customers"] = customers_dict
    
    customer = Customer(user_id, first_name, last_name, username, email, hashed_password)
    customer.set_last_online(last_online)

    customers_dict[customer.get_user_id()] = customer
    db["Customers"] = customers_dict

    print(f"Customer account {user_id:.10s} created")

    db.close()


# Retrieve all customers
def retrieve_all_customers():
    customers_dict = {}
    db = shelve.open("user_accounts.db", "c")
    
    if "Customers" in db:
        customers_dict = db["Customers"]
    else:
        db["Customers"] = customers_dict
        return []

    db.close()

    customers_list = []

    for key in customers_dict:
        customer = customers_dict.get(key)
        customers_list.append(customer)
        print("user id = " + customer.get_user_id())

    return customers_list


# Retrieve Customer Details
def retrieve_cust_details(user_id):
    # Open db to retrieve data
    db = shelve.open("user_accounts.db", "r")
    customers_dict = db["Customers"]
    customer = customers_dict.get(user_id)

    return customer.get_cust_data()


# Update Customer Details
def update_cust_details(user_id, first_name=None, last_name=None, display_name=None, email=None, password=None, is_locked=None, locked_reason=None, unlock_request=None, delete_request=None, last_online=None, profile_pic_name=None):
    # Open db to store data
    db = shelve.open("user_accounts.db", "c")
    customers_dict = db["Customers"]
    customer = customers_dict.get(user_id)

    # Update first_name of customer
    if first_name:
        customer.set_first_name(first_name)
        print(f"Customer account {user_id:.10s}'s first name updated")
    
    # Update last_name of customer
    if last_name:
        customer.set_last_name(last_name)
        print(f"Customer account {user_id:.10s}'s last name updated")
        
    # Update display_name of customer
    if display_name:
        customer.set_display_name(display_name)
        print(f"Customer account {user_id:.10s}'s display name updated")

    # Update email of customer
    if email:
        customer.set_email(email)
        print(f"Customer account {user_id:.10s}'s email updated")
    
    # Update password of customer
    if password:
        # print("exist pass = " + customer.get_password())
        customer.set_password(password)
        # print("new pass = " + customer.get_password())
        print(f"Customer account {user_id:.10s}'s password updated")

    # Update locked status and reason
    if is_locked != None and locked_reason != None:
        customer.set_is_locked(is_locked)
        customer.set_locked_reason(locked_reason)
        print(f"Customer account {user_id:.10s}'s locked status & locked reason updated")
    
    # Update unlock request
    if unlock_request != None:
        customer.set_unlock_request(unlock_request)
        print(f"Customer account {user_id:.10s}'s unlock request updated")
    
    # Update delete request
    if delete_request != None:
        customer.set_delete_request(delete_request)
        print(f"Customer account {user_id:.10s}'s delete request updated")

    # Update last_online date
    if last_online:
        customer.set_last_online(last_online)
        print(f"Customer account {user_id:.10s}'s last online date updated")

    # Update profile picture of admin
    if profile_pic_name:
        customer.set_profile_pic_name(profile_pic_name)
        print(f"Customer account {user_id:.10s}'s profile picutre updated!")

    db["Customers"] = customers_dict
    db.close()


# Detete Customer
def delete_customer(user_id):
    # Open db to delete data
    db = shelve.open("user_accounts.db", "c")
    customers_dict = db["Customers"]
    customers_dict.pop(user_id, None)

    db["Customers"] = customers_dict
    db.close()

    print(f"Customer account {user_id:.10s} was deleted!")


def delete_all_customers():
    db = shelve.open("user_accounts.db", "c")
    print("All customer's data are deleted")
    db["Customers"] = {}
    db.close()


# Testing
# for i in range(7):
#     create_customer({"first_name": "Yeo", "last_name": f"Jun Qi {i+1}", "username": f"Croxvore{i+1}", "email": f"croxvore{i+1}@gmail.com"}, generate_password_hash(f"Unitysec@202{i}", salt_length=8))

# delete_all_customers()
