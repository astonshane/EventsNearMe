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


def parse_event(form, mongo):
    # split up the tags data into a list
    tags = form['tags'].data.split(',')
    for i in range(0, len(tags)):
        # strip each element of whitespace and convert to lowercase
        tags[i] = tags[i].strip().lower()
    uid = str(uuid.uuid4())  # asign a new uuid for this event

    creator_id = session['uid']  # get the creating user's id
    # construct the event info object to be inserted into db
    event = {
        "_id": uid,
        "creator_id": creator_id,
        "title": form['title'].data.decode('unicode-escape'),
        "description": form['description'].data.decode('unicode-escape'),
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
            form['start_datetime'].data, "%a, %d %b %Y %H:%M:%S %Z"),
        "end_date": datetime.strptime(
            form['end_datetime'].data, "%a, %d %b %Y %H:%M:%S %Z"),
        "tags": tags,
        "attending": [creator_id],
    }
    return event
