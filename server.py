from flask import Flask
from flask import request
from flask.ext.pymongo import PyMongo
from flask import render_template, abort
from flask import session

from event import *

app = Flask("mydb")
app.debug = True
mongo = PyMongo(app)

def checkLoggedIn():
    if request.cookies.get('fbsr_1055849787782314') != None:
        session['logged_in'] = True
        session.modified = True
    else:
        session['logged_in'] = False
        session.modified = True

@app.route("/")
def hello():
    checkLoggedIn()
    return render_template("map.html", events=constructTestEvents(mongo))


@app.route("/event/<eventid>")
def event(eventid):
    event = getEvent(mongo, eventid)
    if event == None:
        abort(404)
    return render_template("event.html", event=event)


@app.route("/events/")
def events():
    return render_template("eventsList.html", events=constructTestEvents(mongo))

@app.errorhandler(404)
def page_not_found(error):
    msgs = ["Sorry", "Whoops", "Uh-oh", "Oops!", "You broke it.", "You done messed up, A-a-ron!"]
    choice = random.choice(msgs) #choose one randomly from above
    return render_template('page_not_found.html', choice=choice), 404

if __name__ == "__main__":
    app.secret_key = 'supersecretsecretkey'
    app.run()
