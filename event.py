from pprint import pprint
import random


class Event:
    def __init__(self):
        # unique id (will eventuall be from mongo)
        self.id = "42"

        self.name = ""
        self.description = ""
        self.tags = []

        # what we will give to the map
        self.lat = 0
        self.lon = 0
        # the human readable address
        self.address = ""

        # 10/5/15
        self.start_date = ""
        self.end_date = ""
        # 10:00pm
        self.start_time = ""
        self.end_time = ""
        # 20150923T100000
        self.start_datetime = 0
        self.end_datetime = 0

    def __str__(self):
        return "{%s (%f, %f)}" % (self.name, self.lat, self.lon)

    def __repr__(self):
        return self.__str__()


def constructTestEvents(mongo):
    random.seed()  # used to generate bogus lat/lon cords for tests

    new_events = []
    events = mongo.db.events.find()
    for event in events:
        new_event = Event()

        new_event.id = event['_id']
        new_event.name = event['summary']
        new_event.description = event['description']
        new_event.tags = event['categories']

        # generate random cordinates in these ranges to that it pops up @RPI
        new_event.lat = random.uniform(42.727, 42.737)
        new_event.lon = random.uniform(-73.676, -73.686)
        new_event.address = event['location']['address']

        start = event['start']
        end = event['end']

        new_event.start_date = start['shortdate']
        new_event.end_date = end['shortdate']
        new_event.start_time = start['time']
        new_event.end_time = end['time']
        new_event.start_datetime = start['shortdate']
        new_event.end_datetime = end['shortdate']

        print new_event.name, new_event.address
        new_events.append(new_event)

    return new_events
