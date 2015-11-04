# flask imports
from flask.ext.pymongo import PyMongo
from flask import Flask, request, render_template, abort, jsonify, redirect, url_for, session
# base python imports
import base64
import json
import uuid
import json
from bson.json_util import dumps
from datetime import datetime
# EventsNear.me imports
from event import *
from user import *
from forms import *

# start flask server
app = Flask("mydb")
app.debug = True
# connect to the pymongo server
mongo = PyMongo(app)


# the main map page
@app.route("/")
def hello():
    checkLoggedIn(mongo)  # must be called in each view
    return render_template("map.html", events=generateEvents(mongo))


# the event list page
@app.route("/events/")
def events():
    checkLoggedIn(mongo)
    return render_template("eventsList.html", events=generateEvents(mongo))


# event specific pages
@app.route("/event/<eventid>", methods=['GET', 'POST'])
def event(eventid):
    loggedIn = checkLoggedIn(mongo)
    event = getEvent(mongo, eventid)
    if event is None:
        abort(404)  # the given eventid doesn't exist, 404

    # check if the user is currently attending
    session['attending'] = (session['uid'] in event.attending_ids)
    session.modified = True

    form = commentForm(request.form)
    if request.method == 'POST' and loggedIn:
        if form.validate():
            commenter_id = session['uid']
            comment = {
                "_id": str(uuid.uuid4()),
                "commenter_id": commenter_id,
                "title": form['title'].data.decode('unicode-escape'),
                "msg": form['msg'].data.decode('unicode-escape'),
            }
            result = mongo.db.events.update({"_id": eventid}, {"$addToSet": {"comments": comment}})
            event = getEvent(mongo, eventid)  #need to get the event again since we changed it

    event.fillAttendees(mongo)  # this page needs access to all of the attending user objects
    return render_template("event.html", event=event, form=form)


# route to join an event
@app.route("/join/<eventid>")
def join(eventid):
    loggedIn = checkLoggedIn(mongo)  # ensure the user is currently logged in
    if not loggedIn:
        return redirect(url_for('hello'))  # redirect to the main page if not

    event = getEvent(mongo, eventid)  # get the event from the DB
    if event is None:
        abort(404)  # if the event doesn't exist, 404

    attending = []
    # if the attendance list is a list, there's already people attending
    if type(event.attending_ids) == list:
        attending = event.attending_ids
        # need to check if this user is already attending before adding them
        if session['uid'] not in event.attending_ids:
            attending.append(session['uid'])
    else:
        # no one is attending yet, so just add this user
        attending.append(session['uid'])

    # update the db with the new attending list
    mongo.db.events.update({"_id": eventid}, {"$set": {"attending": attending}})

    # return to the event page for this event
    return redirect(url_for('event', eventid=eventid))


# route to leave an event
@app.route("/leave/<eventid>")
def leave(eventid):
    loggedIn = checkLoggedIn(mongo)  #ensure the user is currently logged in
    if not loggedIn:
        return redirect(url_for('hello'))  # redirect to main page if not

    event = getEvent(mongo, eventid)  # get the evnet from the DB
    if event == None:
        abort(404) # if the event doesn't exist, 404

    attending = []
    if type(event.attending_ids) == list:
        attending = event.attending_ids # set the new attendance list to the current one
        if session['uid'] in event.attending_ids:
            # remove the current user's id if it exists in the list
            attending = attending.remove(session['uid'])

    # update the DB if it changed
    if attending != event.attending_ids:
        mongo.db.events.update({"_id": eventid}, {"$set": {"attending": attending}})

    # return to the event page for this event
    return redirect(url_for('event', eventid=eventid))



# route for creating an event
@app.route("/create", methods=['GET', 'POST'])
def createEvent():
    loggedIn = checkLoggedIn(mongo)  # ensure the user is logged in
    if not loggedIn:
        return redirect(url_for('hello'))

    form = createEventForm(request.form)  # load the createEvent form

    # if we got here with a http POST, we are trying to add an event
    if request.method == 'POST':
        if form.validate():  # validate the form data that was submitted
            tags = form['tags'].data.split(',')  # split up the tags data into a list
            for i in range(0, len(tags)):
                tags[i] = tags[i].strip()  # strip each element of whitespace
            uid = str(uuid.uuid4())  # asign a new uuid for this event
            # get the creating user's id
            creator_id = parseSignedRequest(request.cookies.get('fbsr_1055849787782314'))
            # construct the event info object to be inserted into db
            event = {
                "_id": uid,
                "creator_id": creator_id,
                "title": form['title'].data.decode('unicode-escape'),
                "description": form['description'].data.decode('unicode-escape'),
                "location": {
                    "address": form['address'].data.decode('unicode-escape'),
                    "streetAddress": form['street_address'].data.decode('unicode-escape'),
                    "loc":{
                        "type":"Point", "coordinates":[float(form['lng'].data),float(form['lat'].data)]
                    }
                },
                "start_date": datetime.strptime(form['start_datetime'].data, "%a, %d %b %Y %H:%M:%S %Z"),
                "end_date": datetime.strptime(form['end_datetime'].data, "%a, %d %b %Y %H:%M:%S %Z"),
                "tags": tags,
            }
            # insert the event into the DB
            result = mongo.db.events.insert_one(event)
            # redirect the user to the main map page
            return redirect(url_for('hello'))
    # load the create event page if we are loading from a http GET
    # OR if we're loading from a http POST and there was problems with the info
    return render_template("create_event.html", form=form)


# the page that will load for any 404s that are called
@app.errorhandler(404)
def page_not_found(error):
    checkLoggedIn(mongo)
    msgs = ["Sorry", "Whoops", "Uh-oh", "Oops!", "You broke it.", "You done messed up, A-a-ron!"]
    choice = random.choice(msgs) #choose one randomly from above
    return render_template('page_not_found.html', choice=choice), 404


# the login view
@app.route("/login")
def users():
	uid = request.args.get("uid")
	name = request.args.get("name")
	cursor = mongo.db.users.find( {"_id": uid} )
	if cursor.count() == 1:
		return dumps("FOUND IN DB")
	else:
		result = mongo.db.users.insert_one(
			{
				"_id": uid,
				"name": {
					"first": name.split(' ')[0],
					"last": name.split(' ')[1]
				},
				"age": 999,
				"email" : "test@test.com"
			})
		return dumps("ADDED TO DB")

#Filter route to perform database query
@app.route("/filter")
def filter():
    #get AJAX arguments
    startTime = request.args.get("start")
    endTime = request.args.get("end")
    radius = request.args.get("radius").strip()
    lat = request.cookies.get('lat').strip()
    lon = request.cookies.get('lng').strip()
    startdt = datetime.strptime(startTime, "%a, %d %b %Y %H:%M:%S %Z")
    enddt = datetime.strptime(endTime, "%a, %d %b %Y %H:%M:%S %Z")
    tags = request.args.get("tags");
    filters = json.loads(tags);

    if(len(filters) == 0):
        cursor = mongo.db.events.find({
            "start_date": { "$gte": startdt },
            "end_date": { "$lte": enddt},
            "location.loc":{"$geoWithin":{"$centerSphere": [[float(lon), float(lat)], float(radius)/3963.2]}}})
    else:
        cursor = mongo.db.events.find( {
            "start_date": { "$gte": startdt },
            "end_date": { "$lte": enddt},
            "tags": {'$in':filters},
            "location.loc":{"$geoWithin":{"$centerSphere": [[float(lon), float(lat)], float(radius)/3963.2]}}})

    toSend = []
    print "PRINTING"
    for i in cursor:
    	toSend.append(i)
    	print i

    print "ENDPRINTING"
    return dumps(toSend)


if __name__ == "__main__":
    app.secret_key = 'supersecretsecretkey'
    app.run()
