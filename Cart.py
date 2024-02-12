from random import randint
# from promotional_codes import PromotionalCodes


class Cart:
    # Constructor
    def __init__(self, cust_id):
        self.__cust_id = cust_id
        self.__cart_id = randint(1000000, 9999999)
        self.__checkout_time = ""
        self.__total = 0
        self.__product_dict = {}
        self.__delivery_dict = {
            "method": [0, "Self Collection"],
            "customer_info": {},
            "payment_info": {},
        }
        

    # Getters
    def get_cust_id(self):
        return self.__cust_id

    def get_cart_id(self):
        return self.__cart_id

    def get_total(self):
        return self.__total
    
    def get_checkout_time(self, format=None):
        if format:
            return self.__checkout_time.strftime(format)
        return self.__checkout_time

    def get_product_dict(self):
        return self.__product_dict

    def get_delivery_dict(self, method=False, cust_info=False, payment_info=False):
        if method:
            return self.__delivery_dict.get("method")
        if cust_info:
            return self.__delivery_dict.get("customer_info")
        if payment_info:
            return self.__delivery_dict.get("payment_info")
        return self.__delivery_dict

    def get_all(self):
        return {
            "cust_id": self.__cust_id,
            "cart_id": self.__cart_id,
            "total_price": self.__total,
            "checkout_time": self.__checkout_time,
            "product_dict": self.__product_dict,
            "delivery_dict": self.__delivery_dict,
        }

    # Setters
    def set_cart_id(self, cart_id):
        self.__cart_id = cart_id
    
    def add_product(self, product_id, product_item):
        self.__product_dict[product_id] = product_item
    
    def set_checkout_time(self, checkout_time):
        self.__checkout_time = checkout_time

    def calc_total_price(self):
        total = 0
        for product in self.__product_dict.values():
            total += product.get_total_price()
        total += self.get_delivery_dict(method=True)[0]  # * code
        self.__total = total

    def update_product_qty(self, product_id, new_qty):
        product_data = self.__product_dict.get(product_id)
        product_data["qty"] = new_qty
        self.calc_total_price()

    def change_delivery_method(self, delivery_option, price):
        self.__delivery_dict["method"] = [price, delivery_option]

    def set_delivery_cust_info(self, name, address, postal_code, phone):
        self.__delivery_dict["customer_info"] = {
            "name": name,
            "address": address,
            "postal_code": postal_code,
            "phone": phone,
        }

    def set_payment_info(self, card_type, card_name, card_number, expiration_date, cvc):
        self.__delivery_dict["payment_info"] = {
            "card_type": card_type,
            "card_name": card_name,
            "card_number": card_number,
            "expiration_date": expiration_date,
            "cvc": cvc,
        }


# import shelve
#
# db = shelve.open("cart.db", "c")
# cart_dict = {}
#
# try:
#     if 'Cart' in db:
#         cart_dict = db['Cart']
#         print("yes1")
#
#     else:
#         db['Cart'] = cart_dict
#         print("yes2")
#
# except:
#     print("Error in opening cart.db")
