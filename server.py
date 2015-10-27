from flask.ext.pymongo import PyMongo
from flask import Flask, request, render_template, abort, jsonify, request, redirect, url_for, session

import base64
import json
import uuid
from bson.json_util import dumps

from event import *
from user import *
from forms import *

app = Flask("mydb")
app.debug = True
mongo = PyMongo(app)

def checkLoggedIn():
    if request.cookies.get('fbsr_1055849787782314') != None:
        session['logged_in'] = True
        user_id = parseSignedRequest(request.cookies.get('fbsr_1055849787782314'))

        user = mongo.db.users.find({'_id': user_id})[0]
        name = user['name']
        session['name'] = "%s %s" % (name['first'], name['last'])
        session['uid'] = user_id

        session.modified = True
        return True

    else:
        session['logged_in'] = False
        session.modified = True
        return False


@app.route("/")
def hello():
    checkLoggedIn() # must be called in each view
    return render_template("map.html", events=generateEvents(mongo))


@app.route("/event/<eventid>")
def event(eventid):
    checkLoggedIn()
    event = getEvent(mongo, eventid)
    if event == None:
        abort(404)

    session['attending'] = (session['uid'] in event.attending_ids)
    session.modified = True

    return render_template("event.html", event=event)


@app.route("/events/")
def events():
    checkLoggedIn()
    return render_template("eventsList.html", events=generateEvents(mongo))

@app.route("/join/<eventid>")
def join(eventid):
    loggedIn = checkLoggedIn()
    if not loggedIn:
        return redirect(url_for('hello'))

    event = getEvent(mongo, eventid)
    if event == None:
        abort(404)

    attending = []
    if type(event.attending_ids) == list:
        attending = event.attending_ids
        print "before:", attending
        if session['uid'] not in event.attending_ids:
            attending.append(session['uid'])
    else:
        attending.append(session['uid'])

    mongo.db.events.update({"_id": eventid},{"$set":{"attending":attending}})

    return redirect(url_for('event', eventid=eventid))

@app.route("/leave/<eventid>")
def leave(eventid):
    loggedIn = checkLoggedIn()
    if not loggedIn:
        return redirect(url_for('hello'))

    event = getEvent(mongo, eventid)
    if event == None:
        abort(404)

    attending = []
    if type(event.attending_ids) == list:
        attending = event.attending_ids
        if session['uid'] in event.attending_ids:
            attending = attending.remove(session['uid'])

    if attending != event.attending_ids:
        mongo.db.events.update({"_id": eventid},{"$set":{"attending":attending}})

    return redirect(url_for('event', eventid=eventid))




@app.route("/create", methods=['GET', 'POST'])
def createEvent():
    form = createEventForm(request.form)
    loggedIn = checkLoggedIn()
    if not loggedIn:
        return redirect(url_for('hello'))

    tags = form['tags'].data

    if request.method == 'POST':
        if form.validate():
            tags = form['tags'].data.split(',')
            for i in range(0, len(tags)):
                tags[i] = tags[i].strip()
            tags2 = ['a', 'b']
            uid = str(uuid.uuid4())
            creator_id = parseSignedRequest(request.cookies.get('fbsr_1055849787782314'))
            test = {
                "_id": uid,
                "creator_id": creator_id,
                "title": form['title'].data.decode('unicode-escape'),
                "description": form['description'].data.decode('unicode-escape'),
                "location": {
                    "address": form['address'].data.decode('unicode-escape'),
                    "streetAddress": form['street_address'].data.decode('unicode-escape')
                },
                "start_date": form['start_datetime'].data,
                "end_date": form['end_datetime'].data,
            }
            test['tags'] = tags
            result = mongo.db.events.insert_one(test)
            return redirect(url_for('hello'))
    return render_template("create_event.html", form=form)

@app.errorhandler(404)
def page_not_found(error):
    checkLoggedIn()
    msgs = ["Sorry", "Whoops", "Uh-oh", "Oops!", "You broke it.", "You done messed up, A-a-ron!"]
    choice = random.choice(msgs) #choose one randomly from above
    return render_template('page_not_found.html', choice=choice), 404

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

if __name__ == "__main__":
    app.secret_key = 'supersecretsecretkey'
    app.run()
