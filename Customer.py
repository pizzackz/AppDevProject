from User import User
import shelve

class Customer(User):
    # Constructor
    def __init__(self, user_id, first_name, last_name, username, email, password):
        super().__init__(user_id, first_name, last_name, username, email, password)
        self.__is_locked = False
        self.__last_online = ""


    # Setters    
    def set_is_locked(self, is_locked):
        self.__is_locked = is_locked
    
    def set_last_online(self, last_online):
        self.__last_online = last_online
    

    # Getters
    def get_cust_id(self):
        return self.__cust_id

    def get_is_locked(self):
        return self.__is_locked
    
    def get_last_online(self):
        return self.__last_online

    def get_cust_data(self):
        cust_dict = {
            "user_id": self.get_user_id(),
            "first_name": self.get_first_name(),
            "last_name": self.get_last_name(),
            "display_name": self.get_display_name(),
            "username": self.get_username(),
            "email": self.get_email(),
            "password": self.get_password(),
            "is_locked": self.__is_locked,
            "last_online": self.__last_online
        }
        return cust_dict
