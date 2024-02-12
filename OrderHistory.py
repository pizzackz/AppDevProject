class OrderHistory:
    # Constructor
    def __init__(self, cust_id, cart_id=None, cart_item=None):
        self.__cust_id = cust_id
        self.__cart_dict = {}

        if cart_id and cart_item:
            self.__cart_dict[cart_id] = cart_item
    

    # Getters
    def get_cust_id(self):
        return self.__cust_id
    
    def get_cart_dict(self, cart_id=None, get_checkout_time=False):
        if cart_id:
            if get_checkout_time:
                return self.__cart_dict.get(cart_id).get_checkout_time()

            return self.__cart_dict.get(cart_id)
        return self.__cart_dict
    

    # Setters
    def set_cust_id(self, cust_id):
        self.__cust_id = cust_id
    
    def save_cart(self, cart_id, cart_item):
        self.__cart_dict[cart_id] = cart_item

