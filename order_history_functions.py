import shelve
from cart_functions import retreive_cart_item
from OrderHistory import OrderHistory

def create_new_order_history(cust_id, cart_id):
    cart_item = retreive_cart_item(cart_id)

    history_dict = {}
    db = shelve.open("history.db", "c")
    if "Order History" in db:
        history_dict = db["Order History"]
    else:
        db["Order History"] = history_dict

    order_history = {}
    if cust_id in history_dict.keys():
        order_history = history_dict.get(cust_id)
        order_history.save_cart(cart_id, cart_item)
        history_dict[cust_id] = order_history
    else:
        order_history = OrderHistory(cust_id, cart_id=cart_id, cart_item=cart_item)
        history_dict[cust_id] = order_history

    print("New order history saved")

    db["Order History"] = history_dict
    print("stored history dict = " + str(db["Order History"]))
    db.close()


def retrieve_all_order_histories():
    history_dict = {}

    db = shelve.open("history.db", "c")
    if "Order History" in db:
        history_dict = db["Order History"]
    else:
        db["Order History"] = history_dict
    db.close()

    return history_dict


def retrieve_order_history(cust_id):
    history_dict = {}

    db = shelve.open("history.db", "c")
    if "Order History" in db:
        history_dict = db["Order History"]
    else:
        db["Order History"] = history_dict
    db.close()

    order_history = history_dict.get(cust_id)

    return order_history


def update_order_history(cust_id, cart_id):
    cart_item = retreive_cart_item(cart_id)
    history_dict = {}

    db = shelve.open("history.db", "c")
    if "Order History" in db:
        history_dict = db["Order History"]
    else:
        db["Order History"] = history_dict
    
    order_history = history_dict.get(cust_id)
    order_history.save_cart(cart_id, cart_item)
    
    db["Order History"] = history_dict
    db.close()
