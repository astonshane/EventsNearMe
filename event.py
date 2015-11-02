from pprint import pprint
from flask.ext.pymongo import ObjectId
import random
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
from user import *
from comment import *
from datetime import datetime


# the Event class to store an Event's info
class Event:
    def __init__(self):
        # unique id
        self.id = "42" # initialize the id to 42, because reasons

        self.name = ""
        self.description = ""
        self.tags = ""

        # what we will give to the map
        self.lat = 0
        self.lon = 0
        # the human readable address
        self.address = ""
        self.streetAddress = ""

        # 10/5/15
        self.start_date = ""
        self.end_date = ""
        # 10:00pm
        self.start_time = ""
        self.end_time = ""
        # 20150923T100000
        self.start_datetime = 0
        self.end_datetime = 0

        self.comments = []

        self.creator = None

        self.attending_ids = []
        self.attendees = []

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

# construct an Event object from the mongo storage of it
def eventFromMongo(event, mongo):
    new_event = Event()  # create base event object to add to

    new_event.id = event['_id']
    new_event.name = event['title']
    new_event.description = event['description']
    new_event.tags = event['tags']
    new_event.address = event['location']['address']
    new_event.street_address = event['location']['streetAddress']

    # check if this event already has a location associated with it
    if(('latitude' not in event['location']) or ('longitude' not in event['location'])):
        # we don't have a location, so go get it from google
        searchDict = {"postal_code":"12180"}  # TODO: make this not just TROY
        # use the google api to get a location from the address
        location = GoogleV3().geocode(new_event.street_address, components=searchDict)
        new_event.lat = location.latitude
        new_event.lon = location.longitude
        mongo.db.events.update({"_id": event['_id']},{"$set":{"location.latitude":new_event.lat,"location.longitude":new_event.lon}})
    else:
        new_event.lat = event['location']['latitude']
        new_event.lon = event['location']['longitude']

    start = event['start_date']
    end = event['end_date']
    new_event.start_date = start.date()
    new_event.end_date = end.date()
    new_event.start_time = start.time()
    new_event.end_time = end.time()

    new_event.creator = User(event['creator_id'], mongo)
    new_event.comments.append(Comment(mongo, new_event.creator.id, "Test comment", "test comment contents"))


    if 'attending' in event and type(event['attending']) == list:
        new_event.attending_ids = event['attending']

    return new_event


# return an Event object from the DB based on its id
def getEvent(mongo, eventid):
    #print eventid
    try:
        event = mongo.db.events.find({'_id': eventid})[0]
        return eventFromMongo(event, mongo)
    except:
        return None

# get all of the events to be displayed on the main map page or event list page
def generateEvents(mongo):
    new_events = []
    events = mongo.db.events.find()
    for event in events:
        new_events.append(eventFromMongo(event, mongo))

    return new_events
