
class Comment:
    def __init__(self, creator_id=None, title=None, msg=None):
        self.creator_id = creator_id
        self.title = title
        self.msg = msg

    def __str__(self):
        return "%s (by %s): %s" % (self.title, self.creator_id, self.msg)

    def __repr__(self):
        return self.__str__()
