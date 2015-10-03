from flask import Flask
from flask import render_template

from event import *

app = Flask(__name__)
app.debug = True


@app.route("/")
def hello():
    return render_template("map.html", events=constructTestEvents())


if __name__ == "__main__":
    app.run()
