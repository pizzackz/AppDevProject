import shelve
import random
import hashlib
from Customer import Customer


# Create Customer
def create_customer(session_data, hashed_password):
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


# Retrieve Customer Details
def retrieve_cust_details(user_id):
    # Open db to retrieve data
    db = shelve.open("user_accounts.db", "r")
    customers_dict = db["Customers"]
    customer = customers_dict.get(user_id)

    return customer.get_cust_data()


# Update Customer Details
def update_cust_details(user_id, first_name=None, last_name=None, display_name=None, email=None, password=None):
    # Open db to store data
    db = shelve.open("user_accounts.db", "c")
    customers_dict = db["Customers"]
    customer = customers_dict.get(user_id)

    # Update first_name of customer
    if first_name:
        customer.set_first_name(first_name)
        print(f"Customer account f{user_id:10s}'s first name updated")
    
    # Update last_name of customer
    if last_name:
        customer.set_last_name(last_name)
        print(f"Customer account f{user_id:10s}'s last name updated")
        
    # Update display_name of customer
    if display_name:
        customer.set_display_name(display_name)
        print(f"Customer account f{user_id:10s}'s display name updated")

    # Update email of customer
    if email:
        customer.set_email(email)
        print(f"Customer account f{user_id:10s}'s email updated")
    
    # Update password of customer
    if password:
        customer.set_password(password)
        print(f"Customer account f{user_id:10s}'s password updated")

    db["Customers"] = customers_dict
    db.close()