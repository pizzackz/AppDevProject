from User import User

class Customer(User):
    # Constructor
    def __init__(self, user_id, first_name, last_name, username, email, password):
        super().__init__(user_id, first_name, last_name, username, email, password)
        self.__display_name = username
        self.__is_locked = False
        self.__last_online = ""

    # Setters
    def set_display_name(self, display_name):
        self.__display_name = display_name
    
    def set_is_locked(self, is_locked):
        self.__is_locked = is_locked
    
    def set_last_online(self, last_online):
        self.__last_online = last_online
    
    # Getters
    def get_display_name(self):
        return self.__display_name

    def get_cust_id(self):
        return self.__cust_id

    def get_is_locked(self):
        return self.__is_locked
    
    def get_last_online(self):
        return self.__last_online