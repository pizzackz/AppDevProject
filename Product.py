import hashlib

class Product:
    # Constructor
    def __init__(self, name, desc, price, qty, product_img=None, product_id=None):
        self.__name = name
        self.__desc = desc
        self.__price = price
        self.__qty = qty
        self.__total_price = qty * price
        self.__product_img = product_img or ""
        if product_id:
            self.__product_id = product_id
        else:
            self.__product_id = hashlib.sha256(self.__name.encode("utf-8")).hexdigest()[:6]

    # Getters
    def get_product_id(self):
        return self.__product_id
    
    def get_name(self):
        return self.__name

    def get_desc(self):
        return self.__desc

    def get_price(self):
        return self.__price

    def get_qty(self):
        return self.__qty
    
    def get_price(self):
        return self.__price

    def get_total_price(self):
        return self.__total_price
    
    def get_product_img(self):
        return self.__product_img

    def get_all(self):
        return {
            "product_id": self.__product_id,
            "name": self.__name,
            "desc": self.__desc,
            "price": self.__price,
            "qty": self.__qty,
            "total_price": self.__total_price,
            "product_img": self.__product_img
        }

    # Setters
    def change_product_id(self):
        self.__product_id = hashlib.sha256(self.__name.ecode("utf-8")).hexdigest()[:6]

    def set_name(self, name):
        self.__name = name

    def set_desc(self, desc):
        self.__desc = desc
    
    def set_price(self, price):
        self.__price = price

    def set_qty(self, qty):
        self.__qty = qty
        self.__total_price = qty * self.__price

    def set_product_img(self, img):
        self.__product_img = img

