from pprint import pprint
from flask.ext.pymongo import ObjectId
import random
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3

class Event:
    def __init__(self):
        # unique id (will eventuall be from mongo)
        self.id = "42"

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

        self.comments = [1,2,3]

        self.creator_id = ""

    def __str__(self):
        return "{%s (%f, %f)}" % (self.name, self.lat, self.lon)

    def __repr__(self):
        return self.__str__()


def eventFromMongo(event, mongo):
    new_event = Event()

    new_event.id = event['_id']
    new_event.name = event['title']
    new_event.description = event['description']
    new_event.tags = event['tags']
    new_event.address = event['location']['address']
    new_event.street_address = event['location']['streetAddress']

    if(('latitude' not in event['location']) or ('longitude' not in event['location'])):
        searchDict = {"postal_code":"12180"}
        location = GoogleV3().geocode(new_event.street_address, components=searchDict)
        new_event.lat = location.latitude
        new_event.lon = location.longitude
        mongo.db.events.update({"_id": event['_id']},{"$set":{"location.latitude":new_event.lat,"location.longitude":new_event.lon}})
    else:
        new_event.lat = event['location']['latitude']
        new_event.lon = event['location']['longitude']

    start = event['start_date'].split(" ")
    end = event['end_date'].split(" ")

    new_event.start_date = start[0]
    new_event.end_date = end[0]

    new_event.start_time = "%s %s" % (start[1], start[2])
    new_event.end_time = "%s %s" % (end[1], end[2])

    new_event.creator_id = event['creator_id']

    return new_event


def getEvent(mongo, eventid):
    print eventid
    try:
        event = mongo.db.events.find({'_id': eventid})[0]
        print event
        return eventFromMongo(event, mongo)
    except:
        return None


def generateEvents(mongo):
    new_events = []
    events = mongo.db.events.find()
    for event in events:
        new_events.append(eventFromMongo(event, mongo))

    return new_events
