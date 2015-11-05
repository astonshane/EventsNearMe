# EventsNear.me imports
from user import *


# Basic Comment class for storing comment information
class Comment:
    def __init__(self, mongo, creator_id, title, msg):
        self.creator = User(creator_id, mongo)
        self.title = title
        self.msg = msg

    def __str__(self):
        return "%s (by %s): %s" % (self.title, self.creator_id, self.msg)

    def __repr__(self):
        return self.__str__()
