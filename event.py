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
            self.advice_tips = event['advice_tips']
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

            self.picture = "http://lorempixel.com/g/250/250/"

            self.master = None
            if 'master' in event and event['master'] != "None":
                self.master = MasterEvent(event['master'], mongo)

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

            self.load(mongo)
        except Exception as e:
            print e
            return None

    # simple string representation of the event
    # used for debugging
    def __str__(self):
        return "[%s %s]" % (self.name, self.id)

    # used with __str__
    def __repr__(self):
        return self.__str__()

    def load(self, mongo):
        pass

    # construct User objects for each event id stored in the Event
    def fillAttendees(self, mongo):
        for uid in self.attending_ids:
            self.attendees.append(User(uid, mongo))

    def escapedDescription(self):
        return self.description.replace("\r", "").replace("\n", "\\n")

    def escapedAdviceTips(self):
        return self.advice_tips.replace("\r", "").replace("\n", "\\n")

class MasterEvent(Event):
    def load(self, mongo):
        print "############### HERE"
        self.children = []
        print "here1"
        cursor = mongo.db.events.find({"master": self.id})
        print "here2"
        print cursor.count()
        for child in cursor:
            self.children.append({
                "id": child['_id'],
                "name": child['title']
            })
        print self.children


def isMaster(eventid, mongo):
    cursor = mongo.db.events.find({"master": eventid})
    return cursor.count() > 0

# get all of the events to be displayed on the main map page or event list page
def generateEvents(mongo):
    new_events = []
    events = mongo.db.events.find()
    for event in events:
        new_events.append(Event(event['_id'], mongo))

    return new_events


def potentialMasters(mongo, eventid=None):
    allevents = generateEvents(mongo)
    potentials = []
    for event in allevents:
        # only events that don't already have a master can be potential masters
        if event.master is None and event.id != eventid:
            potentials.append(event)
    return potentials
