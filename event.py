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

    def __str__(self):
        return "{%s (%f, %f)}" % (self.name, self.lat, self.lon)

    def __repr__(self):
        return self.__str__()


def eventFromMongo(event):
    new_event = Event()
    new_event.id = event['_id']
    new_event.name = event['summary']
    new_event.description = event['description']
    new_event.tags = event['categories']

    searchDict = {"postal_code":"12180"}
    new_event.address = event['location']['address']
    new_event.streetAddress = event['location']['streetAddress']
    new_event.lat = GoogleV3().geocode(new_event.streetAddress, components=searchDict).latitude
    new_event.lon = GoogleV3().geocode(new_event.streetAddress, components=searchDict).longitude
    

    start = event['start']
    end = event['end']

    new_event.start_date = start['shortdate']
    new_event.end_date = end['shortdate']
    new_event.start_time = start['time']
    new_event.end_time = end['time']
    new_event.start_datetime = start['shortdate']
    new_event.end_datetime = end['shortdate']

    return new_event


def getEvent(mongo, eventid):
    try:
        event = mongo.db.events.find_one_or_404({'_id': ObjectId(str(eventid))})
        return eventFromMongo(event)
    except:
        return None


def constructTestEvents(mongo):
    new_events = []
    searchDict = {"postal_code":"12180"}
    geolocator = GoogleV3("AIzaSyAzRBQ8AF5pps6IRNkImoB2UBC_cn3hNUo")
    events = mongo.db.events.find()
    for event in events:
        new_event = Event()

        new_event.id = event['_id']
        new_event.name = event['summary']
        new_event.description = event['description']
        new_event.tags = event['categories']
        new_event.address = event['location']['address']
        new_event.streetAddress = event['location']['streetAddress']

        if(('latitude' not in event['location']) or ('longitude' not in event['location'])):
            location = geolocator.geocode(new_event.streetAddress, components=searchDict)
            new_event.lat = location.latitude
            new_event.lon = location.longitude
            mongo.db.events.update({"_id": event['_id']},{"$set":{"location.latitude":new_event.lat,"location.longitude":new_event.lon}})
        else:
            new_event.lat = event['location']['latitude']
            new_event.lon = event['location']['longitude']

        start = event['start']
        end = event['end']

        new_event.start_date = start['shortdate']
        new_event.end_date = end['shortdate']
        new_event.start_time = start['time']
        new_event.end_time = end['time']
        new_event.start_datetime = start['shortdate']
        new_event.end_datetime = end['shortdate']

        new_events.append(new_event)

    return new_events
