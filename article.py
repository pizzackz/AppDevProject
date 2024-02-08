class article_item():
    count_id = 0
    def __init__(self, image, title, category, description):
        article_item.count_id+=1
        self.__id=str(article_item.count_id)
        self.__title=title
        self.__category=category
        self.__image=image
        self.__description=description

    def get_title(self):
        return self.__title

    def set_title(self, title):
        self.__title=title

    def get_category(self):
        return self.__category

    def set_category(self, category):
        self.__category=category

    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image=image

    def get_description(self):
        return self.__description

    def set_description(self, description):
        self.__description=description

    def get_id(self):
        return self.__id



class comment():
    comment_id=0
    def __init__(self, image, name, description):
        comment.comment_id+=1
        self.__id=str(comment.comment_id)
        self.__name=name
        self.__image=image
        self.__description=description

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name==name

    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image=image

    def get_description(self):
        return self.__description

    def set_description(self, description):
        self.__description=description

    def get_id(self):
        return self.__id