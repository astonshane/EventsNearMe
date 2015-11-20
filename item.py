# EventsNear.me imports
from user import *


# Basic Item class for storing comment information
class Item:
    def __init__(self, mongo, uid, name):
        if uid != "":
            self.claimer = User(uid, mongo)
        else:
            self.claimer = ""
        self.claimerUID = uid
        self.itemName = name
# str method for Item class
    def __str__(self):
        return "%s by %s" % (self.itemName, self.uid)

    def __repr__(self):
        return self.__str__()
