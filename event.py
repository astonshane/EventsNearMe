# EventsNear.me imports
from user import *
from comment import *


# the Event class to store an Event's info
class Event:
    def __init__(self, uid="42", mongo=None):
        try:
            event = mongo.db.events.event = mongo.db.events.find({'_id': uid})[0]

            self.id = event['_id']
            self.name = event['title']
            self.description = event['description']
            self.tags = event['tags']

            self.address = event['location']['address']
            self.address = event['location']['streetAddress']

            self.lat = event['location']['loc']['coordinates'][1]
            self.lon = event['location']['loc']['coordinates'][0]

            start = event['start_date']
            end = event['end_date']
            self.start_date = start.date()
            self.end_date = end.date()
            self.start_time = start.time()
            self.end_time = end.time()

            self.comments = []
            self.attending_ids = []
            self.attendees = []

            self.creator = User(event['creator_id'], mongo)
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

            if 'attending' in event and type(event['attending']) == list:
                self.attending_ids = event['attending']
        except:
            return None

    # simple string representation of the event
    # used for debugging
    def __str__(self):
        return "{%s (%f, %f)}" % (self.name, self.lat, self.lon)

    # used with __str__
    def __repr__(self):
        return self.__str__()

    # construct User objects for each event id stored in the Event
    def fillAttendees(self, mongo):
        for uid in self.attending_ids:
            self.attendees.append(User(uid, mongo))


# get all of the events to be displayed on the main map page or event list page
def generateEvents(mongo):
    new_events = []
    events = mongo.db.events.find()
    for event in events:
        new_events.append(Event(event['_id'], mongo))

    return new_events
