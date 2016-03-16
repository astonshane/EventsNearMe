# Python web server built using Flask:
#   http://flask.pocoo.org/docs/0.10/license/

# flask imports
from flask.ext.pymongo import PyMongo
from flask import Flask, request, render_template, abort, jsonify, redirect, url_for, session, flash
from flaskext.markdown import Markdown
from flask.ext.mail import Mail, Message
# base python imports
import os
import string
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
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD')
    )
mail = Mail(app)


# the main map page (controller)
@app.route("/")
def map():
    checkLoggedIn(mongo)
    # access the events model
    return render_template("map.html", events=generateEvents(mongo))  # render the view


@app.route("/auth/login/", methods=['GET', 'POST'])
def auth_login():
    if checkLoggedIn(mongo):
        return redirect(url_for('map'))
    form = loginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            cursor = mongo.db.users.find({"email": request.form['email']})
            if cursor.count() == 0:
                flash("No accout associated with this email!", "error")
            else:
                for c in cursor:
                    hashed = c['hash']
                    salt = c['salt']
                    m = md5.md5()
                    m.update(unicode(salt)+request.form['password'])
                    submitted_hash = m.hexdigest()
                    if hashed != submitted_hash:
                        flash("Email & Password do not match!", "error")
                    else:
                        session['logged_in'] = True
                        session['uid'] = c['_id']
                        session['name'] = User(c['_id'], mongo).fullName()
                        session.modified = True
                        return redirect(url_for('map'))
    return render_template("login_register.html", active="login", form=form, form2=registerForm(request.form))


@app.route("/auth/register/", methods=['GET', 'POST'])
def auth_register():
    form = loginForm(request.form)
    if checkLoggedIn(mongo):
        return redirect(url_for('map'))
    form2 = registerForm(request.form)
    if request.method == 'POST':
        if form2.validate():
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
                    "admin": False,
                    "email": request.form['email']
                }
                mongo.db.users.insert_one(new_user)
                flash("Account created! Please Login", "success")
                return redirect(url_for('auth_login'))
            else:
                return render_template("login_register.html", active="register", form=form, form2=form2, duplicateEmail=True)
    return render_template("login_register.html", active="register", form=form, form2=form2)


# logout page
@app.route("/auth/logout/")
def logout():
    checkLoggedIn(mongo)
    session.clear()
    session.modified = True
    return redirect(url_for('auth_login'))


# the event list page (controller)
@app.route("/events/", methods=['GET', 'POST'])
def events():
    checkLoggedIn(mongo)
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
    return render_template("eventsList.html", events=generateEvents(mongo))  # render the view


# event specific pages (controller)
@app.route("/event/<eventid>", methods=['GET', 'POST'])
def event(eventid):
    # access the events model
    loggedIn = checkLoggedIn(mongo)
    event = Event(eventid, mongo)
    try:
        event.attending_ids
    except:
        flash("This event doesn't exist!", "error")
        abort(404)  # the given eventid doesn't exist, 404
    if event is None:
        flash("This event doesn't exist!", "error")
        abort(404)  # the given eventid doesn't exist, 404

    # check if the user is currently attending
    if loggedIn:
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
                print "this is only a tst"
                flash("Successfully added a comment!", "success")
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
    uid = session.get('uid', None)
    return render_template("event.html", event=event, form=form, uid=uid)


# route to join an event (controller)
@app.route("/join/<eventid>")
def join(eventid):
    # access the events model
    if not checkLoggedIn(mongo):  # ensure the user is logged in
        flash("You must be logged in to join and event!", "error")
        return redirect(url_for('map'))  # redirect to the main page if not

    # access the events model
    event = Event(eventid, mongo)  # get the event from the DB
    if event is None:
        flash("Stop trying to join an event that doesn't exist!", "error")
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
    flash("Successfully joined the event!", "success")

    # return to the event page for this event
    return redirect(request.referrer)


# route to leave an event (controller)
@app.route("/leave/<eventid>")
def leave(eventid):
    # access the events model
    if not checkLoggedIn(mongo):  # ensure the user is logged in
        flash("You must be logged in to leave an event!", "error")
        return redirect(url_for('auth_login'))  # redirect to main page if not

    # access the events model
    event = Event(eventid, mongo)  # get the evnet from the DB
    if event is None:
        flash("Stop trying to leave an event that doen't exist!", "error")
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
    flash("Successfully left the event!", "success")

    # return to the event page for this event
    return redirect(request.referrer)


# route to remove an event (controller)
@app.route("/remove/event/<eventid>")
def remove(eventid, suppress=False):
    if not checkLoggedIn(mongo):  # ensure the user is logged in
        flash("You must be logged in to remove an event!", "error")
        return redirect(url_for('auth_login'))  # redirect to main page if not

    event = Event(eventid, mongo)  # get the event so we can see its owner

    if session['uid'] == event.creator.id or session.get('admin', False):
        # if the owner is not this user, they can't delete it
        # delete the event itself
        # modify the events model
        mongo.db.events.remove({"_id": eventid})
        # remove this event as master anywhere where it was
        # update the events model
        mongo.db.events.update(
            {"master": eventid},
            {"$set": {"master": "None"}}
        )
    else:
        flash("You must be the event owner to delete this event!", "error")
        return redirect(request.referrer)

    if "/event/" in request.referrer:
        return redirect(url_for('map'))
    if not suppress:
        flash("Successfully removed the event!", "success")
    return redirect(request.referrer)


@app.route("/remove/event/allExpired")
def removeAll():
    if not checkLoggedIn(mongo) or not session.get('admin', False):  # ensure the user is logged in
        flash("You must be logged in as an Admin to remove an event!", "error")
        return redirect(url_for('auth_login'))  # redirect to main page if not

    all_events = generateEvents(mongo, True)
    count = 0
    for event in all_events:
        if event.expired:
            count += 1
            remove(event.id, True)

    flash("Successfully removed all %d expired events!" % count, "success")
    return redirect(request.referrer)


@app.route("/remove/user/<userid>")
def removeUser(userid):
    if not checkLoggedIn(mongo):
        flash("You must be logged in to remove a user!", "error")
        return redirect(url_for('auth_login'))

    user = User(userid, mongo)

    if session.get('admin', False) and session.get('uid') != userid:
        # this person has permission to remove the user
        # remove the user
        #   remove any events the user owned first
        cursor = mongo.db.events.find({'creator_id': userid})
        for c in cursor:
            mongo.db.events.remove({'_id': c['_id']})
            mongo.db.events.update(
                {"master": c['_id']},
                {"$set": {"master": "None"}}
            )
        mongo.db.users.remove({'_id': userid})
    else:
        flash("You don't have permission to remove this user!", "error")
        return redirect(request.referrer)
    flash("Successfully removed user and their associated events!", "success")
    return redirect(request.referrer)


# route for creating an event (controller)
@app.route("/create", methods=['GET', 'POST'])
def createEvent():
    if not checkLoggedIn(mongo):  # ensure the user is logged in
        flash("You must be logged in to create an event!", "error")
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
            flash("Successfully created an event!", "success")
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
    if not checkLoggedIn(mongo):  # ensure the user is logged in
        flash("You must be logged in to edit an event!", "error")
        return redirect(url_for('map'))

    event_ = Event(eventid, mongo)
    if event_.creator.id != session['uid'] and not session.get('admin', False):
        flash("You must be the event owner to edit this event!", "error")
        return redirect(url_for('map'))

    form = createEventForm(request.form)  # load the createEvent form
    # if we got here with a http POST, we are trying to add an event
    if request.method == 'POST':
        if form.validate():  # validate the form data that was submitted
            event = modifyEvent(mongo, form, eventid)
            event.pop("_id", None)
            event['creator_id'] = event_.creator.id
            # insert the event into the DB
            # modify the events model
            mongo.db.events.update(
                {"_id": eventid},
                event
            )
            # redirect the user to the main map page
            flash("Successfully modified an event!", "success")
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


@app.route("/admin/")
def admin():
    if not checkLoggedIn(mongo) or not session.get('admin', False):  # ensure the user is logged in
        flash("You must be logged in as an admin to view this page!", "error")
        return redirect(url_for('map'))

    return render_template(
                "admin.html",
                events=generateEvents(mongo, True),
                users=generateUsers(mongo)
            )


@app.route("/toggleadmin/<uid>")
def toggleAdmin(uid):
    if not checkLoggedIn(mongo) or not session.get('admin', False):  # ensure the user is logged in
        flash("You must be logged in as an admin to view this page!", "error")
        return redirect(url_for('map'))

    user = User(uid, mongo)
    if not user.valid:
        flash("That user doesn't exist!", "error")
        return redirect(url_for('map'))

    if user.id == session.get("uid", None):
        flash("You can't change your own admin status!", "error")
        return redirect(request.referrer)

    mongo.db.users.update(
        {"_id": uid}, {
            "$set": {
                "admin": not user.admin
            }
        }
    )
    flash("Successfully toggled %s's admin status" % user.id, "success")

    return redirect(request.referrer)


@app.route("/resetPassword/", methods=['POST'])
def resetPassword():
    if not checkLoggedIn(mongo):  # ensure the user is logged in
        flash("You must be logged in to edit an event!", "error")
        return redirect(url_for('map'))

    form = changePasswordForm(request.form)
    if form.validate():
        uid = session['uid']
        changePassword(uid, request.form['password1'], mongo)
        flash("Successfully changed password!", "success")
    else:
        flash("Failed to change password! Passwords must match!", "error")
    return redirect(request.referrer)


@app.route("/adminreset/<uid>")
def adminReset(uid):
    if not checkLoggedIn(mongo):
        flash("You must be logged in to edit an event!", "error")
        return redirect(url_for('map'))

    if not session.get('admin', False):
        flash("You must be an admin to use this function!", "error")
        return redirect(url_for('map'))

    user = User(uid, mongo)
    if not user.valid:
        flash("That user doesn't exist!", "error")
        return redirect(url_for('map'))

    newPassword = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(25))

    changePassword(uid, newPassword, mongo)
    msg = Message("EventsNear.me Password Change", )
    msg.sender = os.environ.get('MAIL_USERNAME')
    msg.recipients = [user.email]
    msg.html = """
        <h1>EventsNear.me Password Change</h1>
        <h3>Hello, %s</h3>
        <p>Your new EventsNear.me password is %s</p>
        """ % (user.fullName(), newPassword)
    mail.send(msg)
    flash("Successfully changed %s's password!" % user.id, "success")

    return redirect(request.referrer)


@app.route("/profile/", methods=['GET', 'POST'])
def profile():
    if not checkLoggedIn(mongo):  # ensure the user is logged in
        flash("You must be logged in to edit an event!", "error")
        return redirect(url_for('map'))

    uid = session['uid']

    form1 = addUserTagsForm(request.form)
    form2 = updateProfileForm(request.form)
    if request.method == 'POST':
        if form1.validate():
            newTag = request.form['newTag']
            print newTag
            user = User(uid, mongo)
            newTags = user.tags
            newTags.append(newTag)
            mongo.db.users.update(
                {"_id": uid},
                {"$set": {"tags": newTags}}
            )
            flash("Successfully added an Interest!", "success")
        elif form2.validate():
            email = request.form['email']
            name = {}
            name['first'] = request.form['fname']
            name['last'] = request.form['lname']
            picture = request.form['picture']
            if picture == "":
                picture = "http://lorempixel.com/g/250/250/"
            mongo.db.users.update(
                {"_id": uid}, {
                    "$set": {
                        "name": name,
                        "email": email,
                        "picture": picture
                    }
                }
            )
            session['name'] = User(uid, mongo).fullName()
            session.modified = True

    user = User(uid, mongo)
    userform = fillUserForm(form2, user)

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

    user = User(uid, mongo)
    return render_template(
        "profile_private.html",
        user=user,
        created=created,
        attending=attending,
        userform=userform
        )


@app.route("/removeUserTag/<int:tagId>")
def removeUserTag(tagId):
    if not checkLoggedIn(mongo):  # ensure the user is logged in
        flash("You must be logged in to remove a tag!", "error")
        return redirect(url_for('map'))
    uid = session.get('uid')
    user = User(uid, mongo)
    tags = user.tags
    if tagId < 0 or tagId > len(tags)-1:
        flash("You are trying to remove a tag that doesn't exist!", "error")
        return redirect(url_for("profile"))
    newTags = tags[:tagId]
    newTags.extend(tags[tagId+1:])
    mongo.db.users.update(
        {"_id": uid},
        {"$set": {"tags": newTags}}
    )
    flash("Successfully removed an Interest!", "success")
    return redirect(request.referrer)


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


# the page that will load for any 404s that are called (controller)
@app.errorhandler(404)
def page_not_found(error):
    checkLoggedIn(mongo)
    msgs = ["Sorry", "Whoops", "Uh-oh", "Oops!",
            "You broke it.", "You done messed up, A-a-ron!"]
    choice = random.choice(msgs)  # choose one randomly from above
    return render_template('page_not_found.html', choice=choice), 404  # render the view

if __name__ == "__main__":
    app.secret_key = 'supersecretsecretkey'
    app.run()
