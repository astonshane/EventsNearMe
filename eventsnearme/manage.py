# manage.py

from flask.ext.script import Manager, prompt, prompt_pass
from server import app
from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
import md5
import json
import eventful
import json
import pprint

manager = Manager(app)


@manager.command
def hello(name):
    "just say hello"
    print "hello"


@manager.command
def setup():
    print "Entering Setup..."
    gmail_email = prompt(name="Gmail Username")
    gmail_password = prompt_pass(name="Gmail Password")
    sitename = prompt(name="sitename")
    data = {
        "gmail_email": gmail_email,
        "gmail_password": gmail_password,
        "sitename": sitename
    }

    with open('config.json', 'w') as outfile:
        json.dump(data, outfile)


@manager.command
def createAdmin():
    "Create an Admin User"
    print "Creating Admin User..."
    fname = prompt(name="First Name")
    lname = prompt(name="Last Name")
    email = prompt(name="Email")
    password = prompt_pass(name="password")

    name = {"last": lname,
            "first": fname}

    client = MongoClient()
    db = client.mydb
    users = db.users

    uid = str(uuid.uuid4())
    salt = str(uuid.uuid4())
    m = md5.md5()
    m.update(unicode(salt)+password)
    hashed = m.hexdigest()

    admin = {
        "_id": uid,
        "hash": hashed,
        "name": name,
        "admin": False,
        "salt": salt,
        "email": email,
        "admin": True,
        "tags": [],
        "picture": "http://lorempixel.com/g/250/250/"
    }

    users.insert_one(admin)


@manager.command
def getEvents():
    "Get new events from Eventful"
    print "Get new events using the Eventful api..."
    location = prompt(name="Location")
    radius = prompt(name="Radius (miles)")

    api = eventful.API(json.loads(open('config.json').read())['eventful_api_key'])

    # If you need to log in:
    # api.login('username', 'password')

    client = MongoClient()
    db = client.mydb

    events = api.call('/events/search', l=location, within=radius, units='miles', page_size="100")
    pc = int(events['page_count'])
    total_items = int(events['total_items'])

    print "total_items = %d" % total_items
    print "number of pages = %d" % pc

    to_collect = int(prompt(name="Number of items to collect (< %d)" % total_items))
    insert_count = 0

    for i in range(1, pc+1):
        if insert_count >= to_collect:
            break
        print "getting page %d" % i
        events = api.call('/events/search', l=location, within=radius, units='miles', page_size="100", page_number=str(i), sort_order="date")
        print "got page %d" % i
        for event in events.get('events', {}).get('event', {}):
            if insert_count >= to_collect:
                break
            # print "%s at %s" % (event['title'], event['venue_name'])
            # pprint.pprint(event)

            new_event = {}
            new_event['_id'] = event.get('id', str(uuid.uuid4()))
            new_event['creator_id'] = 'eventful'
            new_event['title'] = event.get('title', "Untitled Event")
            new_event['description'] = event.get('description', "No description available")
            new_event['tags'] = []

            location = {}
            try:
                location['loc'] = {
                    "type": "Point",
                    "coordinates": [
                        float(event.get('longitude', 0)),
                        float(event.get('latitude', 0))
                    ]
                }
            except:
                print type(event.get('longitude'), 0)
                continue
            location['address'] = event.get('venue_name')
            location['streetAddress'] = "%s %s, %s %s" % (event.get('venue_address'), event.get('city_name'), event.get('region_abbr'), event.get('postal_code'))
            new_event['location'] = location

            start_time = datetime.strptime(event.get('start_time'), "%Y-%m-%d %H:%M:%S")
            end_time = start_time + timedelta(hours=2)
            new_event['start_date'] = start_time
            new_event['end_date'] = end_time

            new_event['picture'] = ""
            if event.get("image"):
                new_event['picture'] = event['image']['medium']['url']

            # pprint.pprint(new_event)

            try:
                db.events.insert_one(new_event)
                insert_count += 1
            except:
                pass
    print "Inserted %d events into the database" % insert_count

if __name__ == "__main__":
    manager.run()
