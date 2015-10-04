from flask import Flask
from flask import render_template

<<<<<<< HEAD
from event import *

app = Flask(__name__)
app.debug = True


@app.route("/")
def hello():
    return render_template("map.html", events=constructTestEvents())

=======
app = Flask(__name__)
app.debug = True

@app.route("/")
def hello():
    return render_template("map.html")
>>>>>>> c9e8008da9406cf999e276ff8f7a52624edbe725

if __name__ == "__main__":
    app.run()
