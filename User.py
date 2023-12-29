# User class
class User:
    # Constructor
    def __init__(self, user_id, first_name, last_name, username, email, password):
        self.__user_id = user_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__display_name = username
        self.__username = username
        self.__email = email
        self.__password = password
        self.__profile_pic_path = ""


    # Setters
    def set_user_id(self, user_id):
        self.__user_id = user_id

    def set_first_name(self, first_name):
        self.__first_name = first_name

    def set_last_name(self, last_name):
        self.__last_name = last_name
    
    def set_display_name(self, display_name):
        self.__display_name = display_name

    def set_username(self, username):
        self.__username = username
    
    def set_email(self, email):
        self.__email = email
    
    def set_password(self, password):
        self.__password = password
    
    def set_profile_pic_path(self, profile_pic_path):
        self.__profile_pic_path = profile_pic_path
    

    # Getters
    def get_user_id(self):
        return self.__user_id
    
    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_display_name(self):
        return self.__display_name
    
    def get_username(self):
        return self.__username
    
    def get_email(self):
        return self.__email
    
    def get_password(self):
        return self.__password
    
    def get_profile_pic_path(self):
        return self.__profile_pic_path


    # Methods
    # Checks whether data for given username and email are not same as current
    def is_unique_data(self, provided_data, attribute_name):
        value_to_compare = ""

        if attribute_name == "username":
            value_to_compare = self.__username
        elif attribute_name == "email":
            value_to_compare = self.__email

        if value_to_compare == provided_data:
            return False
        return True

