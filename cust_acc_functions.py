import shelve
import random
import hashlib
from flask import flash, render_template
from Customer import Customer


# Create Customer
def create_customer(session_data, hashed_password, form):
    # Get all account details
    first_name = session_data["first_name"]
    last_name = session_data["last_name"]
    username = session_data["username"]
    email = session_data["email"]

    # Hash 1st 4 char of username & add random number in front to get user_id
    hashed_username = hashlib.sha256(username[0:3].encode("utf-8")).hexdigest()
    user_id = f"{random.randint(100, 500)}{hashed_username}"

    # Access database to store customer account details
    customers_dict = {}

    db = shelve.open("user_accounts.db", "c")
    if "Customers" in db:
        customers_dict = db["Customers"]
    else:
        db["Customers"] = customers_dict
    
    customer = Customer(user_id, first_name, last_name, username, email, hashed_password)

    customers_dict[customer.get_user_id()] = customer
    db["Customers"] = customers_dict

    print(f"Customer account {user_id:.10s} created")

    db.close()


# Update Customer data
def update_customer(session_data, form):
    pass