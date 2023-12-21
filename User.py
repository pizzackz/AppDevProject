# User class
class User:
    # Constructor
    def __init__(self, user_id, first_name, last_name, username, email, password):
        self.__user_id = user_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__username = username
        self.__email = email
        self.__password = password

    # Setters
    def set_user_id(self, user_id):
        self.__user_id = user_id
    
    def set_first_name(self, first_name):
        self.__first_name = first_name
    
    def set_last_name(self, last_name):
        self.__last_name = last_name
    
    def set_username(self, username):
        self.__username = username
    
    def set_email(self, email):
        self.__email = email
    
    def set_password(self, password):
        self.__password = password
        
    
    # Getters
    def get_user_id(self):
        return self.__user_id
    
    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name
    
    def get_username(self):
        return self.__username
    
    def get_email(self):
        return self.__email
    
    def get_password(self):
        return self.__password