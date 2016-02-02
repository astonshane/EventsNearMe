# Python web server built using Flask:
#   http://flask.pocoo.org/docs/0.10/license/

# flask imports
from flask.ext.pymongo import PyMongo
from flask import Flask, request, render_template, abort, jsonify, redirect, url_for, session
from flaskext.markdown import Markdown
# base python imports
import json
import md5
import uuid
import random
from bson.json_util import dumps
from datetime import datetime, timedelta
# EventsNear.me imports
from event import *
from user import *
from forms import *
from form_parsers import *

# start flask server
app = Flask("mydb")
app.debug = True
# connect to the pymongo server
mongo = PyMongo(app)
markdown = Markdown(app, safe_mode=True, output_format='html5',)

'''
MVC Design Pattern Documentation:
    - In this project, the Flask server defined here is the "Controller" part of the MVC
    - More Specifically, each route defined bellow is its own controller, which completes any
        interactions with the database (the Models) and updates the Views via render_template()
'''


# the main map page (controller)
@app.route("/")
def map():
    # access the events model
    checkLoggedIn(mongo)  # must be called in each view
    return render_template("map.html", events=generateEvents(mongo))  # render the view


# login page
@app.route("/login/", methods=['GET', 'POST'])
def login():
    checkLoggedIn(mongo)
    form = loginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            cursor = mongo.db.users.find({"email": request.form['email']})
            if cursor.count() == 0:
                return render_template("login.html", form=form, err_msg="No account found with this email!")
            for c in cursor:
                hashed = c['hash']
                salt = c['salt']

                m = md5.md5()
                m.update(unicode(salt)+request.form['password'])
                submitted_hash = m.hexdigest()
                if hashed != submitted_hash:
                    return render_template("login.html", form=form, err_msg="Email & Password do not match!")

                session['logged_in'] = True
                session['uid'] = c['_id']
                session['name'] = User(c['_id'], mongo).fullName()
                session.modified = True
                return redirect(url_for('map'))

    return render_template("login.html", form=form)


# logout page
@app.route("/logout/")
def logout():
    checkLoggedIn(mongo)
    session.clear()
    session.modified = True
    return redirect(url_for('login'))


# register page
@app.route("/register/", methods=['GET', 'POST'])
def register():
    checkLoggedIn(mongo)
    form = registerForm(request.form)
    if request.method == 'POST':
        if form.validate():
            cursor = mongo.db.users.find({"email": request.form['email']})
            if cursor.count() == 0:
                uid = str(uuid.uuid4())
                salt = str(uuid.uuid4())
                m = md5.md5()
                m.update(unicode(salt)+request.form['password1'])
                hashed = m.hexdigest()
                new_user = {
                    "_id": uid,
                    "salt": salt,
                    "hash": hashed,
                    "name": {
                        "first": request.form['fname'],
                        "last": request.form['lname'],
                    },
                    "email": request.form['email']
                }
                mongo.db.users.insert_one(new_user)
                # TODO log the user in
                return redirect(url_for('login'))
            else:
                return render_template("register.html", form=form, duplicateEmail=True)

    return render_template("register.html", form=form)


# the event list page (controller)
@app.route("/events/", methods=['GET', 'POST'])
def events():
    # post gathers info for filtering
    if request.method == "POST":
        if len(str(request.form["tags2"])) == 0:
            tags = ""
        else:
            tags = str(request.form['tags2']).split(',')
            for i in range(0, len(tags)):
                # strip each element of whitespace and convert to lowercase
                tags[i] = tags[i].strip().lower()

        # parse the dates from the datetimepicker
        st = datetime.strptime(request.form["startdt"], "%a, %d %b %Y %H:%M:%S %Z")
        end = datetime.strptime(request.form["enddt"], "%a, %d %b %Y %H:%M:%S %Z")

        # query the db for events that match the filtering requests
        # access the events model
        cursor = performQuery(
            st,
            end,
            request.form["radius2"],
            request.cookies.get("lat"),
            request.cookies.get("lng"),
            tags
        )
        # create event objects from each of the matching events
        ev = []
        for c in cursor:
            # modify the events model
            ev.append(Event(c['_id'], mongo))
        return render_template("eventsList.html", events=ev)

    # access the events model
    checkLoggedIn(mongo)
    return render_template("eventsList.html", events=generateEvents(mongo))  # render the view


# the My Events page (list of all events the user created or is attending) (controller)
@app.route("/myevents")
def myevents():
    # access the events model
    loggedIn = checkLoggedIn(mongo)  # ensure the user is currently logged in
    if not loggedIn:
        return redirect(url_for('map'))  # redirect to the main page if not

    uid = session['uid']

    created = []  # events the user created
    attending = []  # events the user is attending

    # find the events where this user is the creator
    # access the events model
    cursor = mongo.db.events.find({
        "creator_id": uid,
        "end_date": {"$gte": datetime.now()}
    })
    for c in cursor:
        created.append(Event(c['_id'], mongo))

    # find the events where that this user is attending
    # access the events model
    cursor = mongo.db.events.find({
        "attending": session['uid'],
        "end_date": {"$gte": datetime.now()}
    })
    for c in cursor:
        # modify the events model
        attending.append(Event(c['_id'], mongo))

    return render_template("myevents.html", created=created, attending=attending)  # render the view


# event specific pages (controller)
@app.route("/event/<eventid>", methods=['GET', 'POST'])
def event(eventid):
    # access the events model
    loggedIn = checkLoggedIn(mongo)
    event = Event(eventid, mongo)
    try:
        event.attending_ids
    except:
        abort(404)  # the given eventid doesn't exist, 404
    if event is None:
        abort(404)  # the given eventid doesn't exist, 404

    # check if the user is currently attending
    session['attending'] = (session['uid'] in event.attending_ids)
    session.modified = True
    form = commentForm(request.form)
    if('index' in request.form):
        # handle registry item claiming/unclaiming
        # build item query string
        itempos = request.form['index']
        itempos = str(int(itempos) - 1)
        query = 'items.' + (itempos) + '.user'
        # User clicked on an unclaimed item
        if request.form['value'] != "":
            mongo.db.events.update({'_id': eventid}, {'$set': {query: session['uid']}})
        # User clicked on their own item to unclaim it
        else:
            mongo.db.events.update({'_id': eventid}, {'$set': {query: ""}})

    else:
        # handle a comment submit
        if request.method == 'POST' and loggedIn:
            if form.validate():
                comment = parseComment(form)
                mongo.db.events.update(
                    {"_id": eventid},
                    {"$addToSet": {"comments": comment}}
                )
    # need to get the event again since we changed it
    # access the events model
    event = Event(eventid, mongo)

    # make event a master event if if necessary...
    # access the events model
    if isMaster(eventid, mongo):
        # Polymprphism: event is now an instance of MasterEvent, but can be treated like a normal
        #  event in the view
        event = MasterEvent(eventid, mongo)

    # this page needs access to all of the attending user objects
    # access the events model
    event.fillAttendees(mongo)
    # render the view
    return render_template("event.html", event=event, form=form, uid=session['uid'])


# route to join an event (controller)
@app.route("/join/<eventid>")
def join(eventid):
    # access the events model
    loggedIn = checkLoggedIn(mongo)  # ensure the user is currently logged in
    if not loggedIn:
        return redirect(url_for('map'))  # redirect to the main page if not

    # access the events model
    event = Event(eventid, mongo)  # get the event from the DB
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
    # access the events model
    mongo.db.events.update(
        {"_id": eventid},
        {"$set": {"attending": attending}}
    )

    # return to the event page for this event
    return redirect(request.referrer)


# route to leave an event (controller)
@app.route("/leave/<eventid>")
def leave(eventid):
    # access the events model
    loggedIn = checkLoggedIn(mongo)  # ensure the user is currently logged in
    if not loggedIn:
        return redirect(url_for('map'))  # redirect to main page if not

    # access the events model
    event = Event(eventid, mongo)  # get the evnet from the DB
    if event is None:
        abort(404)  # if the event doesn't exist, 404

    attending = []
    if type(event.attending_ids) == list:
        # set the new attendance list to the current one
        attending = event.attending_ids
        if session['uid'] in event.attending_ids:
            # remove the current user's id if it exists in the list
            attending = attending.remove(session['uid'])

    # update the DB if it changed
    if attending != event.attending_ids:
        # update the events model
        mongo.db.events.update(
            {"_id": eventid},
            {"$set": {"attending": attending}}
        )

    # return to the event page for this event
    return redirect(request.referrer)


# route to remove an event (controller)
@app.route("/remove/<eventid>")
def remove(eventid):
    loggedIn = checkLoggedIn(mongo)  # ensure the user is currently logged in
    if not loggedIn:
        return redirect(url_for('map'))  # redirect to main page if not

    event = Event(eventid, mongo)  # get the event so we can see its owner

    if session['uid'] == event.creator.id:  # if the owner is not this user, they can't delete it
        # delete the event itself
        # modify the events model
        mongo.db.events.remove({"_id": eventid})
        # remove this event as master anywhere where it was
        # update the events model
        mongo.db.events.update(
            {"master": eventid},
            {"$set": {"master": "None"}}
        )

    if "/event/" in request.referrer:
        return redirect(url_for('map'))
    return redirect(request.referrer)


# route for creating an event (controller)
@app.route("/create", methods=['GET', 'POST'])
def createEvent():
    loggedIn = checkLoggedIn(mongo)  # ensure the user is logged in
    if not loggedIn:
        return redirect(url_for('map'))

    form = createEventForm(request.form)  # load the createEvent form

    # if we got here with a http POST, we are trying to add an event
    if request.method == 'POST':
        if form.validate():  # validate the form data that was submitted
            event = parseEvent(form, str(uuid.uuid4()))
            # insert the event into the DB
            # modify the events model
            mongo.db.events.insert_one(event)
            # redirect the user to the main map page
            return redirect(url_for('event', eventid=event['_id']))
    # load the create event page if we are loading from a http GET
    # OR if we're loading from a http POST and there was problems with the info
    return render_template(
                "create_event.html",
                form=form,
                potentialMasters=potentialMasters(mongo=mongo)
                )  # render the view


# route for editing an Event (controller)
@app.route("/edit/<eventid>", methods=['GET', 'POST'])
def editEvent(eventid):
    loggedIn = checkLoggedIn(mongo)  # ensure the user is logged in
    if not loggedIn:
        return redirect(url_for('map'))

    event_ = Event(eventid, mongo)
    if event_.creator.id != session['uid']:
        return redirect(url_for('map'))

    form = createEventForm(request.form)  # load the createEvent form
    # if we got here with a http POST, we are trying to add an event
    if request.method == 'POST':
        if form.validate():  # validate the form data that was submitted
            event = modifyEvent(mongo, form, eventid)
            event.pop("_id", None)
            # insert the event into the DB
            # modify the events model
            mongo.db.events.update(
                {"_id": eventid},
                event
            )
            # redirect the user to the main map page
            return redirect(url_for('event', eventid=eventid))
        else:
            print "NOT VALIDATED"
    elif request.method == 'GET':
        event = Event(eventid, mongo)
        form = fillEventForm(form, event)

    # load the create event page if we are loading from a http GET
    # OR if we're loading from a http POST and there was problems with the info
    return render_template(
                "edit_event.html",
                form=form,
                eventid=eventid,
                potentialMasters=potentialMasters(mongo, eventid)
            )


# the page that will load for any 404s that are called (controller)
@app.errorhandler(404)
def page_not_found(error):
    checkLoggedIn(mongo)
    msgs = ["Sorry", "Whoops", "Uh-oh", "Oops!",
            "You broke it.", "You done messed up, A-a-ron!"]
    choice = random.choice(msgs)  # choose one randomly from above
    return render_template('page_not_found.html', choice=choice), 404  # render the view


# the login view (controller)
@app.route("/login")
def users():
    uid = request.args.get("uid")
    name = request.args.get("name")
    cursor = mongo.db.users.find({"_id": uid})
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
                "email": "test@test.com"
            })
        return dumps("ADDED TO DB")


# query the db for events that match the filters (controller)
def performQuery(start, end, r, lat, lng, tags):
    if(len(tags) == 0):
        cursor = mongo.db.events.find({
            "start_date": {"$gte": start},
            "end_date": {"$lte": end},
            "location.loc": {
                "$geoWithin": {
                    "$centerSphere": [
                        [float(lng), float(lat)],
                        float(r)/3963.2
                    ]
                }
            }
        })
    else:
        cursor = mongo.db.events.find({
            "start_date": {"$gte": start},
            "end_date": {"$lte": end},
            "tags": {'$in': tags},
            "location.loc": {
                "$geoWithin": {
                    "$centerSphere": [
                        [float(lng), float(lat)],
                        float(r)/3963.2
                    ]
                }
            }
        })
    return cursor


# Filter route to perform database query (controller)
@app.route("/filter")
def filter():
    # get AJAX arguments
    startTime = request.args.get("start")
    endTime = request.args.get("end")
    radius = request.args.get("radius").strip()
    lat = request.cookies.get('lat').strip()
    lon = request.cookies.get('lng').strip()
    startdt = datetime.strptime(startTime, "%a, %d %b %Y %H:%M:%S %Z")
    enddt = datetime.strptime(endTime, "%a, %d %b %Y %H:%M:%S %Z")
    tags = request.args.get("tags")
    filters = json.loads(tags)

    cursor = performQuery(startdt, enddt, radius, lat, lon, filters)

    toSend = []
    for i in cursor:
        toSend.append(i)

    return dumps(toSend)


if __name__ == "__main__":
    app.secret_key = 'supersecretsecretkey'
    app.run()
