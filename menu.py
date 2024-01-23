class Menu_item():
    count_id = 0

    def __init__(self, name, description, price,image):
        Menu_item.count_id += 1
        self.__id = str(Menu_item.count_id)
        self.__name = name
        self.__description = description
        self.__price = price
        self.__image = image

    def set_name(self,name):
        self.__name = name

    def set_description(self, description):
        self.__description = description

    def set_price(self, price):
        self.__price = price

    def set_image(self, image):
        self.__image = image

    def get_name(self):
        return self.__name

    def get_description(self):
        return self.__description

    def get_price(self):
        return self.__price

    def get_image(self):
        return self.__image

    def get_id(self):
        return self.__id