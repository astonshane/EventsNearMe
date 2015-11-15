# EventsNear.me imports
from user import *
from comment import *


# the Event class to store an Event's info
class Event:
    def __init__(self, uid="42", mongo=None):
        print "############"
        try:
            event = mongo.db.events.event = mongo.db.events.find({'_id': uid})[0]
            print "$$$$"

            self.id = event['_id']
            self.name = event['title']
            self.description = event['description']
            self.tags = event['tags']

            self.address = event['location']['address']
            self.street_address = event['location']['streetAddress']

            self.lat = event['location']['loc']['coordinates'][1]
            self.lon = event['location']['loc']['coordinates'][0]

            self.start = event['start_date']
            self.end = event['end_date']
            self.start_date = self.start.date()
            self.end_date = self.end.date()
            self.start_time = self.start.time()
            self.end_time = self.end.time()

            self.comments = []
            self.attending_ids = []
            self.attendees = []
            print "1"

            self.creator = User(event['creator_id'], mongo)
            print "2"
            if 'comments' in event:
                comments = event['comments']
                for comment in comments:
                    self.comments.append(
                        Comment(mongo,
                                comment['commenter_id'],
                                comment['title'],
                                comment['msg']
                                )
                    )
            print "3"
            if 'attending' in event and type(event['attending']) == list:
                self.attending_ids = event['attending']
            print "4"
        except:
            return None

    # simple string representation of the event
    # used for debugging
    def __str__(self):
        return "[%s %s]" % (self.name, self.id)

    # used with __str__
    def __repr__(self):
        return self.__str__()

    # construct User objects for each event id stored in the Event
    def fillAttendees(self, mongo):
        for uid in self.attending_ids:
            self.attendees.append(User(uid, mongo))

    def escapedDescription(self):
        return self.description.replace("\r", "").replace("\n", "\\n")


# get all of the events to be displayed on the main map page or event list page
def generateEvents(mongo):
    new_events = []
    events = mongo.db.events.find()
    for event in events:
        new_events.append(Event(event['_id'], mongo))

    return new_events


def potentialMasters(mongo):
    return generateEvents(mongo)
