import shelve
from Product import Product


def create_new_product(name, description, price, qty, image=None, product_id=None):
    product_dict = {}

    db = shelve.open("product.db", "c")
    if "Product" in db:
        product_dict = db["Product"]
    else:
        db["Product"] = product_dict

    product_item = Product(name, description, price, qty, image)
    
    if product_id:
        product_item.change_product_id(product_id)

    product_id = product_item.get_product_id()
    product_dict[product_id] = product_item

    db["Product"] = product_dict
    db.close()

    print("New product item created")

    return product_item

# create_new_product(
#     name="Chicken Caesar Salad",
#     description="Our Chicken Caesar Salad contains Romaine lettuce, Caesar dressing, Parmesan, croutons, and grilled/roasted chicken breast. Dressing with garlic, anchovies, olive oil, egg yolks, Dijon mustard, lemon juice, and Worcestershire sauce for rich flavor. Satisfying and popular meal choice.",
#     qty=100,
#     price=9,
#     image="Chicken-Caesar-Salad-17-500x500.jpg"
# )

def retrieve_all_products():
    product_dict = {}
    db = shelve.open("product.db", "c")
    if "Product" in db:
        product_dict = db["Product"]
    else:
        db["Product"] = product_dict
    db.close()

    return product_dict


def retrieve_product_item(product_id):
    product_dict = retrieve_all_products()
    product_item = product_dict.get(product_id)
    return product_item


def update_product_item(product_id, name=None, description=None, price=None, image=None, qty=None, change_old_qty=False, set_new_qty=False):
    product_dict = {}

    db = shelve.open("product.db", "c")
    product_dict = db["Product"]

    product_item = product_dict.get(product_id)

    # Update product name
    if name != None:
        product_item.set_name(name)
        print(f"Product {product_id}'s name changed to {product_item.get_name()}")

    # Update product description
    
    if description != None:
        product_item.set_desc(description)
        print(f"Product {product_id}'s description changed to {product_item.get_desc()}")

    # Update product price
    if price != None:
        product_item.set_price(price)
        print(f"Product {product_id}'s price changed to {product_item.get_price()}")

    # Update product image
    if image != None:
        product_item.set_img(image)
        print(f"Product {product_id}'s image changed to {product_item.get_img()}")

    # Update product quantity
    if qty != None:
        if change_old_qty:
            product_item.set_qty(product_item.get_qty() - qty)
            print(f"Product {product_id}'s qty changed to {product_item.get_qty()}")
        elif set_new_qty:
            product_item.set_qty(qty)
            print(f"Product {product_id}'s qty changed to {product_item.get_qty()}")

    db["Product"] = product_dict
    db.close()

    return product_item


def delete_product_item(product_id):
    product_dict = {}
    
    db = shelve.open("product.db", "c")
    if "Product" in db:
        product_dict = db["Product"]
    else:
        db["Product"] = product_dict

    deleted_product_item = product_dict.pop(product_id)

    db["Product"] = product_dict
    db.close()

    return delete_product_item

