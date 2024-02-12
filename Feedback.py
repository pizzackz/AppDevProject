import hashlib
from datetime import datetime


class Feedback:
    # Constructor
    def __init__(self, cust_id, display_name, id_postfix, category, rating, message):
        self.__cust_id = cust_id
        self.__feedback_id = str(hashlib.sha256(cust_id.encode("utf-8")).hexdigest()[:3]) + "2" + str(id_postfix)
        self.__display_name = display_name
        self.__category = category
        self.__rating = rating
        self.__message = message
        self.__sent_date = datetime.now().replace(microsecond=0)
    

    # Setters
    def set_display_name(self, display_name):
        self.__display_name = display_name

    def set_category(self, category):
        self.__category = category
    
    def set_rating(self, rating):
        self.__rating = rating
    
    def set_message(self, message):
        self.__message = message
    
    def set_sent_date(self, sent_date):
        self.set_sent_date = sent_date

    
    # Getters
    def get_cust_id(self):
        return self.__cust_id
    
    def get_display_name(self):
        return self.__display_name
    
    def get_feedback_id(self):
        return self.__feedback_id
    
    def get_category(self):
        return self.__category
    
    def get_rating(self):
        return self.__rating
    
    def get_message(self):
        return self.__message
    
    def get_sent_date(self, format=None):
        if format:
            return self.__sent_date.strftime(format)
        return self.__sent_date
    
    def get_feedback_data(self):
        data_dict = {
            "cust_id": self.__cust_id,
            "feedback_id": self.__feedback_id,
            "display_name": self.__display_name,
            "category": self.__category,
            "rating": self.__rating,
            "message": self.__message,
            "sent_date": self.__sent_date
        }
        return data_dict
