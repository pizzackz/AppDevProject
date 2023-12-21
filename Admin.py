from User import User

class Admin(User):
    # Constructor
    def __init__(self, user_id, first_name, last_name, username, email, password):
        super().__init__(user_id, first_name, last_name, username, email, password)