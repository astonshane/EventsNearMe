from flask import Flask
from flask.ext.pymongo import PyMongo
from flask import render_template

from event import *

app = Flask("mydb")
app.debug = True
mongo = PyMongo(app)


@app.route("/")
def hello():
    return render_template("map.html", events=constructTestEvents(mongo))


@app.route("/event/<eventid>")
def event(eventid):
    return render_template("event.html", event=eventid)


if __name__ == "__main__":
    app.run()
