import shelve
from datetime import datetime
from product_functions import retrieve_product_item
from Product import Product
from Cart import Cart

def create_new_cart_item(cust_id, product_id, product_qty=1):
    # Create new product object first
    reference_product_item = retrieve_product_item(product_id)
    product_id = reference_product_item.get_product_id()
    name = reference_product_item.get_name()
    desc = reference_product_item.get_desc()
    price = reference_product_item.get_price()
    image = reference_product_item.get_product_img()

    product_item = Product(name, desc, price, product_qty, product_img=image, product_id=product_id)

    # Create new cart object
    cart = Cart(cust_id)
    cart.add_product(product_id, product_item)
    cart_id = cart.get_cart_id()
    cart_dict = {}

    # Open shelve to store cart in db
    db = shelve.open("cart.db", "c")

    if "Cart" in db:
        cart_dict = db["Cart"]
    else:
        db["Cart"] = cart_dict

    cart_dict[cart_id] = cart

    db["Cart"] = cart_dict
    db.close()

    return cart_id


def retreive_cart_item(cart_id):
    cart_dict = {}

    db = shelve.open("cart.db", "r")
    cart_dict = db["Cart"]

    cart_item = cart_dict.get(cart_id)

    db.close()

    return cart_item


def update_cart_item(
    cart_id,
    product_id=None,
    product_qty=None,
    delivery_name=None,
    delivery_price=None,
    delivery_cust_info=None,
    delivery_payment_info=None,
    set_checkout_time=None,
    new_product=False,
    update_product_qty=False,
    remove_product=False,
):
    cart_dict = {}

    db = shelve.open("cart.db", "c")
    if "Cart" in db:
        cart_dict = db["Cart"]
    else:
        db["Cart"] = cart_dict

    print(cart_dict)
    cart_item = cart_dict.get(cart_id)

    # Update product item in cart
    if product_id:
        product_dict = cart_item.get_product_dict()
        product_item = product_dict.get(product_id)

        # Add new product into cart
        if new_product and product_qty:
            wanted_product_details = retrieve_product_item(product_id).get_all()
            product_item = Product(
                product_id,
                wanted_product_details.get("name"),
                wanted_product_details.get("price"),
                product_qty,
            )
            cart_item.add_product(product_id, product_item)

            print("New product added")

        # Update product qty stored in cart
        if update_product_qty and product_qty:
            product_item.set_qty(product_qty)

            print("Product qty in cart updated")

        # Remove product from cart
        if remove_product:
            product_dict.pop(product_id)
            print("Product removed from cart")

    # Update delivery method in cart
    if delivery_name and delivery_price:
        cart_item.change_delivery_method(delivery_name, delivery_price)
        print("Delivery details updated")

    # Update delivery_cust_info in cart
    if delivery_cust_info:
        data_list = delivery_cust_info
        cart_item.set_delivery_cust_info(
            data_list[0], data_list[1], data_list[2], data_list[3]
        )
        print("Customer info for checkout updated")

    # Update delivery_payment_info in cart
    if delivery_payment_info:
        data_list = delivery_payment_info
        cart_item.set_payment_info(
            data_list[0], data_list[1], data_list[2], data_list[3], data_list[4]
        )
        print("Payment info for checkout updated")

    # Set checkout time in cart
    if set_checkout_time:
        cart_item.set_checkout_time(datetime.now().replace(second=0, microsecond=0))
        print("Checkout time added: " + str(cart_item.get_checkout_time()))

    # Always recalculate total when changes made
    cart_item.calc_total_price()

    db["Cart"] = cart_dict
    db.close()

    print(cart_item.get_all())
    print(cart_item.get_checkout_time())

    return cart_item


def delete_cart_item(cart_id):
    cart_dict = {}

    db = shelve.open("cart.db", "c")
    if "Cart" in db:
        cart_dict = db["Cart"]
    else:
        db["Cart"] = cart_dict

    cart_item = cart_dict.pop(cart_id)

    db["Cart"] = cart_dict
    db.close()

    return cart_item
