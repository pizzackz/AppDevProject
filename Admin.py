from User import User

class Admin(User):
    # Constructor
    def __init__(self, user_id, first_name, last_name, username, email, password):
        super().__init__(user_id, first_name, last_name, username, email, password)
    

    # Methods
    def get_admin_data(self):
        admin_dict = {
            "user_id": self.get_user_id(),
            "first_name": self.get_first_name(),
            "last_name": self.get_last_name(),
            "display_name": self.get_display_name(),
            "username": self.get_username(),
            "email": self.get_email(),
            "password": self.get_password(),
            "profile_pic": self.get_profile_pic_name()
        }
        return admin_dict