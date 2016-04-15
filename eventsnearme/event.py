# base python imports
from datetime import datetime
import time
# EventsNear.me imports
from user import *
from comment import *
from item import *


# the Event class to store an Event's info
class Event:
    # constructor for event; takes in id and mongo instances
    def __init__(self, uid="42", mongo=None):
        try:
            # find the matching event in the db
            event = mongo.db.events.event = mongo.db.events.find({'_id': uid})[0]

            self.id = event['_id']

            self.name = event['title']
            self.description = event.get('description', "No Description available")
            if 'advice_tips' in event:
                self.advice_tips = event['advice_tips']
            else:
                self.advice_tips = ""
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

            d = datetime.now()
            e = self.end.replace(tzinfo=None)
            self.expired = e < d

            self.comments = []
            self.attending_ids = []
            self.attendees = []


            if 'picture' in event:
                self.picture = event['picture']
            else:
                self.picture = ""

            self.master = None
            if 'master' in event and event['master'] != "None":
                self.master = MasterEvent(event['master'], mongo)

            self.creator = User(event['creator_id'], mongo)
            # parse the comments for this event, if there are any
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

            self.items = event.get('items', [])
            self.cost = event.get('cost', 0)

            if len(items) > 0:
                self.items = []
                # parse the items for this event, if there are any
                for item in items:
                    self.items.append(Item(mongo, item['user'], item['name']))
            # calls the load() for MasterEvent if this is an instance of MasterEvent
            self.load(mongo)

        except Exception as e:
            print "Exception found: ", e
            return None

    # simple string representation of the event
    def __str__(self):
        return "[%s %s]" % (self.name, self.id)

    # used with __str__
    def __repr__(self):
        return self.__str__()

    # return the url for the picture for this event
    def getPicture(self):
        if self.picture != "":
            # the creator supplied a picture to use
            return self.picture
        else:
            # the creator did not supply a picture, so use the LoremPixel url
            #   this is a random picture that loads
            return "http://lorempixel.com/g/250/250/"

    # no need to define this function in Event, is defined in MasterEvent,
    #   which uses the same constructor
    def load(self, mongo):
        pass

    # construct User objects for each event id stored in the Event
    def fillAttendees(self, mongo):
        for uid in self.attending_ids:
            self.attendees.append(User(uid, mongo))

    # escapes the description text
    def escapedDescription(self):
        return self.description.replace("\r", "").replace("\n", "\\n")

    # escapes the advice tips text
    def escapedAdviceTips(self):
        return self.advice_tips.replace("\r", "").replace("\n", "\\n")


# MasterEvent class; inherits from the Event class
class MasterEvent(Event):
    # defines the laod() function that is called during the constructor
    #   queries the db to find any events that this event is the master of
    def load(self, mongo):
        self.children = []
        cursor = mongo.db.events.find({"master": self.id})
        for child in cursor:
            self.children.append({
                "id": child['_id'],
                "name": child['title']
            })


# returns a boolean for if the event is a mster or not
#   Queries the db to see if any events reference this one as the master
def isMaster(eventid, mongo):
    cursor = mongo.db.events.find({"master": eventid})
    return cursor.count() > 0


# get all of the events to be displayed on the main map page or event list page
def generateEvents(mongo, find_all=False):
    new_events = []
    events = None
    if find_all:
        events = mongo.db.events.find({})
    else:
        events = mongo.db.events.find({
            "end_date": {"$gte": datetime.now()}
        })
    for event in events:
        new_events.append(Event(event['_id'], mongo))

    return new_events


# returns a list of all of the events that could be Master Events
#       i.e. events that are are not this one, and events that do not already have a Master Event
#               of their own
def potentialMasters(mongo, eventid=None):
    allevents = generateEvents(mongo)
    potentials = []
    for event in allevents:
        # only events that don't already have a master can be potential masters
        if event.master is None and event.id != eventid:
            potentials.append(event)
    return potentials
