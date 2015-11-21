# flask imports
from flask.ext.pymongo import PyMongo
from flask import Flask, request, render_template, abort, jsonify, redirect, url_for, session
# base python imports
import json
import uuid
import random
from bson.json_util import dumps
from datetime import datetime
# EventsNear.me imports
from event import *
from user import *
from forms import *


# parses comment data
def parseComment(form):
    commenter_id = session['uid']
    comment = {
        "_id": str(uuid.uuid4()),
        "commenter_id": commenter_id,
        "title": form['title'].data.decode('unicode-escape'),
        "msg": form['msg'].data.decode('unicode-escape'),
    }
    return comment


# parses event data
def parseEvent(form, uid=str(uuid.uuid4())):
    # split up the tags data into a list
    items = form['items'].data.strip().split(',')
    for i in range(0, len(items)):
        items[i] = {"name": items[i], "user": ""}

    tags = form['tags'].data.split(',')
    for i in range(0, len(tags)):
        # strip each element of whitespace and convert to lowercase
        tags[i] = tags[i].strip().lower()

    creator_id = session['uid']  # get the creating user's id
    # construct the event info object to be inserted into db
    event = {
        "_id": uid,
        "creator_id": creator_id,
        "title": form['title'].data.decode('unicode-escape'),
        "description": form['description'].data.decode('unicode-escape'),
        "advice_tips": form['advice_tips'].data.decode('unicode-escape'),
        "location": {
            "address": form['address'].data.decode('unicode-escape'),
            "streetAddress": form['street_address'].data.decode('unicode-escape'),
            "loc": {
                "type": "Point",
                "coordinates": [
                    float(form['lng'].data),
                    float(form['lat'].data)
                ]
            }
        },
        "start_date": datetime.strptime(
            form['start_datetime'].data, "%m/%d/%Y, %I:%M:%S %p"),
        "end_date": datetime.strptime(
            form['end_datetime'].data, "%m/%d/%Y, %I:%M:%S %p"),
        "tags": tags,
        "attending": [creator_id],

        "picture": form['picture'].data,
        "master": form['master'].data,
        "items": items
    }
    print event['start_date']
    return event

def modifyEvent(mongo, form, uid):
    evt = mongo.db.events.event = mongo.db.events.find({'_id': uid})[0]

    # split up the tags data into a list
    items = form['items'].data.strip().split(',')
    # create dictionary of items already in event
    oldItems = {val['name']: val for val in evt['items']}
    # iterate through items
    for i in range(len(items)):
		# if item name is already in event keep the old data
        if items[i] in oldItems.keys():
			items[i] = oldItems[items[i]]
		# insert new item into database
        else:
            items[i] = {"name" : items[i], "user" : ""}

    tags = form['tags'].data.split(',')
    for i in range(0, len(tags)):
        # strip each element of whitespace and convert to lowercase
        tags[i] = tags[i].strip().lower()

    creator_id = session['uid']  # get the creating user's id
    # construct the event info object to be inserted into db
    event = {
        "_id": uid,
        "creator_id": creator_id,
        "title": form['title'].data.decode('unicode-escape'),
        "description": form['description'].data.decode('unicode-escape'),
        "advice_tips": form['advice_tips'].data.decode('unicode-escape'),
        "location": {
            "address": form['address'].data.decode('unicode-escape'),
            "streetAddress": form['street_address'].data.decode('unicode-escape'),
            "loc": {
                "type": "Point",
                "coordinates": [
                    float(form['lng'].data),
                    float(form['lat'].data)
                ]
            }
        },
        "start_date": datetime.strptime(
            form['start_datetime'].data, "%m/%d/%Y, %I:%M:%S %p"),
        "end_date": datetime.strptime(
            form['end_datetime'].data, "%m/%d/%Y, %I:%M:%S %p"),
        "tags": tags,
        "attending": [creator_id],

        "picture": form['picture'].data,
        "master": form['master'].data,
        "items": items,
        # "comments" : evt['comments']
    }
    print event['start_date']
    if 'comments' in evt:
		event['comments'] = evt['comments']
    return event



def fillEventForm(form, event):
    form['title'].data = event.name
    form['description'].data = event.escapedDescription()
    form['address'].data = event.address
    form['street_address'].data = event.street_address
    form['tags'].data = ", ".join(event.tags)
    form['advice_tips'].data = event.escapedAdviceTips()

    form['start_datetime'].data = event.start.strftime("%m/%d/%y %H:%M:%S")
    form['end_datetime'].data = event.end.strftime("%m/%d/%y %H:%M:%S")
    
    form['lat'].data = event.lat
    form['lng'].data = event.lon

    form['picture'].data = event.picture
    
    items = ""
    # Get the names of items from the item object
    for item in event.items:
        items = items + item.itemName + ','
    form['items'].data = items[:-1]

    if event.master is not None:
        form['master'].data = event.master.id
    else:
        form['master'].data = "None"

    return form

