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
    api = eventful.API(json.loads(open('config.json').read())['eventful_api_key'])

    # If you need to log in:
    # api.login('username', 'password')

    events = api.call('/events/search', l='12180', within='10', units='miles')
    for event in events['events']['event']:
        # print "%s at %s" % (event['title'], event['venue_name'])
        # pprint.pprint(event)

        new_event = {}
        new_event['_id'] = str(uuid.uuid4())
        new_event['creator_id'] = 'eventful'
        new_event['title'] = event.get('title', "Untitled Event")
        new_event['description'] = event.get('description', "No description available")
        new_event['tags'] = []

        location = {}
        location['loc'] = {
            "type": "Point",
            "coordinates": [
                event.get('longitude', 0),
                event.get('latitude', 0)
            ]
        }
        location['address'] = event.get('venue_name')
        location['streetAddress'] = "%s %s, %s %s" % (event.get('venue_address'), event.get('city_name'), event.get('region_abbr'), event.get('postal_code'))
        new_event['location'] = location

        start_time = datetime.strptime(event.get('start_time'), "%Y-%m-%d %H:%M:%S")
        end_time = start_time + timedelta(hours=2)
        event['start_date'] = start_time
        event['end_date'] = end_time

        new_event['picture'] = ""
        if event.get("image"):
            new_event['picture'] = event['image']['medium']['url']

        pprint.pprint(new_event)

if __name__ == "__main__":
    manager.run()
